import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import VariantRequest, VariantAnnotation, GwasResponse, GwasAssociation, CompoundSummary, CompoundDetail
from app.services.vep_service import fetch_vep_annotation
from app.services.clinvar_service import fetch_clinvar_data
from app.services.gwas_service import fetch_gwas_associations
from app.services.chembl_local_service import search_compounds, get_compound
from app.services.hpo_service import fetch_phenotypes_for_disease
from app.services.motif_service import analyze_variant_motif_impact
from app.services.conservation_service import calculate_substitution_cost

app = FastAPI(title="GenVarX Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "online", "service": "GenVarX Engine"}

@app.post("/api/annotate", response_model=VariantAnnotation)
async def annotate(payload: VariantRequest):
    # Fire VEP and ClinVar lookups simultaneously in parallel
    vep_task = fetch_vep_annotation(payload.variant)
    clinvar_task = fetch_clinvar_data(payload.variant)

    vep_result, clinvar_result = await asyncio.gather(vep_task, clinvar_task)

    # 1. Check if ClinVar service found a direct match
    clinvar_sig = clinvar_result.get("clinical_significance", "")
    clinvar_diseases = clinvar_result.get("associated_diseases", [])
    
    is_clinvar_found = clinvar_sig and "Not Found in ClinVar" not in clinvar_sig

    # 2. Smart fallback: Prefer MyVariant -> Fallback to VEP colocated ClinVar -> Default to Not Found
    final_sig = (
        clinvar_sig if is_clinvar_found 
        else getattr(vep_result, "clinical_significance", "Uncertain Significance / Not Found in ClinVar")
    )
    
    final_diseases = (
        clinvar_diseases if (is_clinvar_found and clinvar_diseases) 
        else getattr(vep_result, "associated_diseases", [])
    )

    return VariantAnnotation(
        variant=vep_result.variant,
        rs_id=getattr(vep_result, "rs_id", None),
        gene_symbol=vep_result.gene_symbol,
        consequence=vep_result.consequence,
        sift_prediction=vep_result.sift_prediction,
        polyphen_prediction=vep_result.polyphen_prediction,
        amino_acid_change=vep_result.amino_acid_change,
        impact_level=vep_result.impact_level,
        clinical_significance=final_sig,
        associated_diseases=final_diseases
    )


@app.post("/api/gwas", response_model=GwasResponse)
async def gwas(payload: VariantRequest):
    vep_result = await fetch_vep_annotation(payload.variant)
    rs_id = getattr(vep_result, "rs_id", None)
    if not rs_id:
        return GwasResponse(rs_id=None, associations=[], note="rsID not found for this variant")

    assoc_rows = await fetch_gwas_associations(rs_id, limit=20)
    associations = [GwasAssociation(**row) for row in assoc_rows]
    note = None if associations else "No GWAS Catalog associations found"

    return GwasResponse(rs_id=rs_id, associations=associations, note=note)


@app.get("/api/compounds", response_model=list[CompoundSummary])
async def compounds(query: str = "", limit: int = 20):
    try:
        rows = await search_compounds(query=query, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    out = []
    for r in rows:
        out.append(
            CompoundSummary(
                chembl_id=str(r.get("Compound ChEMBL ID") or ""),
                name=r.get("Name") or None,
                compound_type=r.get("Type") or None,
                max_phase=r.get("Max Phase") or None,
                molecular_weight=r.get("Molecular Weight") or None,
                alogp=r.get("AlogP") or None,
                qed_weighted=r.get("QED Weighted") or None,
                targets=r.get("Targets") or None,
                bioactivities=r.get("Bioactivities") or None,
            )
        )
    return out


@app.get("/api/compounds/{chembl_id}", response_model=CompoundDetail)
async def compound_details(chembl_id: str):
    try:
        r = await get_compound(chembl_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not r:
        return CompoundDetail(chembl_id=chembl_id)

    return CompoundDetail(
        chembl_id=str(r.get("Compound ChEMBL ID") or chembl_id),
        name=r.get("Name") or None,
        compound_type=r.get("Type") or None,
        max_phase=r.get("Max Phase") or None,
        molecular_weight=r.get("Molecular Weight") or None,
        alogp=r.get("AlogP") or None,
        qed_weighted=r.get("QED Weighted") or None,
        targets=r.get("Targets") or None,
        bioactivities=r.get("Bioactivities") or None,
        synonyms=r.get("Synonyms") or None,
        polar_surface_area=r.get("Polar Surface Area") or None,
        hba=r.get("HBA") or None,
        hbd=r.get("HBD") or None,
        ro5_violations=r.get("#RO5 Violations") or None,
        rotatable_bonds=r.get("#Rotatable Bonds") or None,
        passes_ro3=r.get("Passes Ro3") or None,
        aromatic_rings=r.get("Aromatic Rings") or None,
        structure_type=r.get("Structure Type") or None,
        inorganic_flag=r.get("Inorganic Flag") or None,
        heavy_atoms=r.get("Heavy Atoms") or None,
        np_likeness_score=r.get("Np Likeness Score") or None,
        molecular_formula=r.get("Molecular Formula") or None,
        smiles=r.get("Smiles") or None,
        inchi_key=r.get("Inchi Key") or None,
        inchi=r.get("Inchi") or None,
        withdrawn_flag=r.get("Withdrawn Flag") or None,
        orphan=r.get("Orphan") or None,
    )


@app.post("/api/phenotypes")
async def get_disease_phenotypes(payload: VariantRequest):
    """Fetch HPO phenotypes associated with a disease name."""
    disease_name = payload.variant  # Reusing variant field for disease name
    try:
        phenotypes = await fetch_phenotypes_for_disease(disease_name)
        return {
            "disease": disease_name,
            "phenotypes": phenotypes,
            "count": len(phenotypes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/motif-analysis")
async def analyze_motif(
    gene_symbol: str,
    ref_aa: str,
    alt_aa: str,
    protein_position: int = None
):
    """Analyze if variant disrupts functional motifs/domains."""
    try:
        result = await analyze_variant_motif_impact(
            protein_sequence="",  # Optional if only checking position
            variant_position=protein_position or 0,
            ref_aa=ref_aa,
            alt_aa=alt_aa,
            gene_symbol=gene_symbol
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conservation-score")
async def get_conservation_score(ref_aa: str, alt_aa: str):
    """Calculate BLOSUM62 conservation score for amino acid substitution."""
    try:
        score, classification = calculate_substitution_cost(ref_aa, alt_aa)
        return {
            "ref_amino_acid": ref_aa,
            "alt_amino_acid": alt_aa,
            "blosum62_score": score,
            "impact_classification": classification,
            "interpretation": {
                "BENIGN": "Conservative substitution - likely tolerated",
                "TOLERATED": "Moderately conservative - may be tolerated",
                "DELETERIOUS": "Non-conservative - likely damaging",
                "SEVERE": "Highly disruptive substitution"
            }.get(classification, "Unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
