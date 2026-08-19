# GWAS Module Quick Guide

## What is GWAS?

**GWAS Catalog** = Genome-Wide Association Studies database maintained by the EBI (European Bioinformatics Institute).

It contains associations between genetic variants and traits/diseases discovered through large population studies (typically thousands to millions of subjects).

---

## When Does GWAS Work?

### ✅ Works for Common Variants
- Variants with a **public rsID** (rs prefix, like rs12345678)
- Found in **large population studies** (MAF > 1%)
- Associated with **population-level traits**

**Example:** LDLR (1:55505647:G:A)
- Has rsID: ✅ YES
- In GWAS Catalog: ✅ YES
- Shows: Multiple cholesterol-related GWAS hits

### ❌ Doesn't Work for Rare Variants
- No public rsID (or not indexed in GWAS)
- Rare familial variants (MAF < 0.1%)
- Clinically significant but not population-level

**Example:** BRCA1 (17:43044295:G:A)
- Has rsID: ❌ NO
- In GWAS Catalog: ❌ NO
- Shows: "rsID not found"

---

## Understanding the Result

### If You See "rsID: N/A"
**This means:**
- Variant doesn't have a public rsID
- Variant is not in GWAS Catalog
- System is working correctly

**What to do:**
1. Check the **Gene Variant module** for ClinVar clinical significance
2. Search medical literature for variant-specific evidence
3. Use population-level data (like allele frequency) from VEP results

### If You See GWAS Associations
**This means:**
- Variant has an rsID: ✅
- Variant is in GWAS Catalog: ✅
- Shows: Traits associated with this variant in population studies

**Example row interpretation:**
| Trait | P-value | Allele | Study |
|---|---|---|---|
| LDL Cholesterol | 3.2e-45 | A | GCST90001410 |
- Very strong association (tiny p-value)
- The A allele is associated with LDL levels
- From study GCST90001410

---

## Quick Lookup Table

| Variant | Category | rsID? | GWAS Data? | Where to Look |
|---|---|---|---|---|
| BRCA1 (17:43044295:G:A) | Rare pathogenic | No | No | Gene Variant (ClinVar) |
| LDLR (1:55505647:G:A) | Common | Yes | Yes | **GWAS Module** ✅ |
| APOE (19:44919406:G:A) | Common | Yes | Yes | **GWAS Module** ✅ |
| Novel de novo | Unknown | No | No | Literature + Scores |
| Copy number variant | Structural | No | No | Specialized databases |

---

## Test These Variants

### Should Show GWAS Data ✅
**Metabolic/Cardiovascular:**
- `1:55505647:G:A` → LDLR (Cholesterol)
- `19:44919406:G:A` → APOE (Heart Disease)
- `7:127387562:C:T` → GCK (Type 2 Diabetes)

**Population Variants:**
- `11:116414097:C:T` → CAD risk
- `10:114758349:T:C` → BMI

### Will Show "rsID: N/A" ⚠️
(These are rare pathogenic - check Gene Variant module instead)
- `17:43044295:G:A` → BRCA1 (Breast Cancer)
- `13:32316462:G:A` → BRCA2 (Ovarian Cancer)
- `17:7673802:C:T` → TP53 (Li-Fraumeni)

---

## Common Questions

### Q: Why doesn't BRCA1 show GWAS data?
**A:** BRCA1 is a rare familial variant. GWAS studies only have data for common variants from large populations. BRCA1 pathogenicity comes from clinical evidence, not population statistics. See the **Gene Variant module** for ClinVar significance instead.

### Q: Is this a bug?
**A:** No. The system correctly identifies when rsID is missing. This is expected behavior for rare variants.

### Q: How do I know if a variant WILL have GWAS data?
**A:** If it has a public rsID (shown in Gene Variant results like "rs80357154"), it might have GWAS data. Try it in the GWAS module. If not, the variant is too rare for GWAS Catalog.

### Q: What's the difference between GWAS and ClinVar?
- **GWAS:** Population-level associations (common variants, many people)
- **ClinVar:** Clinical significance (rare variants, individual cases)

### Q: Can I use GWAS for disease diagnosis?
**A:** No. GWAS shows statistical associations in populations, not direct cause-effect. For genetic diagnosis, use:
- ClinVar (clinical significance)
- HGMD (mutation database)
- Literature evidence
- Functional predictions

---

## Understanding GWAS Results

If results appear, here's how to read them:

```
Associated Trait: LDL Cholesterol
P-value: 3.2e-45
Risk Allele: A (from rs80357154 SNP)
Study: GCST90001410
```

**Translation:**
- "LDL Cholesterol" = This variant is associated with cholesterol levels
- "3.2e-45" = Extremely strong statistical evidence
- "A allele" = The A version of this SNP is linked to the trait
- "GCST90001410" = The GWAS Catalog study ID (look up for details)

---

## Next Steps

1. **For common variants (with rsID):** Use GWAS Module to find population associations
2. **For rare variants (no rsID):** Use Gene Variant Module to see clinical significance
3. **For drug discovery:** Use Drug Discovery Module to search ChEMBL
4. **For details:** See PRESET_QUERY_SETS.md and FIELD_REFERENCE_GUIDE.md

---

**More Info:** See `GWAS_MODULE_ANALYSIS.md` for technical details
