"""Smoke suite: all REST endpoints via in-process ASGI transport.

Run:  & ".venv\\Scripts\\python.exe" -u tests\\smoke_api.py
"""
import asyncio
import sys
import time

import httpx

sys.path.insert(0, ".")

from app.main import app

VALID = "17:43044295:G:A"
NONCODING = "rs6414541"
GENE = "BRCA1"
DISEASE = "breast cancer"
QUERY = "selinexor"
BATCH = '["rs6414541","rs429358"]'


async def main() -> int:
    passed = 0
    failed = 0
    fails = []
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=True)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        table = [
            ("health", "GET", "/health", {}),
            ("gwas datasets", "GET", "/api/datasets/summary", {}),
            ("disease-search available", "GET", "/api/disease-search/available", {}),
            ("rsid-to-disease noncoding", "GET", f"/api/rsid-to-disease/{NONCODING}", {}),
            ("rsid-to-disease batch", "POST", "/api/rsid-to-disease/batch",
             {"content": BATCH, "headers": {"Content-Type": "application/json"}}),
            ("disease-comprehensive", "GET", f"/api/disease-comprehensive/{VALID}", {}),
            ("annotate", "POST", "/api/annotate",
             {"json": {"variant": VALID, "rsid": NONCODING}}),
            ("conservation", "GET", "/api/conservation-score",
             {"params": {"variant": VALID}}),
            ("compounds search", "GET", "/api/compounds",
             {"params": {"query": QUERY, "limit": 5}}),
            ("compounds by gene", "GET", f"/api/compounds/by-gene/{GENE}", {}),
            ("compound detail", "GET", "/api/compounds/CHEMBL237500", {}),
            ("gwas", "POST", "/api/gwas",
             {"json": {"variant": "17:43044295:G:A"}}),
            ("gwas dataset", "POST", "/api/gwas/dataset-analysis",
             {"json": {"variant": "17:43044295:G:A"}}),
            ("disease associations", "POST", "/api/disease-associations",
             {"json": {"variant": VALID}}),
            ("disease search", "POST", "/api/disease-search",
             {"json": {"variant": VALID, "disease": DISEASE}}),
            ("phenotypes", "POST", "/api/phenotypes",
             {"json": {"variant": VALID, "gene": GENE}}),
            ("motif", "POST", "/api/motif-analysis",
             {"json": {"variant": VALID, "gene": GENE}}),
        ]

        for label, method, path, kw in table:
            t0 = time.perf_counter()
            try:
                r = await c.request(method, path, **kw)
                ms = (time.perf_counter() - t0) * 1000
                ok = r.status_code < 500
                if ok:
                    passed += 1
                else:
                    failed += 1
                    fails.append(f"{label} -> {r.status_code}")
                print(f"[{'PASS' if ok else 'FAIL'}] {label:<28} {ms:6.0f}ms  ({r.status_code})", flush=True)
            except Exception as e:
                failed += 1
                fails.append(f"{label} -> EXC {e}")
                print(f"[FAIL] {label:<28}          EXC {e}", flush=True)

    print(f"\nRESULT: {passed}/{passed + failed} passed")
    if fails:
        for f in fails:
            print("  -", f)
        return 1
    print("ALL ENDPOINTS OK")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
