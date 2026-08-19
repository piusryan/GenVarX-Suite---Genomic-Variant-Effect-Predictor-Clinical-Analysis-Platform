# 🛠️ Dataset Implementation Template

Step-by-step guide to add a new dataset to GenVarX. Use this as a template for all datasets.

---

## 📋 Overview

This guide shows how to add **any new dataset** following the GenVarX pattern. We'll use **ClinVar** as an example, but the process is identical for OMIM, DrugBank, DisGeNET, etc.

---

## 🎯 What We're Building

**Goal:** Add ClinVar variants so users can query:
```
"What's the clinical significance of this variant?"
"Are there similar variants with known pathogenicity?"
"What diseases are associated with this mutation?"
```

---

## 📂 Step 1: Create Directory Structure

```bash
# Create the dataset directory
mkdir -p data/datasets/clinvar/

# Create subdirectory for documentation
mkdir -p docs/data_sources/clinvar/

# Verify structure
ls -la data/datasets/clinvar/
```

**Expected structure:**
```
data/datasets/clinvar/
├── clinvar_summary.tsv           # Main dataset (download)
├── variant_disease_associations.tsv  # Relationships
├── clinvar_GRCh38.vcf            # Full VCF (optional)
└── README.md                      # Dataset notes
```

---

## 📥 Step 2: Download Dataset

### **Option A: Command Line (Recommended)**

```bash
# Create dataset directory
mkdir -p data/datasets/clinvar/

# Download ClinVar summary (tab-delimited)
wget -O data/datasets/clinvar/clinvar_summary.tsv \
  ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt

# Download variant-disease associations
wget -O data/datasets/clinvar/variant_disease_associations.tsv \
  ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_disease.txt

# Verify download
ls -lh data/datasets/clinvar/
```

### **Option B: Using Python**

```python
# download_clinvar.py
import urllib.request
import gzip

urls = {
    'summary': 'ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz',
    'disease': 'ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_disease.txt.gz'
}

for name, url in urls.items():
    print(f"Downloading {name}...")
    filename = f"data/datasets/clinvar/clinvar_{name}.tsv.gz"
    urllib.request.urlretrieve(url, filename)
    
    # Decompress
    with gzip.open(filename, 'rb') as f_in:
        with open(filename[:-3], 'wb') as f_out:
            f_out.writelines(f_in)
    
    print(f"✅ Downloaded and decompressed {name}")
```

### **Option C: Manual Download**

1. Go to: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/
2. Download `variant_summary.txt.gz`
3. Decompress and save to `data/datasets/clinvar/clinvar_summary.tsv`
4. Move file to correct location

---

## 📊 Step 3: Explore Dataset Structure

```bash
# Check first few lines
head -20 data/datasets/clinvar/clinvar_summary.tsv

# Check column names
head -1 data/datasets/clinvar/clinvar_summary.tsv | tr '\t' '\n' | nl

# Get row count
wc -l data/datasets/clinvar/clinvar_summary.tsv

# Check file size
du -h data/datasets/clinvar/clinvar_summary.tsv
```

**Expected output:**
```
1    #VariationID
2    Type
3    Locations
4    VariationName
5    GeneSymbol
6    GeneID
7    HGNC_ID
8    ReviewStatus
9    ClinicalSignificance
10   LastEvaluated
11   Number_submitters
12   Guidelines
13   ReferenceClinVarAssertion
14   PhenotypeList
15   Disease
16   ...
```

---

## 🐍 Step 4: Create Service File

**File:** `app/services/clinvar_local_service.py`

