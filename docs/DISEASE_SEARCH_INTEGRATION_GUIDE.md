# Disease Search - Frontend Integration Guide

## Overview
This guide explains how to integrate the new disease-based search functionality into the frontend React/Vue application.

## Backend API Endpoints

### 1. Get List of Available Diseases (for autocomplete)

**Endpoint**: `GET /api/disease-search/available`

**Query Parameters**:
- `limit` (optional): Number of results to return (default: 100)

**Example Request**:
```bash
GET http://localhost:8000/api/disease-search/available?limit=50
```

**Response**:
```json
{
  "total_available": 52847,
  "diseases": [
    "Hereditary breast and ovarian cancer syndrome",
    "Type 2 diabetes mellitus",
    "Cystic fibrosis",
    "Marfan syndrome",
    ...
  ],
  "note": "Diseases from ClinVar disease_names.tsv"
}
```

**Usage in Frontend**:
- Call this endpoint when component mounts
- Store diseases list in state
- Use for autocomplete dropdown
- Filter list on user input

### 2. Search by Disease

**Endpoint**: `POST /api/disease-search`

**Request Body**:
```json
{
  "disease": "Hereditary Breast Cancer"
}
```

**Response**:
```json
{
  "disease_query": "Hereditary Breast Cancer",
  "results": {
    "query": "Hereditary Breast Cancer",
    "variants": [
      {
        "source": "ClinVar",
        "variant": "17:43044295:G:A",
        "gene": "BRCA1",
        "disease": "Hereditary breast and ovarian cancer syndrome",
        "clinical_significance": "Pathogenic",
        "consequence": "missense_variant",
        "impact": "HIGH"
      }
    ],
    "genes": [
      {
        "gene_symbol": "BRCA1",
        "hpo_id": "HP:0000256",
        "phenotype": "Abnormal head morphology",
        "disease_id": "OMIM:604373",
        "frequency": "common"
      }
    ],
    "phenotypes": [
      {
        "hpo_id": "HP:0003002",
        "phenotype": "Breast carcinoma",
        "definition": "",
        "frequency": "common"
      }
    ],
    "drugs": [
      {
        "chembl_id": "CHEMBL3236",
        "name": "TALAZOPARIB",
        "target_gene": "PARP1",
        "indication": "Breast cancer",
        "max_phase": "4",
        "compound_type": "Small molecule"
      }
    ],
    "disease_metadata": {
      "found": true,
      "official_name": "Hereditary breast and ovarian cancer syndrome",
      "concept_id": "C0677776",
      "sources": ["MONDO", "Orphanet"],
      "category": "Disease"
    },
    "summary": {
      "total_variants_found": 12,
      "total_genes_found": 5,
      "total_phenotypes_found": 8,
      "total_drugs_found": 3,
      "disease_sources": ["MONDO", "Orphanet"]
    }
  },
  "source": "LOCAL_DISEASE_SEARCH"
}
```

## Frontend Component Structure

### Suggested Component Hierarchy

```
DiseaseAssocModule
├── DiseaseSearchInput
│   ├── Autocomplete Dropdown
│   └── Search Button
├── SearchResults (shown only after search)
│   ├── TabBar
│   │   ├── Variants Tab
│   │   ├── Genes Tab
│   │   ├── Phenotypes Tab
│   │   ├── Drugs Tab
│   │   └── Metadata Tab
│   ├── VariantsPanel
│   │   └── VariantList
│   │       └── VariantRow
│   ├── GenesPanel
│   │   └── GeneList
│   │       └── GeneRow
│   ├── PhenotypesPanel
│   │   └── PhenotypeList
│   │       └── PhenotypeRow
│   ├── DrugsPanel
│   │   └── DrugList
│   │       └── DrugRow
│   └── MetadataPanel
└── LoadingSpinner (during search)
```

## Implementation Examples

### React Example

