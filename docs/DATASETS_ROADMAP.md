# 🗺️ GenVarX Datasets Roadmap

Complete roadmap for adding disease, drug, and variant datasets to enhance GenVarX.

---

## 📌 Current Status

**Currently Available:**
- ✅ ChEMBL (drugs) - 5 MB
- ✅ HPO (phenotypes) - 50 MB auto-download
- 🏗️ VEP / ClinVar / GWAS (via APIs)

**Total Local Storage:** ~55 MB

---

## 🎯 Recommended Datasets (Priority Order)

### **Phase 1: Foundation (Week 1)**
Essential for core functionality

#### 1. **ClinVar Variants** ⭐⭐⭐⭐⭐
```
Purpose: Clinical significance of variants
Size: 500 MB
Rows: 1.4M variants
Setup: 5 minutes
Impact: 🔥 High - enables pathogenicity lookup
```

**Key Features:**
- Variant pathogenicity classification
- Disease-variant associations
- Expert review status
- Real-world clinical evidence

**Download:**
```bash
mkdir -p data/datasets/clinvar/
wget -O data/datasets/clinvar/clinvar_summary.tsv \
  ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt
```

#### 2. **OMIM Diseases** ⭐⭐⭐⭐⭐
```
Purpose: Mendelian disease database
Size: 20 MB
Rows: 4,000 diseases
Setup: 5 minutes
Impact: 🔥 High - disease-gene mapping
```

**Key Features:**
- Gene-disease associations
- Inheritance patterns
- Clinical manifestations
- Mendelian inheritance info

**Download:**
```bash
mkdir -p data/datasets/omim/
# Manual download from https://www.omim.org/downloads
# (Free registration required)
```

---

### **Phase 2: Enhancement (Week 2)**
Improve drug and variant analysis

#### 3. **DrugBank** ⭐⭐⭐⭐⭐
```
Purpose: Comprehensive drug database
Size: 300 MB
Rows: 13,000+ drugs
Setup: 5 minutes
Impact: 🔥 High - drug-target interactions
```

**Key Features:**
- Drug-protein targets
- Drug-drug interactions
- Clinical indications
- Pharmacokinetic data

**Download:**
```bash
mkdir -p data/datasets/drugbank/
# Download from https://go.drugbank.com/downloads
# (Free account required)
```

#### 4. **DisGeNET** ⭐⭐⭐⭐
```
Purpose: Disease-gene networks
Size: 500 MB
Rows: 1.6M associations
Setup: 5 minutes
Impact: ⚡ High - cross-validation
```

**Key Features:**
- Gene-disease scores
- Literature support
- Multiple disease sources
- Network analysis potential

**Download:**
```bash
mkdir -p data/datasets/disgenet/
wget -O data/datasets/disgenet/diseases.tsv.gz \
  https://www.disgenet.org/downloads/disease_mappings.tsv.gz
gunzip data/datasets/disgenet/diseases.tsv.gz
```

---

### **Phase 3: Advanced (Week 3)**
Cancer and population-level analysis

#### 5. **COSMIC** ⭐⭐⭐⭐
```
Purpose: Cancer mutations database
Size: 100 MB
Rows: 1.5M somatic mutations
Setup: 5 minutes
Impact: ⚡ Medium - cancer variant analysis
```

**Key Features:**
- Cancer-specific mutations
- Tumor tissue types
- Mutation frequencies
- Cancer gene annotations

**Download:**
```bash
mkdir -p data/datasets/cosmic/
# Download from https://cancer.sanger.ac.uk/cosmic/
# (Free registration)
```

#### 6. **GWAS Catalog Extended** ⭐⭐⭐
```
Purpose: GWAS summary statistics
Size: 50 MB
Rows: 250,000+ associations
Setup: 5 minutes
Impact: ⚡ Medium - population association data
```

**Key Features:**
- GWAS associations summary
- Ancestry-specific data
- Effect sizes
- Study metadata

**Download:**
```bash
mkdir -p data/datasets/gwas/
wget -O data/datasets/gwas/associations.tsv \
  https://www.ebi.ac.uk/gwas/api/search/downloads/full
```

---

### **Phase 4: Optional (Future)**
Large/specialized datasets

#### 7. **gnomAD** (Optional) ⭐⭐⭐
```
Purpose: Population allele frequencies
Size: 200+ GB (HUGE!)
Rows: 809M variants
Setup: 30+ minutes (subset only)
Impact: ⚡ Medium - allele frequency filtering
Recommendation: Use API or download chr-specific subsets only
```

#### 8. **TTD** (Optional) ⭐⭐⭐
```
Purpose: Therapeutic targets database
Size: 50 MB
Rows: 3,500+ drugs
Setup: 5 minutes
Impact: 💡 Low - supplementary drug data
```

