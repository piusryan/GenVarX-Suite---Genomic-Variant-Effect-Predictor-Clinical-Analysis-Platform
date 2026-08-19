# GenVarX Datasets Guide

Complete guide to all datasets used in your project, their organization, and how to use them.

---

## 📂 Dataset Directory Structure

```
data/
├── datasets/                    Main datasets
│   ├── chembl/                 ✅ ChEMBL Compounds (Drug Database)
│   │   └── chembl_compounds.csv
│   │
│   ├── hpo/                    🔄 HPO Ontology (Phenotypes)
│   │   └── hp.json
│   │
│   ├── reference/              ⏳ Reference Genomes (Future)
│   │   ├── GRCh38.fa
│   │   └── refseq_proteins.faa
│   │
│   └── clinvar/                ⏳ ClinVar (Future)
│       └── clinvar_GRCh38.vcf
│
└── cache/                       Temporary cached files
```

**Legend:**
- ✅ = Currently Available & Working
- 🔄 = Auto-downloaded on first use
- ⏳ = Available for future implementation

---

## 1️⃣ ChEMBL Compounds Database

### Location
```
data/datasets/chembl/chembl_compounds.csv
```

### Overview
- **Size:** ~5 MB
- **Rows:** 1.8 million compounds
- **Format:** CSV (semicolon-delimited)
- **Source:** https://www.ebi.ac.uk/chembl/
- **License:** Creative Commons Attribution 4.0

### Columns (Sample)
| Column | Example | Purpose |
|--------|---------|---------|
| Compound ChEMBL ID | CHEMBL237500 | Unique identifier |
| Name | Selinexor | Drug name |
| Type | Small molecule | Molecule type |
| Max Phase | 3 | Clinical trial phase |
| Molecular Weight | 428.45 | MW |
| AlogP | 2.5 | Lipophilicity |
| QED Weighted | 0.8 | Drug-likeness |
| Targets | 25 | Number of targets |
| Bioactivities | 150 | Biological activities |

### How to Use

**In Backend Code:**
```python
from app.services.chembl_local_service import search_compounds, get_compound

# Search by name or ID
results = await search_compounds("selinexor", limit=20)
# Returns: [{"chembl_id": "...", "name": "...", ...}]

# Get specific compound
compound = await get_compound("CHEMBL237500")
# Returns: {"name": "Selinexor", "max_phase": "3", ...}
```

**In Frontend:**
```javascript
// User types drug name in search box
// Frontend calls backend
const results = await searchCompounds("selinexor", 20);
// Displays list of compounds with details
```

### Updating the Dataset

**When:** Monthly (usually 1st of month)

**How:**
1. Download from: https://www.ebi.ac.uk/chembl/
2. Replace: `data/datasets/chembl/chembl_compounds.csv`
3. No code changes needed (path is fixed)

**Alternative:** Set environment variable
```bash
export CHEMBL_CSV_PATH=/path/to/custom/compounds.csv
```

### API Endpoints Using ChEMBL
- `GET /api/compounds?query=selinexor&limit=20` — Search compounds
- `GET /api/compounds/CHEMBL237500` — Get compound details

---

## 2️⃣ HPO Ontology (Phenotypes)

### Location
```
data/datasets/hpo/hp.json
```

### Overview
- **Size:** ~50 MB
- **Format:** JSON (OBO graph format)
- **Rows:** ~16,000 phenotype terms
- **Source:** https://hpo.jax.org/app/data/json/hp.json
- **License:** Creative Commons Attribution 4.0
- **Auto-Download:** Yes (first request)

### Content Structure
```json
{
  "graphs": [{
    "nodes": [
      {
        "id": "HP:0000001",
        "name": "All",
        "def": "Root term"
      },
      {
        "id": "HP:0002664",
        "name": "Neoplasm",
        "def": "An abnormal growth of cells"
      },
      {
        "id": "HP:0003002",
        "name": "Breast neoplasm",
        "def": "A tumor of the breast"
      }
    ]
  }]
}
```

### Disease-Phenotype Mapping
```
Disease: Hereditary Breast Cancer
Phenotypes:
├── HP:0003002 - Breast neoplasm
├── HP:0006704 - Breast adenocarcinoma
├── HP:0000016 - Urinary frequency
└── HP:0100894 - Ovarian neoplasm
```

### How to Use

