# Data Directory Structure

This directory contains all datasets, caches, and reference files for GenVarX.

## Directory Organization

```
data/
├── datasets/              # Main datasets for the project
│   ├── chembl/           # ChEMBL compound database
│   ├── reference/        # Reference genomes and sequences
│   ├── hpo/              # Human Phenotype Ontology
│   └── clinvar/          # ClinVar clinical variants (future)
├── cache/                # Temporary cached files
└── README.md            # This file
```

---

## Datasets

### 1. ChEMBL Dataset
**Location:** `data/datasets/chembl/`

**File:** `chembl_compounds.csv`
- **Size:** ~5 MB
- **Format:** CSV (semicolon-delimited)
- **Columns:** 
  - Compound ChEMBL ID
  - Name
  - Type
  - Max Phase
  - Molecular Weight
  - AlogP
  - QED Weighted
  - Targets
  - Bioactivities
  - And 20+ more fields
- **Purpose:** Drug discovery module - searching for compounds by name/ID
- **Update Frequency:** Monthly (from ChEMBL)
- **Source:** https://www.ebi.ac.uk/chembl/

**How to use in code:**
```python
from app.services.chembl_local_service import search_compounds, get_compound

# Search by name
results = await search_compounds("selinexor", limit=20)

# Get specific compound
compound = await get_compound("CHEMBL237500")
```

---

### 2. HPO (Human Phenotype Ontology)
**Location:** `data/datasets/hpo/`

**File:** `hp.json` (auto-downloaded on first use)
- **Size:** ~50 MB
- **Format:** JSON (OBO graph format)
- **Content:**
  - Disease names
  - Phenotype terms
  - Symptoms and clinical features
  - Hierarchical relationships
- **Purpose:** Phenotype-driven variant prioritization
- **Update Frequency:** Monthly
- **Source:** https://hpo.jax.org/app/data/json/hp.json

**How it works:**
- Automatically downloads on first request
- Cached locally to avoid repeated downloads
- Maps diseases → clinical phenotypes

**How to use in code:**
```python
from app.services.hpo_service import fetch_phenotypes_for_disease

phenotypes = await fetch_phenotypes_for_disease("Breast Cancer")
```

---

### 3. Reference Genomes (Future)
**Location:** `data/datasets/reference/`

**Expected files:**
- `GRCh38.fa` — Human reference genome (FASTA format)
- `refseq_proteins.faa` — RefSeq protein sequences
- `gene_annotations.gff3` — Gene coordinates and annotations

**Status:** Not yet implemented - for future sequence alignment features

---

### 4. ClinVar Clinical Database (Future)
**Location:** `data/datasets/clinvar/`

**Expected files:**
- `clinvar_GRCh38.vcf` — Clinical variant annotations
- `clinvar_disease_mappings.tsv` — Variant-to-disease links

**Status:** Currently accessed via external API (myvariant.info)
**Future:** Will add local copy for faster queries

---

## Cache Directory

**Location:** `data/cache/`

**Purpose:** Store temporary downloaded/processed files
- HPO JSON (initial download)
- API response caches
- Intermediate processing results

**Contents are auto-managed** — you can safely delete cache files

---

## Environment Variables

To use custom dataset paths, set these environment variables:

```bash
# Use custom ChEMBL file
export CHEMBL_CSV_PATH=/path/to/custom/compounds.csv

# Use custom HPO file
export HPO_JSON_PATH=/path/to/custom/hp.json
```

---

## Dataset Statistics

| Dataset | Size | Rows | Columns | Format |
|---------|------|------|---------|--------|
| ChEMBL Compounds | 5 MB | 1.8M | 30+ | CSV |
| HPO Ontology | 50 MB | 16K terms | JSON | JSON |
| Reference Genome | 3.2 GB | - | FASTA | FASTA |
| ClinVar (full) | 500 MB | 1.4M variants | VCF | VCF |

---

## Adding New Datasets

### Step 1: Create Directory
```bash
mkdir -p data/datasets/your_dataset/
```

### Step 2: Add Dataset File
```bash
cp your_data.csv data/datasets/your_dataset/
```

### Step 3: Create Data Service
```python
# app/services/your_service.py
import csv
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "datasets" / "your_dataset" / "your_data.csv"

async def load_your_data():
    # Load and process CSV
    pass
```

### Step 4: Update `.env` if needed
```
YOUR_DATASET_PATH=data/datasets/your_dataset/your_data.csv
```

---

## Data Quality Notes

### ChEMBL
- ✅ Curated by EMBL-EBI
- ✅ Regularly updated
- ✅ Semi-colon delimited (important!)
- ⚠️ Some fields may be empty

### HPO
- ✅ Official from JAX
- ✅ Monthly updates
- ⚠️ Large file (50 MB) — first download takes ~30 seconds
- ✅ Auto-cached after first use

### Reference Genomes
- ✅ From NCBI/Ensembl
- ✅ GRCh38 (human reference)
- ⚠️ Very large (3.2 GB) — not included by default
- Download only if needed for alignment tasks

---

## Troubleshooting

### "ChEMBL dataset not found"
**Solution:** Ensure `data/datasets/chembl/chembl_compounds.csv` exists

### "HPO download timeout"
**Solution:** HPO file is 50 MB, may take 30+ seconds
- Increase timeout in `app/services/hpo_service.py`
- Or manually download from https://hpo.jax.org/app/data/json/hp.json

### Out of disk space?
**Solutions:**
1. Delete cache: `rm -rf data/cache/*`
2. Remove unused datasets
3. Move reference genomes to external drive

---

## API Integration

All datasets are automatically loaded and cached by their respective services:

| Service | Dataset | Auto-Load | Cache |
|---------|---------|-----------|-------|
| `chembl_local_service.py` | ChEMBL CSV | ✅ Yes | ✅ Memory |
| `hpo_service.py` | HPO JSON | ✅ Yes | ✅ File |
| `vep_service.py` | Ensembl API | ❌ External | ✅ None |
| `clinvar_service.py` | MyVariant API | ❌ External | ✅ None |

---

## Contributing New Data

To add new datasets:

1. **Create directory:** `data/datasets/your_data/`
2. **Add dataset file** and documentation
3. **Create service:** `app/services/your_data_service.py`
4. **Add endpoint:** Update `app/main.py`
5. **Test:** Verify it works

Example: See `app/services/chembl_local_service.py` for reference

---

## License & Attribution

### ChEMBL
- **License:** Creative Commons Attribution 4.0
- **Citation:** Gaulton et al. 2017
- **Download:** https://www.ebi.ac.uk/chembl/downloads

### HPO
- **License:** Creative Commons Attribution 4.0
- **Citation:** Robinson et al. 2019
- **Download:** https://hpo.jax.org

### Reference Genomes
- **License:** Public domain (NCBI)
- **Source:** https://www.ncbi.nlm.nih.gov/grc/human/

---

## Maintenance

### Regular Updates
- ChEMBL: Monthly (1st of month)
- HPO: Monthly
- Reference genomes: Annually (GRCh38, GRCh39)

### Backup Strategy
```bash
# Backup datasets
tar -czf genvarx_datasets_backup.tar.gz data/datasets/

# Restore from backup
tar -xzf genvarx_datasets_backup.tar.gz
```

---

## Support

For dataset issues:
- **ChEMBL:** https://www.ebi.ac.uk/support/chembl
- **HPO:** https://github.com/obophenotype/human-phenotype-ontology/issues
- **GenVarX:** See PROJECT_ROADMAP.md

---

**Last Updated:** August 2026
**Structure Version:** 1.0
