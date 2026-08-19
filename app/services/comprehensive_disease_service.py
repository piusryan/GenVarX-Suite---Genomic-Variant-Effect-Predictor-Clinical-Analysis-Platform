"""
Comprehensive Variant-to-Disease Query Service

Aggregates disease information from multiple external APIs:
  - Ensembl VEP: Variant effect prediction & rsID resolution
  - MyVariant.info / ClinVar: Clinical significance & conditions
  - Ensembl Variation: Gene lookup for direct rsID input
  - GWAS Catalog (EBI): Trait associations with p-values
  - NCBI E-utilities (PubMed): Related publications

Provides a unified, reciprocal search pipeline:
  Variant Coordinate → RSID → Disease Associations
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from app.services.vep_service import fetch_vep_annotation
from app.services.clinvar_service import fetch_clinvar_data
from app.services.gwas_service import fetch_gwas_associations


# ── External API Endpoints ─────────────────────────────────────────────
ENSEMBL_REST = "https://rest.ensembl.org"
NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

_HEADERS_JSON = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "GenVarX/1.0"}
_HEADERS_XML = {"Accept": "application/xml", "User-Agent": "GenVarX/1.0"}


# ── Ensembl Variation Lookup (rsID → gene & variant details) ──────────
async def _ensembl_variation(rsid: str) -> Dict[str, Any]:
    """
    Query Ensembl REST /variation/human/{rsid} to resolve an rsID
    to its mapped gene, consequence terms, and genomic coordinates.
    """
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            res = await client.get(
                f"{ENSEMBL_REST}/variation/human/{rsid}",
                params={"content-type": "application/json"},
                headers=_HEADERS_JSON,
            )
            if res.status_code != 200:
                return {"gene": None, "consequence": None}

            data = res.json()

            # Extract gene from most_severe_consequence
            gene = None
            consequence = None
            msc = data.get("most_severe_consequence")
            if msc and isinstance(msc, list):
                for entry in msc:
                    if isinstance(entry, dict):
                        gene = gene or entry.get("gene_symbol")
                        consequence = entry.get("consequence_terms", [""])[0] if entry.get("consequence_terms") else None

            # Fallback: extract gene from genomic mappings
            if not gene:
                mappings = data.get("mappings", [])
                if isinstance(mappings, list):
                    for m in mappings:
                        if isinstance(m, dict) and m.get("gene_symbol"):
                            gene = m["gene_symbol"]
                            break

            return {
                "gene": gene,
                "consequence": consequence,
                "rsid": data.get("name", rsid),
            }
        except Exception as e:
            print(f"[DISEASE] Ensembl variation error: {e}")
            return {"gene": None, "consequence": None}


# ── ClinVar via MyVariant.info ─────────────────────────────────────────
async def _clinvar_data(variant_input: str) -> Dict[str, Any]:
    """
    Fetch clinical significance and associated conditions from
    ClinVar via the MyVariant.info aggregation API.
    """
    try:
        result = await fetch_clinvar_data(variant_input)
        clin_sig = result.get("clinical_significance", "")
        diseases = result.get("associated_diseases", [])

        is_found = clin_sig and "Not Found" not in clin_sig and "Uncertain" not in clin_sig
        disease_entries = [
            {"disease": d, "clinical_significance": clin_sig, "source": "ClinVar"}
            for d in diseases if d and d.strip()
        ]

        return {
            "clinical_significance": clin_sig if is_found else None,
            "diseases": disease_entries,
            "found": is_found,
        }
    except Exception as e:
        print(f"[DISEASE] ClinVar error: {e}")
        return {"clinical_significance": None, "diseases": [], "found": False}


# ── GWAS Catalog (EBI REST API + local TSV fallback) ──────────────────
async def _gwas_data(rsid: str) -> Dict[str, Any]:
    """
    Fetch GWAS trait associations from the EBI GWAS Catalog REST API.
    Falls back to the local TSV dump when the API is unreachable.
    """
    try:
        associations = await fetch_gwas_associations(rsid, limit=20)
        trait_entries = [
            {
                "disease": a.get("trait", "Unknown"),
                "pvalue": a.get("pvalue"),
                "gene": a.get("gene") or None,
                "study_id": a.get("study_accession") or None,
                "pubmed_id": a.get("pubmed_id") or None,
                "risk_allele": a.get("strongest_allele") or None,
                "source": "GWAS Catalog",
            }
            for a in associations
        ]
        return {"associations": trait_entries, "found": len(trait_entries) > 0}
    except Exception as e:
        print(f"[DISEASE] GWAS error: {e}")
        return {"associations": [], "found": False}


# ── PubMed Literature Search (NCBI E-utilities) ───────────────────────
async def _pubmed_search(gene: str, disease_terms: List[str] = None) -> List[Dict[str, Any]]:
    """
    Search PubMed for recent publications related to the gene and
    optionally filtered by disease keywords.  Returns up to 10 articles.
    """
    if not gene or gene == "N/A":
        return []

    # Build query: gene + first disease term (or generic "disease")
    disease_word = "disease"
    if disease_terms:
        first = disease_terms[0]
        if first and len(first) < 50:
            disease_word = first.split(",")[0].split("/")[0].strip()

    query = f"{gene}[Gene] AND {disease_word}[Title/Abstract]"

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            # Step 1: Search for article IDs
            search_res = await client.get(
                f"{NCBI_EUTILS}/esearch.fcgi",
                params={
                    "db": "pubmed",
                    "term": query,
                    "retmax": "10",
                    "sort": "relevance",
                    "retmode": "json",
                },
                headers=_HEADERS_XML,
            )
            if search_res.status_code != 200:
                return []

            search_data = search_res.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return []

            # Step 2: Fetch article summaries
            fetch_res = await client.get(
                f"{NCBI_EUTILS}/esummary.fcgi",
                params={"db": "pubmed", "id": ",".join(id_list), "retmode": "json"},
                headers=_HEADERS_XML,
            )
            if fetch_res.status_code != 200:
                return []

            summaries = fetch_res.json().get("result", {})
            publications = []
            for uid in id_list:
                article = summaries.get(uid, {})
                if not isinstance(article, dict):
                    continue
                publications.append({
                    "title": article.get("title", "Untitled"),
                    "authors": ", ".join(
                        a.get("name", "") for a in article.get("authors", [])[:3]
                    ) + ("..." if len(article.get("authors", [])) > 3 else ""),
                    "journal": article.get("fulljournalname", article.get("source", "Unknown")),
                    "year": article.get("pubdate", "")[:4],
                    "pubmed_id": uid,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                })

            return publications
        except Exception as e:
            print(f"[DISEASE] PubMed error: {e}")
            return []


# ── Gene Summary (NCBI Gene API) ──────────────────────────────────────
async def _gene_summary(gene_symbol: str) -> Dict[str, Any]:
    """Fetch gene description and location from NCBI Gene."""
    if not gene_symbol or gene_symbol == "N/A":
        return {}

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            res = await client.get(
                f"https://mygene.info/v3/query",
                params={"q": gene_symbol, "species": "human", "fields": "symbol,name,summary,type_of_gene,genomic_pos", "size": "1"},
                headers=_HEADERS_JSON,
            )
            if res.status_code != 200:
                return {"symbol": gene_symbol}

            hits = res.json().get("hits", [])
            if not hits:
                return {"symbol": gene_symbol}

            hit = hits[0]
            return {
                "symbol": hit.get("symbol", gene_symbol),
                "full_name": hit.get("name", ""),
                "description": hit.get("summary", "")[:500] if hit.get("summary") else "",
                "gene_type": hit.get("type_of_gene", ""),
            }
        except Exception as e:
            print(f"[DISEASE] Gene summary error: {e}")
            return {"symbol": gene_symbol}


# ══════════════════════════════════════════════════════════════════════
#  MAIN AGGREGATOR
# ══════════════════════════════════════════════════════════════════════
async def get_comprehensive_disease(variant_input: str) -> Dict[str, Any]:
    """
    Comprehensive Variant-to-Disease query.

    Accepts either:
      - Genomic coordinate: "7:140753336:A:T"  (GRCh38)
      - RSID directly:      "rs113488022"

    Pipeline:
      1. Resolve variant → rsID  (Ensembl VEP)
      2. Fetch clinical significance (MyVariant / ClinVar)
      3. Fetch GWAS trait associations (EBI GWAS Catalog)
      4. Fetch gene metadata (NCBI / mygene.info)
      5. Fetch related publications (PubMed E-utilities)

    Returns a unified dict with all disease evidence aggregated.
    """
    variant_input = variant_input.strip()
    is_rsid = variant_input.lower().startswith("rs") and ":" not in variant_input

    # ── Phase 1: Resolve variant / rsID ────────────────────────────
    vep_result = None
    resolved_rsid = variant_input if is_rsid else None
    gene_symbol = None
    consequence = None
    sift = None
    polyphen = None
    impact = None
    amino_acid = None
    variant_display = variant_input

    if not is_rsid:
        try:
            vep_result = await fetch_vep_annotation(variant_input)
            resolved_rsid = getattr(vep_result, "rs_id", None)
            gene_symbol = getattr(vep_result, "gene_symbol", None)
            consequence = getattr(vep_result, "consequence", None)
            sift = getattr(vep_result, "sift_prediction", None)
            polyphen = getattr(vep_result, "polyphen_prediction", None)
            impact = getattr(vep_result, "impact_level", None)
            amino_acid = getattr(vep_result, "amino_acid_change", None)
        except Exception as e:
            print(f"[DISEASE] VEP error: {e}")

    # ── Phase 2: Parallel API calls ────────────────────────────────
    clinvar_in = variant_input if not is_rsid else f"{variant_input}:N:N:N"
    ensembl_rsid = resolved_rsid or (variant_input if is_rsid else None)
    gwas_rsid = resolved_rsid or (variant_input if is_rsid else None)

    clinvar_res = {"clinical_significance": None, "diseases": [], "found": False}
    ensembl_res = {"gene": None, "consequence": None}
    gwas_res = {"associations": [], "found": False}
    publications = []
    gene_info = {}

    # Only call APIs that have valid input
    tasks = {}
    if not is_rsid:
        tasks["clinvar"] = _clinvar_data(variant_input)
    if ensembl_rsid:
        tasks["ensembl"] = _ensembl_variation(ensembl_rsid)
    if gwas_rsid:
        tasks["gwas"] = _gwas_data(gwas_rsid)

    if tasks:
        keys = list(tasks.keys())
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        result_map = dict(zip(keys, results))

        clinvar_res = result_map.get("clinvar", clinvar_res)
        if isinstance(clinvar_res, Exception):
            clinvar_res = {"clinical_significance": None, "diseases": [], "found": False}

        ensembl_res = result_map.get("ensembl", ensembl_res)
        if isinstance(ensembl_res, Exception):
            ensembl_res = {"gene": None, "consequence": None}

        gwas_res = result_map.get("gwas", gwas_res)
        if isinstance(gwas_res, Exception):
            gwas_res = {"associations": [], "found": False}

    # Resolve gene from Ensembl if VEP didn't provide one
    if (not gene_symbol or gene_symbol == "N/A") and ensembl_res.get("gene"):
        gene_symbol = ensembl_res["gene"]
    if (not consequence or consequence == "N/A") and ensembl_res.get("consequence"):
        consequence = ensembl_res["consequence"]

    # Fetch gene details and publications (depend on gene_symbol)
    if gene_symbol and gene_symbol != "N/A":
        try:
            gene_info = await _gene_summary(gene_symbol)
        except Exception:
            gene_info = {"symbol": gene_symbol}

        disease_terms = [a["disease"] for a in gwas_res.get("associations", [])[:3]]
        try:
            publications = await _pubmed_search(gene_symbol, disease_terms)
        except Exception:
            publications = []

    # ── Phase 3: Aggregate results ─────────────────────────────────
    disease_associations = []
    seen = set()

    # ClinVar diseases
    for d in clinvar_res.get("diseases", []):
        key = d["disease"].lower().strip()
        if key not in seen:
            seen.add(key)
            disease_associations.append(d)

    # GWAS diseases
    for a in gwas_res.get("associations", []):
        key = a["disease"].lower().strip()
        if key not in seen:
            seen.add(key)
            disease_associations.append({
                "disease": a["disease"],
                "pvalue": a.get("pvalue"),
                "gene": a.get("gene"),
                "study_id": a.get("study_id"),
                "pubmed_id": a.get("pubmed_id"),
                "risk_allele": a.get("risk_allele"),
                "source": "GWAS Catalog",
            })

    return {
        "variant_input": variant_input,
        "variant_display": variant_display,
        "resolved_rsid": resolved_rsid,
        "gene_info": {
            "gene_symbol": gene_symbol or "N/A",
            "full_name": gene_info.get("full_name", ""),
            "description": gene_info.get("description", ""),
            "gene_type": gene_info.get("type_of_gene", ""),
            "consequence": consequence or "N/A",
            "sift_prediction": sift or "N/A",
            "polyphen_prediction": polyphen or "N/A",
            "impact_level": impact or "N/A",
            "amino_acid_change": amino_acid or "N/A",
        },
        "clinical_significance": clinvar_res.get("clinical_significance") or "Not Available",
        "disease_associations": disease_associations,
        "gwas_findings": gwas_res.get("associations", []),
        "publications": publications,
        "source_counts": {
            "clinvar_conditions": len(clinvar_res.get("diseases", [])),
            "gwas_traits": len(gwas_res.get("associations", [])),
            "publications": len(publications),
            "total_associations": len(disease_associations),
        },
    }
