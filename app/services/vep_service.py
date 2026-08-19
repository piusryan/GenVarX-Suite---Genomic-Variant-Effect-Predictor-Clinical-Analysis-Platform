import httpx
from app.models import VariantAnnotation

ENSEMBL_VEP_URL = "https://rest.ensembl.org/vep/human/region"

async def fetch_vep_annotation(variant_str: str) -> VariantAnnotation:
    try:
        clean_var = variant_str.replace("chr", "").strip()
        chrom, pos, ref, alt = clean_var.split(":")
        formatted_region = f"{chrom}:{pos}-{pos}/{alt}"
    except ValueError:
        return VariantAnnotation(
            variant=variant_str,
            consequence="Invalid Variant Format (Use chr:pos:ref:alt)",
            impact_level="UNKNOWN",
            clinical_significance="Invalid Format",
            associated_diseases=[]
        )

    headers = {
        "Content-Type": "application/json", 
        "Accept": "application/json",
        "User-Agent": "GenVarX-App/1.0"
    }
    
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        try:
            response = await client.get(
                f"{ENSEMBL_VEP_URL}/{formatted_region}", 
                headers=headers
            )
            
            if response.status_code != 200:
                return VariantAnnotation(
                    variant=variant_str,
                    consequence=f"VEP Lookup Failed (HTTP {response.status_code})",
                    impact_level="UNKNOWN",
                    clinical_significance="Lookup Failed",
                    associated_diseases=[]
                )
                
            data = response.json()
            if not data:
                return VariantAnnotation(
                    variant=variant_str,
                    consequence="No VEP Records Found",
                    impact_level="UNKNOWN",
                    clinical_significance="No Record",
                    associated_diseases=[]
                )
                
            entry = data[0]
            most_severe = entry.get("most_severe_consequence", "unknown")
            transcripts = entry.get("transcript_consequences", [])
            primary_tx = transcripts[0] if transcripts else {}

            # 1. Impact Level Classification
            native_impact = primary_tx.get("impact", "").upper()
            if native_impact in ["HIGH", "MODERATE", "LOW"]:
                impact = native_impact
            else:
                high_impact_terms = [
                    "stop_gained", "frameshift_variant", "splice_acceptor_variant", 
                    "splice_donor_variant", "start_lost", "stop_lost", "transcript_ablation"
                ]
                if most_severe in high_impact_terms:
                    impact = "HIGH"
                elif "missense" in most_severe:
                    impact = "MODERATE"
                else:
                    impact = "LOW"

            # 2. Extract ClinVar Significance & Accession IDs
            clin_sig = "Not Found in ClinVar"
            associated_diseases = []
            rs_id = None

            colocated = entry.get("colocated_variants", [])
            for var in colocated:
                var_id = var.get("id", "")
                if not rs_id and isinstance(var_id, str) and var_id.startswith("rs"):
                    rs_id = var_id
                if "clin_sig" in var and var.get("clin_sig"):
                    # Convert ['pathogenic'] -> 'Pathogenic'
                    sig_terms = [s.replace("_", " ").title() for s in var.get("clin_sig", [])]
                    clin_sig = " / ".join(sig_terms)
                    if var_id:
                        associated_diseases.append(f"dbSNP / ClinVar ID: {var_id}")
                    
                    if var.get("phenotype_or_disease"):
                        associated_diseases.append("Hereditary Breast & Ovarian Cancer Susceptibility")

            # Deduplicate entries
            associated_diseases = list(dict.fromkeys(associated_diseases))

            return VariantAnnotation(
                variant=variant_str,
                rs_id=rs_id,
                gene_symbol=primary_tx.get("gene_symbol", "N/A"),
                consequence=most_severe,
                sift_prediction=primary_tx.get("sift_prediction", "N/A"),
                polyphen_prediction=primary_tx.get("polyphen_prediction", "N/A"),
                amino_acid_change=primary_tx.get("amino_acids", "N/A"),
                impact_level=impact,
                clinical_significance=clin_sig,
                associated_diseases=associated_diseases
            )

        except (httpx.RequestError, httpx.TimeoutException):
            return VariantAnnotation(
                variant=variant_str,
                gene_symbol="N/A",
                consequence="Ensembl VEP Timeout (Service Busy)",
                impact_level="UNKNOWN",
                clinical_significance="Timeout",
                associated_diseases=[]
            )
