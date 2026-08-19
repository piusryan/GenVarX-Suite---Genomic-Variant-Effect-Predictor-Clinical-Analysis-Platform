# GenVarX Quick Start Cheat Sheet
## One-Page Reference for All Modules

---

## 🎯 GENE VARIANT MODULE

### Input Format
```
chromosome:position:reference:alternate
17:43044295:G:A
```

### Try These (Copy-Paste)
```
Cancer Variants:
• 17:43044295:G:A  (BRCA1 - breast cancer)
• 13:32316462:G:A  (BRCA2 - ovarian cancer)
• 17:7673802:C:T   (TP53 - tumor suppressor)
• 7:55249071:T:G   (EGFR - lung cancer driver)
• 12:25398284:C:A  (KRAS - pancreatic cancer)

Cardiovascular:
• 1:55505647:G:A   (LDLR - cholesterol)
• 19:44919406:G:A  (APOE - heart disease risk)
```

### What to Look For
| Field | What It Means | Good Sign |
|-------|---------------|-----------|
| **impact_level** | Severity | HIGH = likely harmful |
| **consequence** | Type of change | frameshift = very harmful |
| **clinical_significance** | Disease status | Pathogenic = confirmed disease |
| **SIFT** | Conservation | Deleterious = harmful |
| **PolyPhen** | Structure | Probably Damaging = harmful |

### Interpretation
```
✅ PATHOGENIC = This variant causes disease
   └─ Action: Genetic counseling, screening, prevention

❌ BENIGN = This variant is normal
   └─ Action: No concern

⚠️ UNCERTAIN = Don't know yet
   └─ Action: Consult expert, research more
```

---

## 💊 DRUG DISCOVERY MODULE

### Input Types
```
By Name: "selinexor"
By ID: "CHEMBL237500"
By Category: "EGFR inhibitor"
```

### Try These (Copy-Paste)
```
Cancer Drugs:
• selinexor          (nuclear export inhibitor)
• trastuzumab        (HER2 antibody)
• tamoxifen          (estrogen antagonist)
• erlotinib          (EGFR inhibitor - lung)
• vemurafenib        (BRAF inhibitor - melanoma)
• olaparib           (PARP inhibitor - BRCA)
• pembrolizumab      (checkpoint inhibitor)

Cardiovascular:
• statin             (cholesterol drug)
• ACE inhibitor      (blood pressure)
• beta blocker       (heart disease)

Antibiotics:
• penicillin         (bacterial infection)
• fluoroquinolone    (bacterial infection)
```

### What to Look For
| Field | What It Means | Good Sign |
|-------|---------------|-----------|
| **max_phase** | Development stage | 4 = approved, 3 = late trials |
| **qed_weighted** | Drug quality | > 0.7 = good design |
| **ro5_violations** | Drug-likeness | 0 = passes all criteria |
| **targets** | Specificity | Fewer = more specific |
| **bioactivities** | Research | More = better characterized |

### Interpretation
```
✅ max_phase = 4
   └─ Can prescribe today

⏳ max_phase = 3
   └─ Late trials, likely approval soon

🔬 max_phase < 3
   └─ Experimental, uncertain future
```

---

## 🧬 DISEASE ASSOCIATION MODULE

### Input Format
```
Same as Gene Variant:
chromosome:position:reference:alternate
17:43044295:G:A
```

### Try These (Copy-Paste)
```
• 17:43044295:G:A  (BRCA1 - check cancer associations)
• 7:55249071:T:G   (EGFR - check GWAS hits)
• 1:55505647:G:A   (LDLR - check cholesterol links)
```

### What to Look For
| Field | What It Means | Strong Sign |
|-------|---------------|-------------|
| **rs_id** | Database ID | rs123456 = well-documented |
| **trait** | Associated disease | Matches your condition |
| **p-value** | Statistical significance | < 1e-20 = very strong |
| **pubmed_id** | Literature | Check the paper |

### P-Value Quick Guide
```
p < 5e-8       ✅ Genome-wide significant (published)
p < 1e-20      ✅ Very strong association
p < 1e-50      ✅✅✅ Extreme finding (landmark)
p > 1e-8       ⚠️ Not statistically significant
```

