# ⚡ Quick Dataset Setup (5-Minute Guide)

Fast reference for adding datasets. Skip the docs, get coding!

---

## 🚀 TL;DR: 3 Steps to Add ClinVar

### **Step 1: Download**
```bash
mkdir -p data/datasets/clinvar/
wget -O data/datasets/clinvar/clinvar_summary.tsv \
  ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt
```

### **Step 2: Create Service**
Save as `app/services/clinvar_local_service.py`:
```python
import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent.parent / \
           "data/datasets/clinvar/clinvar_summary.tsv"

_cache = {}

async def search_by_gene(gene: str):
    if not _cache:
        with open(CSV_PATH) as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                g = row.get('GeneSymbol', '').upper()
                if g not in _cache:
                    _cache[g] = []
                _cache[g].append(row)
    return _cache.get(gene.upper(), [])
```

### **Step 3: Add Endpoint**
In `app/main.py`:
```python
from app.services.clinvar_local_service import search_by_gene

@app.get("/api/clinvar/gene/{gene}")
async def clinvar_gene(gene: str):
    results = await search_by_gene(gene)
    return {"gene": gene, "variants": results}
```

### **Test:**
```bash
curl http://localhost:8000/api/clinvar/gene/BRCA1
```

Done! ✅

---

## 📋 All Datasets - Quick Links

| Dataset | Download | Size | Setup Time |
|---------|----------|------|-----------|
| **OMIM** | https://www.omim.org/downloads | 20 MB | 5 min |
| **ClinVar** | ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/ | 500 MB | 5 min |
| **DrugBank** | https://go.drugbank.com/ | 300 MB | 5 min |
| **DisGeNET** | https://www.disgenet.org/ | 500 MB | 5 min |
| **GWAS** | https://www.ebi.ac.uk/gwas/downloads | 50 MB | 5 min |

---

## 🎯 Common Patterns

### **Pattern 1: CSV Search by Field**
```python
# For any CSV dataset

async def search_csv(csv_path, search_field, query_value):
    results = []
    with open(csv_path) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            if query_value.lower() in row.get(search_field, '').lower():
                results.append(row)
    return results
```

### **Pattern 2: Indexed Cache (Fast)**
```python
# Build index on load
_index = {}

async def ensure_loaded():
    with open(csv_path) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            key = row.get('primary_key')
            _index[key] = row

async def get_by_key(key):
    return _index.get(key)
```

### **Pattern 3: Multi-field Index**
```python
# Index by multiple fields for fast lookups

_by_gene = {}
_by_disease = {}

async def load():
    with open(csv_path) as f:
        for row in csv.DictReader(f, delimiter='\t'):
            gene = row.get('Gene')
            disease = row.get('Disease')
            
            if gene not in _by_gene:
                _by_gene[gene] = []
            _by_gene[gene].append(row)
            
            if disease not in _by_disease:
                _by_disease[disease] = []
            _by_disease[disease].append(row)
```

---

## 📥 Download Commands

Copy-paste ready!

### **OMIM**
```bash
mkdir -p data/datasets/omim/
# Visit https://www.omim.org/downloads and download manually
# Or use API if available
```

### **ClinVar**
```bash
mkdir -p data/datasets/clinvar/
wget -O data/datasets/clinvar/clinvar_summary.tsv \
  ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt
```

### **DrugBank**
```bash
mkdir -p data/datasets/drugbank/
# Visit https://go.drugbank.com/downloads
# Download CSV files manually (requires free account)
```

### **DisGeNET**
```bash
mkdir -p data/datasets/disgenet/
wget -O data/datasets/disgenet/diseases.tsv.gz \
  https://www.disgenet.org/downloads/disease_mappings.tsv.gz
gunzip data/datasets/disgenet/diseases.tsv.gz
```

### **GWAS Catalog**
```bash
mkdir -p data/datasets/gwas/
wget -O data/datasets/gwas/associations.tsv \
  https://www.ebi.ac.uk/gwas/api/search/downloads/full
```

---

## 🔌 Quick Endpoint Templates

### **Simple Search**
```python
@app.get("/api/{dataset}/search")
async def search(q: str):
    results = await search_dataset(q)
    return {"query": q, "results": results}
```

### **Get by ID**
```python
@app.get("/api/{dataset}/{id}")
async def get_by_id(id: str):
    result = await fetch_by_id(id)
    return result or {"error": "Not found"}
```

### **Advanced Filter**
```python
@app.get("/api/{dataset}/filter")
async def filter_data(field: str, value: str):
    results = await filter_by_field(field, value)
    return {"field": field, "value": value, "results": results}
```

---

## ✅ Minimal Service Template

Copy this for any dataset:

