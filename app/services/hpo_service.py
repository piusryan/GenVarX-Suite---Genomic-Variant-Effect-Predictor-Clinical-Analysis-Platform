"""
Human Phenotype Ontology (HPO) integration.
Maps genetic variants to clinical phenotypes.

Downloads HPO JSON from: https://hpo.jax.org/app/data/json/hp.json
"""

import asyncio
import httpx
import json
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

HPO_JSON_URL = "https://hpo.jax.org/app/data/json/hp.json"
HPO_CACHE_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "datasets" / "hpo" / "hp.json"

_hpo_graph: Dict = {}
_loaded = False
_load_error: Optional[str] = None


async def fetch_phenotypes_for_disease(disease_name: str) -> List[Dict[str, str]]:
    """
    Fetch HPO phenotypes associated with a disease name.
    Searches local genes_to_phenotype.csv file.
    
    Args:
        disease_name: e.g., "Hereditary Breast and Ovarian Cancer Syndrome"
    
    Returns:
        List of phenotype terms with descriptions
    """
    import os
    
    phenotypes = []
    disease_lower = disease_name.lower()
    hpo_path = "data/datasets/hpo/genes_to_phenotype.csv"
    
    if not os.path.exists(hpo_path):
        return []
    
    try:
        import pandas as pd
        df = pd.read_csv(hpo_path, low_memory=False)
        
        # Search in disease_name column
        if 'disease_name' in df.columns:
            matches = df[df['disease_name'].str.lower().str.contains(disease_lower, na=False, regex=False)]
            seen = set()
            for _, row in matches.head(20).iterrows():
                hpo_id = str(row.get('hpo_id', ''))
                hpo_name = str(row.get('hpo_name', 'Unknown'))
                if hpo_id not in seen and hpo_id != 'nan':
                    seen.add(hpo_id)
                    phenotypes.append({
                        "id": hpo_id,
                        "name": hpo_name,
                        "definition": str(row.get('frequency', ''))
                    })
    except Exception as e:
        print(f"[HPO] Phenotype search error: {e}")
    
    # Fallback to HPO JSON if available
    await _ensure_loaded()
    if _hpo_graph and not phenotypes:
        for node_id, node_data in _hpo_graph.items():
            name = node_data.get("name", "").lower()
            if disease_lower in name or name in disease_lower:
                children = node_data.get("children", [])
                for child_id in children[:10]:
                    if child_id in _hpo_graph:
                        child = _hpo_graph[child_id]
                        phenotypes.append({
                            "id": child_id,
                            "name": child.get("name", "Unknown"),
                            "definition": child.get("def", "")
                        })
    
    return phenotypes


async def get_hpo_term(hpo_id: str) -> Optional[Dict]:
    """Retrieve a specific HPO term by ID (e.g., 'HP:0000001')."""
    await _ensure_loaded()
    if _load_error:
        return None
    return _hpo_graph.get(hpo_id)


async def get_disease_phenotype_associations() -> Dict[str, List[str]]:
    """Return mapping of diseases to their phenotype IDs."""
    await _ensure_loaded()
    if _load_error:
        return {}
    
    associations = {}
    for node_id, node_data in _hpo_graph.items():
        name = node_data.get("name", "")
        if "disease" in name.lower() or "syndrome" in name.lower():
            children = node_data.get("children", [])
            associations[name] = children
    
    return associations


async def _ensure_loaded() -> None:
    """Load HPO ontology from cache or download if needed."""
    global _loaded, _load_error, _hpo_graph
    
    if _loaded:
        return
    
    # Try to load from cache
    if HPO_CACHE_FILE.exists():
        try:
            with open(HPO_CACHE_FILE, "r", encoding="utf-8") as f:
                _hpo_graph = json.load(f)
            _loaded = True
            return
        except Exception as e:
            _load_error = f"Failed to load HPO cache: {str(e)}"
            _loaded = True
            return
    
    # Download HPO JSON
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(HPO_JSON_URL)
            if response.status_code != 200:
                _load_error = f"HPO download failed: HTTP {response.status_code}"
                _loaded = True
                return
            
            data = response.json()
            graphs = data.get("graphs", [])
            if graphs:
                nodes = graphs[0].get("nodes", [])
                # Convert list to dict indexed by ID
                _hpo_graph = {node.get("id"): node for node in nodes}
            
            # Cache the result
            HPO_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(HPO_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(_hpo_graph, f)
            
            _loaded = True
    except Exception as e:
        _load_error = f"HPO download error: {str(e)}"
        _loaded = True
