"""
Human Phenotype Ontology (HPO) integration.
Maps genetic variants to clinical phenotypes.

Downloads HPO JSON from: https://hpo.jax.org/app/data/json/hp.json
"""

import asyncio
import httpx
import json
import re
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
    Fetch HPO phenotypes associated with a disease name, gene symbol, or HPO term.
    Searches local genes_to_phenotype.csv by gene_symbol, disease_id, and hpo_name,
    and bridges disease names to OMIM IDs via disease_names.tsv.
    
    Args:
        disease_name: e.g., "Hereditary Breast and Ovarian Cancer Syndrome" or "BRCA1"
    
    Returns:
        List of phenotype terms with descriptions
    """
    import os
    
    phenotypes = []
    disease_lower = (disease_name or "").lower().strip()
    hpo_path = "data/datasets/hpo/genes_to_phenotype.csv"
    
    if not disease_lower or not os.path.exists(hpo_path):
        return []
    
    try:
        import pandas as pd
        df = pd.read_csv(hpo_path, low_memory=False)
        
        mask = pd.Series(False, index=df.index)
        
        # 1. Match gene symbol (e.g., "BRCA1")
        if 'gene_symbol' in df.columns:
            mask |= df['gene_symbol'].astype(str).str.upper() == disease_lower.upper()
        
        # 2. Match HPO term by name (e.g., "carcinoma")
        if 'hpo_name' in df.columns:
            mask |= df['hpo_name'].astype(str).str.lower().str.contains(disease_lower, na=False, regex=False)
        
        # 3. Match disease_id directly (e.g., "OMIM:604370")
        if 'disease_id' in df.columns:
            mask |= df['disease_id'].astype(str).str.lower().str.contains(disease_lower, na=False, regex=False)
        
        # 4. Bridge disease name -> MIM IDs via disease_names.tsv
        if 'disease_id' in df.columns:
            mim_ids = _resolve_mim_ids(disease_name)
            if mim_ids:
                mim_pattern = "|".join(re.escape(m) for m in mim_ids)
                mask |= df['disease_id'].astype(str).str.contains(mim_pattern, na=False, regex=True)
        
        seen = set()
        for _, row in df[mask].head(40).iterrows():
            hpo_id = str(row.get('hpo_id', ''))
            hpo_name = str(row.get('hpo_name', 'Unknown'))
            if hpo_id in seen or hpo_id == 'nan' or not hpo_id:
                continue
            seen.add(hpo_id)
            phenotypes.append({
                "id": hpo_id,
                "name": hpo_name,
                "definition": str(row.get('frequency', '')),
                "gene": str(row.get('gene_symbol', '')),
                "disease_id": str(row.get('disease_id', ''))
            })
    except Exception as e:
        print(f"[HPO] Phenotype search error: {e}")

    # Fallback to HPO JSON if available
    if not phenotypes:
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


def _resolve_mim_ids(disease_name: str) -> List[str]:
    """
    Map a disease name to OMIM IDs via the local disease_names.tsv
    (columns: #DiseaseName, SourceName, ConceptID, SourceID, DiseaseMIM, ...).
    Returns a list of 'OMIM:xxxxxx' strings that can be matched against
    the disease_id column of genes_to_phenotype.csv.
    """
    import os

    try:
        path = "data/datasets/clinvar/disease_names.tsv"
        if not os.path.exists(path):
            return []

        import pandas as pd
        df = pd.read_csv(path, sep='\t', low_memory=False)
        df.columns = [c.lstrip('#') for c in df.columns]

        if 'DiseaseName' not in df.columns:
            return []

        term = (disease_name or "").lower().strip()
        if not term:
            return []

        matches = df[df['DiseaseName'].astype(str).str.lower().str.contains(term, na=False, regex=False)]

        ids = set()
        if 'DiseaseMIM' in df.columns:
            for _, row in matches.head(20).iterrows():
                mim = str(row.get('DiseaseMIM', '')).strip()
                if mim and mim.lower() != 'nan':
                    ids.add(f"OMIM:{mim}")
        return list(ids)
    except Exception as e:
        print(f"[HPO] MIM resolve error: {e}")
        return []


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
