"""
Patient Report Service

Aggregates the three GenVarX analysis features into a single patient-level
report and renders an authentic PDF document:

  1. Gene Variation  -> annotate endpoint (VEP + ClinVar + local datasets)
  2. Disease Association -> comprehensive disease lookup (associations,
     clinical significance, GWAS findings, HPO phenotypes, publications)
  3. Drug Discovery -> compounds targeting the identified gene (ChEMBL)

PRODUCED BY: the FastAPI endpoint /api/patient-report. This module only
derives the unified JSON payload and builds the PDF bytes.
"""

import uuid
import time
from datetime import datetime
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Palette ────────────────────────────────────────────────────────────
_CYAN = colors.HexColor("#0e7490")
_CYAN_DARK = colors.HexColor("#164e63")
_GREEN = colors.HexColor("#047857")
_PURPLE = colors.HexColor("#6d28d9")
_RED = colors.HexColor("#b91c1c")
_AMBER = colors.HexColor("#b45309")
_SLATE = colors.HexColor("#334155")
_SLATE_LIGHT = colors.HexColor("#64748b")
_BG = colors.HexColor("#f8fafc")
_LINE = colors.HexColor("#cbd5e1")


def _clean(value: Any) -> str:
    """Normalise a value to a non-empty display string."""
    if value is None:
        return "N/A"
    s = str(value).strip()
    if not s or s.lower() in ("nan", "none", "n/a", "null", "unknown", "not available"):
        return "N/A"
    return s


def _g(item: Any, key: str, fallback: Any = None) -> Any:
    """Read an attribute from either a dict or a pydantic/object instance."""
    if item is None:
        return fallback
    if isinstance(item, dict):
        return item.get(key, fallback)
    return getattr(item, key, fallback)


