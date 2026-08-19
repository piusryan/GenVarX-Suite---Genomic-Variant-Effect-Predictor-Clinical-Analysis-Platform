# GenVarX Complete Input Guide - Summary
## Quick Start + Links to Detailed Documentation

**Last Updated:** August 2026  
**Version:** 1.0

---

## 🚀 Quick Start (2 Minutes)

### Gene Variant Module - Try This Now:

```
Input:  17:43044295:G:A
        └─ BRCA1 breast cancer mutation

Expected Output:
  ✅ Gene: BRCA1
  ✅ Impact: HIGH
  ✅ Clinical Significance: Pathogenic
  ✅ Disease Risk: Breast & Ovarian Cancer
```

### Drug Discovery Module - Try This Now:

```
Input: selinexor
       └─ Cancer drug name

Expected Output:
  ✅ ChEMBL ID: CHEMBL237500
  ✅ Max Phase: 4 (Approved)
  ✅ Target: XPO1 (nuclear export)
  ✅ Used for: Multiple cancer types
```

### Disease Association Module - Try This Now:

```
Input: 17:43044295:G:A
       └─ Same variant as Gene Variant

Expected Output:
  ✅ RS ID: rs80357154
  ✅ Associated Disease: Breast cancer
  ✅ P-value: 1.5e-50 (extremely strong)
  ✅ Literature: 500+ studies
```

---

## 📚 Detailed Documentation

### For Complete Field Explanations
**→ Read:** `docs/FIELD_REFERENCE_GUIDE.md`

**Covers:**
- Every input field explained
- Every output field explained
- What values mean
- How to interpret results
- Frequently asked questions
- Complete examples

**Use When:**
- "What does `alogp` mean?"
- "How do I interpret p-values?"
- "What's the difference between SIFT and PolyPhen?"

---

### For Ready-to-Use Presets & Examples
**→ Read:** `docs/PRESET_QUERY_SETS.md`

**Covers:**
- 20+ cancer mutation presets
- Organized by disease type
- Drug discovery presets by category
- Complete workflow examples
- Real clinical case studies
- Research query collections

**Use When:**
- "Show me breast cancer variants"
- "What drug searches should I try?"
- "How do I do a complete analysis?"
- "Real patient examples?"

---

## 🎯 Module-Specific Guides

### GENE VARIANT Module

#### Input Format
```
chromosome:position:reference:alternate

Example: 17:43044295:G:A
         │   │        │ └─ What patient has (A)
         │   │        └──── Normal reference (G)
         │   └──────────── Position on chromosome
         └───────────────── Chromosome 17
```

#### Valid Inputs
```
17:43044295:G:A      ✅ Standard SNV
7:55249071:T:G       ✅ EGFR lung cancer
12:25398284:C:A      ✅ KRAS pancreatic cancer
1:55505647:G:A       ✅ LDLR cholesterol
X:123456789:A:T      ✅ Sex chromosome variant
```

#### What You Get Back
```
1. gene_symbol       → Which gene is affected (BRCA1, EGFR, etc)
2. impact_level      → HIGH / MODERATE / LOW severity
3. consequence       → Type of variant (missense, frameshift, etc)
4. sift_prediction   → Deleterious / Tolerated
5. polyphen_prediction → Probably Damaging / Benign
6. amino_acid_change → What protein change (D/V, G/R, etc)
7. clinical_significance → Pathogenic / Benign / Uncertain
8. associated_diseases → List of known diseases
```

#### Popular Presets (All in UI)
```
🔴 HIGH RISK - Cancer
├─ BRCA1:   17:43044295:G:A
├─ BRCA2:   13:32316462:G:A
├─ TP53:    17:7673802:C:T
└─ PTEN:    10:89717702:G:A

🟠 MODERATE RISK - Somatic
├─ EGFR:    7:55249071:T:G
├─ KRAS:    12:25398284:C:A
├─ BRAF:    7:140753336:A:T
└─ APC:     5:112839461:T:A

🔵 CARDIOVASCULAR
├─ LDLR:    1:55505647:G:A
└─ APOE:    19:44919406:G:A

🟣 NEUROLOGICAL
├─ HTT:     4:3076604:CAG
└─ PSEN1:   14:73625380:C:T
```

**→ Full preset list:** See `PRESET_QUERY_SETS.md`

---

### DRUG DISCOVERY Module

#### Input Types
```
1. Drug Name
   Input: "selinexor"
   Search: Drug name search (case-insensitive)
   Returns: All matching compounds

2. ChEMBL ID
   Input: "CHEMBL237500"
   Search: Exact compound by ID
   Returns: Single exact match + details

3. Drug Class/Target
   Input: "EGFR inhibitor"
   Search: Drug category search
   Returns: All drugs in category
```

