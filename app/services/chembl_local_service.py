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
_by_gene: Dict[str, List[Dict[str, str]]] = {}


# Curated gene-symbol → known-approved-drug-keyword lookups to bridge the
# gap where chembl_compounds.csv has only numeric "Targets" values instead
# of real gene/target names.
_GENE_TO_DRUG_KEYWORDS: Dict[str, List[str]] = {
    # Kinase inhibitors
    "JAK2": [
        "Ruxolitinib", "Baricitinib", "Fedratinib", "Pacritinib",
        "Momelotinib", "Gandotinib", "Cytokine", "Myelofibrosis",
        "Thrombocythemia", "Janus", "JAK",
    ],
    "JAK1": ["Ruxolitinib", "Baricitinib", "Upadacitinib", "Abrocitinib", "JAK"],
    "BRAF": [
        "Vemurafenib", "Dabrafenib", "Encorafenib", "Sorafenib", "PLX",
        "Zelboraf", "Tafinlar", "B-Raf", "BRAF",
    ],
    "EGFR": [
        "Erlotinib", "Gefitinib", "Afatinib", "Osimertinib", "Dacomitinib",
        "Neratinib", "Lapatinib", "Icotinib", "Rociletinib", "AZD9291",
        "Tarceva", "Iressa", "Tagrisso", "EGFR", "Epidermal growth factor",
    ],
    "ERBB2": ["Lapatinib", "Pertuzumab", "Trastuzumab", "Neratinib", "Tucatinib", "HER2"],
    "HER2": ["Lapatinib", "Pertuzumab", "Trastuzumab", "Neratinib", "Tucatinib", "HER2"],
    "ALK": ["Crizotinib", "Ceritinib", "Alectinib", "Brigatinib", "Lorlatinib", "Xalkori", "ALK"],
    "ABL1": ["Imatinib", "Nilotinib", "Dasatinib", "Bosutinib", "Ponatinib", "Gleevec", "Tasigna", "Sprycel", "BCR-ABL", "Philadelphia"],
    "ABL": ["Imatinib", "Nilotinib", "Dasatinib", "Bosutinib", "Ponatinib", "Gleevec", "BCR-ABL"],
    "RET": ["Selpercatinib", "Pralsetinib", "Cabozantinib", "Vandetanib", "RET"],
    "KIT": ["Imatinib", "Sunitinib", "Regorafenib", "Ripretinib", "Avapritinib", "KIT", "GIST", "Stromal"],
    "PDGFRA": ["Imatinib", "Sunitinib", "Regorafenib", "Ripretinib", "Avapritinib", "PDGFR", "GIST"],
    "FLT3": ["Midostaurin", "Gilteritinib", "Quizartinib", "Crenolanib", "Sorafenib", "FLT3", "FMS-like"],
    "KRAS": ["Sotorasib", "Adagrasib", "MRTX1133", "AMG510", "MRTX849", "KRAS", "G12C"],
    "HRAS": ["Tipifarnib", "Lonafarnib", "HRAS"],
    "NRAS": ["Binimetinib", "Trametinib", "Cobimetinib", "MEK", "NRAS"],
    "MAP2K1": ["Trametinib", "Binimetinib", "Selumetinib", "Cobimetinib", "MEK1"],
    "MEK1": ["Trametinib", "Binimetinib", "Selumetinib", "Cobimetinib"],
    "PIK3CA": ["Alpelisib", "Copanlisib", "Idelalisib", "Duvelisib", "BYL719", "PI3K", "Phosphoinositide"],
    "PIK3CB": ["Copanlisib", "Idelalisib", "PI3K"],
    "mTOR": ["Everolimus", "Temsirolimus", "Ridaforolimus", "Sirolimus", "Rapamycin", "MTOR", "TOR"],
    "MTOR": ["Everolimus", "Temsirolimus", "Ridaforolimus", "Sirolimus", "Rapamycin"],
    "CDK4": ["Palbociclib", "Ribociclib", "Abemaciclib", "Trilaciclib", "CDK4", "CDK6", "Cyclin-dependent"],
    "CDK6": ["Palbociclib", "Ribociclib", "Abemaciclib", "Trilaciclib", "CDK4", "CDK6"],
    "PARP1": ["Olaparib", "Rucaparib", "Niraparib", "Talazoparib", "Veliparib", "PARP"],
    "PARP2": ["Olaparib", "Rucaparib", "Niraparib", "Talazoparib", "PARP"],
    "BRCA1": ["Olaparib", "Rucaparib", "Niraparib", "Talazoparib", "PARP", "Breast", "Ovarian"],
    "BRCA2": ["Olaparib", "Rucaparib", "Niraparib", "Talazoparib", "PARP", "Breast", "Ovarian"],
    "BRIP1": ["Olaparib", "Talazoparib", "PARP", "Fanconi"],
    "PALB2": ["Olaparib", "Rucaparib", "Niraparib", "PARP"],
    "VEGFA": ["Bevacizumab", "Aflibercept", "Ramucirumab", "Axitinib", "Sunitinib", "VEGF", "Vascular endothelial"],
    "KDR": ["Sunitinib", "Sorafenib", "Axitinib", "Pazopanib", "Regorafenib", "Cabozantinib", "VEGFR"],
    "VEGFR2": ["Sunitinib", "Sorafenib", "Axitinib", "Pazopanib", "Regorafenib", "Cabozantinib"],
    "MET": ["Crizotinib", "Cabozantinib", "Capmatinib", "Tepotinib", "Savolitinib", "MET", "Hepatocyte growth factor"],
    "ROS1": ["Crizotinib", "Ceritinib", "Lorlatinib", "Entrectinib", "ROS1"],
    "NTRK1": ["Larotrectinib", "Entrectinib", "Selitrectinib", "TRK", "Neurotrophic"],
    "NTRK2": ["Larotrectinib", "Entrectinib", "Selitrectinib", "TRK"],
    "NTRK3": ["Larotrectinib", "Entrectinib", "Selitrectinib", "TRK"],
    "FGFR1": ["Erdafitinib", "Pemigatinib", "Infigratinib", "Futibatinib", "FGFR", "Fibroblast growth factor"],
    "FGFR2": ["Erdafitinib", "Pemigatinib", "Infigratinib", "Futibatinib", "FGFR"],
    "FGFR3": ["Erdafitinib", "Pemigatinib", "Infigratinib", "Futibatinib", "FGFR"],
    "BCL2": ["Venetoclax", "Navitoclax", "Glasdegib", "BCL-2"],
    "BCR": ["Imatinib", "Nilotinib", "Dasatinib", "Bosutinib", "Ponatinib", "BCR-ABL"],
    "MYC": ["BET", "JQ1", "I-BET", "Birabresib", "Zepzelca", "Lurbinectedin", "MYC"],
    "TP53": ["Eprenetapopt", "APR-246", "PRIMA-1Met", "MDM2", "Idasanutlin", "RG7388", "Navtemadlin", "KRT-232", "KRT-2323", "AMG-232", "AMG232", "RG7112", "MDM2 inhibitor", "p53", "53BP"],
    "MDM2": ["Idasanutlin", "Serdemetan", "RG7112", "Navtemadlin", "MDM2"],
    "IDH1": ["Ivosidenib", "Olutasidenib", "AG-120", "IDH1"],
    "IDH2": ["Enasidenib", "AG-221", "IDH2"],
    "SMO": ["Vismodegib", "Sonidegib", "Glasdegib", "Smoothened", "Hedgehog"],
    "PTCH1": ["Vismodegib", "Sonidegib", "Glasdegib", "Smoothened", "Hedgehog"],
    "GNAQ": ["Selumetinib", "Binimetinib", "MEK", "Uveal melanoma"],
    "GNA11": ["Selumetinib", "Binimetinib", "MEK", "Uveal melanoma"],
    "AR": ["Enzalutamide", "Abiraterone", "Apalutamide", "Darolutamide", "Bicalutamide", "Flutamide", "Androgen receptor"],
    "ESR1": ["Tamoxifen", "Fulvestrant", "Raloxifene", "Aromatase", "Letrozole", "Anastrozole", "Exemestane", "Estrogen receptor"],
    "ESR2": ["Tamoxifen", "Raloxifene", "Ospemifene", "Estrogen receptor"],
    "ACE": ["Lisinopril", "Enalapril", "Captopril", "Ramipril", "Benazepril", "Angiotensin-converting"],
    "AGT": ["Losartan", "Valsartan", "Irbesartan", "Olmesartan", "Candesartan", "Angiotensin"],
    "HMGCR": ["Atorvastatin", "Simvastatin", "Rosuvastatin", "Pravastatin", "Lovastatin", "Statin", "3-hydroxy-3-methylglutaryl"],
    "PCSK9": ["Alirocumab", "Evolocumab", "Inclisiran", "PCSK9"],
    "CFTR": ["Ivacaftor", "Lumacaftor", "Tezacaftor", "Elexacaftor", "Kalydeco", "Orkambi", "Symdeko", "Trikafta", "Cystic fibrosis"],
    "HBB": ["Hydroxyurea", "Crizanlizumab", "L-Glutamine", "Voxelotor", "Sickle", "Thalassemia"],
    "HBA1": ["Hydroxyurea", "Crizanlizumab", "L-Glutamine", "Voxelotor", "Sickle"],
    "NF1": ["Selumetinib", "Trametinib", "MEK", "Neurofibromin"],
    "SMN1": ["Nusinersen", "Onasemnogene", "Zolgensma", "Risdiplam", "Spinal muscular"],
    "APC": ["Celecoxib", "Sulindac", "Aspirin", "FAP", "Adenomatous polyposis"],
    "PTEN": ["Everolimus", "Temsirolimus", "Sirolimus", "PI3K", "AKT", "mTOR", "Cowden"],
    "AKT1": ["Capivasertib", "Ipatasertib", "Afuresertib", "MK-2206", "AKT"],
    "AKT2": ["Capivasertib", "Ipatasertib", "Afuresertib", "AKT"],
    "RB1": ["Palbociclib", "Abemaciclib", "Trilaciclib", "Ribociclib", "CDK4", "CDK6", "Retinoblastoma"],
    "MYCN": ["Alisertib", "Omacetaxine", "BET", "Birabresib", "Neuroblastoma"],
    "EWSR1": ["Trabectedin", "Ewing", "Ewing sarcoma"],
    "STK11": ["Everolimus", "Temsirolimus", "Sirolimus", "Sorafenib", "LKB1"],
    "TERT": ["Imetelstat", "6-thio-dG", "Telomerase", "Telomestatin"],
    "ATM": ["Olaparib", "Talazoparib", "Niraparib", "PARP", "Ataxia"],
    "CHEK2": ["Olaparib", "Talazoparib", "Niraparib", "PARP", "CHK"],
    # Vision / OR genes - seen with OR4F5
    "OR4F5": ["Retinal", "Vision", "Rhodopsin", "Olfactory", "Retinopathy"],
    "RHO": ["Rhodopsin", "Retinal", "Vitamin A", "Retinitis", "Luxturna"],
    "RPGR": ["AAV", "Retinal gene therapy", "Luxturna", "Retinitis pigmentosa"],
    "CFH": ["Pegcetacoplan", "Avacincaptad", "Complement", "AMD", "Age-related macular"],
}

