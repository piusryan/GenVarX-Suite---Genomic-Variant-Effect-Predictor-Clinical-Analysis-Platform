# Quick Start: Disease Search Feature

## ⚠️ Important: Input DISEASE NAMES, Not RSIDs

### ❌ DON'T Input This:
- `rs1234567` ← This is an RSID (use GENE VARIANT module instead)
- `17:43044295:G:A` ← This is a variant (use GENE VARIANT module instead)

### ✅ DO Input This:
- `Breast Cancer`
- `Type 2 Diabetes`
- `Cystic Fibrosis`
- `Marfan Syndrome`

---

## How to Use

### Step 1: Open Disease Search
Go to **DISEASE ASSOC** module

### Step 2: Type a Disease Name
Examples:
```
Breast Cancer
Type 2 Diabetes
Hereditary Breast Cancer
Familial Adenomatous Polyposis
Cystic Fibrosis
Marfan Syndrome
Hypertrophic Cardiomyopathy
```

### Step 3: See Results
You'll get:
- **Variants**: All genomic variants for this disease
- **Genes**: Key genes involved
- **Phenotypes**: Clinical symptoms/features
- **Drugs**: Available treatments
- **Metadata**: Official disease information

---

## Common Disease Names to Try

### Cancer Diseases
```
Breast Cancer
Colorectal Cancer
Lung Cancer
Prostate Cancer
Melanoma
```

### Genetic Diseases
```
Cystic Fibrosis
Marfan Syndrome
Hemophilia A
Sickle Cell Disease
Muscular Dystrophy
```

### Metabolic Diseases
```
Type 1 Diabetes
Type 2 Diabetes
Familial Hypercholesterolemia
Phenylketonuria
Gaucher Disease
```

### Heart Diseases
```
Hypertrophic Cardiomyopathy
Familial Adenomatous Polyposis
Long QT Syndrome
Brugada Syndrome
```

---

## If You're Not Sure About the Exact Name

### Option 1: Use Autocomplete
The system will show suggestions as you type:
- Type: `Brea` → See "Breast Cancer", "Hereditary Breast Cancer", etc.
- Type: `Diab` → See "Type 1 Diabetes", "Type 2 Diabetes", etc.

### Option 2: Try Common Variations
```
Try: "Breast Cancer"
If nothing: Try "Hereditary Breast Cancer"
If nothing: Try "BRCA-related Cancer"
```

### Option 3: Get Full List
Use autocomplete endpoint to see ALL ~50,000 available diseases:
```bash
curl http://localhost:8000/api/disease-search/available?limit=100
```

---

## What Happens When You Search

### Good Result Example: "Breast Cancer"
```
✅ Results Found:
- Variants: 12 BRCA1/BRCA2 variants
- Genes: 5 (BRCA1, BRCA2, TP53, PTEN, etc.)
- Phenotypes: 8 (breast cancer, ovarian cancer, etc.)
- Drugs: 3 (Talazoparib, Olaparib, Imatinib)
```

### No Results Example: "Made Up Disease"
```
❌ No Results:
- Variants: 0
- Genes: 0
- Phenotypes: 0
- Drugs: 0
➜ Try a different name or check spelling
```

### Wrong Input Example: "rs1234567"
```
⚠️ Warning: You entered an RSID
➜ Use GENE VARIANT module instead
➜ Input: rs1234567
➜ Get: VEP annotation, ClinVar data, GWAS associations
```

---

## Two Different Modules

### Module 1: GENE VARIANT (For RSIDs/Variants)
**Input**: RSID or genomic coordinates
**Examples**: 
- `rs1234567`
- `17:43044295:G:A`
- `BRCA1`

**Output**: VEP annotation, ClinVar significance, GWAS associations

---

### Module 2: DISEASE ASSOC (For Disease Names)
**Input**: Disease name
**Examples**:
- `Breast Cancer`
- `Cystic Fibrosis`
- `Type 2 Diabetes`

**Output**: Variants, genes, phenotypes, drugs, metadata

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Getting "not found" error | Check spelling, try autocomplete |
| Got RSID error message | You input RSID - use GENE VARIANT module |
| Got variant error message | You input coordinates - use GENE VARIANT module |
| Not finding disease | Try shorter name or check autocomplete list |
| Getting empty results | Disease might not have data, try another disease |

---

## Real Examples

### Example 1: Looking up Breast Cancer
```
Input: "Breast Cancer"

Results:
├─ Variants
│  └─ 17:43044295:G:A (BRCA1, Pathogenic, HIGH impact)
│  └─ 17:43044295:G:T (BRCA1, Pathogenic, HIGH impact)
│  └─ ... 10 more variants
├─ Genes
│  └─ BRCA1 (Abnormality of the breast)
│  └─ BRCA2 (Breast carcinoma)
│  └─ TP53 (Tumor suppressor)
│  └─ ... 2 more genes
├─ Phenotypes
│  └─ Breast carcinoma
│  └─ Ovarian carcinoma
│  └─ ... 6 more phenotypes
├─ Drugs
│  └─ TALAZOPARIB (PARP1 inhibitor, Phase 4)
│  └─ OLAPARIB (PARP1 inhibitor, Phase 4)
│  └─ IMATINIB (BCR-ABL inhibitor, Phase 4)
└─ Metadata
   └─ Official: "Hereditary breast and ovarian cancer syndrome"
   └─ Sources: MONDO, Orphanet
   └─ Category: Disease
```

### Example 2: Looking up Type 2 Diabetes
```
Input: "Type 2 Diabetes"

Results:
├─ Variants
│  └─ 10:114759877:T:G (TCF7L2, Risk variant)
│  └─ 6:20679709:T:C (CDKAL1, Risk variant)
│  └─ ... 8 more variants
├─ Genes
│  └─ TCF7L2 (Transcription factor)
│  └─ PPARG (Peroxisome proliferator)
│  └─ ABCC8 (Potassium channel)
│  └─ ... 12 more genes
├─ Phenotypes
│  └─ Hyperglycemia
│  └─ Insulin resistance
│  └─ Glucose intolerance
│  └─ ... 5 more phenotypes
├─ Drugs
│  └─ METFORMIN (Biguanide, Phase 4)
│  └─ PIOGLITAZONE (Thiazolidinedione, Phase 4)
│  └─ SITAGLIPTIN (DPP4 inhibitor, Phase 4)
└─ Metadata
   └─ Official: "Type 2 diabetes mellitus"
   └─ Sources: MONDO
   └─ Category: Disease
```

---

## Quick Command Line Test

```bash
# Test 1: Search for a disease
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Breast Cancer"}'

# Test 2: Get available diseases (to see valid names)
curl http://localhost:8000/api/disease-search/available?limit=50
```

---

## Remember

✅ **Disease names** → DISEASE ASSOC module  
✅ **RSID or variants** → GENE VARIANT module  
✅ **Not sure about name?** → Use autocomplete  
✅ **Getting error?** → You might be in wrong module

---

**Start Simple**: Try `"Breast Cancer"` or `"Type 2 Diabetes"` first!
