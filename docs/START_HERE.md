# 🚀 START HERE - Disease Search Quick Guide

## ⚠️ The Main Issue You Had

You were getting "RSID not found" because you were putting **RSIDs** into the **disease search**.

But disease search wants **disease names**, not RSIDs.

---

## 🎯 The Solution (3 Simple Steps)

### Step 1: Remember the Difference

```
RSID looks like: rs1234567  (← This is ONE specific variant)
Disease looks like: Breast Cancer  (← This is a DISEASE with many variants)
```

### Step 2: Use the Right Module

| What You Have | Use This Module | Input Format |
|---|---|---|
| **RSID** (rs1234567) | **GENE VARIANT** | `rs1234567` |
| **Disease** (Breast Cancer) | **DISEASE ASSOC** | `"Breast Cancer"` |

### Step 3: Type Correctly

```
❌ WRONG: Put rs1234567 into DISEASE ASSOC
✅ CORRECT: Put "Breast Cancer" into DISEASE ASSOC
✅ CORRECT: Put rs1234567 into GENE VARIANT
```

---

## 📋 Copy-Paste Disease Names to Try

```
Breast Cancer
Type 2 Diabetes
Cystic Fibrosis
Hemophilia A
Sickle Cell Disease
Marfan Syndrome
```

Pick any one above and:
1. Go to **DISEASE ASSOC** module
2. Type it in
3. See results!

---

## 📖 Read These Guides (in order)

### 1️⃣ **QUICK** (5 min)
**File**: `QUICK_START_DISEASE_SEARCH.md`
- Fast overview
- Common mistakes
- Simple examples

### 2️⃣ **IMPORTANT** (10 min)
**File**: `RSID_vs_DISEASE_EXPLAINED.md`
- Explains RSID vs Disease clearly
- Visual examples
- Decision flowchart

### 3️⃣ **REFERENCE** (5 min to browse)
**File**: `VALID_DISEASE_NAMES_TO_TRY.md`
- 50+ disease names to copy-paste
- Organized by category

---

## 🔄 Two Different Modules

### Module 1: GENE VARIANT (For RSIDs)
```
✅ Input this:
- rs1234567 (RSID)
- 17:43044295:G:A (Coordinates)
- BRCA1 (Gene)

❌ Don't input this:
- Breast Cancer (Disease)
- Type 2 Diabetes (Disease)

📤 You get:
- VEP annotation
- Clinical significance
- GWAS data
```

### Module 2: DISEASE ASSOC (For Disease Names) ← NEW
```
✅ Input this:
- Breast Cancer
- Type 2 Diabetes
- Cystic Fibrosis
- Any disease name

❌ Don't input this:
- rs1234567 (RSID)
- 17:43044295:G:A (Coordinates)

📤 You get:
- All variants for disease
- Associated genes
- Clinical phenotypes
- Available drugs
- Disease metadata
```

---

## 🎬 Example: What Happens When You Search

### Example 1: Search "Breast Cancer"

```
Input: "Breast Cancer"
Module: DISEASE ASSOC
↓
Output shows:
├─ Variants: 12 BRCA1/BRCA2 variants
├─ Genes: BRCA1, BRCA2, TP53, etc.
├─ Phenotypes: Breast cancer, ovarian cancer, etc.
└─ Drugs: Talazoparib, Olaparib, etc.
```

### Example 2: Search "rs1234567"

```
Input: "rs1234567"
Module: GENE VARIANT
↓
Output shows:
├─ Gene: BRCA1
├─ Significance: Pathogenic
├─ Impact: HIGH
└─ Related diseases: Breast cancer, ovarian cancer
```

### Example 3: Wrong Module

```
Input: "rs1234567"
Module: DISEASE ASSOC (❌ WRONG MODULE)
↓
Output: ⚠️ Warning: "You entered an RSID.
        Use GENE VARIANT module instead."
```

---

## ✅ To Fix Your Issue

