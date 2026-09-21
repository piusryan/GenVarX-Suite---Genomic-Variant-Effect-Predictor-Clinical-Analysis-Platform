# 📊 GenVarX - Additional Datasets Guide

Complete guide to adding comprehensive disease, drug, and variant datasets for enhanced analysis.

---

## 🎯 Dataset Categories & Recommendations

### 1️⃣ **DISEASE DATASETS**

#### Option A: **OMIM (Online Mendelian Inheritance in Man)**
- **Location:** `data/datasets/omim/`
- **Files Needed:**
  - `omim_genemap2.txt` — Gene-disease associations
  - `omim_diseases.json` — Disease descriptions & inheritance patterns
- **Size:** ~20 MB
- **Format:** TSV / JSON
- **Source:** https://www.omim.org/ (requires registration)
- **Rows:** ~4,000 diseases
- **Use Case:** Get disease info, inheritance patterns, clinical features

**Columns (genemap2.txt):**
```
Chromosome | Genomic_Position | Gene_Symbol | MIM_Number | Disease | Inheritance
1          | 11869            | DDX11L1    | 615939     | Fanconi Anemia | AR
1          | 14370            | WASH7P     | 100129534  | Cognitive Disorder | AD
```

#### Option B: **DisGeNET (Disease-Gene Network)**
- **Location:** `data/datasets/disgenet/`
- **Files Needed:**
  - `disgenet_diseases.tsv` — Disease-gene-variant associations
  - `disease_mappings.tsv` — Disease names & IDs
- **Size:** ~500 MB
- **Format:** TSV
- **Source:** https://www.disgenet.org/downloads
- **Rows:** 1.6 million associations
- **Use Case:** Comprehensive disease-gene connections

**Columns (diseases.tsv):**
```
diseaseId | diseaseName | geneId | geneSymbol | score | pmid | yearInitial
C0006941  | Carcinoma   | 672    | BRCA1      | 0.95  | 12345| 1994
C0006947  | Colorectal  | 1026   | CDKN2A    | 0.87  | 12346| 1993
```

#### Option C: **MeSH (Medical Subject Headings)**
- **Location:** `data/datasets/mesh/`
- **Files Needed:**
  - `mesh_disease_descriptors.xml` — Disease hierarchy
  - `mesh_disease_tree.txt` — Tree structure
- **Size:** ~50 MB
- **Format:** XML / TXT
- **Source:** https://www.nlm.nih.gov/mesh/
- **Rows:** ~16,000 disease descriptors
- **Use Case:** Standardized disease terminology

---

### 2️⃣ **DRUG DATASETS**

#### Option A: **DrugBank (Comprehensive Drug Database)**
- **Location:** `data/datasets/drugbank/`
- **Files Needed:**
  - `drugbank_drugs.csv` — Full drug data with targets
  - `drugbank_drug_targets.csv` — Drug-protein targets
  - `drugbank_interactions.csv` — Drug-drug interactions
- **Size:** ~300 MB
- **Format:** CSV
- **Source:** https://www.drugbank.ca/downloads
- **Rows:** 13,000+ drugs
- **Use Case:** Drug targets, interactions, indications

**Columns (drugs.csv):**
```
DrugBank_ID | Name           | Type          | Groups      | Targets | Indication
DB00001     | Lepirudin      | Small Molecule| Experimental| THROMBIN| Thromboembolic
DB00002     | Cetuximab      | Biologic      | Approved    | EGFR    | Cancer
```

#### Option B: **PubChem (Chemical Compound Database)**
- **Location:** `data/datasets/pubchem/`
- **Files Needed:**
  - `pubchem_compounds.csv` — Chemical properties
  - `pubchem_bioassays.csv` — Bioactivity data
- **Size:** ~1 GB (subset recommended)
- **Format:** CSV / JSON
- **Source:** https://pubchem.ncbi.nlm.nih.gov/
- **Rows:** 120M+ compounds (recommend subset)
- **Use Case:** Chemical properties, structure similarity

#### Option C: **TTD (Therapeutic Target Database)**
- **Location:** `data/datasets/ttd/`
- **Files Needed:**
  - `ttd_drugs.txt` — Drug info & targets
  - `ttd_targets.txt` — Target protein info