```python
# app/services/[dataset]_service.py

import csv
from pathlib import Path
from typing import List, Dict

PATH = Path(__file__).resolve().parent.parent.parent / \
       "data/datasets/[dataset]/[filename].tsv"

_loaded = False
_data: Dict = {}

async def load():
    global _loaded, _data
    if _loaded:
        return
    with open(PATH) as f:
        for row in csv.DictReader(f, delimiter='\t'):
            key = row.get('PRIMARY_KEY_COLUMN')
            _data[key] = row
    _loaded = True

async def search(query: str) -> List[Dict]:
    await load()
    return [v for v in _data.values() 
            if query.lower() in str(v).lower()]

async def get(key: str) -> Dict:
    await load()
    return _data.get(key, {})
```

---

## 📡 Minimal API Template

```python
# In app/main.py

from app.services.[dataset]_service import search, get

@app.get("/api/[dataset]/search")
async def dataset_search(q: str):
    results = await search(q)
    return {"query": q, "count": len(results), "results": results}

@app.get("/api/[dataset]/{id}")
async def dataset_get(id: str):
    result = await get(id)
    return result
```

---

## 🧪 Test Script

```bash
#!/bin/bash
# test_dataset.sh [DATASET_NAME] [TEST_QUERY]

DATASET=$1
QUERY=$2

echo "Testing $DATASET with query: $QUERY"

# Check file exists
if [ ! -d "data/datasets/$DATASET/" ]; then
    echo "❌ Dataset directory not found"
    exit 1
fi

echo "✅ Directory exists"

# Check files
FILES=$(ls data/datasets/$DATASET/ | wc -l)
echo "✅ Found $FILES files"

# Test API
RESPONSE=$(curl -s "http://localhost:8000/api/$DATASET/search?q=$QUERY")
if echo "$RESPONSE" | grep -q "results"; then
    echo "✅ API working"
else
    echo "❌ API error"
fi
```

---

## 📊 Dataset Format Reference

### **TSV/CSV**
```python
import csv
with open(path) as f:
    reader = csv.DictReader(f, delimiter='\t')  # or delimiter=','
    for row in reader:
        print(row['ColumnName'])
```

### **JSON**
```python
import json
with open(path) as f:
    data = json.load(f)
    # or for JSON lines:
    # for line in f:
    #     data = json.loads(line)
```

### **VCF**
```python
# Install: pip install pyvcf
import vcf
vcf_reader = vcf.Reader(filename=path)
for record in vcf_reader:
    print(record.CHROM, record.POS, record.REF)
```

### **GFF/GTF**
```python
# GTF is TSV-like
import csv
with open(path) as f:
    reader = csv.DictReader(f, delimiter='\t', comment='#',
                            fieldnames=['seqname','source','feature','start','end','score','strand','frame','attribute'])
    for row in reader:
        print(row)
```

---

## ⚡ Performance Tips

### **Slow loading?**
```python
# Add progress indicator
count = 0
with open(path) as f:
    for row in csv.DictReader(f):
        count += 1
        if count % 100000 == 0:
            print(f"Loaded {count:,}...")
```

### **Out of memory?**
```python
# Load on demand instead of all at once
async def search(query):
    with open(path) as f:  # Open fresh each time
        for row in csv.DictReader(f):
            if query in str(row):
                yield row
```

### **Slow search?**
```python
# Index by search field
index = {}
with open(path) as f:
    for row in csv.DictReader(f):
        key = row['GeneSymbol'].upper()
        if key not in index:
            index[key] = []
        index[key].append(row)

# Fast lookup
result = index.get('BRCA1', [])
```

---

## 🐛 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError` | Path wrong | Check directory exists: `ls data/datasets/` |
| `KeyError` | Column name wrong | Check column names: `head -1 file.tsv` |
| `MemoryError` | File too large | Use lazy loading or index only |
| `UnicodeDecodeError` | Encoding issue | Add `encoding='utf-8', errors='ignore'` |
| `503 Timeout` | Download too slow | Use `timeout` parameter: `wget --timeout=30` |

---

## 🎯 Next: Add Multiple Datasets

After first dataset, adding more is even faster!

```bash
# Download all at once
for dataset in omim clinvar disgenet gwas; do
  mkdir -p data/datasets/$dataset/
  # Add specific download commands
done
```

---

## 📞 Need Help?

1. **Read:** Full guide in `docs/ADDITIONAL_DATASETS.md`
2. **Follow:** Template in `docs/DATASET_IMPLEMENTATION_TEMPLATE.md`
3. **Copy:** Service from `app/services/chembl_local_service.py`
4. **Test:** With curl or Postman

---

**Ready?** Start with ClinVar, DrugBank, or OMIM. Takes 5 minutes!
