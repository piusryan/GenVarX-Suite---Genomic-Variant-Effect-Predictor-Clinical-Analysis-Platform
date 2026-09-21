# Disease Search Testing Guide

## Quick Start Testing

### Prerequisites
- Backend running on `http://localhost:8000`
- Python dependencies installed
- Local datasets available in `data/datasets/`

### Test 1: Check if Service Starts

```bash
# Start the backend
python -m uvicorn app.main:app --reload

# Should see:
# Uvicorn running on http://127.0.0.1:8000
# INFO: Started server process
```

### Test 2: Health Check
```bash
curl http://localhost:8000/health

# Expected Response:
# {"status":"online","service":"GenVarX Engine"}
```

## API Testing

### Test 3: List Available Diseases (Autocomplete)

```bash
curl -X GET "http://localhost:8000/api/disease-search/available?limit=50"

# Expected Response:
# {
#   "total_available": 52847,
#   "diseases": [
#     "Hereditary breast and ovarian cancer syndrome",
#     "Type 2 diabetes mellitus",
#     "Cystic fibrosis",
#     ...
#   ],
#   "note": "Diseases from ClinVar disease_names.tsv"
# }
```

### Test 4: Search by Disease (Main Test)

#### Test 4A: Common Disease - Type 2 Diabetes

```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Type 2 diabetes"}'

# Expected Response Structure:
# {
#   "disease_query": "Type 2 diabetes",
#   "results": {
#     "variants": [...],  # Should have results
#     "genes": [...],     # Should have results
#     "phenotypes": [...],# Should have results
#     "drugs": [...],     # May have results
#     "summary": {
#       "total_variants_found": > 0,
#       "total_genes_found": > 0,
#       ...
#     }
#   }
# }
```

#### Test 4B: Rare Disease - Marfan Syndrome

```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Marfan syndrome"}'

# Expected: Some results from ClinVar and HPO
```

#### Test 4C: Cancer - Breast Cancer

```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Breast cancer"}'

# Expected: Many results from multiple sources
```

#### Test 4D: Invalid Disease

```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "NotADiseaseXYZ123"}'

# Expected: Empty results but no error
# {
#   "disease_query": "NotADiseaseXYZ123",
#   "results": {
#     "variants": [],
#     "genes": [],
#     "phenotypes": [],
#     "drugs": [],
#     "summary": {
#       "total_variants_found": 0,
#       ...
#     }
#   }
# }
```

### Test 5: Error Handling

#### Test 5A: Empty Disease Name

```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": ""}'

# Expected: 400 error
# {"detail": "Disease name must be at least 2 characters"}
```

#### Test 5B: Single Character

```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "X"}'

# Expected: 400 error
# {"detail": "Disease name must be at least 2 characters"}
```

## Response Validation Tests

### Test 6: Validate Response Structure

For any disease search, verify the response contains:

```python
response = {
    "disease_query": str,          # Input disease name
    "results": {
        "query": str,              # Same as disease_query
        "variants": list,          # May be empty
        "genes": list,             # May be empty
        "phenotypes": list,        # May be empty
        "drugs": list,             # May be empty
        "disease_metadata": dict,  # Should have "found" key
        "summary": {
            "total_variants_found": int,
            "total_genes_found": int,
            "total_phenotypes_found": int,
            "total_drugs_found": int,
            "disease_sources": list
        }
    },
    "source": "LOCAL_DISEASE_SEARCH"
}
```

### Test 7: Validate Variant Structure

For variants, each should have:
```python
variant = {
    "source": str,                  # e.g., "ClinVar"
    "variant": str,                 # Format: CHR:POS:REF:ALT
    "gene": str,                    # Gene symbol
    "disease": str,                 # Disease name
    "clinical_significance": str,   # e.g., "Pathogenic"
    "consequence": str,             # e.g., "missense_variant"
    "impact": str                   # e.g., "HIGH"
}
```

### Test 8: Validate Gene Structure

For genes, each should have:
```python
gene = {
    "gene_symbol": str,             # e.g., "BRCA1"
    "hpo_id": str,                  # e.g., "HP:0001234"
    "phenotype": str,               # Clinical feature
    "disease_id": str,              # e.g., "OMIM:604373"
    "frequency": str                # e.g., "common"
}
```

### Test 9: Validate Drug Structure

For drugs, each should have:
```python
drug = {
    "chembl_id": str,               # e.g., "CHEMBL3236"
    "name": str,                    # Drug name
    "target_gene": str,             # Target gene
    "indication": str,              # Disease indication
    "max_phase": str,               # 0-4
    "compound_type": str            # e.g., "Small molecule"
}
```