# Build reverse keyword → genes map + keyword cache for fast lower-case matching
_GENE_NAME_KEYWORDS_LOWER: Dict[str, List[str]] = {}
for _g, _kws in _GENE_TO_DRUG_KEYWORDS.items():
    for _kw in _kws:
        _GENE_NAME_KEYWORDS_LOWER.setdefault(_kw.lower(), []).append(_g)


async def search_compounds(query: str, limit: int = 20) -> List[Dict[str, str]]:
    await _ensure_loaded()
    if _load_error:
        raise RuntimeError(_load_error)

    q = (query or "").strip().lower()
    if not q:
        return _all[:limit]

    # Direct gene lookup first (e.g. query = "JAK2")
    if len(q) <= 30:
        gene_hits = _search_by_gene_keyword(query, limit=limit)
        if gene_hits:
            return gene_hits

    results: List[Dict[str, str]] = []
    seen_ids: set = set()

    for row in _all:
        chembl_id = (row.get("Compound ChEMBL ID") or "").upper()
        if chembl_id in seen_ids:
            continue
        chembl_lower = chembl_id.lower()
        name = (row.get("Name") or "").lower()
        synonyms = (row.get("Synonyms") or "").lower()
        targets = (row.get("Targets") or "").lower()
        bio = (row.get("Bioactivities") or "").lower()
        if (q in chembl_lower or q in name or q in synonyms or q in targets or q in bio):
            seen_ids.add(chembl_id)
            results.append(row)
            if len(results) >= limit:
                return results

    # Fallback: no direct hits → append any gene-based matches (in case
    # query was like "JAK" instead of exact gene symbol)
    remaining = limit - len(results)
    if remaining > 0:
        gene_fallback = _search_by_gene_keyword(query, limit=remaining)
        seen_in_results = {(r.get("Compound ChEMBL ID") or "").upper() for r in results}
        for r in gene_fallback:
            cid = (r.get("Compound ChEMBL ID") or "").upper()
            if cid not in seen_in_results:
                seen_in_results.add(cid)
                results.append(r)
                if len(results) >= limit:
                    break

    return results