- **Size:** ~50 MB
- **Format:** TXT (pipe-delimited)
- **Source:** https://db.idrblab.net/ttd/
- **Rows:** 3,500+ drugs
- **Use Case:** Targeted therapy databases

---

### 3️⃣ **VARIANT DATASETS**

#### Option A: **ClinVar (Clinical Variant Database)**
- **Location:** `data/datasets/clinvar/`
- **Files Needed:**
  - `clinvar_GRCh38.vcf` — Clinical variants in VCF format
  - `clinvar_summary.tsv` — Variant summaries
  - `variant_disease_associations.tsv` — Variant-disease links
- **Size:** ~500 MB
- **Format:** VCF / TSV
- **Source:** https://ftp.ncbi.nlm.nih.gov/pub/clinvar/
- **Rows:** 1.4 million+ variants
- **Use Case:** Ground truth for pathogenicity, validation

**Columns (summary.tsv):**
```
#VariationID | Type    | Name             | GeneSymbol | Phenotype      | ClinicalSignificance
1            | single  | NM_007294.3:c.68 | BRCA1      | Breast Cancer  | Pathogenic
2            | single  | NM_000038.6:c.69 | APOB       | Hyperlipidemia | Pathogenic
```

#### Option B: **gnomAD (Genome Aggregation Database)**
- **Location:** `data/datasets/gnomad/`
- **Files Needed:**
  - `gnomad_variants.vcf` — Allele frequency data
  - `gnomad_coverage.vcf` — Coverage statistics
- **Size:** ~200 GB (huge! recommend filtered subset)
- **Format:** VCF / VCF.gz
- **Source:** https://gnomad.broadinstitute.org/
- **Rows:** 809 million variants
- **Use Case:** Population allele frequencies, filtering
- **Recommendation:** Download chr-specific subsets, not entire dataset

#### Option C: **COSMIC (Cancer Catalog Of Somatic Mutations In Cancer)**
- **Location:** `data/datasets/cosmic/`
- **Files Needed:**
  - `cosmic_cancer_variants.vcf` — Cancer-specific mutations
  - `cosmic_cancer_genes.csv` — Cancer-related genes
- **Size:** ~100 MB
- **Format:** VCF / CSV
- **Source:** https://cancer.sanger.ac.uk/cosmic/
- **Rows:** 1.5 million+ somatic mutations
- **Use Case:** Cancer variant analysis

#### Option D: **GWAS Catalog (Extended Dataset)**
- **Location:** `data/datasets/gwas/`
- **Files Needed:**
  - `gwas_associations.tsv` — GWAS summary statistics
  - `gwas_ancestry_groups.tsv` — Ancestry-specific data
- **Size:** ~50 MB
- **Format:** TSV
- **Source:** https://www.ebi.ac.uk/gwas/downloads
- **Rows:** 250,000+ associations
- **Use Case:** GWAS-derived variant prioritization

---

## 📈 Quick Comparison Matrix

| Dataset | Size | Rows | Format | Focus | Recommended |
|---------|------|------|--------|-------|-------------|
| **OMIM** | 20 MB | 4K | TXT | Mendelian diseases | ⭐⭐⭐⭐⭐ |
| **DisGeNET** | 500 MB | 1.6M | TSV | Gene-disease networks | ⭐⭐⭐⭐ |
| **MeSH** | 50 MB | 16K | XML | Disease hierarchy | ⭐⭐⭐ |
| **DrugBank** | 300 MB | 13K | CSV | Drug info & targets | ⭐⭐⭐⭐⭐ |
| **PubChem** | 1+ GB | 120M+ | CSV | Chemical library | ⭐⭐⭐ |
| **TTD** | 50 MB | 3.5K | TXT | Drug targets | ⭐⭐⭐⭐ |
| **ClinVar** | 500 MB | 1.4M | VCF/TSV | Clinical variants | ⭐⭐⭐⭐⭐ |
| **gnomAD** | 200+ GB | 809M | VCF | Population freq | ⭐⭐⭐⭐ (subset only) |
| **COSMIC** | 100 MB | 1.5M | VCF/CSV | Cancer mutations | ⭐⭐⭐⭐ |
| **GWAS Catalog** | 50 MB | 250K | TSV | GWAS results | ⭐⭐⭐⭐ |

