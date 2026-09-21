# GenVarX Preset & Example Query Sets
## Ready-to-Use Variant Analysis & Drug Discovery Searches

**Last Updated:** August 2026  
**Version:** 1.0

---

## Table of Contents

1. [Gene Variant Presets](#gene-variant-presets)
2. [Drug Discovery Presets](#drug-discovery-presets)
3. [Complete Workflow Examples](#complete-workflow-examples)
4. [Clinical Case Studies](#clinical-case-studies)
5. [Research Query Collections](#research-query-collections)

---

## GENE VARIANT PRESETS

### 🔴 HIGH RISK - Hereditary Cancer (Pathogenic Variants)

These variants are well-documented as disease-causing with clinical significance = "Pathogenic".

#### BRCA1 Mutations (Breast & Ovarian Cancer)
```
┌─────────────────────────────────────────────────────┐
│ BRCA1 (Chromosome 17) - Key Variants                │
└─────────────────────────────────────────────────────┘

Variant          | Position    | Ref:Alt | Impact   | Disease
─────────────────┼─────────────┼─────────┼──────────┼──────────────────
BRCA1 c.68_69    │ 17:43044295 │ G:A     │ HIGH     │ Breast Cancer
BRCA1 c.5266     │ 17:43049120 │ C:G     │ HIGH     │ Ovarian Cancer
BRCA1 c.6852     │ 17:43073473 │ G:A     │ HIGH     │ Hereditary BC/OC
BRCA1 c.1687     │ 17:41196312 │ A:T     │ HIGH     │ Familial Cancer
BRCA1 c.4327     │ 17:41258504 │ G:C     │ MODERATE │ Predisposition
```

**Try First:** `17:43044295:G:A` (BRCA1 classic mutation)
- Expected: rs_id = rs80357154
- Expected: clinical_significance = Pathogenic
- Expected: associated_diseases = [Breast cancer, Ovarian cancer]

---

#### BRCA2 Mutations (Breast, Ovarian, Pancreatic Cancer)
```
┌─────────────────────────────────────────────────────┐
│ BRCA2 (Chromosome 13) - Key Variants                │
└─────────────────────────────────────────────────────┘

Variant          | Position    | Ref:Alt | Impact   | Disease
─────────────────┼─────────────┼─────────┼──────────┼──────────────────
BRCA2 c.9097     │ 13:32316462 │ G:A     │ HIGH     │ Ovarian Cancer
BRCA2 c.5382     │ 13:32890559 │ C:T     │ HIGH     │ Breast Cancer
BRCA2 c.68       │ 13:32889611 │ G:A     │ HIGH     │ Hereditary BC/OC
BRCA2 c.156      │ 13:32889741 │ G:T     │ HIGH     │ Pancreatic Cancer
BRCA2 c.541      │ 13:32890175 │ C:T     │ HIGH     │ Familial Cancer
```

**Try First:** `13:32316462:G:A` (BRCA2 ovarian cancer variant)
- Expected: impact_level = HIGH
- Expected: consequence = frameshift_variant or missense_variant
- Expected: sift_prediction = Deleterious

---

#### TP53 Mutations (Li-Fraumeni Syndrome)
```
┌─────────────────────────────────────────────────────┐
│ TP53 (Chromosome 17) - Key Variants                 │
└─────────────────────────────────────────────────────┘

Variant          | Position    | Ref:Alt | Impact   | Disease
─────────────────┼─────────────┼─────────┼──────────┼──────────────────
TP53 c.818       │ 17:7673802  │ C:T     │ HIGH     │ Li-Fraumeni
TP53 c.468       │ 17:7577121  │ G:A     │ HIGH     │ Tumor Suppression
TP53 c.672       │ 17:7579312  │ A:G     │ HIGH     │ Multiple Cancers
TP53 c.245       │ 17:7571720  │ G:A     │ MODERATE │ Predisposition
TP53 c.742       │ 17:7579472  │ C:A     │ HIGH     │ Breast/Bone Cancer
```

**Try First:** `17:7673802:C:T` (TP53 tumor suppressor)
- Expected: clinical_significance = Pathogenic
- Expected: consequence = missense_variant or stop_gained
- Expected: associated_diseases includes Li-Fraumeni syndrome

---

#### PTEN Mutations (Cowden Syndrome)
```
┌─────────────────────────────────────────────────────┐
│ PTEN (Chromosome 10) - Key Variants                 │
└─────────────────────────────────────────────────────┘

Variant          | Position      | Ref:Alt | Impact   | Disease
─────────────────┼───────────────┼─────────┼──────────┼──────────────────
PTEN c.677       │ 10:89717702   │ G:A     │ HIGH     │ Cowden Syndrome
PTEN c.374       │ 10:89692260   │ C:T     │ HIGH     │ PTEN Hamartoma
PTEN c.1027      │ 10:89720624   │ G:A     │ HIGH     │ Breast Cancer Pred
```

**Try First:** `10:89717702:G:A`

---

### 🟠 MODERATE RISK - Somatic Cancer Mutations

These are commonly found in cancers but may be actionable for targeted therapy.

#### EGFR (Epidermal Growth Factor Receptor)
```
┌─────────────────────────────────────────────────────┐
│ EGFR (Chromosome 7) - Actionable Lung Cancer        │
└─────────────────────────────────────────────────────┘

Variant          | Position    | Ref:Alt | Impact    | Cancer Type
─────────────────┼─────────────┼─────────┼───────────┼──────────────────
EGFR Del19       │ 7:55249071  │ T:G     │ HIGH      │ Lung (NSCLC)
EGFR L858R       │ 7:55249071  │ T:G     │ MODERATE  │ Lung Cancer
EGFR G719X       │ 7:55086714  │ G:A     │ HIGH      │ Lung (NSCLC)
EGFR T790M       │ 7:55324723  │ C:T     │ HIGH      │ Resistance
```

**Try First:** `7:55249071:T:G` (EGFR exon 19 deletion - lung cancer driver)
- Expected: SIFT = Deleterious
- Expected: Associated with lung cancer
- Expected Drug: "EGFR inhibitor" (erlotinib, gefitinib)

---

#### KRAS (Kirsten RAS Oncogene)
```
┌─────────────────────────────────────────────────────┐
│ KRAS (Chromosome 12) - Most Common Cancer Driver    │
└─────────────────────────────────────────────────────┘

Variant          | Position      | Ref:Alt | Cancer Type
─────────────────┼───────────────┼─────────┼──────────────────
KRAS G12C        │ 12:25398284   │ C:A     │ Pancreatic
KRAS G12V        │ 12:25398284   │ C:T     │ Lung
KRAS G12D        │ 12:25398283   │ G:A     │ Colorectal
KRAS G13D        │ 12:25398285   │ G:A     │ Cholangiocarcinoma
```

**Try First:** `12:25398284:C:A` (KRAS G12C - pancreatic cancer driver)
- Expected: impact_level = HIGH
- Expected: consequence = missense_variant
- Expected: associated_diseases = [Pancreatic cancer, Colorectal cancer]

---

#### BRAF (B-Raf Proto-Oncogene)
```
┌─────────────────────────────────────────────────────┐
│ BRAF (Chromosome 7) - Melanoma & Thyroid Cancer    │
└─────────────────────────────────────────────────────┘

Variant          | Position      | Ref:Alt | Cancer Type
─────────────────┼───────────────┼─────────┼──────────────────
BRAF V600E       │ 7:140753336   │ A:T     │ Melanoma
BRAF V600K       │ 7:140753336   │ T:A     │ Papillary Thyroid
BRAF V600R       │ 7:140753337   │ C:A     │ Melanoma
```

**Try First:** `7:140753336:A:T` (BRAF V600E - melanoma driver)
- Expected: rs_id = rs113488022
- Expected: consequence = missense_variant
- Expected Drug: "BRAF inhibitor" (vemurafenib, dabrafenib)

---

#### APC (Adenomatous Polyposis Coli)
```
┌─────────────────────────────────────────────────────┐
│ APC (Chromosome 5) - Familial Adenomatous          │
│     Polyposis & Colorectal Cancer                   │
└─────────────────────────────────────────────────────┘

Variant          | Position      | Ref:Alt | Impact   | Disease
─────────────────┼───────────────┼─────────┼──────────┼──────────────────
APC c.1556       │ 5:112839461   │ T:A     │ HIGH     │ FAP
APC c.3183       │ 5:112912891   │ C:T     │ HIGH     │ Colorectal Cancer
```

**Try First:** `5:112839461:T:A`

---

### 🔵 CARDIOVASCULAR & METABOLIC

#### LDLR (LDL Receptor)
```
┌─────────────────────────────────────────────────────┐
│ LDLR (Chromosome 19) - Cholesterol Metabolism      │
└─────────────────────────────────────────────────────┘

Variant          | Position    | Ref:Alt | Trait
─────────────────┼─────────────┼─────────┼──────────────────
LDLR c.1413      │ 1:55505647  │ G:A     │ LDL Cholesterol
LDLR c.1888      │ 19:11066414 │ C:T     │ Familial Hypercholestemia
```

**Try First:** `1:55505647:G:A` (LDL cholesterol genetic variant)
- Expected associated_diseases: Heart disease, Cardiovascular disease
- Expected Drug queries: statin, "cholesterol lowering"

---

#### APOE (Apolipoprotein E)
```
┌─────────────────────────────────────────────────────┐
│ APOE (Chromosome 19) - Lipid Metabolism            │
└─────────────────────────────────────────────────────┘

Variant          | Position      | Ref:Alt | Disease Risk
─────────────────┼───────────────┼─────────┼──────────────────
APOE ε4          │ 19:44919406   │ G:A     │ Alzheimer Disease
APOE ε2          │ 19:44908684   │ C:T     │ Protective
```

**Try First:** `19:44919406:G:A` (APOE4 - Alzheimer's risk factor)
- Expected: Strong association with Alzheimer disease
- Expected p-value: Very significant (< 1e-30)

---

### 🟣 NEUROLOGICAL & PSYCHIATRIC

#### HTT (Huntingtin)
```
┌─────────────────────────────────────────────────────┐
│ HTT (Chromosome 4) - Huntington's Disease          │
└─────────────────────────────────────────────────────┘

Variant          | Position      | Ref:Alt | Impact   | Disease
─────────────────┼───────────────┼─────────┼──────────┼──────────────────
HTT CAG Repeat   │ 4:3076604     │ CAG     │ Variable │ Huntington's
(36+ repeats = disease; 40+ = juvenile onset)
```

**Note:** HTT uses CAG repeat length, not typical SNV notation
- Try: `4:3076604:CAG:CAGCAGCAG...` (simplified)

---

#### PSEN1 (Presenilin 1)
```
┌─────────────────────────────────────────────────────┐
│ PSEN1 (Chromosome 14) - Alzheimer's Disease        │
└─────────────────────────────────────────────────────┘

Variant          | Position      | Ref:Alt | Impact   | Disease
─────────────────┼───────────────┼─────────┼──────────┼──────────────────
PSEN1 c.1229     │ 14:73625380   │ C:T     │ HIGH     │ Early-Onset AD
PSEN1 c.1166     │ 14:73625317   │ C:T     │ HIGH     │ Familial AD
```

**Try First:** `14:73625380:C:T` (PSEN1 early-onset Alzheimer's)
- Expected: clinical_significance = Pathogenic
- Expected: associated_diseases = Alzheimer disease, dementia

---

## DRUG DISCOVERY PRESETS

### 🔴 CANCER THERAPEUTICS

#### By Mechanism
```
1. MONOCLONAL ANTIBODIES (Immunotherapy)
   Search terms:
   - "trastuzumab" (HER2 target - breast cancer)
   - "pembrolizumab" (PD-1 checkpoint - immunotherapy)
   - "nivolumab" (PD-1 checkpoint - immunotherapy)
   - "ipilimumab" (CTLA-4 checkpoint)
   
   Search by class:
   - "monoclonal antibody"
   - "checkpoint inhibitor"
   - "immune therapy"

2. SMALL MOLECULE TYROSINE KINASE INHIBITORS
   Search terms:
   - "erlotinib" (EGFR inhibitor - lung cancer)
   - "gefitinib" (EGFR inhibitor - lung cancer)
   - "vemurafenib" (BRAF inhibitor - melanoma)
   - "sunitinib" (multi-targeted - renal cell carcinoma)
   
   Search by class:
   - "EGFR inhibitor"
   - "kinase inhibitor"
   - "tyrosine kinase"

3. TARGETED NUCLEAR EXPORT
   - "selinexor" (XPO1 inhibitor - nuclear export)
   
   (Use: CHEMBL237500)

4. HORMONE THERAPY
   - "tamoxifen" (ER antagonist - breast cancer)
   - "anastrozole" (aromatase inhibitor)
   
   Search: "estrogen" or "hormone therapy"

5. CHEMOTHERAPY
   - "paclitaxel" (taxane - tubulin stabilizer)
   - "doxorubicin" (anthracycline - DNA intercalating)
   - "carboplatin" (platinum agent - DNA crosslinker)
   
   Search: "chemotherapy" or specific drug names
```

#### By Cancer Type
```
LUNG CANCER (NSCLC)
├─ EGFR mutations → "EGFR inhibitor"
│  └─ erlotinib, gefitinib, afatinib
├─ ALK fusions → "ALK inhibitor"
│  └─ crizotinib, alectinib
└─ PD-L1+ → "checkpoint inhibitor"
   └─ pembrolizumab, atezolizumab

BREAST CANCER
├─ HER2+ → "trastuzumab" or "HER2 antibody"
├─ ER+ → "tamoxifen" or "aromatase inhibitor"
├─ Triple negative → "chemotherapy" or "checkpoint inhibitor"
└─ BRCA1/2 mutations → "PARP inhibitor"
   └─ olaparib, rucaparib

MELANOMA
├─ BRAF V600E → "BRAF inhibitor"
│  └─ vemurafenib, dabrafenib
├─ NRAS mutations → "MEK inhibitor"
│  └─ trametinib, binimetinib
└─ High tumor burden → "immunotherapy"
   └─ pembrolizumab, nivolumab

COLORECTAL CANCER
├─ KRAS WT → "EGFR inhibitor"
│  └─ cetuximab, panitumumab
├─ High MSI → "checkpoint inhibitor"
│  └─ pembrolizumab
└─ BRAF mutant → "EGFR inhibitor" + "BRAF inhibitor"
   └─ cetuximab + vemurafenib
```

---

### 🔵 CARDIOVASCULAR DRUGS

```
CHOLESTEROL MANAGEMENT
├─ Statins (HMG-CoA inhibitors)
│  └─ atorvastatin, simvastatin, rosuvastatin
├─ PCSK9 inhibitors
│  └─ evolocumab, alirocumab
└─ Ezetimibe
   └─ cholesterol absorption inhibitor

HYPERTENSION (Blood Pressure)
├─ ACE Inhibitors
│  └─ lisinopril, enalapril, ramipril
├─ Angiotensin Receptor Blockers (ARB)
│  └─ losartan, valsartan, irbesartan
├─ Beta Blockers
│  └─ metoprolol, atenolol, bisoprolol
├─ Calcium Channel Blockers
│  └─ amlodipine, diltiazem, verapamil
└─ Diuretics
   └─ hydrochlorothiazide, furosemide

ARRHYTHMIA
├─ Amiodarone
├─ Beta Blockers
└─ Digoxin

ANTICOAGULATION
├─ Warfarin (vitamin K antagonist)
├─ Dabigatran (direct thrombin inhibitor)
└─ Rivaroxaban (Xa inhibitor)

ATHEROSCLEROSIS
├─ Clopidogrel (antiplatelet)
├─ Aspirin (antiplatelet)
└─ Ticagrelor (antiplatelet)
```

**Search Examples:**
- `statin` → All cholesterol drugs
- `ACE inhibitor` → All ACE inhibitors
- `beta blocker` → All beta blockers
- `anticoagulant` → All blood thinners

---

### 🟢 ANTIBIOTICS & ANTIMICROBIALS

```
BACTERIAL INFECTIONS
├─ Penicillins (Beta-lactams)
│  └─ amoxicillin, penicillin V, ampicillin
├─ Cephalosporins
│  └─ cephalexin, ceftriaxone, cephalothin
├─ Fluoroquinolones
│  └─ ciprofloxacin, levofloxacin, moxifloxacin
├─ Macrolides
│  └─ erythromycin, azithromycin, clarithromycin
├─ Aminoglycosides
│  └─ gentamicin, streptomycin, neomycin
└─ Tetracyclines
   └─ tetracycline, doxycycline, minocycline

FUNGAL INFECTIONS
├─ Azoles
│  └─ fluconazole, itraconazole, voriconazole
├─ Polyenes
│  └─ amphotericin B, nystatin
└─ Echinocandins
   └─ caspofungin, micafungin, anidulafungin

VIRAL INFECTIONS
├─ Antiretrovirals (HIV)
│  └─ zidovudine, ritonavir, dolutegravir
├─ Antiherpes
│  └─ acyclovir, valacyclovir, famciclovir
└─ Antiinfluenza
   └─ oseltamivir (Tamiflu), zanamivir

PARASITIC INFECTIONS
├─ Antimalarials
│  └─ chloroquine, artemether
└─ Antihelmintics
   └─ albendazole, mebendazole
```

**Search Examples:**
- `penicillin` → All penicillin-class drugs
- `fluoroquinolone` → All fluoroquinolone antibiotics
- `antifungal` → All antifungal drugs
- `antibiotic` → All antibiotics

---

## COMPLETE WORKFLOW EXAMPLES

### WORKFLOW 1: Analyze BRCA1 Breast Cancer Risk

```
STEP 1: Gene Variant Analysis
┌─────────────────────────────────────────────────┐
│ Input: 17:43044295:G:A                          │
│ Expected Output:                                │
│  - gene_symbol: BRCA1                           │
│  - impact_level: HIGH                           │
│  - consequence: frameshift_variant              │
│  - clinical_significance: Pathogenic            │
│  - associated_diseases: [Breast cancer,         │
│                          Ovarian cancer]        │
└─────────────────────────────────────────────────┘

STEP 2: Disease Association
┌─────────────────────────────────────────────────┐
│ Input: 17:43044295:G:A                          │
│ Expected Output:                                │
│  - rs_id: rs80357154                            │
│  - trait: Breast cancer, ovarian cancer         │
│  - p-value: 1.5e-50 (extremely significant)     │
│  - pubmed articles with evidence                │
└─────────────────────────────────────────────────┘

STEP 3: Drug Discovery - Treatment Options
┌─────────────────────────────────────────────────┐
│ Search 1: "PARP inhibitor"                      │
│  → olaparib, rucaparib, niraparib               │
│  → Specifically for BRCA1/2 mutations           │
│  Expected: max_phase = 4 (approved)             │
│                                                 │
│ Search 2: "chemotherapy breast cancer"          │
│  → paclitaxel, doxorubicin, carboplatin        │
│  Expected: max_phase = 3-4                      │
│                                                 │
│ Search 3: "HER2 inhibitor"                      │
│  → trastuzumab, pertuzumab, lapatinib           │
│  Expected: Used in HER2+ breast cancers         │
│                                                 │
│ Search 4: "immunotherapy breast"                │
│  → pembrolizumab, atezolizumab                  │
│  → Use: Triple-negative breast cancer           │
└─────────────────────────────────────────────────┘

INTERPRETATION:
✅ Patient has pathogenic BRCA1 mutation
✅ High cancer risk (supported by p < 1e-50)
✅ PARP inhibitors are targeted therapy option
✅ Multiple treatment modalities available
✅ Genetic counseling & surveillance recommended
```

---

### WORKFLOW 2: Lung Cancer EGFR Mutation Diagnosis

```
STEP 1: Gene Variant Analysis
┌─────────────────────────────────────────────────┐
│ Input: 7:55249071:T:G (EGFR exon 19 deletion)  │
│ Expected Output:                                │
│  - gene_symbol: EGFR                            │
│  - impact_level: HIGH                           │
│  - consequence: inframe_deletion                │
│  - amino_acid_change: Shows deletion region     │
│  - associated_diseases: [Lung cancer (NSCLC)]   │
└─────────────────────────────────────────────────┘

STEP 2: Disease Association
┌─────────────────────────────────────────────────┐
│ Input: 7:55249071:T:G                           │
│ Expected Output:                                │
│  - trait: Lung adenocarcinoma (NSCLC)           │
│  - p-value: 1.2e-35 (very significant)          │
│  - Note: Most common EGFR-activating mutation   │
└─────────────────────────────────────────────────┘

STEP 3: Drug Discovery - Targeted Therapy
┌─────────────────────────────────────────────────┐
│ Search: "EGFR inhibitor"                        │
│                                                 │
│ Results (APPROVED, max_phase = 4):              │
│ 1. erlotinib (Tarceva)                          │
│    └─ Specifically indicated for EGFR del19     │
│ 2. gefitinib (Iressa)                           │
│    └─ First-generation EGFR inhibitor           │
│ 3. afatinib (Gilotrif)                          │
│    └─ Irreversible EGFR inhibitor               │
│ 4. osimertinib (Tagrisso)                       │
│    └─ Third-generation, treats T790M resistance │
│                                                 │
│ Additional search: "PD-L1 inhibitor"            │
│ → For PD-L1+ tumors: pembrolizumab, atezolizumab
└─────────────────────────────────────────────────┘

INTERPRETATION:
✅ EGFR exon 19 deletion = strong driver mutation
✅ Highly responsive to EGFR inhibitors
✅ erlotinib is first-line recommended therapy
✅ Will eventually develop T790M resistance
✅ Osimertinib for resistant disease
```

---

### WORKFLOW 3: Familial Hypercholesterolemia

```
STEP 1: Gene Variant Analysis
┌─────────────────────────────────────────────────┐
│ Input: 1:55505647:G:A (LDLR)                   │
│ Expected Output:                                │
│  - gene_symbol: LDLR                            │
│  - consequence: missense_variant or stop_gained │
│  - clinical_significance: Pathogenic            │
│  - amino_acid_change: Shows LDL receptor change │
└─────────────────────────────────────────────────┘

STEP 2: Disease Association
┌─────────────────────────────────────────────────┐
│ Input: 1:55505647:G:A                           │
│ Expected Output:                                │
│  - trait: LDL cholesterol levels                │
│  - p-value: < 1e-50                             │
│  - reported_trait: Familial Hypercholesteremia  │
│  - Association: Heart disease, MI risk          │
└─────────────────────────────────────────────────┘

STEP 3: Drug Discovery - Management
┌─────────────────────────────────────────────────┐
│ Search 1: "statin"                              │
│  → atorvastatin, rosuvastatin, simvastatin     │
│  → First-line: Lower cholesterol                │
│  Expected: max_phase = 4 (approved)             │
│                                                 │
│ Search 2: "PCSK9 inhibitor"                     │
│  → evolocumab (Repatha), alirocumab (Praluent) │
│  → Use: Statin-resistant cases                  │
│  Expected: max_phase = 4                        │
│                                                 │
│ Search 3: "ezetimibe"                           │
│  → Blocks cholesterol absorption                │
│  → Adjunct to statins                           │
│  Expected: max_phase = 4                        │
└─────────────────────────────────────────────────┘

CLINICAL MANAGEMENT:
✅ LDLR mutation causes FH (elevated cholesterol)
✅ Increased cardiovascular risk
✅ Start with statins (first-line)
✅ Add PCSK9 inhibitors if inadequate response
✅ Lifestyle modification (diet, exercise)
✅ Consider apheresis for severe cases
```

---

## CLINICAL CASE STUDIES

### CASE 1: 45-Year-Old Woman with Family History of Breast Cancer

**Clinical Presentation:**
- Multiple relatives with breast cancer
- Age of onset: Early 40s in mother
- Seeking genetic testing

**GenVarX Analysis:**

```
STEP 1: Screen Common BRCA Variants
Variants to test:
├─ 17:43044295:G:A (BRCA1 c.68_69)
├─ 13:32316462:G:A (BRCA2 c.9097)
├─ 17:7673802:C:T (TP53 c.818)
└─ 10:89717702:G:A (PTEN c.677)

RESULT: 17:43044295:G:A found
└─ Gene: BRCA1
├─ Impact: HIGH
├─ Clinical Significance: Pathogenic
├─ Risk: 70% breast cancer by age 80
└─ Risk: 40% ovarian cancer by age 80

STEP 2: Disease Confirmation
Query: 17:43044295:G:A
Result: p-value < 1e-50 for breast cancer
Confirmation: Documented in 500+ publications

STEP 3: Treatment Planning (if cancer develops)
Drug Search: "PARP inhibitor"
Results:
├─ olaparib (LYNPARZA) - max_phase 4
├─ rucaparib (RUBRACA) - max_phase 4
└─ niraparib (ZEJULA) - max_phase 4

RECOMMENDATIONS:
1. Genetic counseling (confirmed BRCA1 mutation)
2. Increased surveillance (MRI screening)
3. Consider prophylactic mastectomy/oophorectomy
4. PARP inhibitors if cancer develops
5. Counsel family members (autosomal dominant)
```

---

### CASE 2: 62-Year-Old Man with Lung Cancer

**Clinical Presentation:**
- Never smoker
- Adenocarcinoma histology
- Seeking targeted therapy

**GenVarX Analysis:**

```
STEP 1: Check Common Lung Cancer Drivers
Variants to test:
├─ 7:55249071:T:G (EGFR exon 19 del)
├─ 7:55249071:T:G (EGFR L858R)
├─ 12:25398284:C:A (KRAS G12C)
└─ 2:LOCAL (ALK fusion)

RESULT: 7:55249071:T:G found (EGFR del19)
└─ Gene: EGFR
├─ Impact: HIGH
├─ Consequence: in-frame deletion
├─ Prediction: SIFT=Deleterious, PolyPhen=Damaging
└─ Associated: Lung adenocarcinoma

STEP 2: Drug Discovery
Query 1: "EGFR inhibitor"
Results (max_phase = 4):
├─ erlotinib (first-line choice)
├─ gefitinib
├─ afatinib
└─ osimertinib (for resistance)

Query 2: "immunotherapy"
Results:
├─ pembrolizumab (if PD-L1 positive)
└─ atezolizumab (alternative)

TREATMENT PLAN:
1. Start erlotinib (targeted therapy for EGFR del19)
2. Monitor for T790M resistance (usually 9-12 months)
3. Switch to osimertinib at progression
4. Consider immunotherapy at later stages
5. Median OS with treatment: 2-3 years
```

---

### CASE 3: 35-Year-Old with Familial Elevated Cholesterol

**Clinical Presentation:**
- Total cholesterol: 450 mg/dL (normal < 200)
- Father had MI at age 50
- On statin therapy with inadequate response

**GenVarX Analysis:**

```
STEP 1: Genetic Testing
Query: 1:55505647:G:A (LDLR)
Result:
├─ Gene: LDLR (LDL Receptor)
├─ Impact: MODERATE
├─ Clinical: Pathogenic (familial hypercholesterolemia)
└─ LDL target: Reduce to < 100 mg/dL (very difficult)

STEP 2: Confirm Diagnosis
Query: Disease Association for LDLR variant
Result:
├─ Associated: Familial hypercholesterolemia
├─ p-value: 1.2e-80 (extremely significant)
├─ Cardiovascular risk: 10x baseline
└─ Recommendations: Aggressive treatment

STEP 3: Escalated Drug Therapy
Query 1: "statin" (check adherence first)
├─ atorvastatin 80 mg (high-dose)
└─ Already tried, insufficient response

Query 2: "PCSK9 inhibitor" (next step)
Results:
├─ evolocumab (REPATHA) - Injectable weekly
├─ alirocumab (PRALUENT) - Injectable every 2 weeks
└─ Both: max_phase = 4 (approved)
└─ Effect: 50-60% additional LDL reduction

Query 3: "ezetimibe"
├─ Non-statin cholesterol absorption blocker
└─ Use: Combined with statin + PCSK9

TREATMENT ESCALATION:
1. Statin + ezetimibe + PCSK9 inhibitor
2. Check adherence, diet, exercise
3. If still inadequate: Consider apheresis
4. Target LDL: < 70 mg/dL (aggressive)
5. Cardiovascular prevention critical
```

---

## Research Query Collections

### Collection 1: Cancer Genomics Research
**Goal:** Comprehensive cancer mutation database

```
HIGH-CONFIDENCE DRIVER MUTATIONS:

Breast Cancer:
├─ 17:43044295:G:A (BRCA1)
├─ 13:32316462:G:A (BRCA2)
└─ 17:7673802:C:T (TP53)

Lung Cancer:
├─ 7:55249071:T:G (EGFR)
├─ 2:25245350:G:C (ALK)
└─ 12:25398284:C:A (KRAS)

Colorectal Cancer:
├─ 12:25398284:C:A (KRAS)
├─ 5:112839461:T:A (APC)
└─ 17:7673802:C:T (TP53)

Melanoma:
├─ 7:140753336:A:T (BRAF V600E)
└─ 11:534242:C:T (NRAS Q61R)

Pancreatic Cancer:
├─ 12:25398284:C:A (KRAS)
├─ 17:7673802:C:T (TP53)
└─ 9:21971153:C:T (CDKN2A)

GWAS Validation:
Query each variant for disease associations
Expected: All should show p < 1e-20
```

---

### Collection 2: Pharmacogenomics Drug Response
**Goal:** Identify drug response variants

```
EGFR Mutations → EGFR Inhibitors
├─ erlotinib response: 55249071:T:G
├─ resistance mutation: 7:55324723:C:T (T790M)

HER2 Mutations → Trastuzumab
├─ HER2 amplification: 17:37844394:A:G
├─ Response: Trastuzumab sensitivity

BRAF V600E → Vemurafenib
├─ 7:140753336:A:T
├─ Response: 60-80% response rate

KRAS G12C → KRAS G12C Inhibitor (sotorasib)
├─ 12:25398284:C:A
├─ Response: 30-40% response rate
└─ Emerging therapy
```

---

### Collection 3: Cardiovascular Risk Variants
**Goal:** Comprehensive CV risk assessment

```
LIPID METABOLISM:
├─ LDLR: 1:55505647:G:A (LDL cholesterol)
├─ APOB: 2:21001761:G:A (LDL particle size)
└─ PCSK9: 1:55502371:G:A (PCSK9 protein)

THROMBOSIS RISK:
├─ Factor V Leiden: 1:169549811:G:A
├─ Prothrombin G20210A: 11:46406620:A:G
└─ MTHFR: 1:11959590:C:T (homocysteine)

HYPERTENSION:
├─ ACE: 17:61573377:I→D (insertion/deletion)
└─ AGT: 1:230710048:A:G (angiotensinogen)

INFLAMMATION:
├─ CRP: 1:159714310:C:T (C-reactive protein)
└─ IL-6: 7:22766308:G:C (interleukin-6)
```

---

## Quick Reference Table

| Use Case | Input Module | Drug Search | Expected Result |
|----------|--------------|------------|-----------------|
| High-risk cancer predisposition | Gene Variant (17:43044295:G:A) | "PARP inhibitor" | max_phase=4, pathogenic |
| Actionable somatic mutation | Gene Variant (7:55249071:T:G) | "EGFR inhibitor" | max_phase=4, HIGH impact |
| Drug response prediction | Gene Variant + Drug class | "EGFR inhibitor" for EGFR mut | qed_weighted > 0.7 |
| Familial disease confirmation | Disease Association (1:55505647:G:A) | "statin" or "PCSK9" | p < 1e-50 |
| Treatment options | Any variant + cancer type | Cancer-specific drug class | Multiple max_phase=4 options |

---

**Version History:**
- v1.0 - Complete preset and example sets (August 2026)