```jsx
import React, { useState, useEffect } from 'react';

function DiseaseAssocModule() {
  const [diseases, setDiseases] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDisease, setSelectedDisease] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('variants');

  // Load available diseases on mount
  useEffect(() => {
    const loadDiseases = async () => {
      try {
        const response = await fetch('/api/disease-search/available?limit=100');
        const data = await response.json();
        setDiseases(data.diseases);
      } catch (error) {
        console.error('Failed to load diseases:', error);
      }
    };
    loadDiseases();
  }, []);

  // Handle disease search
  const handleSearch = async (diseaseName) => {
    if (!diseaseName || diseaseName.length < 2) {
      alert('Please enter at least 2 characters');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/disease-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ disease: diseaseName })
      });
      const data = await response.json();
      setResults(data.results);
      setActiveTab('variants');
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Autocomplete handler
  const handleInputChange = (value) => {
    setSearchQuery(value);
  };

  // Get filtered disease list for autocomplete
  const filteredDiseases = diseases.filter(disease =>
    disease.toLowerCase().includes(searchQuery.toLowerCase())
  ).slice(0, 10);

  return (
    <div className="disease-assoc-module">
      {/* Search Input */}
      <div className="search-section">
        <div className="search-input-wrapper">
          <input
            type="text"
            placeholder="Enter disease name (e.g., 'Breast Cancer')"
            value={searchQuery}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
          />
          <button onClick={() => handleSearch(searchQuery)}>
            Search Disease
          </button>
        </div>

        {/* Autocomplete Dropdown */}
        {searchQuery && filteredDiseases.length > 0 && (
          <div className="autocomplete-dropdown">
            {filteredDiseases.map((disease, idx) => (
              <div
                key={idx}
                className="autocomplete-item"
                onClick={() => {
                  setSearchQuery(disease);
                  setSelectedDisease(disease);
                  handleSearch(disease);
                }}
              >
                {disease}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Loading Spinner */}
      {loading && <div className="spinner">Searching...</div>}

      {/* Results */}
      {results && !loading && (
        <div className="results-section">
          <h3>Results for: {results.query}</h3>
          
          {/* Summary Stats */}
          <div className="summary-stats">
            <div className="stat">
              <span className="stat-label">Variants:</span>
              <span className="stat-value">{results.summary.total_variants_found}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Genes:</span>
              <span className="stat-value">{results.summary.total_genes_found}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Phenotypes:</span>
              <span className="stat-value">{results.summary.total_phenotypes_found}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Drugs:</span>
              <span className="stat-value">{results.summary.total_drugs_found}</span>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="tab-bar">
            <button
              className={`tab ${activeTab === 'variants' ? 'active' : ''}`}
              onClick={() => setActiveTab('variants')}
            >
              Variants ({results.variants.length})
            </button>
            <button
              className={`tab ${activeTab === 'genes' ? 'active' : ''}`}
              onClick={() => setActiveTab('genes')}
            >
              Genes ({results.genes.length})
            </button>
            <button
              className={`tab ${activeTab === 'phenotypes' ? 'active' : ''}`}
              onClick={() => setActiveTab('phenotypes')}
            >
              Phenotypes ({results.phenotypes.length})
            </button>
            <button
              className={`tab ${activeTab === 'drugs' ? 'active' : ''}`}
              onClick={() => setActiveTab('drugs')}
            >
              Drugs ({results.drugs.length})
            </button>
            <button
              className={`tab ${activeTab === 'metadata' ? 'active' : ''}`}
              onClick={() => setActiveTab('metadata')}
            >
              Metadata
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'variants' && (
              <div className="variants-panel">
                {results.variants.length === 0 ? (
                  <p>No variants found</p>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Variant</th>
                        <th>Gene</th>
                        <th>Clinical Significance</th>
                        <th>Consequence</th>
                        <th>Impact</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.variants.map((variant, idx) => (
                        <tr key={idx}>
                          <td>{variant.variant}</td>
                          <td>{variant.gene}</td>
                          <td>{variant.clinical_significance}</td>
                          <td>{variant.consequence}</td>
                          <td><span className={`impact-${variant.impact}`}>{variant.impact}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {activeTab === 'genes' && (
              <div className="genes-panel">
                {results.genes.length === 0 ? (
                  <p>No genes found</p>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Gene</th>
                        <th>Phenotype</th>
                        <th>Frequency</th>
                        <th>HPO ID</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.genes.map((gene, idx) => (
                        <tr key={idx}>
                          <td>{gene.gene_symbol}</td>
                          <td>{gene.phenotype}</td>
                          <td>{gene.frequency}</td>
                          <td>{gene.hpo_id}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {activeTab === 'phenotypes' && (
              <div className="phenotypes-panel">
                {results.phenotypes.length === 0 ? (
                  <p>No phenotypes found</p>
                ) : (
                  <ul>
                    {results.phenotypes.map((phenotype, idx) => (
                      <li key={idx}>
                        <strong>{phenotype.phenotype}</strong> ({phenotype.hpo_id})
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {activeTab === 'drugs' && (
              <div className="drugs-panel">
                {results.drugs.length === 0 ? (
                  <p>No drugs found</p>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Drug Name</th>
                        <th>Target Gene</th>
                        <th>Indication</th>
                        <th>Phase</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.drugs.map((drug, idx) => (
                        <tr key={idx}>
                          <td>{drug.name}</td>
                          <td>{drug.target_gene}</td>
                          <td>{drug.indication}</td>
                          <td>
                            <span className={`phase-${drug.max_phase}`}>
                              Phase {drug.max_phase}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {activeTab === 'metadata' && (
              <div className="metadata-panel">
                <dl>
                  <dt>Official Name:</dt>
                  <dd>{results.disease_metadata.official_name}</dd>
                  
                  <dt>Concept ID:</dt>
                  <dd>{results.disease_metadata.concept_id}</dd>
                  
                  <dt>Category:</dt>
                  <dd>{results.disease_metadata.category}</dd>
                  
                  <dt>Data Sources:</dt>
                  <dd>
                    {results.disease_metadata.sources?.join(', ') || 'N/A'}
                  </dd>
                </dl>
              </div>
            )}
          </div>
        </div>
      )}

      {/* No Results Message */}
      {results && results.summary.total_variants_found === 0 && 
           results.summary.total_genes_found === 0 && !loading && (
        <div className="no-results">
          <p>No disease associations found for "{results.query}"</p>
          <p>Try a different disease name or check the autocomplete suggestions.</p>
        </div>
      )}
    </div>
  );
}

export default DiseaseAssocModule;
```

