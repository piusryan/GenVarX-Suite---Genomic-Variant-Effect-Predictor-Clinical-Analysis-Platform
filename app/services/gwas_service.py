import asyncio
import httpx
from typing import Any, Dict, List, Optional
import pandas as pd
import os

GWAS_CATALOG_BASE_URL = "https://www.ebi.ac.uk/gwas/rest/api"

_study_cache: Dict[str, Dict[str, Optional[str]]] = {}
_study_cache_lock = asyncio.Lock()


async def fetch_gwas_associations(rs_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch GWAS associations from external API or local TSV."""
    
    # First try local GWAS TSV
    local_results = await _fetch_local_gwas(rs_id, limit)
    if local_results:
        return local_results
    
    # Fall back to external API
    headers = {"Accept": "application/json", "User-Agent": "GenVarX-App/1.0"}

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        res = await client.get(
            f"{GWAS_CATALOG_BASE_URL}/singleNucleotidePolymorphisms/{rs_id}/associations",
            params={"projection": "associationBySnp", "size": str(limit)},
            headers=headers,
        )

        if res.status_code != 200:
            return []

        payload = res.json()
        embedded = payload.get("_embedded", {}) if isinstance(payload, dict) else {}
        associations = embedded.get("associations", [])
        if not isinstance(associations, list):
            return []

        out: List[Dict[str, Any]] = []
        sem = asyncio.Semaphore(5)
        enrich_tasks: List[asyncio.Task[None]] = []
        for assoc in associations:
            if not isinstance(assoc, dict):
                continue

            row: Dict[str, Any] = {
                "trait": _extract_trait(assoc),
                "pvalue": _extract_pvalue(assoc),
                "reported_trait": None,
                "study_accession": None,
                "pubmed_id": None,
                "strongest_allele": _safe_str(assoc.get("strongestAllele")),
            }
            out.append(row)
            enrich_tasks.append(asyncio.create_task(_enrich_with_study(row, assoc, client, headers, sem)))

        if enrich_tasks:
            await asyncio.gather(*enrich_tasks)

        return out


async def _fetch_local_gwas(rs_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch GWAS data from local TSV file.
    Actual column names in the GWAS Catalog dump:
      SNPS, DISEASE/TRAIT, P-VALUE, MAPPED_GENE, STUDY, PUBMEDID,
      STRONGEST SNP-RISK ALLELE, OR or BETA, CHR_ID, CHR_POS
    Scans entire file via chunked pandas read (no 10K row artificial cap).
    """
    try:
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"
        if not os.path.exists(gwas_path):
            return []

        test_df = pd.read_csv(gwas_path, sep='\t', low_memory=False, nrows=1)
        all_cols = list(test_df.columns)

        def pick_col(candidates):
            for c in candidates:
                if c in all_cols:
                    return c
            return None

        col_snp = pick_col(['SNPS', 'variant_id', 'snp_id', 'SNP_ID_CURRENT'])
        col_disease = pick_col(['DISEASE/TRAIT', 'disease_trait', 'Disease/Trait'])
        col_pval = pick_col(['P-VALUE', 'p_value', 'PVALUE'])
        col_gene = pick_col(['MAPPED_GENE', 'mapped_gene', 'Mapped Gene'])
        col_study = pick_col(['STUDY', 'study_accession', 'STUDY ACCESSION'])
        col_pmid = pick_col(['PUBMEDID', 'pubmed_id', 'PUBMED ID'])
        col_risk = pick_col(['STRONGEST SNP-RISK ALLELE', 'risk_allele', 'RISK ALLELE'])
        col_or = pick_col(['OR or BETA', 'or_or_beta', 'OR_BETA'])

        if not col_snp:
            return []

        usecols = [c for c in (col_snp, col_disease, col_pval, col_gene,
                               col_study, col_pmid, col_risk, col_or) if c]

        rs_lower = rs_id.lower()
        collected: List[Dict[str, Any]] = []
        chunksize = 100000
        for chunk in pd.read_csv(gwas_path, sep='\t', low_memory=False, dtype=str,
                                 usecols=usecols, chunksize=chunksize):
            mask = chunk[col_snp].fillna('').astype(str).str.lower().str.contains(rs_lower, regex=False, na=False)
            matched = chunk[mask].head(max(1, limit - len(collected)))
            if matched.empty:
                continue
            for _, row in matched.iterrows():
                def getval(col):
                    if col is None or col not in row.index:
                        return ''
                    v = row.get(col)
                    if pd.isna(v):
                        return ''
                    return str(v)

                trait_val = getval(col_disease) or 'Unknown'
                pval_val = getval(col_pval) or 'N/A'
                gene_val = getval(col_gene) or ''
                study_val = getval(col_study) or ''
                pmid_val = getval(col_pmid) or ''
                risk_val = getval(col_risk) or ''
                or_val = getval(col_or) or ''

                collected.append({
                    "trait": trait_val,
                    "pvalue": pval_val if pval_val != 'N/A' else None,
                    "reported_trait": trait_val if trait_val != 'Unknown' else None,
                    "study_accession": study_val[:60] if study_val else None,
                    "pubmed_id": pmid_val if pmid_val else None,
                    "strongest_allele": risk_val if risk_val else None,
                    "or_value": or_val if or_val else None,
                    "gene": gene_val if gene_val else None,
                })
            if len(collected) >= limit:
                break

        return collected[:limit]
    except Exception as e:
        print(f"[GWAS] Local TSV search error: {e}")
        return []


def _extract_trait(assoc: Dict[str, Any]) -> str:
    efo_traits = assoc.get("efoTraits")
    if isinstance(efo_traits, list):
        traits: List[str] = []
        for t in efo_traits:
            if not isinstance(t, dict):
                continue
            name = _safe_str(t.get("trait"))
            if name:
                traits.append(name)
            if len(traits) >= 3:
                break
        if traits:
            return ", ".join(traits)

    for key in ("traitName", "efoTrait", "mappedLabel", "diseaseTrait"):
        v = _safe_str(assoc.get(key))
        if v:
            return v

    return "Unknown Trait"


def _extract_pvalue(assoc: Dict[str, Any]) -> Optional[str]:
    direct = _safe_str(assoc.get("pvalue"))
    if direct:
        return direct

    mantissa = assoc.get("pvalueMantissa")
    exponent = assoc.get("pvalueExponent")
    if mantissa is None or exponent is None:
        return None

    try:
        return f"{mantissa}e{int(exponent)}"
    except Exception:
        return _safe_str(f"{mantissa}e{exponent}")


def _extract_link(assoc: Dict[str, Any], link_name: str) -> Optional[str]:
    links = assoc.get("_links")
    if not isinstance(links, dict):
        return None
    link = links.get(link_name)
    if not isinstance(link, dict):
        return None
    return _safe_str(link.get("href"))


def _extract_assoc_id(assoc: Dict[str, Any]) -> Optional[str]:
    href = _extract_link(assoc, "self")
    if not href:
        return None
    return href.rstrip("/").split("/")[-1] or None


async def _enrich_with_study(
    row: Dict[str, Any],
    assoc: Dict[str, Any],
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    sem: asyncio.Semaphore,
) -> None:
    assoc_id = _extract_assoc_id(assoc)
    if not assoc_id:
        return

    cached = await _get_cached_study(assoc_id)
    if cached is None:
        async with sem:
            study_url = _extract_link(assoc, "study") or f"{GWAS_CATALOG_BASE_URL}/associations/{assoc_id}/study"
            try:
                res = await client.get(study_url, headers=headers)
            except Exception:
                return
        if res.status_code != 200:
            await _set_cached_study(assoc_id, {})
            return
        payload = res.json()
        if not isinstance(payload, dict):
            await _set_cached_study(assoc_id, {})
            return

        pub = payload.get("publicationInfo", {})
        pubmed_id = None
        if isinstance(pub, dict):
            pubmed_id = _safe_str(pub.get("pubmedId"))

        cached = {
            "study_accession": _safe_str(payload.get("accessionId")),
            "reported_trait": _safe_str(payload.get("diseaseTrait")),
            "pubmed_id": pubmed_id,
        }
        await _set_cached_study(assoc_id, cached)

    if not isinstance(cached, dict):
        return

    if not row.get("study_accession") and cached.get("study_accession"):
        row["study_accession"] = cached["study_accession"]
    if not row.get("pubmed_id") and cached.get("pubmed_id"):
        row["pubmed_id"] = cached["pubmed_id"]
    if not row.get("reported_trait") and cached.get("reported_trait"):
        row["reported_trait"] = cached["reported_trait"]


async def _get_cached_study(assoc_id: str) -> Optional[Dict[str, Optional[str]]]:
    async with _study_cache_lock:
        if assoc_id in _study_cache:
            return _study_cache[assoc_id]
        return None


async def _set_cached_study(assoc_id: str, value: Dict[str, Optional[str]]) -> None:
    async with _study_cache_lock:
        _study_cache[assoc_id] = value


def _safe_str(value: Optional[Any]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        return v if v else None
    if isinstance(value, dict):
        for k in ("trait", "name", "label", "title", "fullname"):
            if k in value:
                v = value.get(k)
                if isinstance(v, str):
                    s = v.strip()
                    return s if s else None
                if v is not None:
                    return str(v)
    return str(value)
