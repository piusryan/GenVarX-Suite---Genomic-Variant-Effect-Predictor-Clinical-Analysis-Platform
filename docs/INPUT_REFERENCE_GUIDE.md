# Input Reference Guide - What Goes Where?

## Decision Tree

```
Do you have information about a disease?
│
├─ YES → INPUT DISEASE NAME
│        Module: DISEASE ASSOC
│        API: /api/disease-search
│        Input: "Breast Cancer"
│        Get: Variants, Genes, Phenotypes, Drugs
│
└─ NO → Do you have a specific variant or RSID?
        │
        ├─ YES → INPUT RSID/VARIANT
        │        Module: GENE VARIANT
        │        API: /api/annotate
        │        Input: "rs1234567" or "17:43044295:G:A"
        │        Get: VEP annotation, ClinVar, GWAS
        │
        └─ NO → Do you have a drug/compound name?
                │
                ├─ YES → INPUT DRUG NAME
                │        Module: DRUG DISCOVERY
                │        API: /api/compounds
                │        Input: "Ibuprofen"
                │        Get: Drug details, targets
                │
                └─ NO → Try other modules
                        (Motif analysis, Conservation, etc.)
```

---

## Input Format Reference

### DISEASE ASSOC Module (NEW)

**Input Type**: Disease Name  
**Module**: DISEASE ASSOC  
**API Endpoint**: `POST /api/disease-search`

**Valid Inputs**:
```
✅ Breast Cancer
✅ Hereditary Breast Cancer
✅ Type 2 Diabetes
✅ Familial Adenomatous Polyposis
✅ Marfan Syndrome
✅ Cystic Fibrosis
✅ Hemophilia A
✅ Sickle Cell Disease
```

**Invalid Inputs**:
```
❌ rs1234567 (This is an RSID)
❌ 17:43044295:G:A (This is a variant)
❌ BRCA1 (This is a gene - use GENE VARIANT instead)
```

**What You Get**:
```json
{
  "variants": [...],     // All variants causing disease
  "genes": [...],        // Associated genes
  "phenotypes": [...],   // Clinical features
  "drugs": [...],        // Available treatments
  "metadata": {...},     // Disease information
  "summary": {...}       // Statistics
}
```

---

### GENE VARIANT Module (OLD)

**Input Type**: RSID, Variant, or Gene Name  
**Module**: GENE VARIANT  
**API Endpoint**: `POST /api/annotate`

**Valid Inputs**:
```
✅ rs1234567 (RSID)
✅ 17:43044295:G:A (Genomic coordinates)
✅ 12:25398284:C:A (Genomic coordinates)
✅ BRCA1 (Gene name)
```

**Invalid Inputs**:
```
❌ Breast Cancer (This is a disease - use DISEASE ASSOC instead)
❌ Type 2 Diabetes (This is a disease - use DISEASE ASSOC instead)
```

**What You Get**:
```json
{
  "variant": "...",                    // Variant ID
  "gene_symbol": "BRCA1",              // Gene name
  "clinical_significance": "...",      // ClinVar significance
  "associated_diseases": [...]         // Related diseases
}
```

---

### DRUG DISCOVERY Module

**Input Type**: Drug Name or ChEMBL ID  
**Module**: DRUG DISCOVERY  
**API Endpoint**: `GET /api/compounds?query=name`

**Valid Inputs**:
```
✅ Ibuprofen
✅ Aspirin
✅ Metformin
✅ CHEMBL3236 (ChEMBL ID)
```

**Invalid Inputs**:
```
❌ rs1234567 (This is an RSID)
❌ Breast Cancer (This is a disease)
```

**What You Get**:
```json
{
  "chembl_id": "CHEMBL3236",
  "name": "TALAZOPARIB",
  "target_gene": "PARP1",
  "indication": "Breast cancer",
  "max_phase": "4"
}
```

---

## Input Examples by Use Case

### Use Case 1: "What variants cause breast cancer?"
```
Module: DISEASE ASSOC
Input: "Breast Cancer"
Output: 12+ variants from ClinVar
```

### Use Case 2: "What does variant rs1234567 do?"
```
Module: GENE VARIANT
Input: "rs1234567"
Output: VEP annotation, clinical significance, GWAS data
```

### Use Case 3: "What are the genes for type 2 diabetes?"
```
Module: DISEASE ASSOC
Input: "Type 2 Diabetes"
Output: 15+ genes including TCF7L2, PPARG, etc.
```

### Use Case 4: "What does BRCA1 do?"
```
Module: GENE VARIANT
Input: "BRCA1"
Output: Gene information, associated variants, diseases
```

### Use Case 5: "What drugs treat breast cancer?"
```
Module: DISEASE ASSOC
Input: "Breast Cancer"
Output: PARP inhibitors, other cancer drugs
```

### Use Case 6: "What is Ibuprofen used for?"
```
Module: DRUG DISCOVERY
Input: "Ibuprofen"
Output: Drug details, target genes, indications
```

---

## Common Mistakes & Fixes

### Mistake 1: Inputting RSID into Disease Search
```
❌ WRONG:
Module: DISEASE ASSOC
Input: "rs1234567"
Result: ⚠️ Warning: You entered an RSID

✅ CORRECT:
Module: GENE VARIANT
Input: "rs1234567"
Result: ✅ VEP annotation, ClinVar data
```

