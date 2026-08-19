import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.models import VariantRequest, DiseaseRequest, VariantAnnotation, GwasResponse, GwasAssociation, CompoundSummary, CompoundDetail
from app.services.vep_service import fetch_vep_annotation
from app.services.clinvar_service import fetch_clinvar_data
from app.services.gwas_service import fetch_gwas_associations
from app.services.local_gwas_service import search_local_disease_associations, get_dataset_summary
from app.services.disease_search_service import search_disease_associations, get_available_diseases
from app.services.chembl_local_service import search_compounds, get_compound
from app.services.hpo_service import fetch_phenotypes_for_disease
from app.services.motif_service import analyze_variant_motif_impact
from app.services.conservation_service import calculate_substitution_cost
from app.services.rsid_to_disease_service import get_diseases_by_rsid, get_diseases_by_rsids, get_rsid_gene_disease_mapping

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
    variant_input = payload.variant.strip()
    
    # Check if input is just an RSID (e.g., rs71559014)
    if variant_input.startswith('rs') and ':' not in variant_input:
        # It's an RSID - search in GWAS/ClinVar directly
        rsid_diseases = await get_diseases_by_rsid(variant_input)
        
        diseases = [f"{d['disease']} (Gene: {d['gene']})" for d in rsid_diseases.get('diseases', [])[:3]]
        
        return VariantAnnotation(
            variant=variant_input,
            rs_id=variant_input,
            gene_symbol="Multiple",
            consequence="GWAS Variant",
            sift_prediction="N/A",
            polyphen_prediction="N/A",
            amino_acid_change="N/A",
            impact_level="MODERATE",
            clinical_significance=diseases[0] if diseases else "Common variant",
            associated_diseases=diseases
        )
    
    # Otherwise process as full variant
    vep_task = fetch_vep_annotation(variant_input)
    clinvar_task = fetch_clinvar_data(variant_input)

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
    variant_input = payload.variant.strip()
    rs_id = None
    
    # Check if input is just an RSID
    if variant_input.startswith('rs') and ':' not in variant_input:
        rs_id = variant_input
    else:
        # Otherwise extract from VEP
        vep_result = await fetch_vep_annotation(variant_input)
        rs_id = getattr(vep_result, "rs_id", None)
    
    print(f"[GWAS DEBUG] Input variant: {variant_input}")
    print(f"[GWAS DEBUG] Extracted rsID: {rs_id}")
    
    if not rs_id:
        return GwasResponse(
            rs_id=None, 
            associations=[], 
            note="⚠️ rsID not found for this variant - likely rare/familial variant not in GWAS Catalog"
        )

    assoc_rows = await fetch_gwas_associations(rs_id, limit=20)
    associations = [GwasAssociation(**row) for row in assoc_rows]
    note = None if associations else "✓ rsID found but no GWAS Catalog associations available"

    return GwasResponse(rs_id=rs_id, associations=associations, note=note)


@app.post("/api/gwas/dataset-analysis")
async def gwas_dataset_analysis(payload: VariantRequest):
    """Analyze variant against local datasets and show diagnostic info."""
    import os
    import pandas as pd
    
    variant = payload.variant
    vep_result = await fetch_vep_annotation(variant)
    rs_id = getattr(vep_result, "rs_id", None)
    
    analysis = {
        "variant": variant,
        "vep_extraction": {
            "rs_id": rs_id,
            "gene_symbol": vep_result.gene_symbol,
            "consequence": vep_result.consequence,
            "clinical_significance": vep_result.clinical_significance,
            "associated_diseases": vep_result.associated_diseases,
        },
        "local_datasets": {},
        "gwas_catalog_status": None,
        "diagnostic_message": None
    }
    
    # Check local GWAS data if any
    gwas_dir = "data/datasets"
    if os.path.exists(gwas_dir):
        for subdir in os.listdir(gwas_dir):
            subdir_path = os.path.join(gwas_dir, subdir)
            if os.path.isdir(subdir_path):
                files = os.listdir(subdir_path)
                analysis["local_datasets"][subdir] = {
                    "files": files,
                    "file_count": len(files),
                    "path": subdir_path
                }
    
    # Check GWAS associations
    if rs_id:
        assoc_rows = await fetch_gwas_associations(rs_id, limit=5)
        analysis["gwas_catalog_status"] = {
            "found": len(assoc_rows) > 0,
            "count": len(assoc_rows),
            "associations": assoc_rows
        }
        if assoc_rows:
            analysis["diagnostic_message"] = f"✓ GWAS Catalog: Found {len(assoc_rows)} associations"
        else:
            analysis["diagnostic_message"] = f"⚠️ rsID {rs_id} exists but has no GWAS associations"
    else:
        analysis["gwas_catalog_status"] = {
            "found": False,
            "count": 0,
            "associations": []
        }
        analysis["diagnostic_message"] = "✗ No rsID found - variant not recognized by VEP/GWAS"
    
    return analysis


