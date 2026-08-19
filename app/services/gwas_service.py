import asyncio
import httpx
from typing import Any, Dict, List, Optional

GWAS_CATALOG_BASE_URL = "https://www.ebi.ac.uk/gwas/rest/api"

_study_cache: Dict[str, Dict[str, Optional[str]]] = {}
_study_cache_lock = asyncio.Lock()


async def fetch_gwas_associations(rs_id: str, limit: int = 20) -> List[Dict[str, Any]]:
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