### Mistake 2: Inputting Disease into Variant Search
```
❌ WRONG:
Module: GENE VARIANT
Input: "Breast Cancer"
Result: ❌ Error: Not found

✅ CORRECT:
Module: DISEASE ASSOC
Input: "Breast Cancer"
Result: ✅ Variants, genes, phenotypes, drugs
```

### Mistake 3: Inputting Gene into Disease Search
```
❌ WRONG:
Module: DISEASE ASSOC
Input: "BRCA1"
Result: ❌ No disease found

✅ CORRECT:
Module: GENE VARIANT
Input: "BRCA1"
Result: ✅ Gene information, variants, associated diseases
```

### Mistake 4: Wrong Disease Name Spelling
```
❌ WRONG:
Module: DISEASE ASSOC
Input: "Cystyc Fibrosis"
Result: ❌ No results

✅ CORRECT:
Module: DISEASE ASSOC
Input: "Cystic Fibrosis"
Result: ✅ CFTR variants, genes, phenotypes, drugs
```

---

## Format Reference

### Disease Names (DISEASE ASSOC)
```
Format: Plain English text
Examples:
  - "Breast Cancer"
  - "Type 2 Diabetes"
  - "Marfan Syndrome"
  - "Familial Adenomatous Polyposis"
  - "Hereditary Breast and Ovarian Cancer Syndrome"

Acceptable Variations:
  - "breast cancer" ✅ (lowercase ok)
  - "BREAST CANCER" ✅ (uppercase ok)
  - "Breast cancer" ✅ (mixed case ok)

NOT Acceptable:
  - "rs1234567" ❌ (This is RSID)
  - "17:43044295:G:A" ❌ (This is variant)
  - "BRCA1" ❌ (This is gene, use GENE VARIANT)
```

### RSIDs (GENE VARIANT)
```
Format: rs + numbers
Examples:
  - rs1234567
  - rs61818430
  - rs3218713

NOT Acceptable:
  - r1234567 ❌ (missing 's')
  - rs ❌ (no numbers)
  - RS1234567 ❌ (should be lowercase 'rs')
```

### Genomic Coordinates (GENE VARIANT)
```
Format: CHR:POS:REF:ALT
Examples:
  - 17:43044295:G:A
  - 12:25398284:C:A
  - 13:32889611:G:A

Parts:
  - CHR: Chromosome (1-22, X, Y, MT)
  - POS: Position (integer)
  - REF: Reference allele (A, T, G, C)
  - ALT: Alternate allele (A, T, G, C)

NOT Acceptable:
  - 17:43044295:G ❌ (missing ALT)
  - chr17:43044295:G:A ❌ (prefix 'chr' not needed)
  - 43044295:G:A ❌ (missing chromosome)
```

### Gene Names (GENE VARIANT)
```
Format: HUGO gene symbol
Examples:
  - BRCA1
  - TP53
  - EGFR
  - MDM2

NOT Acceptable:
  - brca1 ❌ (should be uppercase)
  - "BRCA1 gene" ❌ (don't add "gene")
  - Breast cancer type 1 susceptibility ❌ (use symbol)
```

### Drug Names (DRUG DISCOVERY)
```
Format: Plain English or ChEMBL ID
Examples:
  - Ibuprofen
  - Metformin
  - CHEMBL3236

Case Doesn't Matter:
  - "ibuprofen" ✅
  - "IBUPROFEN" ✅
  - "Ibuprofen" ✅
```

---

## Quick Reference Table

| What You Have | Module | Input Format | Example |
|---|---|---|---|
| Disease name | DISEASE ASSOC | Plain text | "Breast Cancer" |
| RSID | GENE VARIANT | rs + numbers | "rs1234567" |
| Variant coordinates | GENE VARIANT | CHR:POS:REF:ALT | "17:43044295:G:A" |
| Gene name | GENE VARIANT | HUGO symbol | "BRCA1" |
| Drug name | DRUG DISCOVERY | Plain text | "Ibuprofen" |
| ChEMBL ID | DRUG DISCOVERY | CHEMBL + ID | "CHEMBL3236" |

---

## Validation Checklist

Before inputting, ask yourself:

- [ ] Do I have a disease name? → Use DISEASE ASSOC
- [ ] Do I have an RSID (rs + numbers)? → Use GENE VARIANT
- [ ] Do I have coordinates (CHR:POS:REF:ALT)? → Use GENE VARIANT
- [ ] Do I have a gene symbol? → Use GENE VARIANT
- [ ] Do I have a drug name? → Use DRUG DISCOVERY
- [ ] Am I sure about spelling? → Check autocomplete
- [ ] Am I using the right module? → Verify above
- [ ] Am I in the right format? → Check examples

---

## Getting Help

**If you're confused:**
1. Use the decision tree at the top
2. Check the use cases section
3. Look at the examples
4. Use autocomplete to verify input
5. Read the error message - it will tell you what went wrong

**If you get an error:**
```
Error: "RSID not found"
→ You're in GENE VARIANT but input a disease
→ Use DISEASE ASSOC module instead

Error: "Disease not found"
→ You're in DISEASE ASSOC but input RSID/variant
→ Use GENE VARIANT module instead
→ OR check disease name spelling
```

---

## Pro Tips

1. **Use Autocomplete** - Let the system suggest valid inputs
2. **Start Simple** - Try "Breast Cancer" or "Type 2 Diabetes"
3. **Check Spelling** - Common names work best
4. **Use HUGO Gene Symbols** - Uppercase, no spaces
5. **Include Disease Type** - "Hereditary Breast Cancer" better than just "Breast"