#### What You Get Back
```
Basic Info:
  - chembl_id (unique ID)
  - name (drug name)
  - compound_type (small molecule, antibody, etc)

Development Status:
  - max_phase (0=research, 1-3=trials, 4=approved)

Drug Properties:
  - molecular_weight (ideal: < 500)
  - alogp (lipophilicity, ideal: 0-3)
  - qed_weighted (drug-likeness score, 0-1)
  - ro5_violations (Lipinski Rule of 5)

Activity:
  - targets (number of proteins hit)
  - bioactivities (known activity records)

Detailed Structure:
  - polar_surface_area (PSA, for BBB penetration)
  - hba, hbd (hydrogen bond donors/acceptors)
  - aromatic_rings, rotatable_bonds
  - smiles, inchi_key (chemical structure codes)
```

#### Popular Presets (All in UI)
```
🔴 CANCER THERAPEUTICS
├─ Monoclonal Antibodies: "trastuzumab" (HER2)
├─ EGFR Inhibitors: "erlotinib", "gefitinib"
├─ BRAF Inhibitors: "vemurafenib"
├─ PARP Inhibitors: "olaparib", "rucaparib"
├─ Checkpoint Inhibitors: "pembrolizumab"
└─ Chemotherapy: "paclitaxel", "carboplatin"

🔵 CARDIOVASCULAR
├─ Statins: "statin"
├─ ACE Inhibitors: "ACE inhibitor"
├─ Beta Blockers: "beta blocker"
└─ PCSK9 Inhibitors: "PCSK9 inhibitor"

🟢 ANTIBIOTICS
├─ Penicillins: "penicillin"
├─ Fluoroquinolones: "fluoroquinolone"
└─ Antivirals: "oseltamivir"
```

**→ Full preset list:** See `PRESET_QUERY_SETS.md`

---

### DISEASE ASSOCIATION Module

#### Input Format
```
Same as Gene Variant:
chromosome:position:reference:alternate

Example: 17:43044295:G:A (BRCA1 breast cancer)
```

#### What You Get Back
```
1. rs_id               → dbSNP identifier (rs123456)
2. trait               → Associated disease/trait
3. p-value             → Statistical significance
4. reported_trait      → Clinical disease name
5. study_accession     → GWAS Catalog ID
6. pubmed_id           → Published literature
7. strongest_allele    → Which allele = risk
8. note                → Additional info
```

#### P-Value Interpretation
```
p < 5e-8   → Genome-wide significant (published)
p < 1e-20  → Very strong association
p < 1e-50  → Extreme/landmark discovery (BRCA1 & cancer)
p > 1e-8   → Not significant
```

---

## 🔥 Common Workflows

### Workflow 1: Check if Variant is Harmful
```
1. Input variant in GENE VARIANT module
2. Look at: impact_level (HIGH = likely harmful)
3. Look at: consequence (stop_gained, frameshift = very harmful)
4. Look at: clinical_significance (Pathogenic = confirmed harmful)
5. Look at: SIFT + PolyPhen (both Deleterious = harmful)

If ALL say harmful → Likely pathogenic
If mixed → Requires expert interpretation
```

### Workflow 2: Find Treatment for Cancer
```
1. GENE VARIANT module: Identify cancer driver (EGFR, BRAF, etc)
2. DISEASE ASSOCIATION: Confirm cancer risk (p < 1e-20)
3. DRUG DISCOVERY module: Search for targeted therapy
   - Try: "[Gene name] inhibitor"
   - Try: "[Cancer type] therapy"
   - Try: "targeted therapy"
   - Look for: max_phase = 4 (approved)

Result: Evidence-based treatment options
```

### Workflow 3: Assess Genetic Disease Risk
```
1. GENE VARIANT: Enter patient variant
2. Check: clinical_significance (Pathogenic = disease risk)
3. Check: associated_diseases (which diseases)
4. DISEASE ASSOCIATION: Confirm risk level
   - Look at: p-value (lower = stronger association)
   - Look at: pubmed_id (check literature)
5. Make informed decision about:
   - Surveillance (more frequent screening)
   - Prevention (prophylactic surgery)
   - Family counseling (autosomal dominant pattern)
```

---

## 🆘 Troubleshooting

### "What if rs_id is null?"
**Meaning:** Variant not in dbSNP database (novel or very rare)
**Next Step:** Check clinical_significance; if Pathogenic, likely important

### "What if clinical_significance is 'Uncertain'?"
**Meaning:** Unknown clinical effect (not enough data)
**Next Step:** Look at SIFT/PolyPhen; may require functional studies

### "What if impact_level is 'LOW'?"
**Meaning:** Probably tolerated; silent or intronic mutation
**Next Step:** Usually benign unless conflicting evidence

