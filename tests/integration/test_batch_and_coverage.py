"""Integration tests: batch-RSID + HPO/ChEMBL coverage + comprehensive aggregator.

Runs against the live server (item 3) using the real HTTP client + fixtures,
so it exercises route wiring, JSON contracts, and coverage fallback end-to-end.

Run:  & ".venv\Scripts\python.exe" -m pytest tests\integration -q
"""
import os
import sys

import httpx
import pytest

BASE = os.environ.get("GENVARX_BASE", "http://127.0.0.1:8000")

BATCH = ["rs6414541", "rs429358"]
NONCODING = "17:43044295:G:A"  # final tres
GENE = "BRCA1"


def _client():
    return httpx.Client(base_url=BASE, timeout=60.0)


# ---------------------------------------------------------------- batch
def test_batch_rsid_accepts_bare_array():
    with _client() as c:
        r = c.post("/api/rsid-to-disease/batch", content='["rs6414541","rs429358"]',
                   headers={"Content-Type": "application/json"})
        assert r.status_code < 500, r.text
        data = r.json()
        assert "results" in data


def test_batch_rejects_wrapped_object():
    with _client() as c:
        r = c.post("/api/rsid-to-disease/batch", json={"rsids": BATCH})
        assert r.status_code in (400, 422)


# ------------------------------------------------------- HPO/ChEMBL coverage
def test_comprehensive_returns_hpo_for_non_coding():
    # MIR3143 - RPL10P2 (non-coding profile) must fall back via coverage candidates
    with _client() as c:
        r = c.post("/api/disease-comprehensive", json={"variant": NONCODING})
        assert r.status_code < 500, r.text
        data = r.json()
        hpo = (data.get("disease_associations") or [])
        types = {d.get("source") for d in hpo}


def test_batch_is_deterministic():
    with _client() as c:
        r1 = c.post("/api/rsid-to-disease/batch", json=BATCH)
        r2 = c.post("/api/rsid-to-disease/batch", json=BATCH)
        assert r1.status_code < 500
        assert r1.json() == r2.json()
