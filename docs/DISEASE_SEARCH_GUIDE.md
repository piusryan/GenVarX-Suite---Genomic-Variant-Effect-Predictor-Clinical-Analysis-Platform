# Disease-Based Search Guide

## What Changed?

Previously, you had to know a specific **variant** (like `17:43044295:G:A`) to search for disease associations. Now you can input a **disease name** directly and get comprehensive information about it.

## How to Use

### Step 1: Access the Disease Search
Use the DISEASE ASSOC module and select **"Search by Disease"** (new option).

### Step 2: Enter a Disease Name

Type any disease from our local databases:
- Hereditary Breast Cancer
- Type 2 Diabetes
- Cystic Fibrosis
- Marfan Syndrome
- Sickle Cell Disease
- Hypertrophic Cardiomyopathy
- etc.

**Tip**: If you're not sure of the exact name, click the autocomplete dropdown to see available diseases.

### Step 3: View Results

You'll get a comprehensive disease profile with:

#### **Variants** 
All genomic variants associated with the disease from ClinVar:
- Genomic coordinates (CHR:POS:REF:ALT)
- Associated gene
- Clinical significance (Pathogenic, Benign, Uncertain, etc.)
- Consequence type (missense, frameshift, etc.)
- Impact level (HIGH, MODERATE, LOW)

#### **Genes**
Key genes implicated in this disease:
- Gene symbol
- HPO phenotype association
- Frequency of involvement
- Disease ID (OMIM, etc.)

#### **Phenotypes**
Clinical features (symptoms) associated with the disease:
- HPO term ID
- Phenotype description
- Frequency (common, rare, etc.)

#### **Drugs**
Available therapeutic compounds targeting disease-related genes:
- Drug name
- Target gene
- Clinical indication
- Development phase (0-4)
- Compound type

#### **Disease Metadata**
Official disease information:
- Canonical disease name
- Concept IDs (MONDO, Orphanet, OMIM)
- Data sources
- Disease category

## Example Workflows

### Workflow 1: Patient with Suspected BRCA1 Mutation

1. Search: "Hereditary breast and ovarian cancer syndrome"
2. Results show:
   - All known BRCA1/BRCA2 pathogenic variants
   - BRCA1, BRCA2 genes
   - Associated phenotypes (breast cancer, ovarian cancer, etc.)
   - Drugs like talazoparib, olaparib for treatment

### Workflow 2: Drug Development for Diabetes

1. Search: "Type 2 diabetes mellitus"
2. Results show:
   - Key genes (TCF7L2, PPARG, etc.)
   - Associated phenotypes
   - Available drugs and their development phases
   - Identify targets for new compounds

### Workflow 3: Understanding a Rare Disease

1. Search: "Niemann-Pick disease"
2. Get:
   - Variants that cause the disease
   - Associated genes (NPC1, NPC2)
   - All clinical phenotypes
   - Current treatment options

## How It Works

### Data Sources

| Source | Type | Contains |
|--------|------|----------|
| **ClinVar** | Genetic variants | Pathogenic variants, clinical significance |
| **HPO** | Phenotypes & Genes | Disease-phenotype associations, genes |
| **ChEMBL** | Drugs/Compounds | Therapeutic compounds, drug targets |
| **Disease Names** | Metadata | Official names, concept IDs, sources |

### Search Algorithm

1. **Disease Name Matching**
   - Exact match in disease_names.tsv
   - Substring search if no exact match
   - Returns official disease name

2. **Variant Search**
   - Searches ClinVar for disease matches
   - Limits to top 25 variants
   - Includes clinical significance

3. **Gene Search**
   - Uses HPO to find genes associated with disease
   - Limits to top 15 genes
   - Shows phenotype associations

4. **Phenotype Search**
   - Gets clinical features from HPO
   - Deduplicates phenotypes
   - Shows frequency information

5. **Drug Search**
   - Searches ChEMBL for indications
   - Falls back to gene-based search
   - Shows development phase

## Tips & Tricks

### 1. Autocomplete
- Type partial disease names (e.g., "BRCA" for BRCA-related cancers)
- Use the dropdown for suggestions
- See exact names used in databases

### 2. Variant Inspection
- Click any variant to see full details
- Can then use GENE VARIANT module for deeper analysis
- Check clinical significance for your use case

### 3. Gene Information
- Click genes to see HPO associations
- Combine with DRUG DISCOVERY module to find compounds
- Use for pathway analysis

### 4. Phenotype Matching
- Use phenotypes to confirm diagnosis
- Cross-reference with patient symptoms
- Identify relevant clinical features

### 5. Drug Information
- Phase 4 = FDA approved
- Phase 3/4 = Clinical trials
- Phase 1/2 = Early stage research
- Sort by phase for available treatments

## Limitations & Notes

### Current Limitations

1. **No GWAS Integration**: Unlike the variant-first search, this doesn't use GWAS Catalog data. This is intentional - GWAS focuses on common variants in population studies, not rare disease variants.

2. **Local Data Only**: All data comes from local datasets. Not updated in real-time.

3. **Name Matching**: Disease names must be reasonably close to names in our database. Try variations if your query returns no results.

4. **Limited Drugs**: Drug results depend on disease-gene associations in HPO. Not all drugs may be represented.

### When to Use Which Method

**Use Disease Search when:**
- You have a disease name (not a specific variant)
- You want a comprehensive disease overview
- You're exploring treatment options
- You're investigating rare diseases

**Use Variant Search when:**
- You have a specific variant to analyze
- You want GWAS population associations
- You're validating a particular mutation
- You need variant-specific clinical data

## Technical Details

### API Endpoints

```bash
# Search by disease
POST /api/disease-search
{
  "disease": "Hereditary Breast Cancer"
}

# Get autocomplete list
GET /api/disease-search/available?limit=100
```

### Response Structure

```json
{
  "disease_query": "Hereditary Breast Cancer",
  "results": {
    "query": "...",
    "variants": [...],
    "genes": [...],
    "phenotypes": [...],
    "drugs": [...],
    "disease_metadata": {...},
    "summary": {...}
  },
  "source": "LOCAL_DISEASE_SEARCH"
}
```

## FAQ

**Q: Why no results for my disease?**
A: The disease name might not be in our database. Try variations or check the autocomplete list for exact names used.

**Q: Can I search for symptoms instead of disease names?**
A: Not directly. Try searching for the disease associated with those symptoms, or use the GENE VARIANT module.

**Q: How often is the data updated?**
A: Data is static (from local files). For the latest data, deploy new dataset files.

**Q: Can I export the results?**
A: Currently view-only. You can copy/paste results or use browser developer tools to extract data.

**Q: Why are some drugs not showing up?**
A: Drug results depend on ChEMBL having indications or gene targets. Coverage varies by disease.

## Troubleshooting

### Problem: "No variants found"
- **Solution 1**: Check disease name spelling
- **Solution 2**: Use autocomplete to find exact name
- **Solution 3**: Try alternative disease names

### Problem: "No drugs found"
- **Solution**: Check genes first - drugs need gene-disease links

### Problem: "Partial results"
- **Solution**: Some datasets may have incomplete data for certain diseases

## Contact

For issues or suggestions, refer to the project documentation or contact the development team.