**In Backend Code:**
```python
from app.services.hpo_service import fetch_phenotypes_for_disease, get_hpo_term

# Get phenotypes for disease
phenotypes = await fetch_phenotypes_for_disease("Hereditary Breast Cancer")
# Returns: [{"id": "HP:...", "name": "...", "definition": "..."}, ...]

# Get specific HPO term
term = await get_hpo_term("HP:0002664")
# Returns: {"id": "HP:0002664", "name": "Neoplasm", ...}
```

**In Frontend:**
```javascript
// Show disease phenotypes
const phenotypes = await getDiseasePhenotypes("Breast Cancer");
// Display symptoms and clinical features
```

### Download Behavior

**First Request:**
1. Backend checks if `hp.json` exists
2. If not, downloads from hpo.jax.org (~30 seconds)
3. Saves to `data/datasets/hpo/hp.json`
4. Loads into memory (fast subsequent requests)

**Subsequent Requests:**
1. Loads from cache (instant)

### Update Schedule

**Frequency:** Monthly (aligned with HPO releases)

**Manual Update:**
```bash
# Download new version
curl https://hpo.jax.org/app/data/json/hp.json > data/datasets/hpo/hp.json

# Or set environment variable
export HPO_JSON_PATH=/custom/path/hp.json
```

### API Endpoints Using HPO
- `POST /api/phenotypes` — Get phenotypes for disease

---

## 3️⃣ Reference Genomes (Future)

### Location
```
data/datasets/reference/
```

### Planned Files

#### GRCh38.fa (Human Reference Genome)
- **Size:** 3.2 GB
- **Format:** FASTA
- **Content:** Complete human genome sequence
- **Source:** ftp://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/
- **Purpose:** Sequence alignment, variant verification

#### refseq_proteins.faa (Protein Sequences)
- **Size:** 1.5 GB
- **Format:** FASTA
- **Content:** All RefSeq proteins
- **Source:** NCBI RefSeq
- **Purpose:** Protein annotation

#### gene_annotations.gff3 (Gene Coordinates)
- **Size:** 500 MB
- **Format:** GFF3
- **Content:** Gene positions, exons, features
- **Source:** Ensembl/GENCODE
- **Purpose:** Gene mapping

### When to Add
- After implementing sequence alignment features
- When cross-species validation needed
- For variant verification against reference

---

## 4️⃣ ClinVar Database (Future)

### Location
```
data/datasets/clinvar/
```

### Planned Files

#### clinvar_GRCh38.vcf (Clinical Variants)
- **Size:** 500 MB
- **Format:** VCF (Variant Call Format)
- **Rows:** 1.4 million variants
- **Content:** Known clinical variants with interpretations
- **Source:** ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/
- **Purpose:** Ground truth for training/validation

#### disease_mappings.tsv (Variant-Disease Links)
- **Size:** 100 MB
- **Format:** TSV
- **Content:** Variant → Disease associations
- **Purpose:** Clinical significance mapping

### When to Add
- Phase 3: ML model training
- For benchmarking against ground truth
- For pathogenicity prediction validation

### Example Usage (Future)
```python
# Train ML model on ClinVar variants
from app.services.ml_pathogenicity_service import train_classifier

pathogenic_variants = load_clinvar_pathogenic()
benign_variants = load_clinvar_benign()
classifier = train_classifier(pathogenic_variants, benign_variants)
```

---

## 📊 Dataset Comparison

| Aspect | ChEMBL | HPO | Reference | ClinVar |
|--------|--------|-----|-----------|---------|
| **Size** | 5 MB | 50 MB | 3.2 GB | 500 MB |
| **Format** | CSV | JSON | FASTA | VCF |
| **Rows** | 1.8M | 16K | ~3B bp | 1.4M |
| **Status** | ✅ Ready | ✅ Ready | ⏳ Future | ⏳ Future |
| **Local/Remote** | Local | Hybrid | Local | Local |
| **Update Freq** | Monthly | Monthly | Annual | Daily |
| **License** | CC BY 4.0 | CC BY 4.0 | Public | Public |

---

## 🔄 Data Loading Flow

### Application Startup
```
1. User visits http://localhost:5173
2. Frontend loads (React)
3. User enters variant or drug name
4. Request sent to backend
5. Backend routes to appropriate service
   ├─ ChEMBL service loads CSV (if not cached)
   ├─ HPO service downloads/loads JSON
   ├─ VEP service calls Ensembl API
   └─ Other services load as needed
6. Results returned to frontend
7. UI displays results
```

### Data Caching Strategy

**ChEMBL (CSV):**
- Loaded into memory on first request
- Stays in memory for session
- Re-loaded if file changes

**HPO (JSON):**
- Downloaded on first request (~30 sec)
- Cached at `data/datasets/hpo/hp.json`
- Loaded from cache on subsequent requests

