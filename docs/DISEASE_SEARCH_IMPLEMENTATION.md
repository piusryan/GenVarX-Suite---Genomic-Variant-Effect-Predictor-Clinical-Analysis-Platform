# Disease-First Search Implementation

## Overview
Added a new disease-based search workflow that complements the existing variant-first approach. Users can now input a **disease name** in the DISEASE ASSOC module and get back variants, genes, phenotypes, and drugs associated with that disease.

## Problem Solved
Previously, the GWAS Catalog-based approach required users to:
1. Have a specific variant (SNP)
2. Search for associations with that variant
3. Result depended on GWAS data availability (which often doesn't have common variants)

Now, users can:
1. Input any disease name from the local datasets
2. Get all associated variants from ClinVar
3. Get genes and phenotypes from HPO
4. Get potential drugs from ChEMBL
5. No dependency on external GWAS catalog

## New Components

### 1. New Data Model: `DiseaseRequest`
**File**: `app/models.py`

```python
class DiseaseRequest(BaseModel):
    disease: str = Field(
        ..., 
        json_schema_extra={"example": "Hereditary Breast Cancer"}, 
        description="Disease name to search"
    )
```

### 2. New Service: `disease_search_service.py`
**File**: `app/services/disease_search_service.py`

Provides comprehensive disease-based search with functions:

- **`search_disease_associations(disease_name)`**: Main function that searches all datasets for a disease
- **`_search_clinvar_by_disease()`**: Finds variants from ClinVar matching the disease
- **`_search_genes_by_disease()`**: Finds genes associated with disease phenotypes from HPO
- **`_search_phenotypes_by_disease()`**: Gets HPO phenotypes linked to the disease
- **`_search_drugs_by_disease()`**: Searches ChEMBL for drugs targeting disease-related genes
- **`_get_disease_metadata()`**: Retrieves disease information from disease_names.tsv
- **`get_available_diseases()`**: Returns autocomplete list of searchable diseases

### 3. New API Endpoints
**File**: `app/main.py`

#### POST `/api/disease-search`
**Input**:
```json
{
  "disease": "Hereditary Breast Cancer"
}
```

**Output**:
```json
{
  "disease_query": "Hereditary Breast Cancer",
  "results": {
    "query": "Hereditary Breast Cancer",
    "variants": [
      {
        "source": "ClinVar",
        "variant": "17:43044295:G:A",
        "gene": "BRCA1",
        "disease": "Hereditary breast and ovarian cancer syndrome",
        "clinical_significance": "Pathogenic",
        "consequence": "missense_variant",
        "impact": "HIGH"
      },
      ...
    ],
    "genes": [
      {
        "gene_symbol": "BRCA1",
        "hpo_id": "HP:0000001",
        "phenotype": "Abnormality of the breast",
        "disease_id": "OMIM:604373",
        "frequency": "common"
      },
      ...
    ],
    "phenotypes": [
      {
        "hpo_id": "HP:0003002",
        "phenotype": "Breast carcinoma",
        "definition": "",
        "frequency": "common"
      },
      ...
    ],
    "drugs": [
      {
        "chembl_id": "CHEMBL3236",
        "name": "TALAZOPARIB",
        "target_gene": "PARP1",
        "indication": "Breast cancer",
        "max_phase": "4",
        "compound_type": "Small molecule"
      },
      ...
    ],
    "disease_metadata": {
      "found": true,
      "official_name": "Hereditary breast and ovarian cancer syndrome",
      "concept_id": "C0677776",
      "sources": ["MONDO", "Orphanet"],
      "category": "Disease"
    },
    "summary": {
      "total_variants_found": 12,
      "total_genes_found": 5,
      "total_phenotypes_found": 8,
      "total_drugs_found": 3,
      "disease_sources": ["MONDO", "Orphanet"]
    }
  },
  "source": "LOCAL_DISEASE_SEARCH"
}
```

#### GET `/api/disease-search/available?limit=100`
Returns autocomplete list of available diseases.

**Output**:
```json
{
  "total_available": 52847,
  "diseases": [
    "Hereditary breast and ovarian cancer syndrome",
    "Type 2 diabetes mellitus",
    "Familial adenomatous polyposis",
    ...
  ],
  "note": "Diseases from ClinVar disease_names.tsv"
}
```

## Data Flow

```
User Input: Disease Name
    ↓
┌─────────────────────────────────────────────────────┐
│ search_disease_associations(disease_name)           │
├─────────────────────────────────────────────────────┤
│ Parallel searches:                                  │
│ 1. ClinVar (clinvar.csv + clinvar_conflicting.csv) │
│    → Variants + Clinical significance              │
│                                                     │
│ 2. HPO (genes_to_phenotype.csv)                     │
│    → Associated genes                              │
│    → Phenotypes                                     │
│                                                     │
│ 3. ChEMBL (chembl.csv)                              │
│    → Drugs targeting genes                         │
│                                                     │
│ 4. Disease metadata (disease_names.tsv)             │
│    → Official name, sources, category              │
└─────────────────────────────────────────────────────┘
    ↓
Consolidated Results with Summary
    ↓
User gets complete disease profile
```

## Datasets Used

| Dataset | File | Search Field | Returns |
|---------|------|--------------|---------|
| ClinVar | clinvar.csv, clinvar_conflicting.csv | CLNDN | Variants, genes, clinical significance |
| HPO | genes_to_phenotype.csv | disease_name | Genes, phenotypes, frequencies |
| ChEMBL | chembl.csv | indication, target_gene | Drugs, targets, development phase |
| Disease Names | disease_names.tsv | DiseaseName | Official names, concept IDs, sources |

## Frontend Integration

The frontend should:

1. **For disease input field**: Call `/api/disease-search/available` to get autocomplete suggestions
2. **On disease selection**: Call `/api/disease-search` with the selected disease name
3. **Display results** under different tabs:
   - **Variants**: From ClinVar with clinical significance
   - **Genes**: Associated genes with phenotypes
   - **Phenotypes**: Clinical features (HPO terms)
   - **Drugs**: Available drugs targeting the disease genes

## Example Use Cases

### Use Case 1: Rare Disease Investigation
User: "I want to understand BRCA1-related breast cancer"
- Input: "Hereditary breast and ovarian cancer syndrome"
- Gets: All BRCA1 variants, associated phenotypes, available drugs

### Use Case 2: Drug Discovery
User: "What drugs exist for this disease?"
- Input: "Type 2 diabetes mellitus"
- Gets: All genes, drug candidates with development phase

### Use Case 3: Phenotype Exploration
User: "What are the clinical features of this disease?"
- Input: "Marfan syndrome"
- Gets: Associated phenotypes (skeletal, cardiovascular, ocular)

## Limitations

1. **Disease name matching**: Currently does exact and substring matching. Fuzzy matching could improve results.
2. **Limited ChEMBL data**: Drug search depends on having gene-disease associations in HPO
3. **No external APIs**: All searches are against local datasets (faster but potentially outdated)
4. **Result limits**: Results are capped to prevent overwhelming responses

## Future Enhancements

1. Add fuzzy matching for better disease name matching
2. Integrate additional drug databases (DrugBank, etc.)
3. Add pathway analysis
4. Add literature mining for disease associations
5. Real-time updates from NCBI/EBI APIs
6. Advanced filtering (e.g., by variant frequency, drug phase)
