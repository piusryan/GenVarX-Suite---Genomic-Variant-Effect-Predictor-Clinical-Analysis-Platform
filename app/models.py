from pydantic import BaseModel, Field
from typing import Optional, List

class VariantRequest(BaseModel):
    variant: str = Field(
        ..., 
        json_schema_extra={"example": "17:43044295:G:A"}, 
        description="Format: chr:pos:ref:alt (e.g., 17:43044295:G:A)"
    )

class DiseaseRequest(BaseModel):
    disease: str = Field(
        ..., 
        json_schema_extra={"example": "Hereditary Breast Cancer"}, 
        description="Disease name to search"
    )

class VariantAnnotation(BaseModel):
    variant: str
    rs_id: Optional[str] = None
    gene_symbol: Optional[str] = "N/A"
    consequence: str
    sift_prediction: Optional[str] = "N/A"
    polyphen_prediction: Optional[str] = "N/A"
    amino_acid_change: Optional[str] = "N/A"
    impact_level: str
    clinical_significance: Optional[str] = "Not Specified"
    associated_diseases: List[str] = []


class GwasAssociation(BaseModel):
    trait: str
    pvalue: Optional[str] = None
    reported_trait: Optional[str] = None
    study_accession: Optional[str] = None
    pubmed_id: Optional[str] = None
    strongest_allele: Optional[str] = None


class GwasResponse(BaseModel):
    rs_id: Optional[str] = None
    associations: List[GwasAssociation] = []
    note: Optional[str] = None


class CompoundSummary(BaseModel):
    chembl_id: str
    name: Optional[str] = None
    compound_type: Optional[str] = None
    max_phase: Optional[str] = None
    molecular_weight: Optional[str] = None
    alogp: Optional[str] = None
    qed_weighted: Optional[str] = None
    targets: Optional[str] = None
    bioactivities: Optional[str] = None


class CompoundDetail(CompoundSummary):
    synonyms: Optional[str] = None
    polar_surface_area: Optional[str] = None
    hba: Optional[str] = None
    hbd: Optional[str] = None
    ro5_violations: Optional[str] = None
    rotatable_bonds: Optional[str] = None
    passes_ro3: Optional[str] = None
    aromatic_rings: Optional[str] = None
    structure_type: Optional[str] = None
    inorganic_flag: Optional[str] = None
    heavy_atoms: Optional[str] = None
    np_likeness_score: Optional[str] = None
    molecular_formula: Optional[str] = None
    smiles: Optional[str] = None
    inchi_key: Optional[str] = None
    inchi: Optional[str] = None
    withdrawn_flag: Optional[str] = None
    orphan: Optional[str] = None
