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

class PatientReportRequest(BaseModel):
    patient_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        json_schema_extra={"example": "John Doe"},
        description="Patient full name shown on the report"
    )
    patient_id: Optional[str] = Field(
        default=None,
        max_length=60,
        json_schema_extra={"example": "PT-2024-0001"},
        description="Optional patient / sample identifier"
    )
    variant: str = Field(
        ...,
        json_schema_extra={"example": "7:140753336:A:T"},
        description="Genomic variant for gene-variation analysis (chr:pos:ref:alt)"
    )
    rsid: Optional[str] = Field(
        default=None,
        max_length=40,
        json_schema_extra={"example": "rs113488022"},
        description="RSID used for disease-association lookup (falls back to the variant's resolved RSID)"
    )
    phenotype: Optional[str] = Field(
        default=None,
        max_length=200,
        json_schema_extra={"example": "Malignant melanoma of the skin"},
        description="Phenotype / clinical indication text included on the report"
    )
    captured_results: Optional[dict] = Field(
        default=None,
        description=(
            "Optional captured outputs from the three GenVarX modules: "
            "{gene_variation: VariantAnnotation dict, disease_association: comprehensive dict, "
            "drug_discovery: compounds list}. When present, the report is assembled from these "
            "instead of re-running the pipeline."
        )
    )

class PatientAssembleRequest(BaseModel):
    """Build a patient report from previously-run module outputs
    (gene variation, disease association, drug discovery) instead of
    re-running the entire pipeline on the backend."""
    patient_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        json_schema_extra={"example": "John Doe"},
    )
    patient_id: Optional[str] = Field(
        default=None,
        max_length=60,
        json_schema_extra={"example": "PT-2024-0001"},
    )
    variant: Optional[str] = Field(
        default=None,
        json_schema_extra={"example": "7:140753336:A:T"},
    )
    rsid: Optional[str] = Field(
        default=None,
        max_length=40,
        json_schema_extra={"example": "rs113488022"},
    )
    phenotype: Optional[str] = Field(
        default=None,
        max_length=200,
        json_schema_extra={"example": "Malignant melanoma of the skin"},
    )
    gene_variation: Optional[dict] = Field(
        default=None,
        description="Full annotate endpoint output (VariantAnnotation as returned by /api/annotate)"
    )
    disease_association: Optional[dict] = Field(
        default=None,
        description="Full /api/disease-comprehensive output"
    )
    drug_discovery: Optional[dict] = Field(
        default=None,
        description="{\"gene_symbol\": ..., \"compounds\": [...]}"
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