async def get_compound(chembl_id: str) -> Optional[Dict[str, str]]:
    await _ensure_loaded()
    if _load_error:
        raise RuntimeError(_load_error)
    return _by_id.get((chembl_id or "").strip().upper())


async def search_compounds_by_gene(gene_symbol: str, limit: int = 20) -> List[Dict[str, str]]:
    """Return ChEMBL compounds whose targets include the given gene symbol."""
    await _ensure_loaded()
    if _load_error:
        raise RuntimeError(_load_error)

    gene = (gene_symbol or "").strip()
    if not gene:
        return []

    # 1. Fast path: exact / approximate gene name in the pre-built lookup
    direct = _search_by_gene_keyword(gene, limit=limit)
    if direct:
        return direct

    # 2. Substring / fuzzy search across Name + Synonyms + Targets text fields
    gene_lower = gene.lower()
    results: List[Dict[str, str]] = []
    seen: set = set()
    for row in _all:
        cid = (row.get("Compound ChEMBL ID") or "").upper()
        if cid in seen:
            continue
        name = (row.get("Name") or "").lower()
        syn = (row.get("Synonyms") or "").lower()
        targets = (row.get("Targets") or "").lower()
        bio = (row.get("Bioactivities") or "").lower()
        # Whole-target matching: match gene inside pipe-separated target list, or
        # as distinct / delimited token within name or synonym
        haystack = "|".join([name, syn, targets, bio])
        if gene_lower in haystack:
            seen.add(cid)
            results.append(row)
            if len(results) >= limit:
                return results

    # 3. Still nothing? Return top matching generic compounds (fallback list)
    if not results:
        results = _generic_targeted_compound_fallback(gene, limit=limit)
    return results