## Performance Tests

### Test 10: Response Time

```bash
# Measure response time for a common disease
time curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Type 2 diabetes"}'

# Expected: < 2 seconds
```

### Test 11: Response Time for Rare Disease

```bash
# Measure response time for a rare disease
time curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Niemann-Pick disease type C"}'

# Expected: < 2 seconds
```

## Browser/Frontend Testing

### Test 12: Frontend Integration Points

1. **Autocomplete Dropdown**
   - Call: `GET /api/disease-search/available?limit=100`
   - Display: List of diseases
   - Interaction: User selects one

2. **Disease Search**
   - Call: `POST /api/disease-search` with selected disease
   - Display: Tabs with results
   - Interaction: User explores results

3. **Result Display**
   - Variants Tab: Show genomic coordinates
   - Genes Tab: Show gene symbols and phenotypes
   - Phenotypes Tab: Show HPO terms
   - Drugs Tab: Show drug names and phases
   - Metadata Tab: Show official information

### Test 13: Edge Cases

#### Large Disease Name
```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Autosomal recessive polycystic kidney disease and hepatic disease"}'

# Should still work
```

#### Special Characters
```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "Marfan-like syndrome"}'

# Should handle gracefully
```

#### Very Short Match
```bash
curl -X POST http://localhost:8000/api/disease-search \
  -H "Content-Type: application/json" \
  -d '{"disease": "ab"}'

# Should return any matches or empty results
```

## Data Quality Tests

### Test 14: Verify Data Consistency

After a search, verify:

1. **No duplicate variants**: Same variant appears only once
2. **No duplicate genes**: Same gene appears only once  
3. **Valid variant format**: All variants match CHR:POS:REF:ALT pattern
4. **Valid gene symbols**: All are uppercase without spaces
5. **Clinical significance**: Only valid values (Pathogenic, Benign, etc.)

### Test 15: Cross-Reference Data

For a disease, verify:
- Variants should list genes from the gene results
- Genes should be in the HPO genes_to_phenotype file
- Phenotypes should match HPO term IDs
- Drugs should target genes in the results

## Regression Testing

### Test 16: Existing Variant Search Still Works

Ensure the old variant-first approach still works:

```bash
curl -X POST http://localhost:8000/api/annotate \
  -H "Content-Type: application/json" \
  -d '{"variant": "17:43044295:G:A"}'

# Should still return VEP annotation
```

### Test 17: Other Endpoints Unaffected

- `/api/gwas/{variant}` - Should still work
- `/api/compounds` - Should still work
- `/api/datasets/summary` - Should still work

## Load Testing

### Test 18: Multiple Concurrent Requests

```bash
# Send 10 concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/disease-search \
    -H "Content-Type: application/json" \
    -d '{"disease": "breast cancer"}' &
done
wait

# All should succeed without errors
```

## Integration Testing

### Test 19: Frontend → Backend Flow

1. Frontend calls: `GET /api/disease-search/available`
2. User selects: "Hereditary Breast Cancer"
3. Frontend calls: `POST /api/disease-search` with selection
4. Frontend displays results in tabs
5. User clicks variant → opens GENE VARIANT module
6. User clicks gene → searches compound database
7. User clicks drug → opens DRUG DISCOVERY module

## Documentation Tests

### Test 20: Verify Documentation

- [ ] `docs/DISEASE_SEARCH_GUIDE.md` - Clear and accurate
- [ ] `DISEASE_SEARCH_IMPLEMENTATION.md` - Technical details correct
- [ ] `docs/DISEASE_SEARCH_TESTING.md` - All tests runnable
- [ ] Code comments - Accurate and helpful

## Test Summary Template

```markdown
# Disease Search Testing Report

## Date: [DATE]
## Tester: [NAME]

### API Tests
- [ ] Available diseases endpoint works
- [ ] Disease search endpoint works
- [ ] Error handling works
- [ ] Response structure valid

### Data Quality Tests
- [ ] No duplicates in results
- [ ] Valid data formats
- [ ] Cross-references valid
- [ ] Summary counts accurate

### Performance Tests
- [ ] Response time < 2 seconds
- [ ] Concurrent requests handled
- [ ] Large result sets work

### Integration Tests
- [ ] Frontend integration points working
- [ ] Other endpoints unaffected
- [ ] Documentation matches implementation

### Issues Found
- [List any issues]

### Status: ✅ READY FOR PRODUCTION / ❌ NEEDS FIXES
```

## Cleanup

After testing, verify:
1. No debug prints left in code
2. No test data in production database
3. All error messages are user-friendly
4. Response times are acceptable