## CSS Styling Guide

```css
.disease-assoc-module {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}

.search-section {
  margin-bottom: 30px;
}

.search-input-wrapper {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.search-input-wrapper input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-input-wrapper button {
  padding: 10px 20px;
  background-color: #00a86b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 100px;
  background: white;
  border: 1px solid #ddd;
  max-height: 300px;
  overflow-y: auto;
  z-index: 10;
}

.autocomplete-item {
  padding: 10px;
  cursor: pointer;
}

.autocomplete-item:hover {
  background-color: #f0f0f0;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin: 20px 0;
}

.stat {
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #00a86b;
}

.tab-bar {
  display: flex;
  gap: 5px;
  border-bottom: 2px solid #ddd;
  margin: 20px 0;
}

.tab {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 14px;
}

.tab.active {
  border-bottom-color: #00a86b;
  color: #00a86b;
  font-weight: bold;
}

.tab-content {
  padding: 20px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
  font-weight: bold;
}

tr:hover {
  background-color: #f9f9f9;
}

.impact-HIGH {
  color: #d9534f;
  font-weight: bold;
}

.impact-MODERATE {
  color: #f0ad4e;
}

.impact-LOW {
  color: #5cb85c;
}

.phase-4 {
  background-color: #5cb85c;
  color: white;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
}

.phase-3 {
  background-color: #0275d8;
  color: white;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
}

.phase-2 {
  background-color: #f0ad4e;
  color: white;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
}

.phase-1 {
  background-color: #d9534f;
  color: white;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 12px;
}

.spinner {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.no-results {
  padding: 40px;
  text-align: center;
  background: #f9f9f9;
  border-radius: 4px;
  color: #666;
}
```

## Error Handling

```jsx
// Handle API errors gracefully
const handleSearch = async (diseaseName) => {
  try {
    const response = await fetch('/api/disease-search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ disease: diseaseName })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Search failed');
    }

    const data = await response.json();
    setResults(data.results);
  } catch (error) {
    console.error('Search error:', error);
    alert(`Error: ${error.message}`);
  } finally {
    setLoading(false);
  }
};
```

## Performance Optimization

1. **Debounce autocomplete input**:
```jsx
import { useMemo } from 'react';

const debouncedSearch = useMemo(
  () => debounce((value) => handleInputChange(value), 300),
  []
);
```

2. **Virtualize long lists** if needed:
- Use `react-window` for large variant/gene lists

3. **Cache disease list**:
- Store diseases in localStorage
- Only refetch if stale

4. **Lazy load tabs**:
- Only fetch data for selected tab

## Accessibility

- Add `aria-label` to buttons
- Use semantic HTML (`<table>`, `<dl>`)
- Ensure keyboard navigation works
- Add loading announcements for screen readers

## Testing

```jsx
describe('DiseaseAssocModule', () => {
  test('loads diseases on mount', async () => {
    // Test disease loading
  });

  test('searches disease and displays results', async () => {
    // Test search functionality
  });

  test('handles errors gracefully', async () => {
    // Test error handling
  });

  test('tab switching works', async () => {
    // Test tab navigation
  });
});
```