#### 9. **PubChem** (Optional) ⭐⭐
```
Purpose: Chemical compound library
Size: 1+ GB (recommend subset)
Rows: 120M+ compounds
Setup: 10+ minutes
Impact: 💡 Low - chemical similarity search
```

---

## 📊 Implementation Timeline

### **Week 1: Foundation**
```
Day 1: Add ClinVar service
       ├─ Download dataset
       ├─ Create clinvar_local_service.py
       ├─ Add API endpoints
       └─ Test with variants

Day 2: Add OMIM service
       ├─ Download dataset
       ├─ Create omim_service.py
       ├─ Add API endpoints
       └─ Test with genes

Total Time: 4-6 hours
Total Storage: 520 MB
Impact: Full pathogenicity lookup capability
```

### **Week 2: Enhancement**
```
Day 3: Add DrugBank service
       ├─ Download dataset
       ├─ Create drugbank_service.py
       ├─ Add drug-target endpoints
       └─ Integrate with variant analysis

Day 4: Add DisGeNET service
       ├─ Download dataset
       ├─ Create disgenet_service.py
       ├─ Cross-validate disease associations
       └─ Build network visualization (optional)

Total Time: 4-6 hours
Total Storage: +800 MB (+1.3 GB total)
Impact: Comprehensive disease-gene-drug network
```

### **Week 3: Advanced**
```
Day 5: Add COSMIC service
       ├─ Download dataset
       ├─ Create cosmic_service.py
       ├─ Add cancer-specific analysis
       └─ Test with known cancer variants

Day 6: Extend GWAS Catalog
       ├─ Download summary stats
       ├─ Integrate with existing GWAS service
       ├─ Add ancestry filtering
       └─ Enhance trait associations

Total Time: 3-4 hours
Total Storage: +150 MB (+1.45 GB total)
Impact: Cancer and population-level analysis
```

---

## 🏗️ Storage Planning

| Phase | Datasets | Size | Cumulative | Disk Needed |
|-------|----------|------|------------|-------------|
| **Current** | ChEMBL, HPO | 55 MB | 55 MB | 256 MB |
| **Phase 1** | + ClinVar, OMIM | 520 MB | 575 MB | 1 GB |
| **Phase 2** | + DrugBank, DisGeNET | 800 MB | 1.4 GB | 2 GB |
| **Phase 3** | + COSMIC, GWAS | 150 MB | 1.55 GB | 2 GB |
| **Phase 4** | + gnomAD subset | 100+ GB | 101+ GB | 256 GB |

**Recommendation:** Stop after Phase 3 for local development. Use cloud storage for Phase 4.

---

## 📁 Final Directory Structure

After all implementations:

```
data/datasets/
├── chembl/                          ✅ Existing
│   └── chembl_compounds.csv
├── hpo/                             ✅ Auto-download
│   └── hp.json
├── clinvar/                         ← PHASE 1
│   ├── clinvar_summary.tsv
│   └── variant_disease_associations.tsv
├── omim/                            ← PHASE 1
│   ├── omim_genemap2.txt
│   └── omim_diseases.json
├── drugbank/                        ← PHASE 2
│   ├── drugbank_drugs.csv
│   └── drugbank_drug_targets.csv
├── disgenet/                        ← PHASE 2
│   └── diseases.tsv
├── cosmic/                          ← PHASE 3
│   └── cosmic_cancer_variants.vcf
└── gwas/                            ← PHASE 3
    └── gwas_associations.tsv
```

---

## 🔌 API Endpoints - Final State

### **After Phase 1** (ClinVar + OMIM)
```
GET    /api/clinvar/gene/{gene}              → Variants for gene
GET    /api/clinvar/disease/{disease}        → Variants for disease
GET    /api/omim/gene/{gene}                 → Disease info for gene
GET    /api/omim/disease/{disease}           → Gene info for disease
```

### **After Phase 2** (Add DrugBank + DisGeNET)
```
GET    /api/drugbank/target/{protein}        → Drugs for target
GET    /api/drugbank/drug/{drug_id}          → Drug details
GET    /api/disgenet/gene/{gene}             → Disease-gene scores
GET    /api/disgenet/disease/{disease}       → Associated genes
```

### **After Phase 3** (Add COSMIC + GWAS)
```
GET    /api/cosmic/cancer/{cancer_type}      → Cancer mutations
POST   /api/gwas/associations                → GWAS trait associations
GET    /api/gwas/ancestry/{ancestry}         → Population-specific data
```