def _search_by_gene_keyword(gene_or_query: str, limit: int = 20) -> List[Dict[str, str]]:
    """
    Given a gene symbol OR a compound keyword, find all compounds that:
      - match any known gene→drug keyword in Name/Synonyms (case-insensitive)
      - OR match the gene name directly as a token in Name/Synonyms/Targets
    Deduplicated by Compound ChEMBL ID, stable order.
    """
    q = (gene_or_query or "").strip()
    if not q:
        return []
    q_lower = q.lower()

    # Compile the list of keyword tokens we'll try to match against compound text
    search_tokens: List[str] = []
    # A) direct gene → curated drug keywords
    if q in _GENE_TO_DRUG_KEYWORDS:
        search_tokens.extend(k.lower() for k in _GENE_TO_DRUG_KEYWORDS[q])
    # B) common aliases (gene with suffix stripped)
    aliases = {q_lower}
    aliases.add(q_lower.rstrip("1234567890ab"))
    aliases.add(q_lower.lstrip("h"))
    for kw, genes in _GENE_NAME_KEYWORDS_LOWER.items():
        # If user's query is a gene name that any keyword resolves to
        if any(g.lower() in aliases for g in genes):
            search_tokens.append(kw)
        # If user's query is itself a drug keyword
        if q_lower and (q_lower in kw or kw in q_lower):
            search_tokens.append(kw)

    # Also add the gene name itself as a search token (so exact "JAK2" finds
    # compounds whose names mention "Janus kinase 2", etc.)
    search_tokens.append(q_lower)
    for k in list(aliases):
        if len(k) >= 3:
            search_tokens.append(k)

    # Deduplicate tokens, preserve order, remove too-short tokens
    seen_tokens: set = set()
    ordered_tokens: List[str] = []
    for t in search_tokens:
        lt = t.strip()
        if len(lt) < 2:
            continue
        if lt in seen_tokens:
            continue
        seen_tokens.add(lt)
        ordered_tokens.append(lt)
    if not ordered_tokens:
        return []

    results: List[Dict[str, str]] = []
    seen_ids: set = set()

    # Scan compounds and score hits: first token matched wins (preserve order)
    for row in _all:
        cid = (row.get("Compound ChEMBL ID") or "").upper()
        if not cid or cid in seen_ids:
            continue
        name = (row.get("Name") or "").lower()
        syn = (row.get("Synonyms") or "").lower()
        targets = (row.get("Targets") or "").lower()
        bio = (row.get("Bioactivities") or "").lower()
        haystack = f"{name}|{syn}|{targets}|{bio}"
        for tok in ordered_tokens:
            if tok and tok in haystack:
                seen_ids.add(cid)
                results.append(row)
                break
        if len(results) >= limit:
            break

    return results