```python
"""
ClinVar local dataset integration.
Searches clinical variant database for pathogenicity and disease associations.
"""

import csv
import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

# Path to ClinVar dataset
CLINVAR_TSV = Path(__file__).resolve().parent.parent.parent / \
              "data/datasets/clinvar/clinvar_summary.tsv"

# In-memory cache
_cache_loaded = False
_variants_by_id: Dict[str, Dict] = {}
_variants_by_gene: Dict[str, List[Dict]] = {}
_load_error: Optional[str] = None


async def search_clinvar_by_variant(variant_id: str) -> List[Dict]:
    """
    Search ClinVar by variation ID.
    
    Args:
        variant_id: e.g., "12345" or "NM_000038.6:c.100C>T"
    
    Returns:
        List of matching variants with clinical data
    """
    await _ensure_loaded()
    if _load_error:
        return []
    
    results = []
    search_str = str(variant_id).lower()
    
    # Search in-memory cache
    for vid, variant_data in _variants_by_id.items():
        if search_str in vid.lower():
            results.append(variant_data)
    
    return results[:50]  # Limit results


async def search_clinvar_by_gene(gene_symbol: str) -> List[Dict]:
    """
    Get all ClinVar variants for a specific gene.
    
    Args:
        gene_symbol: e.g., "BRCA1", "TP53"
    
    Returns:
        List of variants for that gene
    """
    await _ensure_loaded()
    if _load_error:
        return []
    
    gene_upper = gene_symbol.upper()
    return _variants_by_gene.get(gene_upper, [])[:100]


async def get_variant_pathogenicity(variant_id: str) -> Optional[Dict]:
    """
    Get detailed clinical significance for a variant.
    
    Args:
        variant_id: Variation ID from ClinVar
    
    Returns:
        Dictionary with clinical data or None if not found
    """
    await _ensure_loaded()
    if _load_error:
        return None
    
    return _variants_by_id.get(str(variant_id).upper())


async def get_disease_variants(disease_name: str) -> List[Dict]:
    """
    Get all variants associated with a disease.
    
    Args:
        disease_name: e.g., "Breast Cancer", "Hereditary Hemochromatosis"
    
    Returns:
        List of variants for that disease
    """
    await _ensure_loaded()
    if _load_error:
        return []
    
    results = []
    search_str = disease_name.lower()
    
    for variant_data in _variants_by_id.values():
        phenotypes = variant_data.get('phenotypes', '').lower()
        if search_str in phenotypes:
            results.append(variant_data)
    
    return results[:100]


async def _ensure_loaded() -> None:
    """Load ClinVar dataset from CSV into memory."""
    global _cache_loaded, _load_error, _variants_by_id, _variants_by_gene
    
    if _cache_loaded:
        return
    
    # Check if file exists
    if not CLINVAR_TSV.exists():
        _load_error = (
            f"ClinVar dataset not found at: {CLINVAR_TSV}\n"
            "Download from: ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/\n"
            "Place 'clinvar_summary.tsv' in data/datasets/clinvar/"
        )
        _cache_loaded = True
        return
    
    try:
        print("Loading ClinVar dataset... (this may take a moment)")
        
        with open(CLINVAR_TSV, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            count = 0
            for row in reader:
                count += 1
                if count % 100000 == 0:
                    print(f"  Loaded {count:,} variants...")
                
                variant_id = row.get('#VariationID', '').strip()
                if not variant_id:
                    continue
                
                # Extract key fields
                variant_data = {
                    'variation_id': variant_id,
                    'type': row.get('Type', 'Unknown'),
                    'gene_symbol': row.get('GeneSymbol', 'Unknown'),
                    'clinical_significance': row.get('ClinicalSignificance', 'Unknown'),
                    'review_status': row.get('ReviewStatus', 'Unknown'),
                    'phenotypes': row.get('PhenotypeList', ''),
                    'disease': row.get('Disease', ''),
                    'variant_name': row.get('VariationName', ''),
                    'last_evaluated': row.get('LastEvaluated', ''),
                    'number_submitters': row.get('Number_submitters', ''),
                }
                
                # Index by variation ID
                _variants_by_id[variant_id] = variant_data
                
                # Index by gene symbol
                gene_symbol = variant_data['gene_symbol'].upper()
                if gene_symbol not in _variants_by_gene:
                    _variants_by_gene[gene_symbol] = []
                _variants_by_gene[gene_symbol].append(variant_data)
        
        print(f"✅ ClinVar loaded: {count:,} variants indexed")
        _cache_loaded = True
        
    except Exception as e:
        _load_error = f"Failed to load ClinVar: {str(e)}"
        _cache_loaded = True
```

---

## 🔌 Step 5: Add API Endpoints

**File:** `app/main.py` (Add these endpoints)