---

## 🔥 THREE WORKFLOWS (Choose One)

### Workflow A: Is This Variant Dangerous?
```
1. Input variant → GENE VARIANT module
2. Check: impact_level = ?
   • HIGH → likely harmful
   • MODERATE → maybe harmful
   • LOW → probably fine
3. Check: clinical_significance = ?
   • Pathogenic → YES it's dangerous
   • Benign → NO it's safe
   • Uncertain → need more info
4. Check: SIFT + PolyPhen agreement
   • Both Deleterious → definitely harmful
   • Both Benign → definitely safe
   • Mixed → conflicting, need expert
```

### Workflow B: What Drug Should I Take?
```
1. GENE VARIANT → Identify cancer driver
   (example: EGFR mutation in lung cancer)
2. DISEASE ASSOCIATION → Confirm cancer risk
   (check p-value < 1e-20)
3. DRUG DISCOVERY → Search for therapy
   • Try: "[gene name] inhibitor"
   • Try: "[cancer type] therapy"
   • Look for: max_phase = 4 (approved)
4. Result: Evidence-based treatment options
```

### Workflow C: Do I Have High Disease Risk?
```
1. GENE VARIANT → Enter patient variant
   (example: LDLR mutation)
2. Check: clinical_significance
   • Pathogenic → YES you have risk
   • Benign → NO you don't
3. DISEASE ASSOCIATION → Confirm risk level
   • p-value < 1e-50 → extreme risk
   • p-value < 1e-20 → very high risk
   • p-value > 1e-8 → weak association
4. Plan: Surveillance, prevention, lifestyle
```

---

## 🚩 RED FLAGS & GREEN LIGHTS

### ✅ Green Lights (Good Signs)
```
clinical_significance = Pathogenic
rs_id = rs123456  (known variant)
impact_level = HIGH
consequence = frameshift_variant
SIFT = Deleterious
p-value < 1e-20  (strong association)
max_phase = 4  (approved drug)
qed_weighted > 0.8  (good drug)
```

### ⚠️ Yellow Flags (Need More Info)
```
clinical_significance = Uncertain
rs_id = null  (novel variant)
impact_level = MODERATE
consequence = missense_variant
SIFT ≠ PolyPhen  (disagreement)
p-value 1e-8 to 1e-20  (moderate association)
max_phase = 2-3  (experimental)
qed_weighted 0.4-0.7  (marginal drug)
```

### ❌ Red Flags (Problems)
```
clinical_significance = Benign BUT high impact
rs_id = null AND max_phase = 0
impact_level = HIGH BUT p-value > 0.05
SIFT = Tolerated BUT PolyPhen = Probably Damaging
consequence = synonymous BUT family history
max_phase = 0-1  (research only)
qed_weighted < 0.4  (poor drug design)
ro5_violations > 2  (likely issues)
```

---

## 📊 INTERPRETATION MATRIX

### Clinical Significance vs Impact Level
```
Pathogenic + HIGH Impact
  → Confirmed disease, needs action
  → Genetic counseling, surveillance

Pathogenic + MODERATE Impact
  → Likely disease, depends on context
  → Consult expert

Pathogenic + LOW Impact
  → Mild disease or silent variant
  → May not cause symptoms

Benign + HIGH Impact
  → Conflicting signals, need expert review
  → Likely false alarm

Uncertain + Any Impact
  → Not enough data
  → Requires functional studies
```

### Drug Stage vs Efficacy
```
Phase 4 (Approved) = Can prescribe
Phase 3 (Late Trials) = Likely approval soon
Phase 2 (Mid Trials) = Efficacy being tested
Phase 1 (Early Trials) = Safety being tested
Phase 0 (Research) = Laboratory only
Discontinued = Development stopped
```

---

## 💡 TIPS & TRICKS

### To Find a Specific Variant
```
1. Know the gene name? Search: "GENE chromosome"
2. Know the disease? Search: "DISEASE gene"
3. Copy-paste example from this sheet
4. Use color-coded presets in UI
```

### To Find a Drug
```
By name: selinexor
By ID: CHEMBL237500
By mechanism: "EGFR inhibitor"
By disease: "breast cancer therapy"
By category: "checkpoint inhibitor"
```