1. **Understand**: Read `RSID_vs_DISEASE_EXPLAINED.md`
2. **Pick Disease**: Choose from `VALID_DISEASE_NAMES_TO_TRY.md`
3. **Go to DISEASE ASSOC**: Not GENE VARIANT
4. **Type Disease Name**: Like `"Breast Cancer"`
5. **Get Results**: Variants, genes, drugs, phenotypes

---

## 🎯 Quick Decision Tree

```
Do I have:
│
├─ RSID (starts with "rs")? → Use GENE VARIANT
├─ Coordinates (CHR:POS:REF:ALT)? → Use GENE VARIANT
├─ Gene name (BRCA1, TP53)? → Use GENE VARIANT
└─ Disease name (Breast Cancer)? → Use DISEASE ASSOC ✅
```

---

## ⚡ Super Quick Reference

| Scenario | Module | Input | Gets |
|---|---|---|---|
| "What is rs1234567?" | GENE VARIANT | rs1234567 | Variant info |
| "Tell me about Breast Cancer" | DISEASE ASSOC | Breast Cancer | Disease info |
| "I have RSID" | GENE VARIANT | RSID | Variant details |
| "I want disease overview" | DISEASE ASSOC | Disease | All variants + genes + drugs |

---

## 🔥 Try Right Now

```
Step 1: Go to DISEASE ASSOC module
Step 2: Type: Breast Cancer
Step 3: Press Enter/Search
Step 4: See results!
```

That's it! 🎉

---

## 🆘 If Something Goes Wrong

| Error | Cause | Fix |
|---|---|---|
| "RSID not found" | Inputted RSID into DISEASE ASSOC | Use GENE VARIANT module |
| "Disease not found" | Wrong disease name or typo | Check spelling or use autocomplete |
| "Gene not found" | Inputted disease into GENE VARIANT | Use DISEASE ASSOC module |
| No results | Disease might not have data | Try different disease from list |

---

## 📚 Full Documentation

### Quick Start
- `QUICK_START_DISEASE_SEARCH.md` - Fast guide

### Understanding
- `RSID_vs_DISEASE_EXPLAINED.md` - Main explanation
- `SEARCH_MODES_EXPLAINED.md` - Detailed comparison

### Reference
- `VALID_DISEASE_NAMES_TO_TRY.md` - Disease list
- `INPUT_REFERENCE_GUIDE.md` - All input formats

### Implementation Details
- `DISEASE_SEARCH_IMPLEMENTATION.md` - Technical spec
- `DISEASE_SEARCH_INTEGRATION_GUIDE.md` - Frontend guide

---

## 🎓 Key Concepts

✅ **RSID** = Single genetic variant identified by rs + number  
✅ **Disease** = Medical condition that might be caused by multiple variants  
✅ **GENE VARIANT** module = Search by RSID/variant  
✅ **DISEASE ASSOC** module = Search by disease name  

---

## 🚀 You're Ready!

1. ✅ Understand RSID vs Disease
2. ✅ Pick disease name
3. ✅ Go to DISEASE ASSOC
4. ✅ Type and search
5. ✅ Get results!

---

## 💡 Pro Tips

1. **Use autocomplete** - System suggests disease names as you type
2. **Start simple** - Try "Breast Cancer" first
3. **Check spelling** - Disease names must be exactly right
4. **Use this list** - `VALID_DISEASE_NAMES_TO_TRY.md`
5. **Don't mix modules** - RSID → GENE VARIANT, Disease → DISEASE ASSOC

---

## 📍 Where to Go Next

**For understanding**: `RSID_vs_DISEASE_EXPLAINED.md`  
**For trying it**: `VALID_DISEASE_NAMES_TO_TRY.md`  
**For quick tips**: `QUICK_START_DISEASE_SEARCH.md`  
**For complete reference**: `INPUT_REFERENCE_GUIDE.md`  

---

**You've got this! Pick a disease and search! 🎯**
