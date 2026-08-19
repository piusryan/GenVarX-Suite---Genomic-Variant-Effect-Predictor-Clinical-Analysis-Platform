# GenVarX Field Reference Guide
## Complete Explanation of All Input & Output Fields

**Last Updated:** August 2026  
**Version:** 1.0

---

## Table of Contents

1. [Gene Variant Module - Input Fields](#gene-variant-module---input-fields)
2. [Gene Variant Module - Output Fields](#gene-variant-module---output-fields)
3. [Drug Discovery Module - Input Fields](#drug-discovery-module---input-fields)
4. [Drug Discovery Module - Output Fields](#drug-discovery-module---output-fields)
5. [Disease Association Module - Input Fields](#disease-association-module---input-fields)
6. [Disease Association Module - Output Fields](#disease-association-module---output-fields)
7. [Example Query Sets](#example-query-sets)
8. [Interpretation Guide](#interpretation-guide)

---

## GENE VARIANT MODULE - INPUT FIELDS

### Format
```
chromosome:position:reference_base:alternate_base
```

### Field Definitions

#### **Chromosome (chr)**
- **Definition:** Human chromosome number (1-22 for autosomes, X or Y for sex chromosomes)
- **Type:** Integer or letter
- **Examples:**
  - `17` - Autosome 17 (where BRCA1 is located)
  - `13` - Autosome 13 (where BRCA2 is located)
  - `X` - X chromosome
  - `Y` - Y chromosome
- **Valid Range:** 1-22, X, Y (case-insensitive)

#### **Position (pos)**
- **Definition:** Genomic coordinate on GRCh38 (human reference genome build 38)
- **Type:** Integer
- **Units:** Base pairs from chromosome start
- **Examples:**
  - `43044295` - BRCA1 mutation site
  - `32316462` - BRCA2 mutation site
- **Reference:** These are absolute positions on GRCh38, NOT relative to genes

**⚠️ Important:** Different genome builds use different positions:
- **GRCh37:** Older build (hg19) - most online databases use GRCh38 now
- **GRCh38:** Current standard (hg38) - USE THIS

#### **Reference Base (ref)**
- **Definition:** The normal/wild-type DNA base at this position in the reference genome
- **Type:** Single letter
- **Valid Values:** `A`, `T`, `G`, `C` (DNA bases)
- **Cannot Be:** `N` (unknown base)
- **Examples:**
  - `G` - Reference genome has Guanine
  - `A` - Reference genome has Adenine
- **Function:** Used to validate you're looking at the right variant

#### **Alternate Base (alt)**
- **Definition:** The mutant/variant DNA base found in the patient
- **Type:** Single letter (most common) or multiple letters (indels)
- **Valid Values:** `A`, `T`, `G`, `C` (single nucleotide variants)
- **Indels:** Can be multi-character (e.g., `ATG` for insertion)
- **Examples:**
  - `A` - Patient has Adenine instead of reference
  - `DEL` - Deletion (whole gene deleted)
  - `ATG` - Insertion of ATG sequence

### Complete Input Example

```
17:43044295:G:A
│  │        │ └─ Alternate base (mutation)
│  │        └──── Reference base (normal)
│  └──────────── Position
└────────────── Chromosome
```

**Meaning:** On chromosome 17, at position 43044295, the reference is G but this patient has A (a G→A substitution at BRCA1 c.68_69delAG location).

---

## GENE VARIANT MODULE - OUTPUT FIELDS

### 1. **variant**
- **Type:** String
- **Example:** `17:43044295:G:A`
- **Meaning:** Echo of your input (confirmation of what was analyzed)
- **Use:** Verify the correct variant was analyzed

### 2. **rs_id** (dbSNP ID)
- **Type:** String or null
- **Format:** `rs` followed by numbers (e.g., `rs80357154`)
- **Examples:**
  - `rs80357154` - BRCA1 mutation, well-documented
  - `null` - Novel/undocumented variant (not in dbSNP database)
- **Meaning:** Unique identifier in the NCBI dbSNP database
- **Use:** Cross-reference with literature, other databases
- **Reference:** https://www.ncbi.nlm.nih.gov/snp/

### 3. **gene_symbol** (Gene Name)
- **Type:** String
- **Examples:**
  - `BRCA1` - Breast Cancer Type 1 Susceptibility Protein
  - `EGFR` - Epidermal Growth Factor Receptor
  - `TP53` - Tumor Protein P53
- **Meaning:** Official HGNC (Human Gene Nomenclature Committee) gene name
- **Use:** 
  - Identify which gene is affected
  - Literature search (all papers use HGNC names)
  - Functional databases (GenCards, UniProt)
- **Reference:** https://www.genenames.org/

### 4. **consequence** (Variant Type)
- **Type:** String
- **Common Values:**
  | Consequence | Severity | Meaning |
  |-------------|----------|---------|
  | `stop_gained` | HIGHEST | Premature STOP codon → truncated protein |
  | `frameshift_variant` | HIGHEST | Insertion/deletion disrupts reading frame |
  | `splice_acceptor_variant` | HIGH | Damages splicing signal → exon skipped |
  | `splice_donor_variant` | HIGH | Damages splicing signal → exon skipped |
  | `start_lost` | HIGH | ATG start codon mutated → no protein |
  | `missense_variant` | MODERATE | Amino acid change → altered function |
  | `inframe_deletion` | MODERATE | Deletion, maintains reading frame |
  | `inframe_insertion` | MODERATE | Insertion, maintains reading frame |
  | `synonymous_variant` | LOW | Same amino acid (silent mutation) |
  | `intron_variant` | LOW | In non-coding intron region |
  | `intergenic_variant` | LOW | Between genes, no effect |

- **Meaning:** What type of change the variant causes
- **Use:** Quick severity assessment

### 5. **impact_level** (Severity Classification)
- **Type:** String
- **Values:** `HIGH`, `MODERATE`, `LOW`
- **Definition:**
  - **HIGH:** Likely to disable protein function (premature stop, frameshift)
  - **MODERATE:** May affect protein function (missense, inframe indel)
  - **LOW:** Probably tolerated (synonymous, intronic, intergenic)
- **Example:**
  - `HIGH` for BRCA1 frameshift → loss of tumor suppression
  - `MODERATE` for missense → depends on position/amino acid
  - `LOW` for silent mutation → no amino acid change
- **Use:** Primary severity metric

### 6. **sift_prediction** (Conservation Prediction)
- **Type:** String
- **Values:**
  - `Deleterious` - Likely harmful (mutate evolutionarily conserved residue)
  - `Tolerated` - Likely benign (variable position in evolution)
  - `N/A` - Unable to predict (insufficient data)
- **Scale:** Scores 0-1 (0 = deleterious, 1 = tolerated)
- **What it measures:**
  - How conserved this amino acid position is across species
  - If a residue is conserved, changing it is likely harmful
  - If variable across evolution, changing it is likely tolerated
- **Example:**
  - `Deleterious` for BRCA1 mutation → critical region
  - `Tolerated` for position 1000 in 1200-AA protein → variable region
- **Reference:** SIFT algorithm (Ng & Henikoff, 2003)

### 7. **polyphen_prediction** (Structure Impact)
- **Type:** String
- **Values:**
  - `Probably Damaging` - Likely to harm protein structure/function
  - `Possibly Damaging` - May harm protein structure/function
  - `Benign` - Likely to not affect function
  - `N/A` - Unable to predict
- **Scale:** Scores 0-1 (0 = benign, 1 = damaging)
- **What it measures:**
  - Physical protein structure changes
  - Conservation at mutation site
  - Biochemical similarity of amino acids
- **Example:**
  - `Probably Damaging` for D→V (acidic→hydrophobic) in active site
  - `Benign` for A→V (both hydrophobic) on surface
- **Reference:** PolyPhen-2 algorithm (Adzhubei et al., 2010)

### 8. **amino_acid_change** (Protein Substitution)
- **Type:** String
- **Formats:**
  - Single letter: `D/V` (reference/alternate)
  - Three letter: `Asp/Val`
  - With position: `D123V`
- **Meaning:** What amino acid is changed to what
- **Examples:**
  - `D/V` - Aspartate (negatively charged) → Valine (hydrophobic)
  - `G/R` - Glycine (small) → Arginine (large, charged)
  - `N/A` - Silent mutation (no amino acid change)
- **Use:**
  - Biochemical assessment
  - Literature searching
  - Pathway analysis

**Amino Acid Properties:**
| Type | Examples | Property |
|------|----------|----------|
| Hydrophobic | A, V, I, L, M, F, W, P | Water-repelling, often buried |
| Polar | S, T, C, Y, N, Q | Water-attracting, often on surface |
| Positive | K, R, H | Positively charged |
| Negative | D, E | Negatively charged |
| Special | G, P | Flexible, rigid |

### 9. **clinical_significance** (ClinVar Classification)
- **Type:** String
- **Values:**
  | Value | Meaning | Risk |
  |-------|---------|------|
  | `Pathogenic` | Causes disease | DISEASE |
  | `Likely Pathogenic` | Probably causes disease | HIGH RISK |
  | `Uncertain Significance` | Unknown effect | UNKNOWN |
  | `Likely Benign` | Probably harmless | LOW RISK |
  | `Benign` | Not disease-causing | SAFE |
  | `Not Found in ClinVar` | Not in clinical database | UNVERIFIED |

- **Source:** ClinVar database (https://www.ncbi.nlm.nih.gov/clinvar/)
- **Based On:**
  - Published literature
  - Lab submissions
  - Consensus of experts
- **Examples:**
  - `Pathogenic` for BRCA1 frameshift → 100+ papers, cancer predisposition
  - `Uncertain Significance` for novel missense → no clinical data yet
  - `Benign` for silent mutation in intron
- **Use:** Clinical interpretation

### 10. **associated_diseases** (Phenotypes)
- **Type:** Array of strings
- **Examples:**
  ```json
  [
    "Hereditary Breast and Ovarian Cancer Syndrome",
    "Fanconi Anemia",
    "Pancreatic Cancer Predisposition"
  ]
  ```
- **Meaning:** Known diseases associated with this variant
- **Source:** ClinVar, OMIM, literature
- **Use:**
  - Understand disease risk
  - Genetic counseling
  - Family planning
  - Clinical management

---

## DRUG DISCOVERY MODULE - INPUT FIELDS

### 1. **Drug Name**
- **Type:** String (case-insensitive)
- **Examples:**
  - `selinexor` - Will match "Selinexor", "SELINEXOR", "selinexor"
  - `tamoxifen` - Estrogen receptor antagonist
  - `paclitaxel` - Tubulin stabilizer
- **Behavior:** Fuzzy matching (partial matches work)
- **Try:** Brand names, generic names, abbreviations

### 2. **ChEMBL ID**
- **Type:** String, format `CHEMBL` + number
- **Examples:**
  - `CHEMBL237500` - Selinexor (KPT-330)
  - `CHEMBL1201579` - Trastuzumab (Herceptin)
  - `CHEMBL60` - Tamoxifen
- **Source:** ChEMBL database unique identifier
- **Lookup:** Find IDs at https://www.ebi.ac.uk/chembl/

### 3. **Drug Class or Target**
- **Type:** String (descriptive)
- **Examples:**
  - `EGFR inhibitor` - Targets EGFR protein
  - `kinase inhibitor` - Targets protein kinases
  - `checkpoint inhibitor` - Targets immune checkpoints
  - `statin` - Cholesterol-lowering drugs
  - `antibiotic` - Infection-fighting drugs
- **Behavior:** Searches drug name AND description fields
- **Returns:** All drugs matching that category

---

## DRUG DISCOVERY MODULE - OUTPUT FIELDS

### 1. **chembl_id**
- **Type:** String
- **Format:** `CHEMBL` followed by numbers
- **Example:** `CHEMBL237500`
- **Use:** Unique identifier for cross-referencing
- **Reference:** https://www.ebi.ac.uk/chembl/

### 2. **name**
- **Type:** String
- **Example:** `Selinexor`
- **Includes:** 
  - Generic drug names
  - Brand names (if available)
- **Use:** Literature search, prescription lookup

### 3. **compound_type**
- **Type:** String
- **Common Values:**
  - `Small molecule` - Traditional drug (<500 Da)
  - `Protein` - Recombinant protein
  - `Antibody` - Monoclonal antibody
  - `Peptide` - Short amino acid chain
  - `Polymer` - Large molecule
  - `Unspecified` - Unknown structure type
- **Example:** `Small molecule` for selinexor
- **Use:** Understand drug chemistry

### 4. **max_phase** (Highest Development Stage)
- **Type:** String or Integer
- **Values:**
  | Phase | Status | Meaning |
  |-------|--------|---------|
  | `0` | Discovery | In laboratory research |
  | `1` | Phase 1 Trial | Safety/dosage in 20-100 people |
  | `2` | Phase 2 Trial | Efficacy in 100-300 people |
  | `3` | Phase 3 Trial | Efficacy in 1000+ people |
  | `4` | FDA Approved | On the market |
  | `-1` | Discontinued | Development stopped |

- **Examples:**
  - `4` - Approved, can prescribe
  - `3` - Late stage trials, likely approval soon
  - `1` - Early trials, uncertain future
- **Use:** Assess drug maturity
- **Note:** Check FDA.gov for actual US approval status

### 5. **molecular_weight**
- **Type:** Float (Daltons)
- **Units:** g/mol (or Da)
- **Examples:**
  - `428.45` - Selinexor (normal small molecule)
  - `<150` - Very small, penetrates well
  - `>500` - Large, may have absorption issues
- **Lipinski's Rule:** Ideal MW < 500 Da
- **Use:** Assess drug-likeness

### 6. **alogp** (Lipophilicity)
- **Type:** Float
- **Full Name:** Octanol-Water Partition Coefficient (Log P)
- **Range:** Typically -5 to +5
- **Ideal Range:** 0 to 3 (hydrophobic enough to cross membranes, hydrophilic enough to dissolve)
- **Meaning:**
  - Low AlogP (< 0): Very hydrophilic (water-loving)
    - Pro: Dissolves well in blood, kidney clearance easy
    - Con: Hard to cross cell membranes
  - High AlogP (> 3): Very lipophilic (fat-loving)
    - Pro: Easy to cross cell membranes
    - Con: Poor solubility, hard to clear from body, tissue accumulation
- **Examples:**
  - `2.5` - Selinexor (ideal balance)
  - `-0.5` - Hydrophilic drug (e.g., antibiotic)
  - `4.5` - Lipophilic drug (potential toxicity issues)
- **Use:** Predict absorption, distribution, toxicity

### 7. **qed_weighted** (Quantitative Estimate of Drug-likeness)
- **Type:** Float
- **Range:** 0 to 1
- **Meaning:** Overall "drug-likeness" score
- **Calculation:** Combines MW, AlogP, HBA, HBD, rotatable bonds
- **Interpretation:**
  - `0.8-1.0` - Excellent (likely approvable)
  - `0.6-0.8` - Good (probably okay)
  - `0.4-0.6` - Marginal (potential issues)
  - `<0.4` - Poor (likely problems)
- **Example:**
  - `0.8` - Selinexor (well-designed drug)
  - `0.2` - Bad drug-likeness (poor candidates)
- **Reference:** Bickerton et al., 2012
- **Use:** Quick quality check

### 8. **targets** (Number of Protein Targets)
- **Type:** Integer
- **Examples:**
  - `1` - Highly specific (targets only EGFR)
  - `25` - Selinexor (targets XPO1, hits other kinases)
  - `100+` - Promiscuous/poorly selective
- **Meaning:** How many proteins the drug interacts with
- **Implications:**
  - Few targets: Specific, fewer side effects
  - Many targets: Off-target effects, side effects
- **Use:** Selectivity assessment

### 9. **bioactivities** (Known Activity Records)
- **Type:** Integer
- **Examples:**
  - `150` - Selinexor (many published binding/inhibition studies)
  - `5` - Unknown drug (little research)
  - `1000+` - Well-studied drug (e.g., aspirin)
- **Meaning:** Number of biological activity measurements published
- **Use:** How well-characterized is this drug?

### 10. **synonyms** (Alternative Names)
- **Type:** String
- **Examples:**
  - `KPT-330, Karyopharm, XPO1 inhibitor` - Selinexor
  - `Herceptin, trastuzumab humanized` - Trastuzumab
- **Separated by:** Commas or semicolons
- **Use:** Find drug under different names

### 11. **polar_surface_area** (PSA)
- **Type:** Float
- **Units:** Ų (square Angstroms)
- **Meaning:** Surface area of polar atoms (O, N)
- **Ideal Range:** 20-130 Ų
- **Implications:**
  - Low PSA (<20): Lipophilic, poor water solubility
  - High PSA (>130): Hydrophilic, poor cell penetration
  - Mid-range (20-130): Good balance
- **Example:** `68.0` for selinexor (ideal)
- **Use:** Predict blood-brain barrier penetration

### 12. **hba** (Hydrogen Bond Acceptors)
- **Type:** Integer
- **Meaning:** Number of atoms that can accept H-bonds (N, O)
- **Lipinski's Rule:** HBA ≤ 10 (max 10)
- **Typical Range:** 1-8
- **Example:** `9` for selinexor
- **Use:** Predict binding interactions

### 13. **hbd** (Hydrogen Bond Donors)
- **Type:** Integer
- **Meaning:** Number of atoms that can donate H-bonds (N-H, O-H)
- **Lipinski's Rule:** HBD ≤ 5 (max 5)
- **Typical Range:** 0-4
- **Example:** `2` for selinexor
- **Use:** Predict binding interactions

### 14. **ro5_violations** (Lipinski Rule of 5 Violations)
- **Type:** Integer
- **Lipinski's Rule:** For oral absorption, drug should have:
  - MW < 500 Da
  - AlogP < 5
  - HBA ≤ 10
  - HBD ≤ 5
- **Violations:**
  - `0` - Passes all rules (good)
  - `1-2` - Marginal (acceptable, may have issues)
  - `>2` - Poor (likely problems)
- **Example:** `0` for selinexor (passes all)
- **Reference:** Lipinski et al., 1997
- **Use:** Predict oral bioavailability

### 15. **rotatable_bonds** (Number of Rotatable Bonds)
- **Type:** Integer
- **Meaning:** Bonds that can freely rotate (not aromatic, not in rings)
- **Ideal Range:** 0-10
- **Implications:**
  - Low count (<5): Rigid, less flexible
  - High count (>15): Flexible, entropy loss upon binding
  - Ideal (5-10): Balance of rigidity and flexibility
- **Example:** `8` for selinexor (ideal)
- **Use:** Predict binding efficiency

### 16. **passes_ro3** (Rule of 3 for Fragments)
- **Type:** String
- **Values:** `Yes`, `No`, `N/A`
- **Rule of 3:** For fragment-based drug discovery, should have:
  - MW < 300 Da
  - AlogP < 3
  - HBA ≤ 3
  - HBD ≤ 3
  - Rotatable bonds ≤ 3
- **Example:** `Yes` for fragments
- **Use:** Fragment library selection

### 17. **aromatic_rings**
- **Type:** Integer
- **Typical Range:** 0-4
- **Example:** `3` for selinexor
- **Meaning:** Number of aromatic ring systems
- **Too many rings:** Reduced solubility, hydrophobic

### 18. **inorganic_flag**
- **Type:** String
- **Values:** `Yes`, `No`, `N/A`
- **Example:** `No` for selinexor (organic molecule)
- **Meaning:** Is this an inorganic compound?

### 19. **heavy_atoms**
- **Type:** Integer
- **Example:** `28` for selinexor
- **Meaning:** Total number of heavy atoms (not H)
- **Correlation:** Higher = larger, more complex molecule

### 20. **np_likeness_score** (Natural Product-likeness)
- **Type:** Float
- **Range:** -5 to +5
- **Meaning:** How similar to natural products
- **High score (+5):** Natural product-like
- **Low score (-5):** Synthetic, unnatural
- **Use:** Predict metabolic stability, toxicity

### 21. **molecular_formula**
- **Type:** String
- **Example:** `C23H25N3O5` for selinexor
- **Meaning:** Chemical composition
- **Use:** Calculate molar mass, verify compound

### 22. **smiles** (SMILES Notation)
- **Type:** String
- **Example:** `CC(C)c1ccc...` (selinexor SMILES)
- **Meaning:** Simplified Molecular Input Line Entry System
- **Use:** Visualization, cheminformatics tools
- **Reference:** https://www.daylight.com/smiles/

### 23. **inchi_key** (InChI Key)
- **Type:** String
- **Example:** `ULVAGXBQMUHXTQ-PXHHCJKDSA-N`
- **Meaning:** International Chemical Identifier (hashed)
- **Use:** Unique identifier across databases

### 24. **inchi** (Full InChI)
- **Type:** String (very long)
- **Meaning:** Complete chemical structure representation
- **Use:** Structure verification

### 25. **withdrawn_flag**
- **Type:** String
- **Values:** `Yes`, `No`, `N/A`
- **Example:** `No` (drug not withdrawn)
- **Meaning:** Has this drug been withdrawn from market?
- **Use:** Identify safety issues

### 26. **orphan**
- **Type:** String
- **Values:** `Yes`, `No`, `N/A`
- **Example:** `Yes` for some cancer drugs
- **Meaning:** Orphan drug designation (rare disease)
- **Use:** Identify niche medicines

---

## DISEASE ASSOCIATION MODULE - INPUT FIELDS

### Input Format
Same as Gene Variant:
```
chromosome:position:reference:alternate
```

### Fields Explained
(See Gene Variant Input Fields section above)

---

## DISEASE ASSOCIATION MODULE - OUTPUT FIELDS

### 1. **rs_id** (dbSNP ID)
- **Type:** String or null
- **Format:** `rs` + numbers
- **Example:** `rs80357154`
- **Use:** Links variant to GWAS studies
- **Note:** Must be in GWAS Catalog database

### 2. **associations** (Array of GWAS Hits)
- **Type:** Array of objects
- **Each object contains:**
  - `trait`
  - `pvalue`
  - `reported_trait`
  - `study_accession`
  - `pubmed_id`
  - `strongest_allele`

### 3. **trait** (Associated Disease/Trait)
- **Type:** String
- **Examples:**
  - `Breast cancer, ovarian cancer, prostate cancer`
  - `Type 2 diabetes mellitus`
  - `LDL cholesterol levels`
  - `Height`
- **Source:** EFO (Experimental Factor Ontology) terms
- **Meaning:** What disease/trait is associated with this variant
- **Can be:** Multiple traits (comma-separated)

### 4. **pvalue** (Statistical Significance)
- **Type:** Float (scientific notation)
- **Format:** `1.5e-50` (means 0.000...0015 with 50 zeros)
- **Range:** Typically 1e-10 to 1e-500
- **Interpretation:**
  - `< 1e-50` - Extremely significant (definitely associated)
  - `1e-50 to 1e-20` - Very significant (strong association)
  - `1e-20 to 1e-8` - Significant (genome-wide threshold is 5e-8)
  - `> 1e-8` - Not significant
- **Example:**
  - `1.5e-50` for BRCA1 → breast cancer (extremely strong)
  - `2.3e-8` for cholesterol SNP (just crosses genome-wide threshold)
- **Use:** Filter strong associations
- **Note:** Lower p-value = stronger association

### 5. **reported_trait** (Clinical Name)
- **Type:** String
- **Examples:**
  - `Hereditary Breast and Ovarian Cancer Syndrome`
  - `Type 2 Diabetes Mellitus`
  - `Coronary Artery Disease`
- **Meaning:** Human-readable disease name
- **vs. trait:** More formal clinical terminology
- **Use:** Medical/genetic counseling

### 6. **study_accession** (GWAS Catalog ID)
- **Type:** String
- **Format:** `GCST` + numbers
- **Example:** `GCST000001`
- **Use:** Look up original study
- **Reference:** https://www.ebi.ac.uk/gwas/

### 7. **pubmed_id** (Literature Reference)
- **Type:** String (numeric ID)
- **Example:** `12345678`
- **Use:** Find published paper
- **Reference:** https://pubmed.ncbi.nlm.nih.gov/
- **Lookup:** https://pubmed.ncbi.nlm.nih.gov/12345678

### 8. **strongest_allele** (Risk Allele)
- **Type:** String
- **Examples:**
  - `A` - The A allele at this position increases risk
  - `T` - The T allele increases risk
- **Meaning:**
  - If you have this allele = increased disease risk
  - If you don't have it = baseline risk
- **Important:** NOT the same as "ref" or "alt"
- **Example:**
  - Variant: `17:43044295:G:A`
  - Strongest allele: `A`
  - Interpretation: If you have A, higher cancer risk
- **Use:** Risk assessment

### 9. **note** (Additional Information)
- **Type:** String or null
- **Examples:**
  - `null` - No special notes
  - `"No GWAS Catalog associations found"` - Variant not in database
- **Use:** Additional context

---

## Example Query Sets

### SET 1: Breast Cancer Genetics
**Goal:** Comprehensive BRCA1 mutation analysis

```
1. Gene Variant Analysis
   Input: 17:43044295:G:A
   Focus on: impact_level, clinical_significance, associated_diseases
   
2. Disease Association
   Input: 17:43044295:G:A
   Look for: Cancer traits, p-values < 1e-20
   
3. Drug Discovery
   Queries:
   - "breast cancer"
   - "HER2 inhibitor"
   - "ER antagonist"
   - "chemotherapy"
```

### SET 2: Personalized Cancer Treatment
**Goal:** Find drugs for specific mutation

```
1. Analyze Mutation
   Input: 7:55249071:T:G (EGFR)
   
2. Find Associated Diseases
   Input: Same
   
3. Search Target Drugs
   Query: "EGFR inhibitor"
   Look for: max_phase = 4 (approved), high targets count
```

### SET 3: Cardiovascular Risk
**Goal:** Understand cholesterol risk and treatment

```
1. Cholesterol Variant
   Input: 1:55505647:G:A (LDLR)
   
2. Disease Associations
   Input: Same
   Look for: LDL levels, heart disease
   
3. Treatment Options
   Query: "statin" or "ACE inhibitor"
   Focus on: approved drugs, side effects, bioactivities
```

### SET 4: Rare Genetic Disease
**Goal:** Novel variant interpretation

```
1. Analyze Variant
   Input: Unknown variant coordinates
   Note: May have rs_id = null, clinical_significance = "Uncertain"
   
2. Check Literature
   Input: Check disease module for any associations
   
3. Research Drug Options
   Query: Disease name (if available)
   
4. Next Steps:
   - Consult genetics expert
   - Contact disease foundations
   - Send for laboratory validation
```

---

## Interpretation Guide

### Reading Severity Levels

#### Impact Level + Consequence Combo
```
HIGH IMPACT + stop_gained
  → Severe: Truncated protein, complete loss of function
  → Disease likely

HIGH IMPACT + frameshift_variant
  → Severe: Wrong reading frame, gibberish protein
  → Disease likely

MODERATE + missense_variant
  → Variable: Depends on SIFT/PolyPhen predictions
  → Check amino acid change

LOW + synonymous_variant
  → Usually benign: Same amino acid
  → But check for splicing effects
```

#### Prediction Algorithm Combination
```
SIFT: Deleterious + PolyPhen: Probably Damaging
  → Very likely harmful
  → Clinical significance often = Pathogenic

SIFT: Tolerated + PolyPhen: Benign
  → Very likely harmless
  → Clinical significance often = Benign

SIFT: Deleterious + PolyPhen: Benign
  → Conflicting predictions
  → Likely requires expert review
```

### Drug Development Stage Interpretation
```
Phase 4 (Approved)
  → Can prescribe today
  → FDA/regulatory approval complete

Phase 3 (Late Trials)
  → Likely approval in 1-2 years
  → Clinical efficacy proven

Phase 2 (Mid Trials)
  → Experimental, uncertain future
  → Works in animals, being tested in humans

Phase 1 (Early Trials)
  → Very experimental
  → Safety/dosage being determined

Phase 0 or Discontinued
  → Not available
  → Research only or failed
```

### GWAS P-value Interpretation
```
p < 5e-8 (Genome-Wide Significant)
  → Strong association, published
  → Likely causative or in LD with causal variant

p < 1e-20 (Very Strong)
  → Extremely confident association
  → Major effect size

p < 1e-50 (Extreme)
  → Landmark discovery level
  → Example: BRCA1 mutations and breast cancer
```

---

## Quick Reference Cheat Sheet

### When You See `N/A`
- **rs_id:** Not in dbSNP (novel variant)
- **clinical_significance:** Not in ClinVar (unknown)
- **sift_prediction:** Cannot calculate (gaps/alignment issues)
- **associated_diseases:** No known associations

### When You See `null`
- Field not available / no data
- For associations: No GWAS hits found

### Green Flags ✅
- `clinical_significance = Pathogenic`
- `impact_level = HIGH`
- `rs_id = rs...` (known variant)
- `max_phase = 4` (approved drug)
- `p-value < 1e-20` (strong association)

### Red Flags 🚩
- `clinical_significance = Pathogenic` (unverified)
- `impact_level = HIGH` + `SIFT: Deleterious` (likely harmful)
- `ro5_violations > 2` (poor drug candidate)
- `max_phase = 0-1` (very experimental)
- No associated diseases found (uncharacterized)

---

## Frequently Asked Questions

### Q: What if rs_id is null?
A: Novel or very rare variant. Not in public databases. May be family-specific or require functional validation.

### Q: Can one variant cause multiple diseases?
A: Yes! Gene products have multiple functions. BRCA1 mutations cause breast cancer, ovarian cancer, and prostate cancer.

### Q: What's the difference between "trait" and "reported_trait"?
A: `trait` = standardized term (EFO). `reported_trait` = how authors described it in publication.

### Q: Why do drug predictions conflict (SIFT vs PolyPhen)?
A: They use different algorithms. SIFT emphasizes conservation. PolyPhen emphasizes structure. Can get different answers.

### Q: What does "strongest_allele" mean?
A: If you carry this allele at this position, your risk is higher. Not necessarily the same as the "alt" allele in your variant!

### Q: How do I know if I should worry about my variant?
A: Look at: `clinical_significance`, `impact_level`, associated diseases. If unsure, see a genetic counselor.

### Q: Which drug should I take?
A: **This is NOT medical advice.** Talk to your doctor. Look at: approval status (max_phase), drug-likeness (QED), safety data (bioactivities).

---

## Resources & References

### Variant Interpretation
- ClinVar: https://www.ncbi.nlm.nih.gov/clinvar/
- OMIM: https://www.omim.org/
- VEP Documentation: https://useast.ensembl.org/Homo_sapiens/Tools/VEP

### Drug Information
- ChEMBL: https://www.ebi.ac.uk/chembl/
- DrugBank: https://go.drugbank.com/
- FDA Approvals: https://www.fda.gov/drugs

### Disease Association
- GWAS Catalog: https://www.ebi.ac.uk/gwas/
- dbSNP: https://www.ncbi.nlm.nih.gov/snp/

### Gene Information
- HGNC: https://www.genenames.org/
- UniProt: https://www.uniprot.org/
- GenCards: https://www.genecards.org/

### Learning Resources
- SIFT algorithm: https://sift.bii.a-star.edu.sg/
- PolyPhen-2: http://genetics.bwh.harvard.edu/pph2/
- Lipinski's Rule of 5: https://en.wikipedia.org/wiki/Lipinski%27s_rule_of_five

---

**Version History:**
- v1.0 - Initial comprehensive guide (August 2026)

**Report Issues:** GitHub Issues or contact support

