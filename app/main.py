from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from typing import List
from app.models import VariantRequest, DiseaseRequest, PatientReportRequest, VariantAnnotation, GwasResponse, GwasAssociation, CompoundSummary, CompoundDetail
from app.services.vep_service import fetch_vep_annotation
from app.services.clinvar_service import fetch_clinvar_data
from app.services.gwas_service import fetch_gwas_associations
from app.services.local_gwas_service import search_local_disease_associations, get_dataset_summary
from app.services.disease_search_service import search_disease_associations, get_available_diseases
from app.services.chembl_local_service import search_compounds, get_compound, search_compounds_by_gene
from app.services.hpo_service import fetch_phenotypes_for_disease
from app.services.motif_service import analyze_variant_motif_impact
from app.services.conservation_service import calculate_substitution_cost
from app.services.rsid_to_disease_service import get_diseases_by_rsid, get_diseases_by_rsids, get_rsid_gene_disease_mapping, resolve_rsid_to_variant
from app.services.comprehensive_disease_service import get_comprehensive_disease, _local_clinvar_vcf_search
from app.services.patient_report_service import build_report_json, generate_patient_pdf

app = FastAPI(title="GenVarX Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "online", "service": "GenVarX Engine"}

# ── Shared helper: clinvar_conflicting.csv lookup by coords ──────────
_CONFLICT_COL_SIFT = "SIFT"
_CONFLICT_COL_POLYPHEN = "PolyPhen"
_CONFLICT_COL_AA = "Amino_acids"
_CONFLICT_COL_SYMBOL = "SYMBOL"
_CONFLICT_COL_CONS = "Consequence"
_CONFLICT_COL_IMPACT = "IMPACT"
_CONFLICT_COL_CLNDN = "CLNDN"
_CONFLICT_COL_CHROM = "CHROM"
_CONFLICT_COL_POS = "POS"
_CONFLICT_COL_REF = "REF"
_CONFLICT_COL_ALT = "ALT"


def _lookup_conflicting_by_coords(chrom_no_prefix: str, pos: str,
                                   ref: str, alt: str):
    """Look up clinvar_conflicting.csv by exact CHROM/POS/REF/ALT.
    Returns dict with {sift, polyphen, amino_acids, gene, consequence,
    impact, diseases} or None if not found. Uses column names from actual
    dataset header: CHROM,POS,REF,ALT, ..., SIFT,PolyPhen,Amino_acids,SYMBOL
    """
    import os as _os
    import pandas as _pd
    _path = "data/datasets/clinvar/clinvar_conflicting.csv"
    if not _os.path.exists(_path):
        return None
    try:
        chrom_q = str(chrom_no_prefix).replace("chr", "").lower()
        pos_q = str(pos).strip()
        ref_q = str(ref).strip().upper()
        alt_q = str(alt).strip().upper()
        _cols = [_CONFLICT_COL_CHROM, _CONFLICT_COL_POS, _CONFLICT_COL_REF,
                 _CONFLICT_COL_ALT, _CONFLICT_COL_SIFT, _CONFLICT_COL_POLYPHEN,
                 _CONFLICT_COL_AA, _CONFLICT_COL_SYMBOL, _CONFLICT_COL_CONS,
                 _CONFLICT_COL_IMPACT, _CONFLICT_COL_CLNDN]
        for _chunk in _pd.read_csv(_path, usecols=_cols, chunksize=30000, low_memory=False):
            _c = _chunk[_CONFLICT_COL_CHROM].astype(str).str.replace("chr", "").str.lower()
            _p = _chunk[_CONFLICT_COL_POS].astype(str).str.strip()
            _r = _chunk[_CONFLICT_COL_REF].astype(str).str.strip().str.upper()
            _a = _chunk[_CONFLICT_COL_ALT].astype(str).str.strip().str.upper()
            mask = (_c == chrom_q) & (_p == pos_q) & (_r == ref_q) & (_a == alt_q)
            hits = _chunk[mask]
            if len(hits) > 0:
                row = hits.iloc[0]
                def _g(col):
                    v = row.get(col)
                    if v is None:
                        return ""
                    s = str(v).strip()
                    return "" if s.lower() in ("nan", "none", "n/a") else s
                sift = _g(_CONFLICT_COL_SIFT)
                poly = _g(_CONFLICT_COL_POLYPHEN)
                aa = _g(_CONFLICT_COL_AA)
                gene = _g(_CONFLICT_COL_SYMBOL)
                cons = _g(_CONFLICT_COL_CONS)
                impact = _g(_CONFLICT_COL_IMPACT)
                cldn_raw = _g(_CONFLICT_COL_CLNDN)
                diseases = []
                if cldn_raw:
                    for raw in cldn_raw.split("|"):
                        dname = raw.replace("_", " ").strip()
                        if dname and dname.lower() not in ("not specified", "not_provided", "not provided", "unknown", "nan"):
                            diseases.append(dname)
                return {"sift": sift, "polyphen": poly, "amino_acids": aa,
                        "gene": gene, "consequence": cons, "impact": impact,
                        "diseases": diseases}
        return None
    except Exception:
        return None


def _lookup_conflicting_by_rsid(rsid: str):
    """Scan clinvar_conflicting.csv for an RSID token inside any string column.
    RSIDs don't live in a dedicated column here, so we search the whole row.
    Returns same shape as _lookup_conflicting_by_coords or None."""
    import os as _os
    import pandas as _pd
    _path = "data/datasets/clinvar/clinvar_conflicting.csv"
    if not _os.path.exists(_path) or not rsid:
        return None
    try:
        rs = str(rsid).strip().lower()
        for _chunk in _pd.read_csv(_path, chunksize=20000, low_memory=False):
            found_mask = None
            for _c in _chunk.columns:
                if _chunk[_c].dtype == object:
                    m = _chunk[_c].astype(str).str.lower().str.contains(rs, na=False, regex=False)
                    found_mask = m if found_mask is None else (found_mask | m)
            if found_mask is not None and found_mask.any():
                row = _chunk[found_mask].iloc[0]
                def _g(col):
                    if col not in _chunk.columns:
                        return ""
                    v = row.get(col)
                    if v is None:
                        return ""
                    s = str(v).strip()
                    return "" if s.lower() in ("nan", "none", "n/a") else s
                sift = _g(_CONFLICT_COL_SIFT)
                poly = _g(_CONFLICT_COL_POLYPHEN)
                aa = _g(_CONFLICT_COL_AA)
                gene = _g(_CONFLICT_COL_SYMBOL)
                cons = _g(_CONFLICT_COL_CONS)
                impact = _g(_CONFLICT_COL_IMPACT)
                cldn_raw = _g(_CONFLICT_COL_CLNDN)
                diseases = []
                if cldn_raw:
                    for raw in cldn_raw.split("|"):
                        dname = raw.replace("_", " ").strip()
                        if dname and dname.lower() not in ("not specified", "not_provided", "not provided", "unknown", "nan"):
                            diseases.append(dname)
                return {"sift": sift, "polyphen": poly, "amino_acids": aa,
                        "gene": gene, "consequence": cons, "impact": impact,
                        "diseases": diseases,
                        "chrom": _g(_CONFLICT_COL_CHROM),
                        "pos": _g(_CONFLICT_COL_POS),
                        "ref": _g(_CONFLICT_COL_REF),
                        "alt": _g(_CONFLICT_COL_ALT)}
        return None
    except Exception:
        return None


@app.post("/api/annotate", response_model=VariantAnnotation)
async def annotate(payload: VariantRequest):
    variant_input = payload.variant.strip()

    # ──────────────────────────────────────────────────────────────
    # BRANCH A: Pure RSID input (no colons, starts with rs)
    # ──────────────────────────────────────────────────────────────
    if variant_input.startswith('rs') and ':' not in variant_input:
        # Step A1: resolve RSID → chr:pos:ref:alt + gene via ClinVar VCF
        resolved = await resolve_rsid_to_variant(variant_input)
        resolved_gene = (resolved.get("gene_symbol") or "").strip()
        resolved_variant = resolved.get("variant") or variant_input  # chr:pos:ref:alt or just RSID
        resolved_sig = (resolved.get("clinical_significance") or "").strip() or None
        resolved_cons = (resolved.get("consequence") or "").strip() or ""
        resolved_impact = (resolved.get("impact") or "").strip() or ""
        resolved_diseases_list = resolved.get("diseases") or []

        # Step A2: get diseases from the RSID mapper (ClinVar VCF + GWAS TSV)
        rsid_diseases_result = await get_diseases_by_rsid(variant_input)
        rsid_diseases_raw = rsid_diseases_result.get("diseases", []) or []

        # Step A3: split resolved_variant → coords if we have them, for VEP call
        has_full_coords = bool(resolved_variant and ':' in resolved_variant
                               and resolved_variant.count(':') >= 3)
        coord_chrom = coord_pos = coord_ref = coord_alt = None
        if has_full_coords:
            _p = resolved_variant.split(":")
            coord_chrom = _p[0].replace("chr", "")
            coord_pos = _p[1] if len(_p) > 1 else None
            coord_ref = _p[2] if len(_p) > 2 else None
            coord_alt = _p[3] if len(_p) > 3 else None

        # Step A4: call VEP with the resolved coordinates so we get REAL SIFT/PolyPhen
        sift_pred = "N/A"
        polyphen_pred = "N/A"
        amino_acid = "N/A"
        vep_gene = None
        vep_cons = None
        vep_impact = None
        vep_sig = None
        vep_rsid = None
        vep_diseases = []
        if has_full_coords:
            try:
                vep_result = await fetch_vep_annotation(resolved_variant)
                vep_gene = getattr(vep_result, "gene_symbol", None)
                vep_cons = getattr(vep_result, "consequence", None)
                vep_impact = getattr(vep_result, "impact_level", None)
                vep_sig = getattr(vep_result, "clinical_significance", None)
                vep_rsid = getattr(vep_result, "rs_id", None)
                vep_diseases = getattr(vep_result, "associated_diseases", []) or []
                # VEP results only count if they look real (not "N/A", not blocking keywords)
                def _ok(v): return v and isinstance(v, str) and v not in ("N/A", "", None)
                if _ok(vep_gene):
                    resolved_gene = vep_gene
                if _ok(vep_cons) and not any(t in vep_cons for t in ("Unavailable", "Failed", "Invalid", "Timeout")):
                    resolved_cons = vep_cons
                if _ok(vep_impact) and vep_impact not in ("UNKNOWN", ""):
                    resolved_impact = vep_impact
                if vep_sig and "Not Found" not in str(vep_sig) and "Uncertain" not in str(vep_sig):
                    resolved_sig = resolved_sig or str(vep_sig).strip()
                _sv = getattr(vep_result, "sift_prediction", "N/A") or "N/A"
                _pv = getattr(vep_result, "polyphen_prediction", "N/A") or "N/A"
                _av = getattr(vep_result, "amino_acid_change", "N/A") or "N/A"
                if _sv and _sv != "N/A": sift_pred = _sv
                if _pv and _pv != "N/A": polyphen_pred = _pv
                if _av and _av != "N/A": amino_acid = _av
            except Exception:
                pass

        # Step A5: clinvar_conflicting.csv lookup (by coords first, by RSID string scan as fallback)
        conflict_hit = None
        if has_full_coords and coord_chrom and coord_pos and coord_ref and coord_alt:
            conflict_hit = _lookup_conflicting_by_coords(coord_chrom, coord_pos, coord_ref, coord_alt)
        if conflict_hit is None:
            conflict_hit = _lookup_conflicting_by_rsid(variant_input)
            # If we found it by RSID scan, we now have coords from conflict CSV
            if conflict_hit and conflict_hit.get("chrom") and conflict_hit.get("pos") and not has_full_coords:
                coord_chrom = conflict_hit["chrom"]
                coord_pos = conflict_hit["pos"]
                coord_ref = conflict_hit.get("ref") or ""
                coord_alt = conflict_hit.get("alt") or ""
                if coord_ref and coord_alt:
                    resolved_variant = f"{coord_chrom}:{coord_pos}:{coord_ref}:{coord_alt}"
        if conflict_hit is not None:
            if sift_pred == "N/A" and conflict_hit.get("sift"):
                sift_pred = conflict_hit["sift"]
            if polyphen_pred == "N/A" and conflict_hit.get("polyphen"):
                polyphen_pred = conflict_hit["polyphen"]
            if amino_acid == "N/A" and conflict_hit.get("amino_acids"):
                amino_acid = conflict_hit["amino_acids"]
            if not resolved_gene or resolved_gene in ("N/A", "Unknown", "Multiple") and conflict_hit.get("gene"):
                resolved_gene = conflict_hit["gene"]
            if not resolved_cons and conflict_hit.get("consequence"):
                resolved_cons = conflict_hit["consequence"]
            if not resolved_impact and conflict_hit.get("impact"):
                resolved_impact = conflict_hit["impact"]
            if not resolved_sig and conflict_hit.get("diseases"):
                resolved_sig = f"Associated with {len(conflict_hit['diseases'])} condition(s)"

        # Step A6: finalise defaults, never show "Multiple" if we can avoid it
        gene_symbol = (
            resolved_gene
            if resolved_gene and resolved_gene not in ("Unknown", "N/A", "", None)
            else "Multiple"
        )
        if not resolved_cons:
            resolved_cons = "GWAS / Catalog variant"
        if not resolved_impact:
            resolved_impact = "MODERATE"

        # Step A7: merge clinical significance from all available sources
        if not resolved_sig and rsid_diseases_raw:
            _sigs = set()
            for _d in rsid_diseases_raw:
                _s = (_d.get("clinical_significance") or "").strip()
                if _s and _s.lower() not in ("unknown", ""):
                    _sigs.add(_s.replace("_", " "))
            if _sigs:
                resolved_sig = ", ".join(sorted(_sigs))

        # Step A8: build merged disease display list
        _seen_diseases = set()
        diseases_display = []
        for _d in rsid_diseases_raw:
            _txt = f"{_d.get('disease', '')} (Gene: {_d.get('gene', '')})" if _d.get("gene") and _d.get("gene") != "Unknown" else str(_d.get("disease", ""))
            _key = _txt.lower().strip()
            if _key and _key not in _seen_diseases:
                _seen_diseases.add(_key)
                diseases_display.append(_txt)
        for _d in resolved_diseases_list:
            if isinstance(_d, str):
                _key = _d.lower().strip()
                if _key and _key not in _seen_diseases:
                    _seen_diseases.add(_key)
                    diseases_display.append(_d)
        if conflict_hit and conflict_hit.get("diseases"):
            for _d in conflict_hit["diseases"]:
                _key = _d.lower().strip()
                if _key and _key not in _seen_diseases:
                    _seen_diseases.add(_key)
                    diseases_display.append(_d)
        for _d in vep_diseases:
            _s = str(_d)
            _key = _s.lower().strip()
            if _key and _key not in _seen_diseases:
                _seen_diseases.add(_key)
                diseases_display.append(_s)

        if not resolved_sig:
            resolved_sig = diseases_display[0] if diseases_display else "Common variant (no ClinVar entry)"

        return VariantAnnotation(
            variant=resolved_variant,
            rs_id=vep_rsid or variant_input,
            gene_symbol=gene_symbol,
            consequence=resolved_cons,
            sift_prediction=sift_pred,
            polyphen_prediction=polyphen_pred,
            amino_acid_change=amino_acid,
            impact_level=resolved_impact,
            clinical_significance=resolved_sig,
            associated_diseases=diseases_display,
        )

    # ──────────────────────────────────────────────────────────────
    # BRANCH B: Full coordinate variant input (chr:pos:ref:alt)
    # ──────────────────────────────────────────────────────────────
    vep_result = await fetch_vep_annotation(variant_input)
    clinvar_result = await fetch_clinvar_data(variant_input, rsid=getattr(vep_result, "rs_id", None))
    local_vcf = await _local_clinvar_vcf_search(variant_input, is_rsid=False)

    # Parse input coords for conflicting CSV lookup
    _parts = variant_input.replace("chr", "").split(":")
    _c_chrom = _parts[0] if len(_parts) > 0 else None
    _c_pos = _parts[1] if len(_parts) > 1 else None
    _c_ref = _parts[2] if len(_parts) > 2 else None
    _c_alt = _parts[3] if len(_parts) > 3 else None
    conflict_hit = None
    if _c_chrom and _c_pos and _c_ref and _c_alt:
        conflict_hit = _lookup_conflicting_by_coords(_c_chrom, _c_pos, _c_ref, _c_alt)

    # 0. Local ClinVar VCF data
    local_diseases = []
    local_gene = None
    local_clinsig = None
    if local_vcf and local_vcf.get("found"):
        local_gene = local_vcf.get("gene")
        local_clinsig = local_vcf.get("clinical_significance")
        for h in local_vcf.get("hits", []) or []:
            if h.get("disease"):
                local_diseases.append(h["disease"])

    # Merge in conflicting.csv diseases and gene/significance if missing from VCF
    conflict_diseases = []
    conflict_gene = None
    if conflict_hit:
        conflict_diseases = conflict_hit.get("diseases") or []
        conflict_gene = conflict_hit.get("gene") or None
        if not local_gene and conflict_gene:
            local_gene = conflict_gene

    # 1. Clinical significance cascade: external ClinVar → local VCF → conflicting → VEP → default
    clinvar_sig = (clinvar_result.get("clinical_significance") or "").strip()
    clinvar_diseases = clinvar_result.get("associated_diseases", []) or []

    _BLOCKED_CS = ("", "Not Found in ClinVar", "Uncertain Significance / Not Found in ClinVar",
                   "Timeout", "Invalid Format", "Lookup Failed", "No Record")
    merged_sig = ""
    if clinvar_sig and clinvar_sig not in _BLOCKED_CS and "Not Found" not in clinvar_sig and "Uncertain" not in clinvar_sig:
        merged_sig = clinvar_sig
    if not merged_sig and local_clinsig:
        merged_sig = local_clinsig
    if not merged_sig:
        vep_cs = getattr(vep_result, "clinical_significance", None)
        if vep_cs and vep_cs not in _BLOCKED_CS and "Not Found" not in str(vep_cs) and "Uncertain" not in str(vep_cs):
            merged_sig = str(vep_cs).strip()
    # Never let a real ambiguous-looking "Conflicting" cover-row override a clear Pathogenic
    if "Conflict" in merged_sig and local_clinsig and "Pathogenic" in local_clinsig:
        merged_sig = local_clinsig
    final_sig = merged_sig or "Uncertain Significance / Not Found in ClinVar"

    # 1b. Local GWAS Catalog TSV enrichment by resolved coordinate → rsID + pubmed references
    _gwas_extra_traits = []
    _gwas_extra_refs = []
    if variant_input:
        _gw_rsid = getattr(vep_result, "rs_id", None) or (local_vcf or {}).get("rsid")
        if not _gw_rsid and conflict_hit:
            _gw_rsid = conflict_hit.get("rs_id") or conflict_hit.get("rsid")
        if _gw_rsid:
            _gw_rows = await _lookup_conflicting_by_rsid(str(_gw_rsid)) if False else None
            try:
                from app.services.gwas_service import fetch_gwas_associations as _fga
                _gwas_rows = await _fga(str(_gw_rsid), limit=12)
                for _a in _gwas_rows or []:
                    _tr = str(_a.get("trait") or "").strip()
                    if _tr and _tr not in _gwas_extra_traits:
                        _gwas_extra_traits.append(_tr)
                    _pm = _a.get("pubmed_id") or _a.get("pubmedId") or ""
                    if _pm and str(_pm).strip() and str(_pm).strip().lower() not in ("nan", "none", "n/a", ""):
                        _ref = f"PMID:{_pm} {_tr}" if _tr else f"PMID:{_pm}"
                        if _ref not in _gwas_extra_refs:
                            _gwas_extra_refs.append(_ref)
            except Exception:
                pass

    # 2. Disease merging: LOCAL first — highest priority!
    _seen_diseases = set()
    merged_diseases = []
    for src in (local_diseases, conflict_diseases, clinvar_diseases,
                getattr(vep_result, "associated_diseases", []) or []):
        for d in src:
            s = str(d).replace("_", " ").strip()
            k = s.lower()
            if not k or k in _seen_diseases:
                continue
            _seen_diseases.add(k)
            merged_diseases.append(s)
    for _tr in _gwas_extra_traits:
        _st = str(_tr).replace("_", " ").strip()
        _k = _st.lower()
        if _k and _k not in _seen_diseases:
            _seen_diseases.add(_k)
            merged_diseases.append(f"GWAS: {_st}")

    # 3. Gene: VEP → local VCF → conflicting → N/A
    final_gene = getattr(vep_result, "gene_symbol", None)
    if not final_gene or final_gene in ("N/A", ""):
        final_gene = local_gene or "N/A"

    # 4. Consequence: prefer VEP (if usable) → local VCF → conflicting → fallback
    _vep_cons = str(getattr(vep_result, "consequence", "") or "")
    _vep_ok = not any(t in _vep_cons for t in ("Unavailable", "Failed", "Invalid", "Timeout", "No VEP Records"))
    if _vep_ok and _vep_cons:
        final_consequence = _vep_cons
    else:
        final_consequence = ""
        if local_vcf and local_vcf.get("hits"):
            for h in local_vcf["hits"]:
                hc = h.get("consequence", "")
                if hc:
                    final_consequence = hc.replace("_", " ")
                    break
        if not final_consequence and conflict_hit and conflict_hit.get("consequence"):
            final_consequence = conflict_hit["consequence"].replace("_", " ")
        if not final_consequence:
            if _vep_cons:
                final_consequence = _vep_cons  # even the failed message is better than nothing
            elif final_gene != "N/A":
                final_consequence = "Gene-located variant"
            else:
                final_consequence = "Intergenic / not-yet-annotated variant"

    # 5. Impact: VEP → local VCF → conflicting → MODERATE/UNKNOWN
    final_impact = getattr(vep_result, "impact_level", None)
    if not final_impact or final_impact in ("UNKNOWN", ""):
        if local_vcf and local_vcf.get("hits"):
            for h in local_vcf["hits"]:
                hi = h.get("impact", "")
                if hi and hi not in ("UNKNOWN", ""):
                    final_impact = hi
                    break
    if not final_impact or final_impact in ("UNKNOWN", ""):
        if conflict_hit and conflict_hit.get("impact"):
            final_impact = conflict_hit["impact"]
    if not final_impact or final_impact in ("UNKNOWN", ""):
        final_impact = "MODERATE" if final_gene != "N/A" else "UNKNOWN"

    # 6. Functional predictions: VEP → conflicting → N/A
    final_sift = getattr(vep_result, "sift_prediction") or "N/A"
    final_poly = getattr(vep_result, "polyphen_prediction") or "N/A"
    final_aa = getattr(vep_result, "amino_acid_change") or "N/A"
    if conflict_hit:
        if (not final_sift or final_sift == "N/A") and conflict_hit.get("sift"):
            final_sift = conflict_hit["sift"]
        if (not final_poly or final_poly == "N/A") and conflict_hit.get("polyphen"):
            final_poly = conflict_hit["polyphen"]
        if (not final_aa or final_aa == "N/A") and conflict_hit.get("amino_acids"):
            final_aa = conflict_hit["amino_acids"]

    return VariantAnnotation(
        variant=getattr(vep_result, "variant", variant_input) or variant_input,
        rs_id=(getattr(vep_result, "rs_id", None) or (local_vcf or {}).get("rsid")),
        gene_symbol=final_gene,
        consequence=final_consequence,
        sift_prediction=final_sift,
        polyphen_prediction=final_poly,
        amino_acid_change=final_aa,
        impact_level=final_impact,
        clinical_significance=final_sig,
        associated_diseases=merged_diseases,
    )


@app.post("/api/gwas", response_model=GwasResponse)
async def gwas(payload: VariantRequest):
    variant_input = payload.variant.strip()
    rs_id = None
    
    # Check if input is just an RSID
    if variant_input.startswith('rs') and ':' not in variant_input:
        rs_id = variant_input
    else:
        # Otherwise extract from VEP
        vep_result = await fetch_vep_annotation(variant_input)
        rs_id = getattr(vep_result, "rs_id", None)
    
    print(f"[GWAS DEBUG] Input variant: {variant_input}")
    print(f"[GWAS DEBUG] Extracted rsID: {rs_id}")
    
    if not rs_id:
        return GwasResponse(
            rs_id=None, 
            associations=[], 
            note="⚠️ rsID not found for this variant - likely rare/familial variant not in GWAS Catalog"
        )

    assoc_rows = await fetch_gwas_associations(rs_id, limit=20)
    associations = [GwasAssociation(**row) for row in assoc_rows]
    note = None if associations else "✓ rsID found but no GWAS Catalog associations available"

    return GwasResponse(rs_id=rs_id, associations=associations, note=note)


@app.post("/api/gwas/dataset-analysis")
async def gwas_dataset_analysis(payload: VariantRequest):
    """Analyze variant against local datasets and show diagnostic info."""
    import os
    import pandas as pd

    raw_input = payload.variant.strip()
    is_pure_rsid = raw_input.lower().startswith('rs') and ':' not in raw_input

    # Pre-resolve pure RSID input to chr:pos:ref:alt + gene via local files
    resolved = await resolve_rsid_to_variant(raw_input) if is_pure_rsid else None

    if resolved and resolved.get("variant") and ':' in resolved["variant"] and resolved["variant"].count(':') >= 2:
        # Have a real chr:pos:ref:alt now; use this for VEP so it won't fail
        effective_variant = resolved["variant"]
    else:
        effective_variant = raw_input

    vep_result = await fetch_vep_annotation(effective_variant)
    # If VEP failed but we resolved RSID, fill from resolver
    vep_rs = getattr(vep_result, "rs_id", None)
    vep_gene = getattr(vep_result, "gene_symbol", None) or "N/A"
    vep_cons = getattr(vep_result, "consequence", None) or "N/A"
    vep_clinsig = getattr(vep_result, "clinical_significance", None) or "N/A"
    vep_assoc = getattr(vep_result, "associated_diseases", None) or []

    if is_pure_rsid and resolved:
        if not vep_rs:
            vep_rs = resolved.get("rsid") or raw_input
        if (not vep_gene) or vep_gene == "N/A" or "Invalid" in str(vep_gene):
            resolved_gene = resolved.get("gene_symbol")
            if resolved_gene:
                vep_gene = resolved_gene
        if (not vep_cons) or vep_cons == "N/A" or "Failed" in vep_cons or "Invalid" in vep_cons:
            resolved_cons = resolved.get("consequence") or (
                f"via {resolved['source']}" if resolved.get('source') else None
            )
            if resolved_cons:
                vep_cons = resolved_cons
        if (not vep_clinsig) or vep_clinsig == "N/A" or "Invalid" in vep_clinsig:
            resolved_cs = resolved.get("clinical_significance")
            if resolved_cs:
                vep_clinsig = resolved_cs
        if not vep_assoc and resolved.get("diseases"):
            vep_assoc = resolved["diseases"]

    rs_id = vep_rs

    analysis = {
        "variant": raw_input,
        "vep_extraction": {
            "rs_id": rs_id,
            "gene_symbol": vep_gene,
            "consequence": vep_cons,
            "clinical_significance": vep_clinsig,
            "associated_diseases": vep_assoc,
        },
        "local_datasets": {},
        "gwas_catalog_status": None,
        "diagnostic_message": None
    }

    # Check local datasets (file listing)
    gwas_dir = "data/datasets"
    if os.path.exists(gwas_dir):
        for subdir in os.listdir(gwas_dir):
            subdir_path = os.path.join(gwas_dir, subdir)
            if os.path.isdir(subdir_path):
                files = os.listdir(subdir_path)
                analysis["local_datasets"][subdir] = {
                    "files": files,
                    "file_count": len(files),
                    "path": subdir_path
                }

    # For pure RSID input, fetch GWAS by rs_id directly, even if the VEP resolver
    # fallback gave an rs_id value we trust it because we already validated it.
    if is_pure_rsid and not rs_id:
        rs_id = raw_input

    # Check GWAS associations
    if rs_id:
        assoc_rows = await fetch_gwas_associations(rs_id, limit=5)
        analysis["gwas_catalog_status"] = {
            "found": len(assoc_rows) > 0,
            "count": len(assoc_rows),
            "associations": assoc_rows
        }
        if assoc_rows:
            analysis["diagnostic_message"] = f"✓ GWAS Catalog: Found {len(assoc_rows)} associations"
        else:
            analysis["diagnostic_message"] = f"⚠️ rsID {rs_id} exists but has no GWAS associations"
    else:
        # 3b. Coordinate input with NO resolved rsID (VEP/variant-Effects blocked or rare):
        #      fall back to the LOCAL GWAS Catalog TSV searched by COORDINATES.
        #      This is fully offline and returns real rows incl. pubmed_id (research ref).
        coord_hits = []
        try:
            from app.services.comprehensive_disease_service import _local_gwas_tsv_search as _lgc
            _co = _parts
            _coord_str = (raw_input.replace("chr", "") if (":" in raw_input) else raw_input)
            if ":" in _coord_str and _coord_str.count(":") >= 1:
                _fold = []
                for _seg in _coord_str.split(":")[:2]:
                    _fold.append(str(_seg).strip())
                _chrom_q = _fold[0] if len(_fold) > 0 else ""
                _pos_q = _fold[1] if len(_fold) > 1 else ""
                _rows = await _lgc(_coord_str)
                if isinstance(_rows, dict):
                    _rows = _rows.get("hits", []) or []
                for _r in _rows or []:
                    _r2 = dict(_r or {})
                    _g = _r2.get("chromosome") or _r2.get("chr") or ""
                    _p = _r2.get("position") or _r2.get("pos") or ""
                    if str(_g).replace("chr", "") == str(_chrom_q).replace("chr", "") and (
                        not _pos_q or str(_p) == str(_pos_q) or _pos_q in str(_p)
                    ):
                        coord_hits.append(_r2)
        except Exception as _e:
            coord_hits = []

        if coord_hits:
            _seen_t = set()
            _unique_h = []
            for _rk in coord_hits:
                _t = str(_rk.get("trait") or _rk.get("reported_trait") or "GWAS-association for this locus").strip()
                _t = _t.replace("_", " ").strip()
                _k = _t.lower()
                if _k and _k not in _seen_t:
                    _seen_t.add(_k)
                    _unique_h.append({
                        "trait": _t,
                        "pvalue": _rk.get("pvalue") or _rk.get("p_value") or "",
                        "pubmed_id": _rk.get("pubmed_id") or _rk.get("pubmedId") or "",
                        "chromosome": _rk.get("chromosome") or _rk.get("chr") or "",
                        "position": _rk.get("position") or _rk.get("pos") or "",
                        "strongest_allele": _rk.get("strongest_allele") or _rk.get("risk_allele") or "",
                        "gene": _rk.get("gene") or _rk.get("gene_symbol") or "N/A",
                    })
            analysis["gwas_catalog_status"] = {
                "found": True,
                "count": len(_unique_h),
                "associations": _unique_h,
            }
            analysis["diagnostic_message"] = (
                f"✓ GWAS Catalog: Found {len(_unique_h)} local association(s) by coordinate "
                f"(offline local TSV, research/pubmed refs included)"
            )
        else:
            analysis["gwas_catalog_status"] = {
                "found": False,
                "count": 0,
                "associations": [],
                "note": "Not found in local GWAS Catalog TSV by coordinate — may be rare/familial"
            }
            analysis["diagnostic_message"] = (
                "✗ Coordinate present but no local GWAS Catalog row; "
                "if this is a rare/familial variant it will not be in the GWAS Catalog"
            )

    # Step A5: if local ClinVar VCF said Pathogenic etc., never keep showing
    # the conflicting-CSV's "Conflicting significance" cosmetic over it…
    if conflict_hit and conflict_hit.get("clinical_significance"):
        if "Conflict" in str(conflict_hit["clinical_significance"]):
            if local_clinsig and "Pathogenic" in str(local_clinsig):
                analysis["datasets"]["clinvar"]["status"] = {
                    "pathogenic_found": True,
                    "display": f"✓ {local_clinsig} (local ClinVar VCF confirms; conflicting-CSV matched by position only)"
                }
    return analysis


@app.post("/api/disease-associations")
async def disease_associations(payload: VariantRequest):
    """
    Find disease associations from LOCAL datasets.
    Handles both full variants and RSIDs. Robust to VEP failures: resolves
    the gene from the local ClinVar VCF *first* so HPO / gene-based lookups
    always run against a real gene when possible.
    """
    variant_input = payload.variant.strip()

    # ── Pure RSID input ──
    if variant_input.startswith('rs') and ':' not in variant_input:
        rsid_result = await get_diseases_by_rsid(variant_input)
        resolved = await resolve_rsid_to_variant(variant_input)
        resolved_gene = (resolved.get("gene_symbol") or "").strip()
        gene_symbol = (
            resolved_gene
            if resolved_gene and resolved_gene not in ("Unknown", "N/A", "")
            else "Multiple"
        )
        # Also search local datasets using the resolved gene so HPO phenos come back
        extra_local = await search_local_disease_associations(variant_input, gene_symbol)

        # Pull clinvar_conflicting.csv data too
        _conflict = _lookup_conflicting_by_rsid(variant_input)

        return {
            "variant": variant_input,
            "rsid": variant_input,
            "gene_symbol": gene_symbol,
            "rsid_mapping": rsid_result,
            "local_findings": extra_local,
            "clinvar_conflicting": _conflict,
            "source": "LOCAL_RSID_MAPPING + LOCAL_DATASETS + CLINVAR_CONFLICTING"
        }

    # ── Coordinate input ──
    # Step 1: pre-resolve gene/clinvar from LOCAL ClinVar VCF BEFORE VEP call.
    #         This makes this endpoint 100% usable even if Ensembl is offline.
    local_vcf = await _local_clinvar_vcf_search(variant_input, is_rsid=False)
    fallback_gene = None
    local_extra = {}
    if local_vcf and local_vcf.get("found"):
        fallback_gene = local_vcf.get("gene")
        local_extra = {
            "clinvar_vcf_direct": {
                "clinical_significance": local_vcf.get("clinical_significance"),
                "gene": local_vcf.get("gene"),
                "rsid": local_vcf.get("rsid"),
                "hits": local_vcf.get("hits", [])[:15],
            }
        }

    # Parse coords for conflicting CSV
    _parts = variant_input.replace("chr", "").split(":")
    _conflict = None
    if len(_parts) >= 4:
        _conflict = _lookup_conflicting_by_coords(_parts[0], _parts[1], _parts[2], _parts[3])
    if fallback_gene is None and _conflict and _conflict.get("gene"):
        fallback_gene = _conflict["gene"]

    # Step 2: try VEP but swallow failures
    gene_symbol = "N/A"
    try:
        vep_result = await fetch_vep_annotation(variant_input)
        g = getattr(vep_result, "gene_symbol", None)
        if g and g not in ("N/A", "", None):
            gene_symbol = g
    except Exception:
        gene_symbol = "N/A"

    if not gene_symbol or gene_symbol in ("N/A", "Unknown", ""):
        gene_symbol = fallback_gene or "N/A"

    # Step 3: local dataset search with the best gene symbol possible
    local_results = await search_local_disease_associations(variant_input, gene_symbol)

    # Merge in direct ClinVar VCF + conflicting findings
    merged_findings = dict(local_results) if isinstance(local_results, dict) else {"raw": local_results}
    merged_findings.update(local_extra)
    if _conflict:
        merged_findings["clinvar_conflicting_csv"] = _conflict

    return {
        "variant": variant_input,
        "gene_symbol": gene_symbol,
        "local_findings": merged_findings,
        "source": "LOCAL_DATASETS (+ local ClinVar VCF + ClinVar conflicting gene fallback)"
    }


@app.post("/api/disease-search")
async def search_by_disease(payload: DiseaseRequest):
    """
    Search for disease associations using disease name as input.
    Returns variants, genes, phenotypes, and drugs associated with the disease.
    This is the inverse of the variant-first approach - disease-first search.
    """
    disease_name = payload.disease.strip()
    
    if not disease_name or len(disease_name) < 2:
        raise HTTPException(status_code=400, detail="Disease name must be at least 2 characters")
    
    results = await search_disease_associations(disease_name)
    
    return {
        "disease_query": disease_name,
        "results": results,
        "source": "LOCAL_DISEASE_SEARCH"
    }


@app.get("/api/disease-search/available")
async def list_available_diseases(limit: int = 100):
    """
    Get list of available diseases that can be searched.
    Useful for autocomplete in UI.
    """
    diseases = await get_available_diseases(limit)
    
    return {
        "total_available": len(diseases),
        "diseases": diseases,
        "note": "Diseases from ClinVar disease_names.tsv"
    }


@app.get("/api/datasets/summary")
async def datasets_summary():
    """Get summary of available datasets."""
    summary = await get_dataset_summary()
    return {
        "datasets": summary,
        "timestamp": "2024",
        "note": "Shows first 10 entries per dataset"
    }



@app.get("/api/compounds", response_model=list[CompoundSummary])
async def compounds(query: str = "", limit: int = 20):
    try:
        rows = await search_compounds(query=query, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    out = []
    for r in rows:
        out.append(_compound_row_to_summary(r))
    return out


@app.get("/api/compounds/by-gene/{gene_symbol}", response_model=list[CompoundSummary])
async def compounds_by_gene(gene_symbol: str, limit: int = 20):
    """Return ChEMBL compounds whose targets include the given gene symbol."""
    try:
        rows = await search_compounds_by_gene(gene_symbol=gene_symbol, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return [_compound_row_to_summary(r) for r in rows]


def _compound_row_to_summary(r: dict) -> CompoundSummary:
    return CompoundSummary(
        chembl_id=str(r.get("Compound ChEMBL ID") or ""),
        name=r.get("Name") or None,
        compound_type=r.get("Type") or None,
        max_phase=r.get("Max Phase") or None,
        molecular_weight=r.get("Molecular Weight") or None,
        alogp=r.get("AlogP") or None,
        qed_weighted=r.get("QED Weighted") or None,
        targets=r.get("Targets") or None,
        bioactivities=r.get("Bioactivities") or None,
    )


@app.get("/api/compounds/{chembl_id}", response_model=CompoundDetail)
async def compound_details(chembl_id: str):
    try:
        r = await get_compound(chembl_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not r:
        return CompoundDetail(chembl_id=chembl_id)

    return CompoundDetail(
        chembl_id=str(r.get("Compound ChEMBL ID") or chembl_id),
        name=r.get("Name") or None,
        compound_type=r.get("Type") or None,
        max_phase=r.get("Max Phase") or None,
        molecular_weight=r.get("Molecular Weight") or None,
        alogp=r.get("AlogP") or None,
        qed_weighted=r.get("QED Weighted") or None,
        targets=r.get("Targets") or None,
        bioactivities=r.get("Bioactivities") or None,
        synonyms=r.get("Synonyms") or None,
        polar_surface_area=r.get("Polar Surface Area") or None,
        hba=r.get("HBA") or None,
        hbd=r.get("HBD") or None,
        ro5_violations=r.get("#RO5 Violations") or None,
        rotatable_bonds=r.get("#Rotatable Bonds") or None,
        passes_ro3=r.get("Passes Ro3") or None,
        aromatic_rings=r.get("Aromatic Rings") or None,
        structure_type=r.get("Structure Type") or None,
        inorganic_flag=r.get("Inorganic Flag") or None,
        heavy_atoms=r.get("Heavy Atoms") or None,
        np_likeness_score=r.get("Np Likeness Score") or None,
        molecular_formula=r.get("Molecular Formula") or None,
        smiles=r.get("Smiles") or None,
        inchi_key=r.get("Inchi Key") or None,
        inchi=r.get("Inchi") or None,
        withdrawn_flag=r.get("Withdrawn Flag") or None,
        orphan=r.get("Orphan") or None,
    )


@app.post("/api/phenotypes")
async def get_disease_phenotypes(payload: VariantRequest):
    """Fetch HPO phenotypes associated with a disease name."""
    disease_name = payload.variant  # Reusing variant field for disease name
    try:
        phenotypes = await fetch_phenotypes_for_disease(disease_name)
        return {
            "disease": disease_name,
            "phenotypes": phenotypes,
            "count": len(phenotypes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/motif-analysis")
async def analyze_motif(
    gene_symbol: str,
    ref_aa: str,
    alt_aa: str,
    protein_position: int = None
):
    """Analyze if variant disrupts functional motifs/domains."""
    try:
        result = await analyze_variant_motif_impact(
            protein_sequence="",  # Optional if only checking position
            variant_position=protein_position or 0,
            ref_aa=ref_aa,
            alt_aa=alt_aa,
            gene_symbol=gene_symbol
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conservation-score")
async def get_conservation_score(ref_aa: str, alt_aa: str):
    """Calculate BLOSUM62 conservation score for amino acid substitution."""
    try:
        score, classification = calculate_substitution_cost(ref_aa, alt_aa)
        return {
            "ref_amino_acid": ref_aa,
            "alt_amino_acid": alt_aa,
            "blosum62_score": score,
            "impact_classification": classification,
            "interpretation": {
                "BENIGN": "Conservative substitution - likely tolerated",
                "TOLERATED": "Moderately conservative - may be tolerated",
                "DELETERIOUS": "Non-conservative - likely damaging",
                "SEVERE": "Highly disruptive substitution"
            }.get(classification, "Unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/rsid-to-disease/{rsid}")
async def get_rsid_diseases(rsid: str):
    """
    Get all diseases associated with a given RSID.
    
    Args:
        rsid: SNP rsID (e.g., rs3093017)
    
    Returns:
        List of diseases and associated information for this variant
    
    Example:
        GET /api/rsid-to-disease/rs3093017
    """
    try:
        result = await get_diseases_by_rsid(rsid)
        return {
            "query": rsid,
            "result": result,
            "source": "RSID_TO_DISEASE_MAPPER"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rsid-to-disease/batch")
async def get_rsids_diseases_batch(rsids: List[str]):
    """
    Get diseases associated with multiple RSIDs (batch query).
    
    Args:
        rsids: List of SNP rsIDs
    
    Returns:
        Dictionary with disease associations for each RSID
    
    Example:
        POST /api/rsid-to-disease/batch
        {
            "rsids": ["rs3093017", "rs6311", "rs1234567"]
        }
    """
    try:
        if not rsids or len(rsids) == 0:
            raise HTTPException(status_code=400, detail="At least one RSID required")
        
        if len(rsids) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 RSIDs per batch allowed")
        
        result = await get_diseases_by_rsids(rsids)
        return {
            "query_type": "batch",
            "result": result,
            "source": "RSID_TO_DISEASE_MAPPER"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rsid-to-disease/mapping/info")
async def get_rsid_disease_mapping_info():
    """
    Get information about available RSID-to-Disease mappings.
    
    Returns:
        Statistics about the RSID to Gene to Disease mapping dataset
    
    Example:
        GET /api/rsid-to-disease/mapping/info
    """
    try:
        result = await get_rsid_gene_disease_mapping()
        return {
            "mapping_info": result,
            "source": "ClinVar",
            "note": "Use /api/rsid-to-disease/{rsid} to query specific RSID"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/disease-comprehensive/{variant:path}")
async def comprehensive_disease_lookup(variant: str):
    """
    Comprehensive Variant-to-Disease query pipeline.
    Accepts genomic coordinates (7:140753336:A:T) or RSID (rs113488022).
    Aggregates data from VEP, ClinVar, GWAS Catalog, Ensembl, and PubMed.
    """
    try:
        result = await get_comprehensive_disease(variant)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════
#  PATIENT-BASED ANALYSIS PIPELINE
#  Runs all three GenVarX features (gene variation, disease association,
#  drug discovery) for a single patient and emits a unified report.
# ══════════════════════════════════════════════════════════════════════

async def _run_patient_pipeline(payload: PatientReportRequest) -> dict:
    """Execute gene variation + disease association + drug discovery."""
    # 1. Gene variation analysis (VEP + ClinVar + local datasets)
    gene_result = await annotate(VariantRequest(variant=payload.variant.strip()))

    # 2. Disease association (comprehensive multi-source lookup).
    #    Prefer the explicitly provided rsID, fall back to the variant input.
    disease_source = (payload.rsid or "").strip() or payload.variant.strip()
    comp_result = await get_comprehensive_disease(disease_source)

    # 3. Drug discovery: compounds targeting the identified gene.
    gene_symbol = gene_result.gene_symbol
    if not gene_symbol or gene_symbol in ("N/A", "Unknown", "Multiple", "nan"):
        gene_symbol = (comp_result.get("gene_info") or {}).get("gene_symbol") or "N/A"
    compounds = []
    if gene_symbol and gene_symbol not in ("N/A", "Unknown", "Multiple", "nan"):
        try:
            compounds = await compounds_by_gene(gene_symbol)
        except Exception:
            compounds = []

    return build_report_json(payload, gene_result, comp_result, compounds)


@app.post("/api/patient-report")
async def patient_report(payload: PatientReportRequest):
    """
    Run the full patient analysis pipeline (gene variation, disease
    association, drug discovery) and return the unified patient report.
    """
    try:
        return await _run_patient_pipeline(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patient report failed: {e}")


@app.post("/api/patient-report/assemble")
async def patient_report_assemble(payload: PatientReportRequest):
    """
    Assemble a patient report from previously-generated module outputs
    instead of re-running the three-feature pipeline. The frontend passes
    the captured outputs it already produced:

      captured_results = {
        "gene_variation": {dict from /api/annotate},
        "disease_association": {dict from /api/disease-comprehensive/...},
        "drug_discovery": [list of compound dicts from ChEMBL search],
      }

    Falls back to running the pipeline when no captured data is supplied.
    """
    captured = payload.captured_results or {}

    gene_variation_dict = captured.get("gene_variation") or {}
    comp_result = captured.get("disease_association") or {}
    compounds = captured.get("drug_discovery") or []

    # Normalise the captured gene-variation dict into a VariantAnnotation so the
    # report builder can read it with attribute access.
    if gene_variation_dict:
        gene_result = VariantAnnotation(
            variant=str(gene_variation_dict.get("variant") or payload.variant or "N/A"),
            rs_id=gene_variation_dict.get("rs_id") or None,
            gene_symbol=gene_variation_dict.get("gene_symbol") or "N/A",
            consequence=str(gene_variation_dict.get("consequence") or "N/A"),
            sift_prediction=gene_variation_dict.get("sift_prediction") or "N/A",
            polyphen_prediction=gene_variation_dict.get("polyphen_prediction") or "N/A",
            amino_acid_change=gene_variation_dict.get("amino_acid_change") or "N/A",
            impact_level=str(gene_variation_dict.get("impact_level") or "MODERATE"),
            clinical_significance=gene_variation_dict.get("clinical_significance") or "Not Specified",
            associated_diseases=gene_variation_dict.get("associated_diseases") or [],
        )
    else:
        gene_result = await annotate(VariantRequest(variant=payload.variant))

    return build_report_json(payload, gene_result, comp_result, compounds)


@app.post("/api/patient-report/pdf")
async def patient_report_pdf(payload: dict):
    """
    Render a patient report (the exact JSON returned by POST /api/patient-report)
    into a downloadable authentic PDF document.
    """
    try:
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Expected patient report JSON object")
        pdf_bytes = generate_patient_pdf(payload)
        safe_name = str(payload.get("patient", {}).get("patient_name", "patient")).replace(" ", "_")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="GenVarX_Patient_Report_{safe_name}.pdf"'
                )
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")
