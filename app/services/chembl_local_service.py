import asyncio
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional


_lock = asyncio.Lock()
_loaded = False
_load_error: Optional[str] = None
_by_id: Dict[str, Dict[str, str]] = {}
_all: List[Dict[str, str]] = []


async def search_compounds(query: str, limit: int = 20) -> List[Dict[str, str]]:
    await _ensure_loaded()
    if _load_error:
        raise RuntimeError(_load_error)

    q = (query or "").strip().lower()
    if not q:
        return _all[:limit]

    results: List[Dict[str, str]] = []
    for row in _all:
        chembl_id = (row.get("Compound ChEMBL ID") or "").lower()
        name = (row.get("Name") or "").lower()
        synonyms = (row.get("Synonyms") or "").lower()
        if q in chembl_id or q in name or q in synonyms:
            results.append(row)
            if len(results) >= limit:
                break

    return results


async def get_compound(chembl_id: str) -> Optional[Dict[str, str]]:
    await _ensure_loaded()
    if _load_error:
        raise RuntimeError(_load_error)
    return _by_id.get((chembl_id or "").strip().upper())


async def _ensure_loaded() -> None:
    global _loaded, _load_error
    if _loaded:
        return

    async with _lock:
        if _loaded:
            return

        env_path = (os.environ.get("CHEMBL_CSV_PATH") or "").strip()
        dataset_path = Path(env_path) if env_path else (Path(__file__).resolve().parents[2] / "data" / "datasets" / "chembl" / "chembl_compounds.csv")
        if not dataset_path.exists():
            _load_error = (
                f"ChEMBL dataset not found at: {dataset_path}. "
                "Place chembl_compounds.csv in data/datasets/chembl/ or set CHEMBL_CSV_PATH environment variable."
            )
            _loaded = True
            return

        with dataset_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                if not isinstance(row, dict):
                    continue
                chembl = (row.get("Compound ChEMBL ID") or "").strip().upper()
                if not chembl:
                    continue
                _by_id[chembl] = row
                _all.append(row)

        _loaded = True