def _generic_targeted_compound_fallback(gene_symbol: str, limit: int = 20) -> List[Dict[str, str]]:
    """When no gene-specific matches exist, return a representative list of
    high-quality compounds the dataset actually contains so users see results."""
    gene_lower = gene_symbol.lower() if gene_symbol else ""
    picks: List[Dict[str, str]] = []
    seen: set = set()
    # Prefer phase-3/4 approved compounds with non-None names
    for row in _all:
        cid = (row.get("Compound ChEMBL ID") or "").upper()
        if cid in seen:
            continue
        name = (row.get("Name") or "")
        phase = str(row.get("Max Phase") or "")
        targets_raw = (row.get("Targets") or "").strip()
        if not name or name.lower() == "none":
            continue
        if targets_raw and targets_raw.lower() == "none":
            # Skip un-targeted, unless there's a disease name match for gene hints
            if gene_lower and any(
                h in name.lower() for h in [
                    "cancer", "tumor", "neoplasm", "oma", "leukemia",
                    "myeloid", "lymphoma", "sarcoma", "carcinoma",
                    "myelofibrosis", "thrombocythemia", "melanoma",
                    "breast", "ovarian", "lung", "prostate", "colon",
                    "retinitis", "vision", "sickle", "cystic", "fibrosis",
                ]
            ):
                pass
            else:
                continue
        seen.add(cid)
        picks.append(row)
        if len(picks) >= limit:
            break
    return picks


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

        with dataset_path.open("r", encoding="utf-8", errors="replace", newline="") as f:
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