**External APIs:**
- Called each time (no local cache)
- Some implement their own caching

---

## 💾 Storage & Management

### Disk Usage

| Dataset | Size | Notes |
|---------|------|-------|
| ChEMBL | 5 MB | Manageable, always keep |
| HPO | 50 MB | Auto-downloaded, can delete & re-download |
| Cache | ~10 MB | Safe to delete anytime |
| **Total** | **~65 MB** | Very reasonable |

### Cleanup

**If disk space needed:**
```bash
# Delete HPO cache (will re-download)
rm data/datasets/hpo/hp.json

# Delete temporary cache
rm -rf data/cache/*

# Keep ChEMBL (local dataset)
```

### Backup

**To backup datasets:**
```bash
tar -czf genvarx_datasets.tar.gz data/datasets/
```

**To restore:**
```bash
tar -xzf genvarx_datasets.tar.gz
```

---

## 🔐 Security & Privacy

### Data Handling
- ✅ All data is public/research data
- ✅ No personal health information stored locally
- ✅ No authentication required for datasets
- ✅ All external APIs use HTTPS

### Credentials
- No API keys needed for ChEMBL
- No API keys needed for HPO
- Some external APIs (Ensembl, GWAS) are free/public
- Consider API rate limiting for production

---

## 📝 Adding New Datasets

### Step 1: Create Directory
```bash
mkdir -p data/datasets/my_dataset/
```

### Step 2: Add Data File
```bash
cp my_data.csv data/datasets/my_dataset/
```

### Step 3: Create Service
```python
# app/services/my_dataset_service.py
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parent.parent.parent / \
               "data" / "datasets" / "my_dataset" / "my_data.csv"

async def load_my_data():
    # Load and process CSV
    pass
```

### Step 4: Add Endpoint
```python
# In app/main.py
from app.services.my_dataset_service import load_my_data

@app.get("/api/my_data")
async def get_my_data():
    data = await load_my_data()
    return data
```

### Step 5: Document
```bash
# Update data/README.md with new dataset details
```

---

## 🐛 Troubleshooting

### "ChEMBL dataset not found"
**Solution:** Check file exists
```bash
ls -lh data/datasets/chembl/chembl_compounds.csv
```

### "HPO download timeout"
**Solution:** Manual download
```bash
curl -o data/datasets/hpo/hp.json \
  https://hpo.jax.org/app/data/json/hp.json
```

### "CSV parsing error"
**Solution:** Verify delimiter
```bash
head -1 data/datasets/chembl/chembl_compounds.csv
# Should show semicolon-separated values
```

### "Out of disk space"
**Solutions:**
1. Delete HPO cache: `rm data/datasets/hpo/hp.json`
2. Clear temporary cache: `rm -rf data/cache/*`
3. Delete unused datasets

---

## 📚 References

### ChEMBL
- Website: https://www.ebi.ac.uk/chembl/
- Download: https://www.ebi.ac.uk/chembl/downloads
- Citation: Gaulton et al. 2017
- License: CC BY 4.0

### HPO
- Website: https://hpo.jax.org/
- Download: https://hpo.jax.org/app/data/json/hp.json
- Citation: Robinson et al. 2019
- License: CC BY 4.0

### Reference Genomes
- NCBI: https://www.ncbi.nlm.nih.gov/grc/human/
- Ensembl: https://www.ensembl.org/
- License: Public domain

### ClinVar
- Website: https://www.ncbi.nlm.nih.gov/clinvar/
- Download: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/
- License: Public domain

---

## ✅ Dataset Checklist

- [x] ChEMBL organized at `data/datasets/chembl/`
- [x] HPO configured to use `data/datasets/hpo/`
- [x] Service paths updated
- [x] Documentation created
- [x] Future datasets planned
- [x] Backup/restore strategy documented
- [x] Troubleshooting guide created

---

## 🎯 Next Steps

1. **Verify datasets exist:**
   ```bash
   ls -la data/datasets/chembl/
   ```

2. **Run backend to test:**
   ```bash
   uvicorn app.main:app --port 8000 --reload
   ```

3. **Test ChEMBL endpoint:**
   ```bash
   curl http://localhost:8000/api/compounds?query=selinexor
   ```

4. **Test HPO (auto-downloads):**
   ```bash
   curl -X POST http://localhost:8000/api/phenotypes \
     -H "Content-Type: application/json" \
     -d '{"variant":"Breast Cancer"}'
   ```

---

**Version:** 1.0
**Last Updated:** August 2026
**Status:** ✅ Organized & Ready
