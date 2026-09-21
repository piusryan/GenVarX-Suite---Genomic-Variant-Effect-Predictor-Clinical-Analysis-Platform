# ⚠️ RSID vs Disease - The Key Difference

## The Confusion

You're getting "RSID not found" errors because you're trying to input **RSIDs** (like `rs1234567`) into the **Disease Search**, but it expects a **disease name** (like `"Breast Cancer"`).

These are **TWO DIFFERENT THINGS** and need **TWO DIFFERENT MODULES**.

---

## What is an RSID?

**RSID** = Reference SNP ID

An identifier for a specific genetic variant in the human genome.

### Examples of RSIDs:
```
rs1234567      ← One specific variant
rs61818430     ← Another specific variant
rs3218713      ← Yet another specific variant
```

### What an RSID represents:
```
rs1234567 might mean:
  - Chromosome: 17
  - Position: 43,044,295
  - Change: G→A (one person has G, another has A)
  - Gene: BRCA1
```

### What you use RSIDs for:
```
"What information do we have about variant rs1234567?"
  ↓
Input: rs1234567
Module: GENE VARIANT
Output: Clinical significance, associated diseases, GWAS data
```

---

## What is a Disease Name?

**Disease** = Medical condition or illness

A human-readable name for a health condition.

### Examples of Disease Names:
```
Breast Cancer              ← One disease
Type 2 Diabetes           ← Another disease
Cystic Fibrosis           ← Yet another disease
Marfan Syndrome           ← And another
```

### What a disease represents:
```
"Breast Cancer" means:
  - Multiple genes involved (BRCA1, BRCA2, TP53, etc.)
  - Multiple variants causing it
  - Multiple clinical features (symptoms)
  - Multiple treatment options
```

### What you use disease names for:
```
"What do we know about Breast Cancer?"
  ↓
Input: "Breast Cancer"
Module: DISEASE ASSOC
Output: All variants, genes, phenotypes, drugs
```

---

## Side-by-Side Comparison

| Aspect | RSID | Disease |
|--------|------|---------|
| **Example** | `rs1234567` | `"Breast Cancer"` |
| **What it is** | Single variant | Medical condition |
| **Module** | GENE VARIANT | DISEASE ASSOC |
| **Input format** | `rs + numbers` | `Plain text` |
| **What you get** | Info about ONE variant | Info about MANY variants |
| **Starts with** | `rs` | Letters/words |
| **Use when** | You have specific variant | You want disease overview |

---

## Visual Example

### Scenario 1: You have RSID rs1234567
```
❌ WRONG:
Input: "rs1234567" into DISEASE ASSOC
Error: "RSID not found"

✅ CORRECT:
Input: "rs1234567" into GENE VARIANT
Output: This specific variant affects BRCA1 gene, 
        causes Breast Cancer in pathogenic form,
        ClinVar says "Pathogenic"
```

### Scenario 2: You have Disease name "Breast Cancer"
```
❌ WRONG:
Input: "Breast Cancer" into GENE VARIANT
Error: "Gene not found" or no results

✅ CORRECT:
Input: "Breast Cancer" into DISEASE ASSOC
Output: 12+ variants (rs1234567, rs987654, etc.),
        5 genes (BRCA1, BRCA2, TP53, etc.),
        8 phenotypes,
        3 available drugs
```

---

## How They Relate

```
Disease "Breast Cancer"
    │
    ├─ Gene 1: BRCA1
    │  │
    │  ├─ Variant 1: rs1234567 (RSID)
    │  ├─ Variant 2: rs987654 (RSID)
    │  └─ Variant 3: rs5555555 (RSID)
    │
    ├─ Gene 2: BRCA2
    │  │
    │  ├─ Variant 4: rs1111111 (RSID)
    │  └─ Variant 5: rs2222222 (RSID)
    │
    └─ Gene 3: TP53
       │
       └─ Variant 6: rs3333333 (RSID)

So:
- Disease "Breast Cancer" contains MULTIPLE genes
- Each gene has MULTIPLE variants (RSIDs)
- When you search disease, you get ALL of them
- When you search RSID, you get just THAT ONE
```

---

## Real Example: BRCA1 and Breast Cancer

### If you search RSID: rs80357906
```
Input: rs80357906
Module: GENE VARIANT
Output:
  - Gene: BRCA1
  - Position: Chr17:43044295
  - Change: G→A
  - Impact: Missense variant
  - Significance: Pathogenic (likely causes disease)
  - Associated disease: Hereditary Breast and Ovarian Cancer
```

### If you search Disease: "Breast Cancer"
```
Input: "Breast Cancer"
Module: DISEASE ASSOC
Output:
  - Variants: [rs80357906, rs1799966, rs16942, ... 12 more RSIDs]
  - Genes: [BRCA1, BRCA2, TP53, PTEN, CDH1, ... 5 total]
  - Phenotypes: [Breast carcinoma, Ovarian carcinoma, ...]
  - Drugs: [Talazoparib, Olaparib, Imatinib, ...]
```

