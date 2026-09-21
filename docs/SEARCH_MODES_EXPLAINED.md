# Two Different Search Modes Explained

## Mode 1: Variant/RSID Search (OLD - Still Works)
**What to input**: A specific variant or RSID  
**Examples**:
- `rs1234567` (RSID)
- `17:43044295:G:A` (Genomic coordinates)
- `12:25398284:C:A`

**How to use it**:
- Use the **GENE VARIANT** module
- Or use `/api/annotate` endpoint
- Or use `/api/gwas/{variant}` endpoint

**Output**: Information about that specific variant

---

## Mode 2: Disease Search (NEW - What You Need)
**What to input**: A disease name  
**Examples**:
- `Breast Cancer`
- `Hereditary Breast Cancer`
- `Type 2 Diabetes`
- `Cystic Fibrosis`
- `Marfan Syndrome`
- `Familial Adenomatous Polyposis`

**How to use it**:
- Use the **DISEASE ASSOC** module
- Or use `/api/disease-search` endpoint
- Or use `/api/disease-search/available` to see list

**Output**: All variants, genes, phenotypes, and drugs for that disease

---

## Comparison Table

| Aspect | Variant Search | Disease Search |
|--------|---|---|
| **Input** | RSID or coordinates | Disease name |
| **Module** | GENE VARIANT | DISEASE ASSOC |
| **Endpoint** | `/api/annotate`, `/api/gwas` | `/api/disease-search` |
| **Output** | One variant's info | All disease-related data |
| **Data Source** | VEP, ClinVar, GWAS | ClinVar, HPO, ChEMBL |
| **Use When** | You have a specific variant | You want disease overview |

---

## Step-by-Step Guide

### If You Have a Specific RSID
Example: You have `rs1234567`

1. Go to **GENE VARIANT** module
2. Input: `rs1234567`
3. Get: VEP annotation, ClinVar significance, GWAS associations

### If You Want Information About a Disease
Example: You want to know about "Breast Cancer"

1. Go to **DISEASE ASSOC** module
2. Input: `Breast Cancer`
3. Get: All BRCA1/BRCA2 variants, genes, phenotypes, drugs

---

## What Diseases Are Available?

The system has ~50,000 diseases you can search for. Here are common ones:

### Cancers
- Breast Cancer
- Colorectal Cancer
- Lung Cancer
- Prostate Cancer
- Melanoma
- Leukemia
- Lymphoma

### Genetic Diseases
- Cystic Fibrosis
- Marfan Syndrome
- Huntington Disease
- Hemophilia A
- Sickle Cell Disease
- Thalassemia
- Duchenne Muscular Dystrophy

### Metabolic Diseases
- Type 1 Diabetes
- Type 2 Diabetes
- Familial Hypercholesterolemia
- Phenylketonuria (PKU)
- Gaucher Disease

### Cardiovascular
- Familial Adenomatous Polyposis
- Hypertrophic Cardiomyopathy
- Long QT Syndrome
- Brugada Syndrome
- Dilated Cardiomyopathy

### Neurological
- Alzheimer Disease
- Parkinson Disease
- Schizophrenia
- Autism Spectrum Disorder
- Epilepsy

### Other
- Hemochromatosis
- Wilson Disease
- Familial Mediterranean Fever
- Ehlers-Danlos Syndrome

---

## How to Find Valid Disease Names

### Option 1: Use Autocomplete
```bash
GET /api/disease-search/available?limit=50

# Shows: "Breast Cancer", "Type 2 Diabetes", etc.
```

### Option 2: Try Common Names
```
Try: "Breast Cancer"
If not found, try: "Hereditary Breast Cancer"
Or try: "Breast and Ovarian Cancer"
```

### Option 3: Use Exact Names from Medical Databases
Search on:
- MONDO (mondo.obo.org)
- Orphanet (orphanet.org)
- OMIM (omim.org)

---

## Examples

### Example 1: Understanding Cystic Fibrosis

**Step 1**: Search for "Cystic Fibrosis"

