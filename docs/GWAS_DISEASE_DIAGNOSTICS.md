# GWAS Disease Association Diagnostics

## Overview
The DISEASE ASSOC module now includes **comprehensive dataset analysis and diagnostic output** to help you understand why a variant may or may not show GWAS associations.

## What's New

### 1. **Dataset Analysis & Diagnostics Panel**
When you search for a variant in the DISEASE ASSOC module, you now see:

#### **VEP Extraction Results**
- **Input Variant**: The exact variant coordinates you queried
- **Resolved rsID**: Whether the variant has a registered rsID in the Ensembl database
- **Gene**: Associated gene symbol
- **Consequence**: Variant type (missense, synonymous, etc.)
- **Clinical Significance**: ClinVar clinical classification

#### **GWAS Catalog Status**
- **Status**: ✓ FOUND or ✗ NOT FOUND
- **Associations Found**: Number of disease associations from GWAS Catalog

#### **Local Datasets Available**
- Lists all dataset directories configured in `/data/datasets/`
- Shows file counts and samples of available data

#### **Diagnostic Message**
- Explains what was found or why something wasn't found
- Examples:
  - `✓ GWAS Catalog: Found 5 associations`
  - `⚠️ rsID exists but has no GWAS associations`
  - `✗ No rsID found - variant not recognized by VEP/GWAS`

---

## Why You Might See "RSID NOT FOUND"

### Common Reasons:
1. **Rare/Familial Variant**: GWAS Catalog only includes common variants (MAF > 1%)
2. **New Mutations**: Recently discovered variants may not have rsIDs assigned yet
3. **Invalid Format**: Variant coordinates may be incorrectly formatted
4. **Chromosome/Position Outside Known Regions**: Coordinates outside cataloged regions

### What to Do:
- Check the **VEP Extraction Results** panel for clues
- If rsID exists but no associations: variant is rare
- If no rsID at all: variant may not be in public databases yet
- Try test presets like **LDLR** or **APOE** to verify system works

---

## How to Use

### Step 1: Query a Variant
Enter variant in format: `CHR:POS:REF:ALT`
Example: `7:127387562:C:T`

### Step 2: Review Diagnostic Output
The **Dataset Analysis & Diagnostics** panel shows:
- ✓ Whether rsID was found
- ✓ What local datasets are available
- ✓ Why associations were or weren't found

### Step 3: Understand Results
- **If GWAS Catalog associations found**: See disease traits and p-values
- **If no associations**: Check diagnostic message to understand why
- **If rsID not found**: Refer to ClinVar or Gene Variant module instead

---

## Example Scenarios

### Scenario 1: Common Variant with GWAS Data
```
Input: 7:127387562:C:T (GCK - Type 2 Diabetes)
✓ Resolved rsID: rs4148856
✓ Associations Found: 3
→ Shows GWAS Catalog disease associations
```

### Scenario 2: Rare Variant Without GWAS Data
```
Input: 17:43044295:G:A (Unknown rare variant)
✗ Resolved rsID: None
→ Diagnostic: No rsID found - variant not in public GWAS Catalog
→ Check Gene Variant or ClinVar modules instead
```

### Scenario 3: rsID Exists But No Associations
```
Input: 11:116414097:C:T (rs1333049)
✓ Resolved rsID: rs1333049
⚠️ Associations Found: 0
→ rsID recognized but no GWAS studies available
```

---

## Troubleshooting

### Backend Not Showing Debug Output?
Check server logs for `[GWAS DEBUG]` messages:
```
[GWAS DEBUG] Input variant: 7:127387562:C:T
[GWAS DEBUG] Extracted rsID: rs4148856
[GWAS DEBUG] Gene: GCK
```

### Still Can't Find Your Variant?
1. Verify variant format is correct: `CHR:POS:REF:ALT`
2. Try a test preset to confirm system works
3. Check if variant is in published GWAS studies (gwascatalog.org)

### Want to Add Local GWAS Data?
Place your datasets in `/data/datasets/` and the diagnostic panel will automatically detect them.

---

## Dataset Locations
Local datasets are scanned from:
- `/data/datasets/chembl/` - Chemical compounds
- `/data/datasets/clinvar/` - Clinical variants
- `/data/datasets/gwas/` - GWAS associations (if added)
- `/data/datasets/hpo/` - Human phenotypes
- `/data/datasets/reference/` - Reference genomes