def _safe_text(value: Any) -> str:
    """Strip characters reportlab paragraph flowables cannot render."""
    s = _clean(value)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_report_json(
    payload,
    gene_result,
    comp_result: Dict[str, Any],
    compounds: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Assemble the unified patient report dictionary from pipeline results."""
    gene_info = (comp_result or {}).get("gene_info", {}) or {}

    gene_symbol = _clean(gene_result.gene_symbol)
    if gene_symbol in ("N/A", "Unknown", "Multiple", "nan"):
        gene_symbol = _clean(gene_info.get("gene_symbol"))

    gene_type = _clean(gene_info.get("gene_type"))
    gene_desc = _clean(gene_info.get("description"))
    gene_full = _clean(gene_info.get("full_name"))

    if gene_type in ("N/A", "nan"):
        gene_type = "Not specified"

    drug_compounds = []
    for c in compounds or []:
        name = _g(c, "name") or _g(c, "Name") or None
        drug_compounds.append({
            "chembl_id": _clean(_g(c, "chembl_id") or _g(c, "Compound ChEMBL ID")),
            "name": _clean(name) if name else "Unnamed compound",
            "max_phase": _clean(_g(c, "max_phase") or _g(c, "Max Phase")),
            "molecular_weight": _clean(_g(c, "molecular_weight") or _g(c, "Molecular Weight")),
            "targets": _clean(_g(c, "targets") or _g(c, "Targets")),
            "bioactivities": _clean(_g(c, "bioactivities") or _g(c, "Bioactivities")),
        })

    local_chembl = [
        {
            "chembl_id": _clean(c.get("chembl_id")),
            "name": _clean(c.get("name")) if c.get("name") else "Unnamed compound",
            "max_phase": _clean(c.get("max_phase")),
            "type": _clean(c.get("type")),
        }
        for c in (comp_result or {}).get("chembl_compounds", []) or []
    ]

    now = datetime.now()
    return {
        "report_id": f"GVX-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "patient": {
            "patient_name": _clean(payload.patient_name),
            "patient_id": _clean(payload.patient_id) if payload.patient_id else "N/A",
            "phenotype": _clean(payload.phenotype) if payload.phenotype else "N/A",
        },
        "gene_variation": {
            "input_variant": _clean(payload.variant),
            "variant": _clean(getattr(gene_result, "variant", None)),
            "rs_id": _clean(getattr(gene_result, "rs_id", None)),
            "gene_symbol": gene_symbol,
            "gene_type": gene_type,
            "gene_full_name": gene_full,
            "gene_description": gene_desc,
            "consequence": _clean(getattr(gene_result, "consequence", None)),
            "impact_level": _clean(getattr(gene_result, "impact_level", None)),
            "amino_acid_change": _clean(getattr(gene_result, "amino_acid_change", None)),
            "sift_prediction": _clean(getattr(gene_result, "sift_prediction", None)),
            "polyphen_prediction": _clean(getattr(gene_result, "polyphen_prediction", None)),
            "clinical_significance": _clean(getattr(gene_result, "clinical_significance", None)),
            "associated_diseases": (getattr(gene_result, "associated_diseases", None) or [])[:20],
        },
        "disease_association": {
            "resolved_rsid": _clean((comp_result or {}).get("resolved_rsid")),
            "clinical_significance": _clean((comp_result or {}).get("clinical_significance")),
            "disease_associations": (comp_result or {}).get("disease_associations", []),
            "gwas_findings": (comp_result or {}).get("gwas_findings", [])[:30],
            "hpo_phenotypes": (comp_result or {}).get("hpo_phenotypes", [])[:30],
            "source_counts": (comp_result or {}).get("source_counts", {}),
            "local_dataset_stats": (comp_result or {}).get("local_dataset_stats", {}),
        },
        "publications": (comp_result or {}).get("publications", []),
        "drug_discovery": {
            "gene_symbol": gene_symbol,
            "compounds": drug_compounds,
            "local_chembl_compounds": local_chembl,
        },
    }


# ══════════════════════════════════════════════════════════════════════
#  PDF RENDERING
# ══════════════════════════════════════════════════════════════════════

_SECT_TITLE = ParagraphStyle(
    "SectTitle",
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
    textColor=_CYAN_DARK,
    spaceBefore=14,
    spaceAfter=6,
)

_H2 = ParagraphStyle(
    "H2",
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=12,
    textColor=_SLATE,
    spaceBefore=8,
    spaceAfter=3,
)

_BODY = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=8.5,
    leading=11.5,
    textColor=_SLATE,
    alignment=TA_LEFT,
)

_BODY_SMALL = ParagraphStyle(
    "BodySmall",
    fontName="Helvetica",
    fontSize=7.5,
    leading=10,
    textColor=_SLATE_LIGHT,
)

_CELL = ParagraphStyle(
    "Cell",
    fontName="Helvetica",
    fontSize=7.5,
    leading=9.5,
    textColor=_SLATE,
)

_CELL_BOLD = ParagraphStyle(
    "CellBold",
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=9.5,
    textColor=colors.white,
)

_HEAD = ParagraphStyle(
    "Head",
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=9.5,
    textColor=colors.white,
)

_DISCLAIMER = ParagraphStyle(
    "Disclaimer",
    fontName="Helvetica-Oblique",
    fontSize=6.5,
    leading=8.5,
    textColor=_SLATE_LIGHT,
)


def _kv_table(rows: List[tuple]) -> Table:
    """Render a two-column label/value parameter table."""
    data = []
    for label, value in rows:
        data.append([
            Paragraph(f"<b>{_safe_text(label)}</b>", _CELL),
            Paragraph(_safe_text(value), _CELL),
        ])
    t = Table(data, colWidths=[42 * mm, 122 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), _BG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, _BG]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, _LINE),
    ]))
    return t


def _data_table(headers: List[str], rows: List[list], widths: List[float]) -> Table:
    data = [[Paragraph(h, _HEAD) for h in headers]]
    for row in rows:
        data.append([Paragraph(_safe_text(c), _CELL) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _CYAN_DARK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _BG]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, _LINE),
    ]))
    return t


def _section_banner(title: str, color):
    t = Table([[Paragraph(f"&#x25A0; {_safe_text(title)}", ParagraphStyle(
        "banner", fontName="Helvetica-Bold", fontSize=10, leading=13,
        textColor=colors.white))]])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def _guard(value: Any, fallback: str = "N/A") -> str:
    return _safe_text(value) if value not in (None, "", "N/A", "Unknown", "Multiple", "nan") else fallback


def generate_patient_pdf(report: Dict[str, Any]) -> bytes:
    """Render the patient report dict into PDF bytes."""
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm,
        title=f"GenVarX Patient Report - {report['patient']['patient_name']}",
        author="GenVarX Engine",
    )

    story = []

    # ── Header block ─────────────────────────────────────────────
    header = Table([[Paragraph("GENVARX PATIENT GENOMIC REPORT", ParagraphStyle(
        "title", fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=colors.white))],
        [Paragraph("GENOMIC PATHOLOGY &amp; PHARMACOGENOMICS ANALYSIS :: SYS.V1.0.9", ParagraphStyle(
            "sub", fontName="Helvetica", fontSize=8, leading=10, textColor=_CYAN))]],
        colWidths=[178 * mm])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _CYAN_DARK),
        ("TOPPADDING", (0, 0), (0, 0), 10),
        ("TOPPADDING", (0, 1), (0, 1), 0),
        ("BOTTOMPADDING", (0, 0), (0, 0), 0),
        ("BOTTOMPADDING", (0, 1), (0, 1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(header)
    story.append(Spacer(1, 8))

    # ── Patient identity ─────────────────────────────────────────
    story.append(_section_banner("PATIENT IDENTITY", _CYAN))
    p = report["patient"]
    story.append(_kv_table([
        ("Patient Name", _guard(p.get("patient_name"))),
        ("Patient ID", _guard(p.get("patient_id"))),
        ("Phenotype / Indication", _guard(p.get("phenotype"))),
        ("Report ID", _guard(report.get("report_id"))),
        ("Generated At", _guard(report.get("generated_at"))),
    ]))
    story.append(Spacer(1, 4))

    # ── 1. Gene Variation ────────────────────────────────────────
    gv = report["gene_variation"]
    story.append(_section_banner("1. GENE VARIATION // EFFECT PREDICTION", _GREEN))
    story.append(_kv_table([
        ("Input Variant", _guard(gv.get("input_variant"))),
        ("Resolved Variant", _guard(gv.get("variant"))),
        ("RSID", _guard(gv.get("rs_id"))),
        ("Gene Symbol", _guard(gv.get("gene_symbol"))),
        ("Gene Type", _guard(gv.get("gene_type"))),
        ("Full Gene Name", _guard(gv.get("gene_full_name"))),
        ("What Changed (AA)", _guard(gv.get("amino_acid_change"))),
        ("Consequence", _guard(gv.get("consequence"))),
        ("Impact Level", _guard(gv.get("impact_level"))),
        ("SIFT Prediction", _guard(gv.get("sift_prediction"))),
        ("PolyPhen Prediction", _guard(gv.get("polyphen_prediction"))),
        ("Clinical Significance", _guard(gv.get("clinical_significance"))),
    ]))
    if gv.get("gene_description") not in (None, "", "N/A"):
        story.append(Paragraph(_H2 and "Gene Summary:", _H2))
        story.append(Paragraph(_safe_text(gv["gene_description"]), _BODY))

    assoc = gv.get("associated_diseases") or []
    if assoc:
        story.append(Paragraph("Associated Conditions (from gene-variation pipeline)", _H2))
        story.append(_data_table(
            ["Condition"],
            [[a] for a in assoc],
            [164 * mm],
        ))
    story.append(Spacer(1, 2))

    # ── 2. Disease Association ────────────────────────────────────
    da = report["disease_association"]
    story.append(_section_banner("2. DISEASE ASSOCIATION // MULTI-SOURCE EVIDENCE", _PURPLE))
    sc = da.get("source_counts") or {}
    story.append(_kv_table([
        ("Resolved RSID", _guard(da.get("resolved_rsid"))),
        ("Clinical Significance", _guard(da.get("clinical_significance"))),
        ("Total Associations", _guard(sc.get("total_associations"))),
        ("GWAS Traits (API + Local)", _guard((sc.get("gwas_traits", 0) or 0) + (sc.get("gwas_tsv_local", 0) or 0))),
        ("ClinVar Conditions", _guard(sc.get("clinvar_conditions"))),
        ("Publications Found", _guard(sc.get("publications"))),
    ]))

    diseases = da.get("disease_associations") or []
    if diseases:
        story.append(Paragraph(f"Disease Associations ({len(diseases)})", _H2))
        rows = []
        for d in diseases[:25]:
            rows.append([
                _guard(d.get("disease"), "N/A"),
                _guard(d.get("source"), "N/A"),
                _guard(d.get("pvalue"), ""),
                _guard(d.get("clinical_significance"), ""),
                _guard(d.get("gene"), ""),
            ])
        story.append(_data_table(
            ["Disease / Trait", "Source", "P-Value", "Clinical Sig.", "Gene"],
            rows,
            [52 * mm, 40 * mm, 24 * mm, 32 * mm, 16 * mm],
        ))

    gwas = da.get("gwas_findings") or []
    if gwas:
        story.append(Paragraph(f"GWAS Catalog Findings ({len(gwas)})", _H2))
        rows = []
        for g in gwas[:20]:
            rows.append([
                _guard(g.get("disease")),
                _guard(g.get("pvalue"), ""),
                _guard(g.get("risk_allele"), ""),
                _guard(g.get("gene"), ""),
                _guard(g.get("pubmed_id"), ""),
            ])
        story.append(_data_table(
            ["Disease / Trait", "P-Value", "Risk Allele", "Gene", "PMID"],
            rows,
            [56 * mm, 24 * mm, 32 * mm, 28 * mm, 24 * mm],
        ))

    hpo = da.get("hpo_phenotypes") or []
    if hpo:
        story.append(Paragraph(f"HPO Phenotypes ({len(hpo)})", _H2))
        rows = []
        for hp in hpo[:20]:
            rows.append([
                _guard(hp.get("hpo_id"), ""),
                _guard(hp.get("phenotype"), ""),
                _guard(hp.get("frequency"), ""),
            ])
        story.append(_data_table(
            ["HPO ID", "Phenotype", "Frequency"],
            rows,
            [30 * mm, 96 * mm, 38 * mm],
        ))
    story.append(Spacer(1, 2))

    # ── 3. Publications ───────────────────────────────────────────
    pubs = report.get("publications") or []
    story.append(_section_banner("3. RELATED PUBLICATIONS // PUBMED", _AMBER))
    if pubs:
        for pub in pubs[:10]:
            title = _guard(pub.get("title"), "Untitled")
            authors = _guard(pub.get("authors"), "")
            journal = _guard(pub.get("journal"), "")
            year = _guard(pub.get("year"), "")
            pmid = _guard(pub.get("pubmed_id"), "")
            story.append(Paragraph(f"&#8227; {title}", _BODY))
            story.append(Paragraph(
                f"Authors: {authors} | {journal} ({year}) | PMID: {pmid}",
                _BODY_SMALL,
            ))
            story.append(Spacer(1, 3))
    else:
        story.append(Paragraph("No publications found for this gene/condition.", _BODY))
    story.append(Spacer(1, 2))

    # ── 4. Drug Discovery ─────────────────────────────────────────
    dd = report["drug_discovery"]
    story.append(_section_banner("4. DRUG DISCOVERY // CANDIDATE MEDICINES", colors.HexColor("#7c3aed")))
    story.append(Paragraph(
        f"Compounds targeting gene <b>{_safe_text(dd.get('gene_symbol'))}</b> "
        f"(ChEMBL target match - {(len(dd.get('compounds') or []))} external + "
        f"{(len(dd.get('local_chembl_compounds') or []))} local records)",
        _BODY,
    ))
    compounds = dd.get("compounds") or []
    if compounds:
        rows = []
        for c in compounds[:20]:
            rows.append([
                _guard(c.get("name")),
                _guard(c.get("chembl_id"), ""),
                _guard(c.get("max_phase"), ""),
                _guard(c.get("targets"), ""),
            ])
        story.append(_data_table(
            ["Compound Name", "ChEMBL ID", "Max Phase", "Targets"],
            rows,
            [54 * mm, 34 * mm, 22 * mm, 54 * mm],
        ))
    else:
        local_c = dd.get("local_chembl_compounds") or []
        if local_c:
            rows = []
            for c in local_c[:15]:
                rows.append([
                    _guard(c.get("name")),
                    _guard(c.get("chembl_id"), ""),
                    _guard(c.get("max_phase"), ""),
                    _guard(c.get("type"), ""),
                ])
            story.append(_data_table(
                ["Compound Name", "ChEMBL ID", "Max Phase", "Type"],
                rows,
                [54 * mm, 34 * mm, 22 * mm, 54 * mm],
            ))
        else:
            story.append(Paragraph("No drug-target compounds discovered for this gene.", _BODY))
    story.append(Spacer(1, 6))

    # ── Footer / disclaimer ───────────────────────────────────────
    story.append(Table([[""]], colWidths=[178 * mm],
                       style=[("LINEABOVE", (0, 0), (-1, -1), 0.8, _CYAN)]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "DISCLAIMER: This report is a research-grade computational output generated by the "
        "GenVarX engine from public databases (ClinVar, GWAS Catalog, HPO, ChEMBL, Ensembl VEP, "
        "PubMed). It is provided for informational and educational purposes only and does not "
        "constitute medical advice, diagnosis, or a treatment plan. Any therapeutic decision "
        "must be made by a licensed physician after proper clinical validation.",
        _DISCLAIMER,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()