---

## 🚀 Recommended Setup (Start Here)

### **Minimum Viable Setup** (~900 MB)
Perfect for MVP and local development:

```
data/datasets/
├── chembl/              ✅ Already have
│   └── chembl_compounds.csv
├── omim/                ← ADD FIRST
│   ├── omim_genemap2.txt
│   └── omim_diseases.json
├── clinvar/             ← ADD SECOND
│   ├── clinvar_summary.tsv
│   └── variant_disease_associations.tsv
├── drugbank/            ← ADD THIRD
│   ├── drugbank_drugs.csv
│   └── drugbank_drug_targets.csv
├── gwas/                ← ADD FOURTH
│   └── gwas_associations.tsv
└── hpo/                 ✅ Auto-downloads
    └── hp.json
```

**Why this combination?**
- ✅ Covers diseases, drugs, and variants
- ✅ Manageable size for local dev (~900 MB)
- ✅ High-quality, well-documented sources
- ✅ Directly improves GenVarX functionality

### **Production Setup** (~2 GB)
For deployed/shared systems:

Add to above:
- `disgenet/` — Enhanced disease-gene network
- `ttd/` — Comprehensive drug-target database
- `cosmic/` — Cancer variant database

---

## 📥 Download & Setup Instructions

### **1. OMIM Dataset**
```bash
# 1. Download from OMIM website (requires free registration)
# https://www.omim.org/downloads

# 2. Create directory
mkdir -p data/datasets/omim/

# 3. Extract files
unzip omim-genemap2.txt.gz -d data/datasets/omim/
unzip omim-diseases.json.gz -d data/datasets/omim/

# 4. Verify
ls -lh data/datasets/omim/
```

### **2. ClinVar Dataset**
```bash
# Download from NCBI FTP
mkdir -p data/datasets/clinvar/

# Get current month's data
wget -O data/datasets/clinvar/clinvar_summary.tsv.gz \
  ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz

# Decompress
gunzip data/datasets/clinvar/clinvar_summary.tsv.gz

# Get VCF (optional, larger file)
wget -O data/datasets/clinvar/clinvar_GRCh38.vcf.gz \
  ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz

gunzip data/datasets/clinvar/clinvar_GRCh38.vcf.gz
```

### **3. DrugBank Dataset**
```bash
# 1. Download from DrugBank (requires registration)
# https://go.drugbank.com/

# 2. Create directory
mkdir -p data/datasets/drugbank/

# 3. Extract CSV files
unzip drugbank_all_full_database.csv.zip -d data/datasets/drugbank/

# 4. Extract targets
unzip drugbank_all_drug_targets.csv.zip -d data/datasets/drugbank/
```

### **4. GWAS Catalog**
```bash
# Download from EBI GWAS
mkdir -p data/datasets/gwas/

# Get associations
wget -O data/datasets/gwas/gwas_associations.tsv \
  https://www.ebi.ac.uk/gwas/api/search/downloads/full

# Get ancestry groups
wget -O data/datasets/gwas/gwas_ancestry.tsv \
  https://www.ebi.ac.uk/gwas/api/search/downloads/full_ancestry
```

### **5. DisGeNET Dataset**
```bash
# Download from DisGeNET
mkdir -p data/datasets/disgenet/

wget -O data/datasets/disgenet/diseases.tsv.gz \
  https://www.disgenet.org/downloads/disease_mappings.tsv.gz

gunzip data/datasets/disgenet/diseases.tsv.gz
```

---

## 🔧 Service Integration Examples