**Output**:
- **Variants**: All CFTR mutations causing CF
- **Genes**: CFTR gene details
- **Phenotypes**: Lung disease, pancreatic insufficiency, etc.
- **Drugs**: Ivacaftor (Kalydeco), Lumacaftor, etc.

### Example 2: Understanding Type 2 Diabetes

**Step 1**: Search for "Type 2 Diabetes"

**Output**:
- **Variants**: Associated genetic variants
- **Genes**: TCF7L2, PPARG, ABCC8, etc.
- **Phenotypes**: Hyperglycemia, insulin resistance
- **Drugs**: Metformin, Pioglitazone, GLP-1 agonists

### Example 3: Understanding Familial Breast Cancer

**Step 1**: Search for "Hereditary Breast Cancer" or "Breast Cancer"

**Output**:
- **Variants**: BRCA1, BRCA2 pathogenic variants
- **Genes**: BRCA1, BRCA2, TP53, PTEN, etc.
- **Phenotypes**: Breast cancer, ovarian cancer
- **Drugs**: PARP inhibitors (Talazoparib, Olaparib)

---

## Common Mistakes

### ❌ WRONG: Inputting RSID into Disease Search
```
Disease Search Input: "rs1234567"
❌ Error: No disease found
```

### ✅ CORRECT: Use right module for RSIDs
```
GENE VARIANT Module Input: "rs1234567"
✅ Result: VEP annotation, ClinVar data, GWAS associations
```

### ❌ WRONG: Using exact medical names that don't match
```
Disease Search Input: "autosomal dominant hypertrophic cardiomyopathy"
❌ Error: Not found (name too specific)
```

### ✅ CORRECT: Use common disease name
```
Disease Search Input: "Hypertrophic Cardiomyopathy"
✅ Result: Gene data, variants, phenotypes, drugs
```

---

## Quick Reference

### Where to Input What

| What You Have | Where to Input | Module |
|---|---|---|
| RSID (rs1234567) | GENE VARIANT | Variant Search |
| Coordinates (chr:pos:ref:alt) | GENE VARIANT | Variant Search |
| Gene name (BRCA1) | GENE VARIANT | Variant Search |
| Disease name (Breast Cancer) | DISEASE ASSOC | Disease Search |
| Drug name (Ibuprofen) | DRUG DISCOVERY | Drug Search |
| Protein motif | MOTIF ANALYSIS | Motif Search |

---

## Troubleshooting

### Problem: "No disease found"
**Solution**: 
1. Check spelling
2. Try shorter name (e.g., "Breast Cancer" instead of "Hereditary Breast and Ovarian Cancer")
3. Use autocomplete to see available names: `GET /api/disease-search/available`

### Problem: "Getting error with RSIDs"
**Solution**:
1. You're using the wrong module
2. Use GENE VARIANT module for RSIDs
3. Use DISEASE ASSOC module for disease names

### Problem: "Not finding results"
**Solution**:
1. Verify the disease exists in database
2. Try alternative names
3. Check if data is loaded (`GET /api/datasets/summary`)

---

## API Usage Examples

### Search by Disease Name
```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Breast Cancer"}'
```

### Get Available Diseases (to find right name)
```bash
curl http://localhost:8000/api/disease-search/available?limit=100
```

### Search by Variant (Different endpoint!)
```bash
curl -X POST http://localhost:8000/api/annotate \
  -H "Content-Type: application/json" \
  -d '{"variant": "17:43044295:G:A"}'
```

---

## Summary

| Question | Answer |
|----------|--------|
| I have RSID, what do I do? | Use GENE VARIANT module, input the RSID |
| I have a disease name? | Use DISEASE ASSOC module, input disease name |
| I don't know disease name? | Use `/api/disease-search/available` to see list |
| I'm getting "not found" error? | Check if you're using the right module and input format |
| Where do I find valid disease names? | MONDO, Orphanet, or use autocomplete API |

---

**Key Takeaway**: 
- **RSID/Variant** → Use GENE VARIANT module
- **Disease Name** → Use DISEASE ASSOC module
- Don't mix them up!