```python
from app.services.clinvar_local_service import (
    search_clinvar_by_variant,
    search_clinvar_by_gene,
    get_disease_variants,
    get_variant_pathogenicity
)

# ... existing imports ...

@app.get("/api/clinvar/variant/{variant_id}")
async def clinvar_variant(variant_id: str):
    """Get ClinVar data for a specific variant."""
    try:
        data = await search_clinvar_by_variant(variant_id)
        if not data:
            return {"error": "Variant not found in ClinVar"}
        return {
            "variant_id": variant_id,
            "matches": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clinvar/gene/{gene_symbol}")
async def clinvar_gene(gene_symbol: str):
    """Get all ClinVar variants for a gene."""
    try:
        variants = await search_clinvar_by_gene(gene_symbol)
        return {
            "gene": gene_symbol,
            "variants": variants,
            "count": len(variants)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clinvar/disease/{disease_name}")
async def clinvar_disease(disease_name: str):
    """Get all variants associated with a disease."""
    try:
        variants = await get_disease_variants(disease_name)
        return {
            "disease": disease_name,
            "variants": variants,
            "count": len(variants)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📝 Step 6: Create Frontend Service

**File:** `src/services/api.js` (Add or update)

```javascript
// Add ClinVar search functions

export const searchClinVarVariant = async (variantId) => {
  const response = await fetch(
    `${API_BASE_URL}/api/clinvar/variant/${variantId}`
  );
  if (!response.ok) throw new Error('ClinVar search failed');
  return response.json();
};

export const searchClinVarGene = async (geneSymbol) => {
  const response = await fetch(
    `${API_BASE_URL}/api/clinvar/gene/${geneSymbol}`
  );
  if (!response.ok) throw new Error('ClinVar gene search failed');
  return response.json();
};

export const searchClinVarDisease = async (diseaseName) => {
  const response = await fetch(
    `${API_BASE_URL}/api/clinvar/disease/${diseaseName}`
  );
  if (!response.ok) throw new Error('ClinVar disease search failed');
  return response.json();
};
```

---

## 🧪 Step 7: Test the Service

### **Test 1: Service Loading**
```bash
# Start backend
uvicorn app.main:app --port 8000 --reload

# In another terminal, test the endpoint
curl http://localhost:8000/api/clinvar/gene/BRCA1
```

**Expected response:**
```json
{
  "gene": "BRCA1",
  "variants": [
    {
      "variation_id": "12345",
      "clinical_significance": "Pathogenic",
      "phenotypes": "Breast Cancer, Ovarian Cancer",
      "review_status": "reviewed by expert panel"
    },
    ...
  ],
  "count": 247
}
```

### **Test 2: Variant Lookup**
```bash
curl http://localhost:8000/api/clinvar/disease/Breast%20Cancer
```

### **Test 3: Error Handling**
```bash
curl http://localhost:8000/api/clinvar/gene/NONEXISTENT_GENE

# Should return empty results gracefully
```

---

## 📚 Step 8: Document Your Dataset

**File:** `data/datasets/clinvar/README.md`

```markdown
# ClinVar Dataset

## Overview
- **Rows:** 1.4+ million variants
- **Size:** ~500 MB
- **Format:** TSV
- **Source:** https://www.ncbi.nlm.nih.gov/clinvar/

## Files
- `clinvar_summary.tsv` - Main dataset
- `variant_disease_associations.tsv` - Disease links

## Key Columns
- `#VariationID` - Unique identifier
- `GeneSymbol` - Associated gene
- `ClinicalSignificance` - Pathogenic/Benign/Uncertain
- `ReviewStatus` - Expert review status
- `PhenotypeList` - Associated diseases
- `Disease` - Disease name

## Update Frequency
- Daily

## License
- Public domain

## Last Updated
- August 2026
```

---

## 🚀 Step 9: Add to Requirements

**File:** `requirements.txt` (if needed)

Most datasets only need standard Python libraries:
- `csv` (built-in)
- `json` (built-in)
- `pathlib` (built-in)

If you need special formats:
```txt
# For VCF files
pyvcf>=0.6.8

# For large files
pandas>=1.3.0