### To Understand an Output Field
```
1. Look it up in FIELD_REFERENCE_GUIDE.md
2. Search (Ctrl+F) for the field name
3. Read the explanation + examples
4. Check the interpretation guide
```

### To Learn More
```
Quick Start? → INPUT_GUIDE_SUMMARY.md
Field meanings? → FIELD_REFERENCE_GUIDE.md
Real examples? → PRESET_QUERY_SETS.md
Clinical cases? → PRESET_QUERY_SETS.md (cases section)
```

---

## 🎯 DECISION TREE

```
START HERE
    ↓
Is this about a VARIANT?
    ├─ YES → Use GENE VARIANT module
    │         ↓
    │        Is it in my patient/family?
    │         ├─ YES → Check clinical_significance
    │         │        ├─ Pathogenic → Disease risk
    │         │        ├─ Benign → No concern
    │         │        └─ Uncertain → Need expert
    │         └─ NO → Use for research/learning
    │
    ├─ NO → Is this about a DRUG?
    │        ├─ YES → Use DRUG DISCOVERY module
    │        │        ├─ For cancer? Search "inhibitor"
    │        │        ├─ For prevention? Search "statin"
    │        │        └─ For treatment? Search by target
    │        │
    │        └─ NO → Use DISEASE ASSOCIATION module
    │                ├─ Check disease links
    │                ├─ Look at p-values
    │                └─ Find GWAS studies
    ↓
DONE! You have your answer.
```

---

## 🔗 WHERE TO FIND THINGS

| Question | File | Section |
|----------|------|---------|
| What does this field mean? | FIELD_REFERENCE_GUIDE.md | Field definitions |
| Show me an example | PRESET_QUERY_SETS.md | Presets section |
| How do I start? | INPUT_GUIDE_SUMMARY.md | Quick start |
| Real patient story? | PRESET_QUERY_SETS.md | Clinical case studies |
| What to search for? | PRESET_QUERY_SETS.md | Query collections |
| This seems wrong | INPUT_GUIDE_SUMMARY.md | Troubleshooting |

---

## 📋 COPY-PASTE TEMPLATE

### Template 1: Analyze Cancer Risk
```
Variant: 17:43044295:G:A
Input to: GENE VARIANT module
Check these fields:
  - gene_symbol: should be BRCA1
  - impact_level: should be HIGH
  - clinical_significance: should be Pathogenic
  - associated_diseases: should include cancer

Then: DISEASE ASSOCIATION for same variant
Check: p-value (look for < 1e-20)

Then: DRUG DISCOVERY
Search: "PARP inhibitor" or "cancer drug"
Look for: max_phase = 4
```

### Template 2: Check Drug Options
```
Your disease: Lung cancer
Your mutation: EGFR exon 19 deletion

GENE VARIANT: 7:55249071:T:G
Check: consequence (should be deletion/missense)

DRUG DISCOVERY: Search "EGFR inhibitor"
Results should include:
  - erlotinib (Phase 4)
  - gefitinib (Phase 4)
  - afatinib (Phase 4)

Choose: Highest max_phase with best qed_weighted
```

### Template 3: Assess Disease Risk
```
Your variant: 1:55505647:G:A (LDLR)
Your symptom: High cholesterol

GENE VARIANT: 1:55505647:G:A
Check: clinical_significance (Pathogenic?)
       impact_level (HIGH?)

DISEASE ASSOCIATION: Same variant
Check: p-value (< 1e-20?)
       reported_trait (hypercholesterolemia?)

DRUG DISCOVERY:
Search: "statin" for first-line
Search: "PCSK9 inhibitor" for escalation
```

---

## ✨ REMEMBER

✅ **For variants:** Focus on impact_level + clinical_significance  
✅ **For drugs:** Focus on max_phase + qed_weighted  
✅ **For diseases:** Focus on p-value + reported_trait  
✅ **When unsure:** Use color-coded UI presets  
✅ **For details:** Check FIELD_REFERENCE_GUIDE.md  
✅ **For examples:** Check PRESET_QUERY_SETS.md  

---

**Print this page & keep it handy!**

Last Updated: August 2026 | Version 1.0