### "What if drug has max_phase = 1?"
**Meaning:** Early stage trials, uncertain future
**Next Step:** Look for phase 3-4 alternatives; don't rely on this drug

### "What if p-value is > 1e-8?"
**Meaning:** Not genome-wide significant
**Next Step:** Weak association; not reliable for clinical use

---

## 📖 How to Read Output Fields

### High-Priority Fields
```
These 3 fields tell you the most important info:

1. clinical_significance
   Pathogenic → Disease
   Benign → Normal
   Uncertain → Unknown

2. impact_level
   HIGH → Likely harmful
   MODERATE → Maybe harmful
   LOW → Probably fine

3. associated_diseases
   If match your patient's condition → Likely relevant
   If no match → Unexpected finding
```

### For Drug Selection
```
These fields matter most:

1. max_phase
   4 = Approved (can prescribe)
   3 = Late trials (likely approval soon)
   < 3 = Experimental (uncertain)

2. qed_weighted
   > 0.8 = Good drug design
   < 0.4 = Poor drug design

3. ro5_violations
   0 = Good (passes all criteria)
   > 2 = Problems expected
```

### For Disease Risk
```
These fields matter most:

1. p-value
   < 1e-20 = Very strong
   < 1e-50 = Extreme

2. reported_trait
   If matches patient diagnosis → Relevant

3. pubmed_id
   Check literature to understand mechanism
```

---

## 🎓 Learning Path

**Day 1: Basics (30 minutes)**
1. Read this summary file
2. Try the 3 quick examples above
3. Explore the UI presets

**Day 2: Understand Output (1 hour)**
1. Read `FIELD_REFERENCE_GUIDE.md` (understand each field)
2. Try 5 variant searches
3. Note what fields change based on input

**Day 3: Drug Discovery (30 minutes)**
1. Read drug discovery section of `FIELD_REFERENCE_GUIDE.md`
2. Try 3 drug searches
3. Compare results (approved vs experimental)

**Day 4: Real Examples (1 hour)**
1. Read `PRESET_QUERY_SETS.md` (clinical case studies)
2. Work through one complete case workflow
3. Understand interpretation logic

**Day 5+: Deep Dives**
- Advanced topics in `FIELD_REFERENCE_GUIDE.md`
- Research query collections in `PRESET_QUERY_SETS.md`
- Explore specific diseases/genes of interest

---

## 📞 Quick Reference Card

### When You See...

| Output | Meaning | Action |
|--------|---------|--------|
| `clinical_significance: Pathogenic` | Disease-causing | ⚠️ Important finding |
| `impact_level: HIGH` | Likely harmful | ⚠️ Requires attention |
| `rs_id: rs123456` | Documented variant | ✅ Check literature |
| `rs_id: null` | Novel variant | ⚠️ Needs validation |
| `max_phase: 4` | Approved drug | ✅ Can prescribe |
| `max_phase: 1` | Early trials | ❌ Don't use yet |
| `qed_weighted: 0.8` | Good drug | ✅ Likely works |
| `qed_weighted: 0.2` | Poor drug | ❌ Problems likely |
| `p-value: 1e-50` | Extremely strong | ✅✅✅ Definite link |
| `p-value: 0.05` | Not significant | ⚠️ Weak evidence |

---

## 🔗 File Navigation

```
docs/
├─ INPUT_GUIDE_SUMMARY.md          ← You are here
├─ FIELD_REFERENCE_GUIDE.md         ← Complete field meanings
├─ PRESET_QUERY_SETS.md            ← Ready-to-use examples
│
├─ README.md                        ← General project overview
├─ HOW_TO_RUN.md                   ← Run instructions
├─ START_HERE.md                   ← Getting started
│
├─ DATASET*.md                     ← Dataset documentation
│
└─ REFERENCE.pdf                   ← Scientific references
```

---

## ✅ Checklist: Ready to Use GenVarX?

- [ ] Read this summary file
- [ ] Try 1 variant search
- [ ] Try 1 drug search
- [ ] Try 1 disease association
- [ ] Read FIELD_REFERENCE_GUIDE.md for any unclear fields
- [ ] Read PRESET_QUERY_SETS.md for more examples
- [ ] Bookmark these docs for reference

---

## 🎉 You're Ready!

You now have:
✅ Expanded variant presets (20+ cancer variants)
✅ Expanded drug presets (50+ drug searches)
✅ Complete field documentation (26 output fields explained)
✅ Real clinical examples (3 case studies)
✅ Research query collections (organized by disease)

**Start exploring:** Open GenVarX UI and try the presets!

---

**Questions?** 
→ Check FIELD_REFERENCE_GUIDE.md
→ Check PRESET_QUERY_SETS.md
→ Review this summary again

**Version History:**
- v1.0 - Complete input guide summary (August 2026)