### **Add OMIM Disease Service**
```python
# Create: app/services/omim_service.py

import csv
import json
from pathlib import Path
from typing import Dict, List

OMIM_GENEMAP = Path(__file__).resolve().parent.parent.parent / \
               "data/datasets/omim/omim_genemap2.txt"
OMIM_DISEASES = Path(__file__).resolve().parent.parent.parent / \
               "data/datasets/omim/omim_diseases.json"

async def search_omim_diseases(gene_symbol: str) -> List[Dict]:
    """Find all diseases associated with a gene"""
    results = []
    
    with open(OMIM_GENEMAP, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if row.get('Gene_Symbol', '').upper() == gene_symbol.upper():
                results.append({
                    'gene': row.get('Gene_Symbol'),
                    'mim_number': row.get('MIM_Number'),
                    'disease': row.get('Disease'),
                    'inheritance': row.get('Inheritance')
                })
    
    return results

async def get_disease_info(disease_name: str) -> Dict:
    """Get detailed disease information"""
    with open(OMIM_DISEASES, 'r') as f:
        diseases = json.load(f)
        return diseases.get(disease_name, {})
```

### **Add ClinVar Variant Service**
```python
# Create: app/services/clinvar_local_service.py

import csv
import vcf
from pathlib import Path

CLINVAR_TSV = Path(__file__).resolve().parent.parent.parent / \
              "data/datasets/clinvar/clinvar_summary.tsv"

async def search_clinvar_variants(variant_id: str) -> List[Dict]:
    """Search ClinVar for variant information"""
    results = []
    
    with open(CLINVAR_TSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if variant_id in row.get('Variation ID', ''):
                results.append({
                    'variation_id': row.get('Variation ID'),
                    'type': row.get('Type'),
                    'gene': row.get('Gene Symbol'),
                    'phenotype': row.get('Phenotype(s)'),
                    'clinical_sig': row.get('Clinical Significance'),
                    'evidence': row.get('Review Status')
                })
    
    return results
```

### **Add DrugBank Service**
```python
# Create: app/services/drugbank_service.py

import csv
from pathlib import Path
from typing import Dict, List

DRUGBANK_CSV = Path(__file__).resolve().parent.parent.parent / \
               "data/datasets/drugbank/drugbank_drugs.csv"

async def search_drugbank_by_target(protein_target: str) -> List[Dict]:
    """Find drugs that target a specific protein"""
    results = []
    
    with open(DRUGBANK_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            targets = row.get('Targets', '').split('|')
            if protein_target.upper() in [t.strip().upper() for t in targets]:
                results.append({
                    'drugbank_id': row.get('DrugBank_ID'),
                    'name': row.get('Name'),
                    'type': row.get('Type'),
                    'indication': row.get('Indication'),
                    'targets': targets
                })
    
    return results
```

---

## 📡 New API Endpoints Example

### **Disease-Gene Lookup**
```bash
GET /api/diseases?gene=BRCA1

Response:
{
  "gene": "BRCA1",
  "diseases": [
    {
      "name": "Breast Cancer",
      "mim": "113705",
      "inheritance": "Autosomal Dominant",
      "severity": "High"
    }
  ]
}
```

### **Drug-Target Lookup**
```bash
GET /api/drugs?target=EGFR

Response:
{
  "target": "EGFR",
  "drugs": [
    {
      "name": "Cetuximab",
      "drugbank_id": "DB00002",
      "indication": "Cancer",
      "approval_status": "Approved"
    }
  ]
}
```

### **Variant Pathogenicity (Enhanced)**
```bash
POST /api/annotate-enhanced

Body:
{
  "variant": "17:43044295:G:A",
  "include_datasets": ["clinvar", "omim", "drugbank"]
}

Response:
{
  "variant": "17:43044295:G:A",
  "gene": "BRCA1",
  "clinical_significance": "Pathogenic",
  "diseases": [...from OMIM],
  "similar_variants": [...from ClinVar],
  "drug_targets": [...from DrugBank],
  "conservation_score": 0.95
}
```

---

## 📊 Database Schema Recommendations

### **Diseases Table**
```sql
CREATE TABLE diseases (
    id PRIMARY KEY,
    gene_symbol VARCHAR(100),
    disease_name VARCHAR(255),
    mim_number VARCHAR(10),
    inheritance_pattern VARCHAR(50),
    severity_level VARCHAR(20),
    tissue_affected VARCHAR(255),
    phenotypes TEXT,
    created_at TIMESTAMP
);
```