### **Comprehensive Endpoints**
```
POST   /api/comprehensive/analyze            → All datasets at once
POST   /api/comprehensive/variant-disease    → Variant → Disease pathway
POST   /api/comprehensive/drug-target        → Drug → Target → Gene pathway
```

---

## 🚀 Getting Started Now

### **Option A: Minimal Setup (30 minutes)**
Just ClinVar + OMIM:
```bash
# 1. Download
mkdir -p data/datasets/{clinvar,omim}/
wget -O data/datasets/clinvar/clinvar_summary.tsv \
  ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt

# 2. Follow template in docs/DATASET_IMPLEMENTATION_TEMPLATE.md
# 3. Create services and endpoints
# 4. Test with curl
```

### **Option B: Recommended Setup (2 hours)**
Add DrugBank + DisGeNET:
```bash
# Follow same process for DrugBank and DisGeNET
# Now you have comprehensive analysis capability
```

### **Option C: Full Setup (5 hours)**
All of Phases 1-3:
```bash
# Maximum local analysis capability
# +1.55 GB storage
# 10+ API endpoints
```

---

## 📚 Documentation Guide

| Document | Use For |
|----------|---------|
| `ADDITIONAL_DATASETS.md` | Detailed dataset descriptions |
| `DATASET_IMPLEMENTATION_TEMPLATE.md` | Step-by-step implementation |
| `QUICK_DATASET_SETUP.md` | Copy-paste quick setup |
| `DATASETS_ROADMAP.md` | This file - overall planning |

---

## ✅ Implementation Checklist

### **Phase 1 Checklist**
- [ ] ClinVar dataset downloaded
- [ ] ClinVar service created
- [ ] ClinVar API endpoints working
- [ ] OMIM dataset downloaded
- [ ] OMIM service created
- [ ] OMIM API endpoints working
- [ ] Integration tests pass
- [ ] Documentation updated

### **Phase 2 Checklist**
- [ ] DrugBank dataset downloaded
- [ ] DrugBank service created
- [ ] DrugBank endpoints integrated
- [ ] DisGeNET dataset downloaded
- [ ] DisGeNET service created
- [ ] Cross-dataset queries working
- [ ] Performance acceptable

### **Phase 3 Checklist**
- [ ] COSMIC dataset downloaded
- [ ] COSMIC service created
- [ ] Cancer analysis working
- [ ] GWAS extended data integrated
- [ ] Population filters working
- [ ] All previous phases still working

---

## 🎯 Success Metrics

After **Phase 1:**
- ✅ Can search variants by pathogenicity
- ✅ Can find diseases by gene
- ✅ Can validate against clinical data
- ✅ 500M+ clinical variants indexed

After **Phase 2:**
- ✅ Can identify drug targets
- ✅ Can cross-validate gene-disease
- ✅ Can suggest therapeutic options
- ✅ Full disease-gene-drug network

After **Phase 3:**
- ✅ Can analyze cancer mutations
- ✅ Can filter by population frequency
- ✅ Can identify disease traits
- ✅ Comprehensive genomic analysis

---

## 🔐 Data Quality & Attribution

All recommended datasets:
- ✅ Public domain or CC-licensed
- ✅ Well-maintained and peer-reviewed
- ✅ Regularly updated
- ✅ Properly cited in publications
- ✅ No API keys required

---

## 💡 Tips for Success

1. **Start small:** Begin with Phase 1 (ClinVar + OMIM)
2. **Test incrementally:** Add one dataset, test thoroughly
3. **Monitor performance:** Check loading times
4. **Document changes:** Keep track of what you added
5. **Backup data:** Store important datasets safely
6. **Plan updates:** Set schedule for data refreshes

---

## 🚀 Next Actions

**Today:**
1. Read `QUICK_DATASET_SETUP.md`
2. Download ClinVar dataset
3. Follow implementation template

**This Week:**
1. Complete Phase 1 (ClinVar + OMIM)
2. Test all endpoints
3. Update documentation

**Next Week:**
1. Start Phase 2 (DrugBank + DisGeNET)
2. Build cross-dataset queries
3. Add visualization/analysis

---

## 📞 Questions?

- **"How do I start?"** → Read `QUICK_DATASET_SETUP.md`
- **"How do I add a dataset?"** → Read `DATASET_IMPLEMENTATION_TEMPLATE.md`
- **"What datasets should I add?"** → This roadmap
- **"How much storage?"** → See storage planning section

---

**Status:** Ready for implementation
**Estimated Total Time:** 1-2 weeks (all phases)
**Expected Impact:** 10x more functionality
**Difficulty:** Easy (follow templates)

🚀 **Let's build GenVarX into a comprehensive genomic analysis platform!**