# For compression
gzip (built-in)
```

---

## ✅ Step 10: Integration Checklist

- [ ] Dataset directory created
- [ ] Data downloaded and verified
- [ ] Service file created (`clinvar_local_service.py`)
- [ ] API endpoints added to `main.py`
- [ ] Frontend service updated
- [ ] Tests pass
- [ ] Documentation written
- [ ] README added to dataset folder
- [ ] No errors in logs
- [ ] Performance acceptable (check loading time)

---

## 🔍 Verification Script

```bash
#!/bin/bash
# verify_dataset.sh

echo "Verifying ClinVar dataset..."

# 1. Check file exists
if [ -f "data/datasets/clinvar/clinvar_summary.tsv" ]; then
    echo "✅ File exists"
else
    echo "❌ File missing"
    exit 1
fi

# 2. Check file size
SIZE=$(du -h data/datasets/clinvar/clinvar_summary.tsv | cut -f1)
echo "✅ File size: $SIZE"

# 3. Check row count
ROWS=$(wc -l < data/datasets/clinvar/clinvar_summary.tsv)
echo "✅ Rows: $ROWS"

# 4. Check columns
COLS=$(head -1 data/datasets/clinvar/clinvar_summary.tsv | tr '\t' '\n' | wc -l)
echo "✅ Columns: $COLS"

# 5. Test backend endpoint
echo "Testing API endpoint..."
RESPONSE=$(curl -s http://localhost:8000/api/clinvar/gene/BRCA1)
if echo "$RESPONSE" | grep -q "variants"; then
    echo "✅ API working"
else
    echo "❌ API not responding"
fi

echo "✅ All checks passed!"
```

---

## 📊 Performance Tuning

If dataset is large (>1GB), consider:

### **Option 1: Lazy Loading**
```python
# Load only when needed, not on startup
if not _cache_loaded:
    await _ensure_loaded()  # Load on first request
```

### **Option 2: Indexed Search**
```python
# Use indexed dictionaries (already done above)
_variants_by_gene[gene] = [variants...]  # Fast lookup
```

### **Option 3: Database**
```python
# For very large datasets, use PostgreSQL
CREATE INDEX idx_gene ON variants(gene_symbol);
CREATE INDEX idx_disease ON variants(disease);
```

### **Option 4: Pagination**
```python
# Return limited results
async def search_clinvar(query, limit=100, offset=0):
    results = all_results[offset:offset+limit]
    return {"results": results, "total": len(all_results)}
```

---

## 🎓 Learning Path

### For Beginners
1. Follow this template exactly
2. Use ChEMBL or HPO as first dataset (simpler)
3. Test each step before moving forward

### For Intermediate
1. Adapt template for your dataset structure
2. Add custom parsing for unique formats
3. Implement error handling

### For Advanced
1. Add database layer
2. Implement caching strategies
3. Add data validation pipeline
4. Create update automation

---

## 📞 Common Issues & Solutions

### **Issue: "Module not found" error**
```
Solution: Add import to app/main.py
from app.services.clinvar_local_service import search_clinvar_by_gene
```

### **Issue: "File not found" error**
```
Solution: Download dataset to correct path
data/datasets/clinvar/clinvar_summary.tsv
```

### **Issue: "Out of memory" (large datasets)**
```
Solution: Add pagination or lazy loading
Load only requested rows, not entire file
```

### **Issue: "Slow API response"**
```
Solution: Index data on load (already done)
Or use database with indexes
Or add caching layer
```

---

## 🎉 You're Done!

Your new dataset is now integrated! You can:

1. ✅ Search by gene: `/api/clinvar/gene/BRCA1`
2. ✅ Search by disease: `/api/clinvar/disease/Breast%20Cancer`
3. ✅ Lookup variants: `/api/clinvar/variant/12345`
4. ✅ Use in frontend: `searchClinVarGene("BRCA1")`

---

## 🚀 Next: Add More Datasets

Repeat this process for:
- OMIM (disease ontology)
- DrugBank (drug-target database)
- DisGeNET (disease-gene network)
- COSMIC (cancer variants)
- GWAS Catalog (GWAS associations)

Each follows the same pattern!

---

**Status:** Template ready for your use
**Version:** 1.0
**Last Updated:** August 2026