### **Drugs Table**
```sql
CREATE TABLE drugs (
    id PRIMARY KEY,
    drugbank_id VARCHAR(20),
    name VARCHAR(255),
    type VARCHAR(50),
    indication VARCHAR(255),
    approval_status VARCHAR(50),
    targets TEXT,
    interactions TEXT,
    created_at TIMESTAMP
);
```

### **Variants Table**
```sql
CREATE TABLE variants (
    id PRIMARY KEY,
    variant_id VARCHAR(50),
    chromosome VARCHAR(5),
    position INT,
    ref_allele VARCHAR(1000),
    alt_allele VARCHAR(1000),
    gene_symbol VARCHAR(100),
    clinical_significance VARCHAR(50),
    allele_frequency FLOAT,
    sources TEXT,
    created_at TIMESTAMP
);
```

---

## 🎯 Implementation Priority

### **Phase 1: MVP** (Weeks 1-2)
- [ ] Add OMIM disease dataset
- [ ] Add ClinVar variant dataset
- [ ] Create `omim_service.py` and `clinvar_local_service.py`
- [ ] Add 2 new API endpoints

### **Phase 2: Enhancement** (Weeks 3-4)
- [ ] Add DrugBank dataset
- [ ] Create `drugbank_service.py`
- [ ] Enhance drug search capabilities
- [ ] Add drug-gene interaction endpoint

### **Phase 3: Advanced** (Weeks 5-6)
- [ ] Add DisGeNET for network analysis
- [ ] Add COSMIC for cancer variants
- [ ] Create network visualization
- [ ] Add cross-dataset correlation

### **Phase 4: Production** (Weeks 7+)
- [ ] Add database layer (PostgreSQL)
- [ ] Implement caching strategy
- [ ] Add data update pipeline
- [ ] Performance optimization

---

## ⚠️ Storage Considerations

| Setup | Total Size | Recommended System |
|-------|-----------|-------------------|
| **Minimal** (ChEMBL + HPO) | 55 MB | Any laptop |
| **Recommended** (Add OMIM + ClinVar + DrugBank) | 800 MB | Any laptop |
| **Full** (All datasets) | 200+ GB | Server with SSD |
| **Production** (With gnomAD) | 1+ TB | Cloud storage |

---

## 🔗 Data Sources (Direct Links)

| Dataset | Link | Format | Size |
|---------|------|--------|------|
| OMIM | https://www.omim.org/downloads | TXT/JSON | 20 MB |
| DisGeNET | https://www.disgenet.org/downloads | TSV | 500 MB |
| MeSH | https://www.nlm.nih.gov/mesh/ | XML | 50 MB |
| DrugBank | https://go.drugbank.com/ | CSV | 300 MB |
| PubChem | https://pubchem.ncbi.nlm.nih.gov/downloads/ | CSV/JSON | 1+ GB |
| TTD | https://db.idrblab.net/ttd/ | TXT | 50 MB |
| ClinVar | ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/ | VCF/TSV | 500 MB |
| gnomAD | https://gnomad.broadinstitute.org/ | VCF.gz | 200+ GB |
| COSMIC | https://cancer.sanger.ac.uk/cosmic/ | VCF/CSV | 100 MB |
| GWAS Catalog | https://www.ebi.ac.uk/gwas/downloads | TSV | 50 MB |

---

## ✅ Checklist

- [ ] Download OMIM dataset
- [ ] Download ClinVar dataset
- [ ] Download DrugBank dataset
- [ ] Create service files
- [ ] Add API endpoints
- [ ] Test with sample data
- [ ] Document new features
- [ ] Update requirements.txt
- [ ] Verify data loading speed
- [ ] Add error handling

---

## 📞 Next Steps

1. **Choose your datasets** based on your research focus
2. **Download** using provided commands
3. **Create services** using provided templates
4. **Add endpoints** to `app/main.py`
5. **Test thoroughly** before deployment
6. **Document** your additions
7. **Optimize** for performance if needed

---

**Status:** Ready for implementation
**Last Updated:** August 2026
**Version:** 1.0