---

## How to Know Which to Use

### Ask Yourself:

#### Question 1: Do I have a number that starts with "rs"?
```
YES → Use GENE VARIANT module
      Example: rs1234567

NO → Go to Question 2
```

#### Question 2: Do I have coordinates (CHR:POS:REF:ALT)?
```
YES → Use GENE VARIANT module
      Example: 17:43044295:G:A

NO → Go to Question 3
```

#### Question 3: Do I have a disease name?
```
YES → Use DISEASE ASSOC module
      Example: "Breast Cancer"

NO → Use other modules (Drug Discovery, etc.)
```

---

## Error Messages and What They Mean

### Error: "RSID not found"
```
Meaning: You input an RSID into DISEASE ASSOC
Solution: Use GENE VARIANT module instead

Example:
  ❌ Input "rs1234567" into DISEASE ASSOC
  ✅ Input "rs1234567" into GENE VARIANT
```

### Error: "Disease not found"
```
Meaning 1: You input an RSID into DISEASE ASSOC
Solution: Use GENE VARIANT module

Meaning 2: You input a disease name that doesn't exist
Solution: Try different name or use autocomplete

Example of Meaning 2:
  ❌ Input "Made Up Disease" into DISEASE ASSOC
  ✅ Input "Breast Cancer" into DISEASE ASSOC
```

### Warning: "You entered an RSID"
```
Meaning: You input an RSID into DISEASE ASSOC
Solution: Use GENE VARIANT module instead

This is the NEW warning message that tells you:
  "Hey, this looks like an RSID. 
   You should use GENE VARIANT module instead."
```

---

## Decision Flow

```
What do I want to search?
│
├─ Information about ONE specific variant (RSID like rs1234567)
│  └─> GENE VARIANT Module
│      Input: rs1234567
│      Get: VEP data, clinical significance, GWAS associations
│
├─ Information about ALL variants that cause a disease
│  └─> DISEASE ASSOC Module
│      Input: "Breast Cancer"
│      Get: All variants, genes, phenotypes, drugs
│
├─ Information about a specific gene
│  └─> GENE VARIANT Module
│      Input: BRCA1
│      Get: Gene info, associated variants, diseases
│
├─ Information about a drug
│  └─> DRUG DISCOVERY Module
│      Input: "Talazoparib"
│      Get: Drug info, targets, indications
│
└─ Something else
   └─> Check other modules
```

---

## Common Mistake Patterns

### Pattern 1: Confusing RSID with Disease
```
"I want to search rs1234567"
  │
  ├─ WRONG: Put it in DISEASE ASSOC
  │ ❌ Get error: "RSID not found"
  │
  └─ RIGHT: Put it in GENE VARIANT
    ✅ Get: VEP annotation, clinical data
```

### Pattern 2: Confusing Disease with RSID
```
"I want to search Breast Cancer"
  │
  ├─ WRONG: Put it in GENE VARIANT
  │ ❌ Get error: "Gene not found"
  │
  └─ RIGHT: Put it in DISEASE ASSOC
    ✅ Get: Variants, genes, phenotypes, drugs
```

### Pattern 3: Using RSID Format in Disease Search
```
"I put rs1234567 into disease search"
  │
  ├─ NEW: Get warning: "You entered an RSID"
  │ ⚠️  System recognizes it's RSID
  │
  └─ Solution: Use GENE VARIANT module
    ✅ Get correct results
```

---

## Summary Table

| You Want to Know | Search Type | Example Input | Module | Result |
|---|---|---|---|---|
| About one variant | RSID | rs1234567 | GENE VARIANT | VEP data, significance |
| About all variants for a disease | Disease | Breast Cancer | DISEASE ASSOC | All variants, genes, drugs |
| About a specific gene | Gene | BRCA1 | GENE VARIANT | Gene info, variants |
| Variant coordinates | Coordinates | 17:43044295:G:A | GENE VARIANT | VEP data, clinical data |
| About a drug | Drug | Talazoparib | DRUG DISCOVERY | Drug info, targets |

---

## Key Takeaways

✅ **RSID** = One specific variant = GENE VARIANT module = Input: `rs1234567`

✅ **Disease** = Many variants + genes + phenotypes = DISEASE ASSOC module = Input: `"Breast Cancer"`

✅ **Don't mix them** = RSID in disease search = Error

✅ **Use right module** = Get correct results

---

## Now You Know!

- RSIDs are for specific variants
- Disease names are for medical conditions
- They use different modules
- Don't put RSID into disease search
- The system now warns you if you do

**Ready to search?** Pick a disease name and use DISEASE ASSOC module! 🚀
