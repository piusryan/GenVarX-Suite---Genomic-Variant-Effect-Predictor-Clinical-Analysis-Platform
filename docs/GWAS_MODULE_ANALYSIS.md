# GWAS Module Analysis: Why rsID Returns N/A

## Problem Summary
When users enter variants like BRCA1 (17:43044295:G:A) into the GWAS module, they see:
- **RESOLVED RSID: N/A**
- **NO GENOME-WIDE ASSOCIATIONS RECORDED**

## Root Cause Analysis

### What is happening (technical flow):
1. User enters variant in format: `chr:pos:ref:alt` (e.g., `17:43044295:G:A`)
2. System calls VEP (Variant Effect Predictor) to annotate the variant
3. VEP returns variant data including `colocated_variants` array
4. Service searches `colocated_variants` for an rsID (identifier starting with "rs")
5. If rsID found → System queries EBI GWAS Catalog API with that rsID
6. If rsID NOT found → Returns: `rs_id=None` and note "rsID not found for this variant"

### Why BRCA1 returns N/A:
**BRCA1 (17:43044295:G:A) is a rare, pathogenic variant that:**
- Doesn't have an rsID in public databases (Ensembl/dbSNP)
- Is a familial/hereditary variant (not a common population variant)
- Isn't tracked in GWAS Catalog (which focuses on common variants from large epidemiological studies)

**GWAS Catalog itself:**
- Contains results from Genome-Wide Association Studies
- Focuses on **common variants** (MAF typically > 1%)
- Uses **population-level phenotype data** from large cohorts
- Is NOT designed for rare monogenic/syndromic variants

This is **expected and correct behavior** – not a bug.

---

## Why This Design Makes Sense

| Variant Type | Has rsID? | In GWAS Catalog? | Use Case |
|---|---|---|---|
| Common variants (MAF > 1%) | Yes (rs#####) | Often yes | Disease associations, risk prediction |
| Rare pathogenic (MAF < 0.1%) | Rarely | Almost never | Monogenic disease diagnosis |
| Copy number variants | No | Rarely | Structural variation analysis |
| De novo variants | No | No | Novel genetic findings |

**BRCA1 variants** fall into the "rare pathogenic" category. They're diagnosed using:
- ClinVar database (shows clinical significance)
- Literature evidence (medical genetics databases)
- NOT GWAS Catalog (which is population statistics)

---

## What's Working Correctly

✅ **VEP service** correctly identifies when rsID is missing
✅ **GWAS service** correctly returns note: "rsID not found for this variant"
✅ **UI displays** the "N/A" appropriately
✅ **Alternative data** (ClinVar) IS shown in Gene Variant module for BRCA1

---

## Recommendations for Improvement

### Option 1: Better User Education (Quick Fix)
**Add informative message in GWAS UI:**
```
"rsID not found - This is a rare variant not tracked in GWAS Catalog. 
GWAS contains only common population variants (MAF > 1%). 
For rare pathogenic variants like this, see the Gene Variant module 
which shows ClinVar clinical significance."
```

**Where to implement:** `src/App.jsx` line ~524 in the GWAS result section

### Option 2: Add Local GWAS Fallback (Medium Effort)
Create a local GWAS Catalog snapshot for variants without rsIDs:
- Download GWAS Catalog VCF/TSV
- Index by genomic coordinates
- Query as fallback when rsID lookup fails
- **Benefit:** More robust, works offline
- **Cost:** ~50-100MB dataset, maintenance burden

### Option 3: Coordinate-Based GWAS Lookup (Advanced)
Instead of requiring rsID:
- Query GWAS by genomic coordinates directly
- Map coordinates to GWAS variants via interval overlap
- Return associations if coordinate is within GWAS variant window
- **Benefit:** Catches more variants
- **Cost:** More complex API integration, need coordinate indexing

### Option 4: Add HPO/OntoGenesis Links (Clinical Enhancement)
For rare variants without GWAS data:
- Link to Human Phenotype Ontology (HPO)
- Show disease-gene relationships
- Complement ClinVar with phenotype networks
- **Benefit:** More clinically useful for rare disease
- **Cost:** Need HPO API/dataset integration

---

## Test Cases to Verify Behavior

### Should Show "rsID not found" (Expected, Correct):
- ✅ BRCA1: `17:43044295:G:A` (rare pathogenic)
- ✅ BRCA2: `13:32316462:G:A` (rare pathogenic)
- ✅ TP53: `17:7673802:C:T` (rare pathogenic)

### Should Show GWAS Associations (if rsID found):
- ⏳ LDLR: `1:55505647:G:A` (cholesterol GWAS trait)
- ⏳ APOE: `19:44919406:G:A` (heart disease GWAS trait)
- ⏳ KRAS: `12:25398284:C:A` (cancer predisposition)

**Note:** Testing requires backend running with external EBI GWAS API access

---

## Implementation Priority

| Task | Priority | Effort | Impact |
|---|---|---|---|
| Add better UI messaging | HIGH | 15 min | Immediate clarity for users |
| Document behavior | HIGH | 5 min | Prevents user confusion |
| Update GWAS presets | MEDIUM | 30 min | Guide users to testable variants |
| Add local GWAS fallback | MEDIUM | 2-3 hrs | Robustness + offline capability |
| Coordinate-based lookup | LOW | 4+ hrs | Advanced feature, complex |

---

## Files Involved

**Backend:**
- `app/services/vep_service.py` (line ~74-80) - rsID extraction logic
- `app/services/gwas_service.py` (line ~11-17) - GWAS API call
- `app/main.py` (line ~66-78) - GWAS endpoint logic

**Frontend:**
- `src/App.jsx` (line ~515-560) - GWAS UI and result display

**Documentation:**
- `docs/PRESET_QUERY_SETS.md` - Add note about rsID dependency
- `docs/FIELD_REFERENCE_GUIDE.md` - Explain GWAS limitation

---

## Conclusion

The system is **working as designed**. BRCA1 showing "rsID: N/A" is correct because:
1. BRCA1 is a rare variant without an rsID
2. GWAS Catalog only indexes common variants with rsIDs
3. The ClinVar data shown in Gene Variant module is the appropriate source for BRCA1

**Recommended next step:** Improve UI messaging to explain this clearly, then test with common variants that DO have GWAS data (like LDLR, APOE).
