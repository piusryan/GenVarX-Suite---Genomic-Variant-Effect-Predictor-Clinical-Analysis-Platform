import httpx
from typing import Dict, Any

MYVARIANT_URL = "https://myvariant.info/v1"

async def fetch_clinvar_data(variant_str: str) -> Dict[str, Any]:
    try:
        clean_var = variant_str.replace("chr", "").strip()
        chrom, pos, ref, alt = clean_var.split(":")
    except ValueError:
        return {"clinical_significance": "Invalid Format", "associated_diseases": []}

    headers = {
        "Accept": "application/json",
        "User-Agent": "GenVarX-App/1.0"
    }
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            # 1. Flexible query searching both hg38 and hg19 indexes
            query_str = (
                f"chrom:{chrom} AND "
                f"(hg38.start:{pos} OR hg19.start:{pos} OR vcf.pos:{pos}) AND "
                f"(vcf.ref:{ref} OR hg38.ref:{ref}) AND "
                f"(vcf.alt:{alt} OR hg38.alt:{alt})"
            )
            
            res = await client.get(
                f"{MYVARIANT_URL}/query", 
                params={"q": query_str, "fields": "clinvar"}, 
                headers=headers
            )
            
            clinvar_records = []
            if res.status_code == 200:
                hits = res.json().get("hits", [])
                for hit in hits:
                    if "clinvar" in hit:
                        cdata = hit["clinvar"]
                        if isinstance(cdata, list):
                            clinvar_records.extend(cdata)
                        elif isinstance(cdata, dict):
                            clinvar_records.append(cdata)

            # 2. Fallback: Try direct HGVS ID if search returned empty
            if not clinvar_records:
                hgvs_id = f"chr{chrom}:g.{pos}{ref}>{alt}"
                direct_res = await client.get(f"{MYVARIANT_URL}/variant/{hgvs_id}", headers=headers)
                if direct_res.status_code == 200:
                    cdata = direct_res.json().get("clinvar")
                    if isinstance(cdata, list):
                        clinvar_records.extend(cdata)
                    elif isinstance(cdata, dict):
                        clinvar_records.append(cdata)

            if not clinvar_records:
                return {
                    "clinical_significance": "Uncertain Significance / Not Found in ClinVar", 
                    "associated_diseases": []
                }

            sig_set = set()
            diseases = set()

            # Safely iterate through clinvar records regardless of nested structure
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

                # Catch top-level clinical significance strings if present
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
                "associated_diseases": disease_list
            }

        except Exception:
            return {
                "clinical_significance": "Uncertain Significance / Not Found in ClinVar", 
                "associated_diseases": []
            }