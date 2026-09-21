import httpx
from typing import Dict, Any, List, Optional

MYVARIANT_URL = "https://myvariant.info/v1"


async def _myvariant_query(
    client: httpx.AsyncClient,
    query_str: str,
    hg38: bool = False,
) -> List[Dict[str, Any]]:
    """Run a MyVariant.info query and return raw hits (empty list on failure)."""
    params = {"q": query_str, "fields": "clinvar", "size": "10"}
    if hg38:
        params["hg38"] = "true"

    res = await client.get(
        f"{MYVARIANT_URL}/query",
        params=params,
        headers={"Accept": "application/json", "User-Agent": "GenVarX-App/1.0"},
    )
    if res.status_code != 200:
        return []
    return res.json().get("hits", [])


def _clinvar_records_from_hits(
    hits: List[Dict[str, Any]],
    ref: Optional[str] = None,
    alt: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Flatten `clinvar` entries from query hits. When both ref and alt are known,
    skip hits that clearly describe a different allele.
    """
    records = []
    for hit in hits:
        if ref is not None and alt is not None:
            hit_ref = hit.get("ref")
            hit_alt = hit.get("alt")
            if hit_ref is not None or hit_alt is not None:
                ref_ok = hit_ref is None or str(hit_ref) == str(ref)
                alt_ok = hit_alt is None or str(hit_alt) == str(alt)
                if not (ref_ok and alt_ok):
                    continue

        cdata = hit.get("clinvar")
        if isinstance(cdata, list):
            records.extend(cdata)
        elif isinstance(cdata, dict):
            records.append(cdata)
    return records


async def fetch_clinvar_data(
    variant_str: str,
    rsid: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        chrom = pos = ref = alt = None
        is_rsid_input = variant_str.lower().startswith("rs") and ":" not in variant_str

        if is_rsid_input:
            rsid = rsid or variant_str
        elif rsid is None:
            try:
                clean_var = variant_str.replace("chr", "").strip()
                chrom, pos, ref, alt = clean_var.split(":")
            except ValueError:
                return {"clinical_significance": "Invalid Format", "associated_diseases": []}

        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            clinvar_records = []

            # 1. rsID lookup (assembly-agnostic — reliable for both hg19/hg38)
            if rsid:
                hits = await _myvariant_query(client, f"dbsnp.rsid:{rsid}")
                clinvar_records = _clinvar_records_from_hits(hits, ref=ref, alt=alt)

            # 2. Coordinate region lookups (fallback when no rsID or empty result)
            if not clinvar_records and chrom and pos:
                for hg38_flag in (False, True):
                    hits = await _myvariant_query(
                        client, f"chr{chrom}:{pos}-{pos}", hg38=hg38_flag
                    )
                    clinvar_records = _clinvar_records_from_hits(hits, ref=ref, alt=alt)
                    if clinvar_records:
                        break

            if not clinvar_records:
                return {
                    "clinical_significance": "Uncertain Significance / Not Found in ClinVar",
                    "associated_diseases": [],
                }

            sig_set = set()
            diseases = set()

            for record in clinvar_records:
                rcv_data = record.get("rcv", [])
                if isinstance(rcv_data, dict):
                    rcv_data = [rcv_data]
                elif not isinstance(rcv_data, list):
                    rcv_data = []

                for entry in rcv_data:
                    if isinstance(entry, dict):
                        sig = entry.get("clinical_significance")
                        if sig:
                            sig_set.add(str(sig).strip())

                        conditions = entry.get("conditions", {})
                        if isinstance(conditions, dict):
                            name = conditions.get("name")
                            if name and str(name).lower() != "not provided":
                                diseases.add(str(name).strip())
                        elif isinstance(conditions, list):
                            for cond in conditions:
                                if isinstance(cond, dict) and cond.get("name"):
                                    c_name = cond["name"]
                                    if c_name and str(c_name).lower() != "not provided":
                                        diseases.add(str(c_name).strip())

                top_sig = record.get("clinsig")
                if top_sig:
                    if isinstance(top_sig, list):
                        for s in top_sig:
                            sig_set.add(str(s).strip())
                    elif isinstance(top_sig, str):
                        sig_set.add(top_sig.strip())

            significance = ", ".join(sorted(sig_set)) if sig_set else "Uncertain Significance"
            disease_list = list(diseases)[:5]

            return {
                "clinical_significance": significance.title(),
                "associated_diseases": disease_list,
            }

    except Exception:
        return {
            "clinical_significance": "Uncertain Significance / Not Found in ClinVar",
            "associated_diseases": [],
        }