@app.post("/api/disease-associations")
async def disease_associations(payload: VariantRequest):
    """
    Find disease associations from LOCAL datasets.
    Handles both full variants and RSIDs.
    """
    variant_input = payload.variant.strip()
    
    # Check if input is just an RSID
    if variant_input.startswith('rs') and ':' not in variant_input:
        rsid_result = await get_diseases_by_rsid(variant_input)
        return {
            "variant": variant_input,
            "rsid": variant_input,
            "gene_symbol": "Multiple",
            "local_findings": rsid_result,
            "source": "LOCAL_RSID_MAPPING"
        }
    
    # Otherwise process as full variant
    vep_result = await fetch_vep_annotation(variant_input)
    gene_symbol = vep_result.gene_symbol
    
    # Search local datasets
    local_results = await search_local_disease_associations(variant_input, gene_symbol)
    
    return {
        "variant": variant_input,
        "gene_symbol": gene_symbol,
        "local_findings": local_results,
        "source": "LOCAL_DATASETS"
    }


@app.post("/api/disease-search")
async def search_by_disease(payload: DiseaseRequest):
    """
    Search for disease associations using disease name as input.
    Returns variants, genes, phenotypes, and drugs associated with the disease.
    This is the inverse of the variant-first approach - disease-first search.
    """
    disease_name = payload.disease.strip()
    
    if not disease_name or len(disease_name) < 2:
        raise HTTPException(status_code=400, detail="Disease name must be at least 2 characters")
    
    results = await search_disease_associations(disease_name)
    
    return {
        "disease_query": disease_name,
        "results": results,
        "source": "LOCAL_DISEASE_SEARCH"
    }


@app.get("/api/disease-search/available")
async def list_available_diseases(limit: int = 100):
    """
    Get list of available diseases that can be searched.
    Useful for autocomplete in UI.
    """
    diseases = await get_available_diseases(limit)
    
    return {
        "total_available": len(diseases),
        "diseases": diseases,
        "note": "Diseases from ClinVar disease_names.tsv"
    }


@app.get("/api/datasets/summary")
async def datasets_summary():
    """Get summary of available datasets."""
    summary = await get_dataset_summary()
    return {
        "datasets": summary,
        "timestamp": "2024",
        "note": "Shows first 10 entries per dataset"
    }



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



@app.get("/api/rsid-to-disease/{rsid}")
async def get_rsid_diseases(rsid: str):
    """
    Get all diseases associated with a given RSID.
    
    Args:
        rsid: SNP rsID (e.g., rs3093017)
    
    Returns:
        List of diseases and associated information for this variant
    
    Example:
        GET /api/rsid-to-disease/rs3093017
    """
    try:
        result = await get_diseases_by_rsid(rsid)
        return {
            "query": rsid,
            "result": result,
            "source": "RSID_TO_DISEASE_MAPPER"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsid-to-disease/batch")
async def get_rsids_diseases_batch(rsids: List[str]):
    """
    Get diseases associated with multiple RSIDs (batch query).
    
    Args:
        rsids: List of SNP rsIDs
    
    Returns:
        Dictionary with disease associations for each RSID
    
    Example:
        POST /api/rsid-to-disease/batch
        {
            "rsids": ["rs3093017", "rs6311", "rs1234567"]
        }
    """
    try:
        if not rsids or len(rsids) == 0:
            raise HTTPException(status_code=400, detail="At least one RSID required")
        
        if len(rsids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 RSIDs per batch allowed")
        
        result = await get_diseases_by_rsids(rsids)
        return {
            "query_type": "batch",
            "result": result,
            "source": "RSID_TO_DISEASE_MAPPER"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rsid-to-disease/mapping/info")
async def get_rsid_disease_mapping_info():
    """
    Get information about available RSID-to-Disease mappings.
    
    Returns:
        Statistics about the RSID to Gene to Disease mapping dataset
    
    Example:
        GET /api/rsid-to-disease/mapping/info
    """
    try:
        result = await get_rsid_gene_disease_mapping()
        return {
            "mapping_info": result,
            "source": "ClinVar",
            "note": "Use /api/rsid-to-disease/{rsid} to query specific RSID"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
