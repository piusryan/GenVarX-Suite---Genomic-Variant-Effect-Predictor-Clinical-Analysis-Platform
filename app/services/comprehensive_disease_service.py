"""
Comprehensive Variant-to-Disease Query Service

Aggregates disease information from BOTH external APIs AND local datasets:

  External APIs:
    - Ensembl VEP: Variant effect prediction & rsID resolution
    - MyVariant.info / ClinVar: Clinical significance & conditions
    - Ensembl Variation: Gene lookup for direct rsID input
    - GWAS Catalog (EBI): Trait associations with p-values
    - NCBI E-utilities (PubMed): Related publications

  Local Datasets:
    - ClinVar VCF (4.4M variants): Clinical significance, disease names, rsIDs
    - GWAS Catalog TSV (1.18M associations): Trait, p-value, mapped gene
    - HPO genes_to_phenotype (293K entries): Phenotype terms per gene
    - disease_names.tsv (67K entries): Disease metadata & concept IDs
    - clinvar_conflicting.csv (65K entries): Conflicting interpretations
    - ChEMBL compounds (1K entries): Drug-target associations

Provides a unified, reciprocal search pipeline:
  Variant Coordinate → RSID → Disease Associations
"""

import httpx
import asyncio
import os
import pandas as pd
from typing import Dict, List, Any, Optional
from app.services.vep_service import fetch_vep_annotation
from app.services.clinvar_service import fetch_clinvar_data
from app.services.gwas_service import fetch_gwas_associations


# ── External API Endpoints ─────────────────────────────────────────────
ENSEMBL_REST = "https://rest.ensembl.org"
NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

_HEADERS_JSON = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "GenVarX/1.0"}
_HEADERS_XML = {"Accept": "application/xml", "User-Agent": "GenVarX/1.0"}


# ── Local Dataset Paths ──────────────────────────────────────────────
_LOCAL_CLINVAR_VCF = "data/datasets/clinvar/clinvar.vcf"
_LOCAL_GWAS_TSV = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"
_LOCAL_HPO_CSV = "data/datasets/hpo/genes_to_phenotype.csv"
_LOCAL_DISEASE_TSV = "data/datasets/clinvar/disease_names.tsv"
_LOCAL_CLINVAR_CONFLICT = "data/datasets/clinvar/clinvar_conflicting.csv"
_LOCAL_CHEMBL_CSV = "data/datasets/chembl/chembl_compounds.csv"


# ── Ensembl Variation Lookup (rsID → gene & variant details) ──────────
async def _ensembl_variation(rsid: str) -> Dict[str, Any]:
    """
    Query Ensembl REST /variation/human/{rsid} to resolve an rsID
    to its mapped gene, consequence terms, and genomic coordinates.
    """
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            res = await client.get(
                f"{ENSEMBL_REST}/variation/human/{rsid}",
                params={"content-type": "application/json"},
                headers=_HEADERS_JSON,
            )
            if res.status_code != 200:
                return {"gene": None, "consequence": None}

            data = res.json()

            # Extract gene from most_severe_consequence
            gene = None
            consequence = None
            msc = data.get("most_severe_consequence")
            if msc and isinstance(msc, list):
                for entry in msc:
                    if isinstance(entry, dict):
                        gene = gene or entry.get("gene_symbol")
                        consequence = entry.get("consequence_terms", [""])[0] if entry.get("consequence_terms") else None

            # Fallback: extract gene from genomic mappings
            if not gene:
                mappings = data.get("mappings", [])
                if isinstance(mappings, list):
                    for m in mappings:
                        if isinstance(m, dict) and m.get("gene_symbol"):
                            gene = m["gene_symbol"]
                            break

            return {
                "gene": gene,
                "consequence": consequence,
                "rsid": data.get("name", rsid),
            }
        except Exception as e:
            print(f"[DISEASE] Ensembl variation error: {e}")
            return {"gene": None, "consequence": None}


# ── ClinVar via MyVariant.info ─────────────────────────────────────────
async def _clinvar_data(variant_input: str) -> Dict[str, Any]:
    """
    Fetch clinical significance and associated conditions from
    ClinVar via the MyVariant.info aggregation API.
    """
    try:
        result = await fetch_clinvar_data(variant_input)
        clin_sig = result.get("clinical_significance", "")
        diseases = result.get("associated_diseases", [])

        is_found = clin_sig and "Not Found" not in clin_sig and "Uncertain" not in clin_sig
        disease_entries = [
            {"disease": d, "clinical_significance": clin_sig, "source": "ClinVar"}
            for d in diseases if d and d.strip()
        ]

        return {
            "clinical_significance": clin_sig if is_found else None,
            "diseases": disease_entries,
            "found": is_found,
        }
    except Exception as e:
        print(f"[DISEASE] ClinVar error: {e}")
        return {"clinical_significance": None, "diseases": [], "found": False}


# ── GWAS Catalog (EBI REST API + local TSV fallback) ──────────────────
async def _gwas_data(rsid: str) -> Dict[str, Any]:
    """
    Fetch GWAS trait associations from the EBI GWAS Catalog REST API.
    Falls back to the local TSV dump when the API is unreachable.
    """
    try:
        associations = await fetch_gwas_associations(rsid, limit=20)
        trait_entries = [
            {
                "disease": a.get("trait", "Unknown"),
                "pvalue": a.get("pvalue"),
                "gene": a.get("gene") or None,
                "study_id": a.get("study_accession") or None,
                "pubmed_id": a.get("pubmed_id") or None,
                "risk_allele": a.get("strongest_allele") or None,
                "source": "GWAS Catalog",
            }
            for a in associations
        ]
        return {"associations": trait_entries, "found": len(trait_entries) > 0}
    except Exception as e:
        print(f"[DISEASE] GWAS error: {e}")
        return {"associations": [], "found": False}


# ── PubMed Literature Search (NCBI E-utilities) ───────────────────────
async def _pubmed_search(gene: str, disease_terms: List[str] = None) -> List[Dict[str, Any]]:
    """
    Search PubMed for recent publications related to the gene and
    optionally filtered by disease keywords.  Returns up to 10 articles.
    """
    if not gene or gene == "N/A":
        return []

    # Build query: gene + first disease term (or generic "disease")
    disease_word = "disease"
    if disease_terms:
        first = disease_terms[0]
        if first and len(first) < 50:
            disease_word = first.split(",")[0].split("/")[0].strip()

    query = f"{gene}[Gene] AND {disease_word}[Title/Abstract]"

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            # Step 1: Search for article IDs
            search_res = await client.get(
                f"{NCBI_EUTILS}/esearch.fcgi",
                params={
                    "db": "pubmed",
                    "term": query,
                    "retmax": "10",
                    "sort": "relevance",
                    "retmode": "json",
                },
                headers=_HEADERS_XML,
            )
            if search_res.status_code != 200:
                return []

            search_data = search_res.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return []

            # Step 2: Fetch article summaries
            fetch_res = await client.get(
                f"{NCBI_EUTILS}/esummary.fcgi",
                params={"db": "pubmed", "id": ",".join(id_list), "retmode": "json"},
                headers=_HEADERS_XML,
            )
            if fetch_res.status_code != 200:
                return []

            summaries = fetch_res.json().get("result", {})
            publications = []
            for uid in id_list:
                article = summaries.get(uid, {})
                if not isinstance(article, dict):
                    continue
                publications.append({
                    "title": article.get("title", "Untitled"),
                    "authors": ", ".join(
                        a.get("name", "") for a in article.get("authors", [])[:3]
                    ) + ("..." if len(article.get("authors", [])) > 3 else ""),
                    "journal": article.get("fulljournalname", article.get("source", "Unknown")),
                    "year": article.get("pubdate", "")[:4],
                    "pubmed_id": uid,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                })

            return publications
        except Exception as e:
            print(f"[DISEASE] PubMed error: {e}")
            return []


# ── Gene Summary (NCBI Gene API) ──────────────────────────────────────
async def _gene_summary(gene_symbol: str) -> Dict[str, Any]:
    """Fetch gene description and location from NCBI Gene."""
    if not gene_symbol or gene_symbol == "N/A":
        return {}

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            res = await client.get(
                f"https://mygene.info/v3/query",
                params={"q": gene_symbol, "species": "human", "fields": "symbol,name,summary,type_of_gene,genomic_pos", "size": "1"},
                headers=_HEADERS_JSON,
            )
            if res.status_code != 200:
                return {"symbol": gene_symbol}

            hits = res.json().get("hits", [])
            if not hits:
                return {"symbol": gene_symbol}

            hit = hits[0]
            return {
                "symbol": hit.get("symbol", gene_symbol),
                "full_name": hit.get("name", ""),
                "description": hit.get("summary", "")[:500] if hit.get("summary") else "",
                "gene_type": hit.get("type_of_gene", ""),
            }
        except Exception as e:
            print(f"[DISEASE] Gene summary error: {e}")
            return {"symbol": gene_symbol}


# ══════════════════════════════════════════════════════════════════════
#  LOCAL DATASET SEARCH FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

async def _local_clinvar_vcf_search(variant_input: str, is_rsid: bool) -> Dict[str, Any]:
    """
    Search local ClinVar VCF (4.4M variants) by coordinates or RSID.
    Returns clinical significance, disease names, gene, rsID.
    """
    results = []
    rsid_found = None
    clinical_sig = None
    gene_symbol = None
    
    if not os.path.exists(_LOCAL_CLINVAR_VCF):
        return {"hits": [], "rsid": None, "clinical_significance": None, "gene": None, "found": False}
    
    try:
        parts = variant_input.split(':') if not is_rsid else []
        search_chrom = parts[0] if len(parts) >= 2 else None
        search_pos = parts[1] if len(parts) >= 2 else None
        
        with open(_LOCAL_CLINVAR_VCF, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                
                vparts = line.strip().split('\t')
                if len(vparts) < 8:
                    continue
                
                matched = False
                
                if is_rsid:
                    # Match by RSID in the ID column
                    variant_ids = vparts[2].split(';')
                    if variant_input.lower() in [vid.lower() for vid in variant_ids]:
                        matched = True
                else:
                    # Match by chromosome + position
                    chrom = vparts[0].replace('chr', '')
                    pos = vparts[1]
                    if chrom == search_chrom and pos == search_pos:
                        matched = True
                
                if matched:
                    info = vparts[7]
                    info_dict = {}
                    for item in info.split(';'):
                        if '=' in item:
                            k, v = item.split('=', 1)
                            info_dict[k] = v
                    
                    disease = info_dict.get('CLNDN', '')
                    clin_sig = info_dict.get('CLNSIG', '')
                    gene = info_dict.get('SYMBOL', '')
                    consequence = info_dict.get('Consequence', '')
                    impact_val = info_dict.get('IMPACT', '')
                    rsid_val = vparts[2] if vparts[2].startswith('rs') else ''
                    
                    if disease and disease != 'not_provided' and disease != 'not_specified':
                        results.append({
                            "disease": disease.replace('_', ' '),
                            "clinical_significance": clin_sig.replace('_', ' ') if clin_sig else '',
                            "gene": gene,
                            "rsid": rsid_val,
                            "consequence": consequence,
                            "impact": impact_val,
                            "source": "ClinVar VCF (Local)",
                        })
                    
                    if rsid_val and not rsid_found:
                        rsid_found = rsid_val
                    if clin_sig and not clinical_sig:
                        clinical_sig = clin_sig.replace('_', ' ')
                    if gene and not gene_symbol:
                        gene_symbol = gene
    except Exception as e:
        print(f"[DISEASE-LOCAL] ClinVar VCF search error: {e}")
    
    return {
        "hits": results[:30],
        "rsid": rsid_found,
        "clinical_significance": clinical_sig,
        "gene": gene_symbol,
        "found": len(results) > 0,
    }


async def _local_gwas_tsv_search(rsid: str) -> Dict[str, Any]:
    """
    Search local GWAS Catalog TSV (1.18M associations) by RSID.
    Reads the FULL file (not just first 10K rows).
    """
    if not rsid or not os.path.exists(_LOCAL_GWAS_TSV):
        return {"hits": [], "found": False}
    
    try:
        # Actual column names: SNPS, DISEASE/TRAIT, P-VALUE, MAPPED_GENE, CHR_ID, CHR_POS,
        # STRONGEST SNP-RISK ALLELE, STUDY, PUBMEDID, OR or BETA, RISK ALLELE FREQUENCY
        df = pd.read_csv(_LOCAL_GWAS_TSV, sep='\t', low_memory=False,
                         usecols=['SNPS', 'DISEASE/TRAIT', 'P-VALUE', 'MAPPED_GENE',
                                  'CHR_ID', 'CHR_POS', 'STRONGEST SNP-RISK ALLELE', 'STUDY',
                                  'PUBMEDID', 'OR or BETA', 'RISK ALLELE FREQUENCY'])
        
        matches = df[df['SNPS'].astype(str).str.contains(rsid, na=False, case=False)]
        
        results = []
        for _, row in matches.iterrows():
            results.append({
                "disease": str(row.get('DISEASE/TRAIT', 'Unknown')),
                "pvalue": str(row.get('P-VALUE', 'N/A')),
                "gene": str(row.get('MAPPED_GENE', '')),
                "risk_allele": str(row.get('STRONGEST SNP-RISK ALLELE', '')),
                "study_id": str(row.get('STUDY', ''))[:60],
                "pubmed_id": str(row.get('PUBMEDID', '')),
                "or_value": str(row.get('OR or BETA', '')),
                "risk_frequency": str(row.get('RISK ALLELE FREQUENCY', '')),
                "source": "GWAS Catalog TSV (Local)",
            })
        
        return {"hits": results[:50], "found": len(results) > 0}
    except Exception as e:
        print(f"[DISEASE-LOCAL] GWAS TSV search error: {e}")
        return {"hits": [], "found": False}


async def _local_hpo_search(gene_symbol: str) -> Dict[str, Any]:
    """
    Search local HPO genes_to_phenotype.csv (293K entries) by gene symbol.
    Returns phenotype terms, HPO IDs, frequencies, disease IDs.
    """
    if not gene_symbol or not os.path.exists(_LOCAL_HPO_CSV):
        return {"phenotypes": [], "found": False}
    
    try:
        df = pd.read_csv(_LOCAL_HPO_CSV, low_memory=False)
        
        if 'gene_symbol' not in df.columns:
            return {"phenotypes": [], "found": False}
        
        matches = df[df['gene_symbol'].str.upper() == gene_symbol.upper()]
        
        phenotypes = []
        seen = set()
        for _, row in matches.iterrows():
            hpo_id = str(row.get('hpo_id', ''))
            if hpo_id not in seen and hpo_id != 'nan':
                seen.add(hpo_id)
                phenotypes.append({
                    "hpo_id": hpo_id,
                    "phenotype": str(row.get('hpo_name', '')),
                    "frequency": str(row.get('frequency', '')),
                    "disease_id": str(row.get('disease_id', '')),
                })
        
        return {"phenotypes": phenotypes[:30], "found": len(phenotypes) > 0}
    except Exception as e:
        print(f"[DISEASE-LOCAL] HPO search error: {e}")
        return {"phenotypes": [], "found": False}


async def _local_disease_names_lookup(disease_terms: List[str]) -> Dict[str, Any]:
    """
    Look up disease metadata from disease_names.tsv (67K entries).
    Returns concept IDs, sources, categories for matched diseases.
    """
    if not disease_terms or not os.path.exists(_LOCAL_DISEASE_TSV):
        return {"metadata": {}, "found": False}
    
    try:
        # Column name starts with '#' → read and strip it
        df = pd.read_csv(_LOCAL_DISEASE_TSV, sep='\t', low_memory=False)
        # Fix column names: #DiseaseName → DiseaseName
        df.columns = [c.lstrip('#') for c in df.columns]
        
        metadata = {}
        for term in disease_terms:
            if not term or len(term) < 3:
                continue
            term_lower = term.lower()
            if 'DiseaseName' in df.columns:
                matches = df[df['DiseaseName'].str.lower().str.contains(term_lower, na=False, regex=False)]
            else:
                # Fallback: search all string columns
                matches = pd.DataFrame()
                for col in df.columns:
                    if df[col].dtype == object:
                        m = df[df[col].str.lower().str.contains(term_lower, na=False, regex=False)]
                        if len(m) > 0:
                            matches = pd.concat([matches, m]).drop_duplicates()
            
            if len(matches) > 0:
                row = matches.iloc[0]
                metadata[term] = {
                    "official_name": str(row.get('DiseaseName', row.iloc[0] if len(row) > 0 else '')),
                    "concept_id": str(row.get('ConceptID', '')),
                    "source": str(row.get('SourceName', '')),
                    "category": str(row.get('Category', '')),
                    "disease_mim": str(row.get('DiseaseMIM', '')),
                }
        
        return {"metadata": metadata, "found": len(metadata) > 0}
    except Exception as e:
        print(f"[DISEASE-LOCAL] Disease names lookup error: {e}")
        return {"metadata": {}, "found": False}


async def _local_clinvar_conflicting_search(variant_input: str, is_rsid: bool) -> Dict[str, Any]:
    """
    Search clinvar_conflicting.csv (65K entries) for conflicting clinical interpretations.
    """
    if not os.path.exists(_LOCAL_CLINVAR_CONFLICT):
        return {"hits": [], "found": False}
    
    try:
        df = pd.read_csv(_LOCAL_CLINVAR_CONFLICT, low_memory=False)
        
        matches = pd.DataFrame()
        if is_rsid:
            # Search by rsID in any column that might contain it
            for col in df.columns:
                if df[col].dtype == object:
                    col_matches = df[df[col].astype(str).str.contains(variant_input, na=False, case=False)]
                    if len(col_matches) > 0:
                        matches = pd.concat([matches, col_matches]).drop_duplicates()
        else:
            parts = variant_input.split(':')
            if len(parts) >= 2:
                for col in df.columns:
                    if df[col].dtype == object:
                        col_matches = df[df[col].astype(str).str.contains(parts[1], na=False, case=False)]
                        if len(col_matches) > 0:
                            matches = pd.concat([matches, col_matches]).drop_duplicates()
        
        results = []
        for _, row in matches.head(10).iterrows():
            results.append({
                "data": {str(k): str(v) for k, v in row.items() if pd.notna(v) and str(v).strip()},
                "source": "ClinVar Conflicting (Local)",
            })
        
        return {"hits": results, "found": len(results) > 0}
    except Exception as e:
        print(f"[DISEASE-LOCAL] ClinVar conflicting search error: {e}")
        return {"hits": [], "found": False}


async def _local_chembl_search(gene_symbol: str) -> Dict[str, Any]:
    """
    Search ChEMBL compounds targeting the given gene (for drug-gene links).
    """
    if not gene_symbol or not os.path.exists(_LOCAL_CHEMBL_CSV):
        return {"compounds": [], "found": False}
    
    try:
        df = pd.read_csv(_LOCAL_CHEMBL_CSV, sep=';', low_memory=False, encoding='utf-8', on_bad_lines='skip')
        
        # Search in Targets column for gene symbol
        matches = pd.DataFrame()
        if 'Targets' in df.columns:
            matches = df[df['Targets'].astype(str).str.contains(gene_symbol, na=False, case=False)]
        
        results = []
        for _, row in matches.head(10).iterrows():
            results.append({
                "name": str(row.get('Name', '')),
                "chembl_id": str(row.get('Compound ChEMBL ID', '')),
                "max_phase": str(row.get('Max Phase', '')),
                "molecular_weight": str(row.get('Molecular Weight', '')),
                "type": str(row.get('Type', '')),
            })
        
        return {"compounds": results, "found": len(results) > 0}
    except Exception as e:
        print(f"[DISEASE-LOCAL] ChEMBL search error: {e}")
        return {"compounds": [], "found": False}


# ══════════════════════════════════════════════════════════════════════
#  MAIN AGGREGATOR
# ══════════════════════════════════════════════════════════════════════
async def get_comprehensive_disease(variant_input: str) -> Dict[str, Any]:
    """
    Comprehensive Variant-to-Disease query.

    Accepts either:
      - Genomic coordinate: "7:140753336:A:T"  (GRCh38)
      - RSID directly:      "rs113488022"

    Pipeline:
      1. Resolve variant → rsID  (Ensembl VEP)
      2. Fetch clinical significance (MyVariant / ClinVar)
      3. Fetch GWAS trait associations (EBI GWAS Catalog)
      4. Fetch gene metadata (NCBI / mygene.info)
      5. Fetch related publications (PubMed E-utilities)

    Returns a unified dict with all disease evidence aggregated.
    """
    variant_input = variant_input.strip()
    is_rsid = variant_input.lower().startswith("rs") and ":" not in variant_input

    # ── Phase 1: Resolve variant / rsID ────────────────────────────
    vep_result = None
    resolved_rsid = variant_input if is_rsid else None
    gene_symbol = None
    consequence = None
    sift = None
    polyphen = None
    impact = None
    amino_acid = None
    variant_display = variant_input

    if not is_rsid:
        try:
            vep_result = await fetch_vep_annotation(variant_input)
            resolved_rsid = getattr(vep_result, "rs_id", None)
            gene_symbol = getattr(vep_result, "gene_symbol", None)
            consequence = getattr(vep_result, "consequence", None)
            sift = getattr(vep_result, "sift_prediction", None)
            polyphen = getattr(vep_result, "polyphen_prediction", None)
            impact = getattr(vep_result, "impact_level", None)
            amino_acid = getattr(vep_result, "amino_acid_change", None)
        except Exception as e:
            print(f"[DISEASE] VEP error: {e}")

    # ── Phase 2: Parallel API calls (EXTERNAL + LOCAL) ────────────
    clinvar_in = variant_input if not is_rsid else f"{variant_input}:N:N:N"
    ensembl_rsid = resolved_rsid or (variant_input if is_rsid else None)
    gwas_rsid = resolved_rsid or (variant_input if is_rsid else None)

    clinvar_res = {"clinical_significance": None, "diseases": [], "found": False}
    ensembl_res = {"gene": None, "consequence": None}
    gwas_res = {"associations": [], "found": False}
    publications = []
    gene_info = {}

    # --- LOCAL DATASET SEARCHES (run in parallel with external APIs) ---
    local_clinvar = {"hits": [], "rsid": None, "clinical_significance": None, "gene": None, "found": False}
    local_gwas = {"hits": [], "found": False}
    local_hpo = {"phenotypes": [], "found": False}
    local_disease_meta = {"metadata": {}, "found": False}
    local_conflicting = {"hits": [], "found": False}
    local_chembl = {"compounds": [], "found": False}

    # Only call APIs that have valid input
    tasks = {}
    if not is_rsid:
        tasks["clinvar"] = _clinvar_data(variant_input)
    if ensembl_rsid:
        tasks["ensembl"] = _ensembl_variation(ensembl_rsid)
    if gwas_rsid:
        tasks["gwas"] = _gwas_data(gwas_rsid)

    # Local dataset searches (run alongside external APIs)
    tasks["local_clinvar"] = _local_clinvar_vcf_search(variant_input, is_rsid)
    if gwas_rsid:
        tasks["local_gwas"] = _local_gwas_tsv_search(gwas_rsid)
    tasks["local_conflicting"] = _local_clinvar_conflicting_search(variant_input, is_rsid)

    if tasks:
        keys = list(tasks.keys())
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        result_map = dict(zip(keys, results))

        clinvar_res = result_map.get("clinvar", clinvar_res)
        if isinstance(clinvar_res, Exception):
            clinvar_res = {"clinical_significance": None, "diseases": [], "found": False}

        ensembl_res = result_map.get("ensembl", ensembl_res)
        if isinstance(ensembl_res, Exception):
            ensembl_res = {"gene": None, "consequence": None}

        gwas_res = result_map.get("gwas", gwas_res)
        if isinstance(gwas_res, Exception):
            gwas_res = {"associations": [], "found": False}

        # Collect local results
        local_clinvar = result_map.get("local_clinvar", local_clinvar)
        if isinstance(local_clinvar, Exception):
            local_clinvar = {"hits": [], "rsid": None, "clinical_significance": None, "gene": None, "found": False}

        local_gwas = result_map.get("local_gwas", local_gwas)
        if isinstance(local_gwas, Exception):
            local_gwas = {"hits": [], "found": False}

        local_conflicting = result_map.get("local_conflicting", local_conflicting)
        if isinstance(local_conflicting, Exception):
            local_conflicting = {"hits": [], "found": False}

    # Resolve rsID from local ClinVar if external didn't provide one
    if not resolved_rsid and local_clinvar.get("rsid"):
        resolved_rsid = local_clinvar["rsid"]

    # Resolve gene from local ClinVar if external didn't provide one
    if (not gene_symbol or gene_symbol == "N/A") and local_clinvar.get("gene"):
        gene_symbol = local_clinvar["gene"]

    # Resolve clinical significance from local if external failed
    if (not clinvar_res.get("clinical_significance") or clinvar_res.get("clinical_significance") == "Not Available") and local_clinvar.get("clinical_significance"):
        clinvar_res["clinical_significance"] = local_clinvar["clinical_significance"]

    # If we now have an rsID from local, search GWAS local TSV
    if resolved_rsid and not local_gwas.get("found"):
        try:
            local_gwas = await _local_gwas_tsv_search(resolved_rsid)
        except Exception:
            pass

    # Resolve gene from Ensembl if VEP didn't provide one
    if (not gene_symbol or gene_symbol == "N/A") and ensembl_res.get("gene"):
        gene_symbol = ensembl_res["gene"]
    if (not consequence or consequence == "N/A") and ensembl_res.get("consequence"):
        consequence = ensembl_res["consequence"]

    # Run HPO + ChEMBL + disease_names lookup (depend on gene_symbol or disease terms)
    hpo_task = _local_hpo_search(gene_symbol) if gene_symbol and gene_symbol != "N/A" else None
    chembl_task = _local_chembl_search(gene_symbol) if gene_symbol and gene_symbol != "N/A" else None

    # Collect disease terms for disease_names lookup
    disease_terms_for_meta = []
    for d in clinvar_res.get("diseases", []):
        disease_terms_for_meta.append(d.get("disease", ""))
    for h in local_clinvar.get("hits", []):
        disease_terms_for_meta.append(h.get("disease", ""))
    for h in local_gwas.get("hits", []):
        disease_terms_for_meta.append(h.get("disease", ""))
    disease_terms_for_meta = [t for t in disease_terms_for_meta if t and len(t) > 2][:10]
    
    disease_meta_task = _local_disease_names_lookup(disease_terms_for_meta) if disease_terms_for_meta else None

    secondary_tasks = {}
    if hpo_task:
        secondary_tasks["hpo"] = hpo_task
    if chembl_task:
        secondary_tasks["chembl"] = chembl_task
    if disease_meta_task:
        secondary_tasks["disease_meta"] = disease_meta_task
    if gene_symbol and gene_symbol != "N/A":
        secondary_tasks["gene_info"] = _gene_summary(gene_symbol)

    if secondary_tasks:
        sec_keys = list(secondary_tasks.keys())
        sec_results = await asyncio.gather(*secondary_tasks.values(), return_exceptions=True)
        sec_map = dict(zip(sec_keys, sec_results))

        local_hpo = sec_map.get("hpo", local_hpo)
        if isinstance(local_hpo, Exception):
            local_hpo = {"phenotypes": [], "found": False}

        local_chembl = sec_map.get("chembl", local_chembl)
        if isinstance(local_chembl, Exception):
            local_chembl = {"compounds": [], "found": False}

        local_disease_meta = sec_map.get("disease_meta", local_disease_meta)
        if isinstance(local_disease_meta, Exception):
            local_disease_meta = {"metadata": {}, "found": False}

        gene_info = sec_map.get("gene_info", gene_info)
        if isinstance(gene_info, Exception):
            gene_info = {"symbol": gene_symbol}

    # Fetch publications (depends on gene_symbol + disease terms)
    if gene_symbol and gene_symbol != "N/A":
        all_disease_terms = [a.get("disease", "") for a in gwas_res.get("associations", [])[:3]]
        all_disease_terms += [h.get("disease", "") for h in local_gwas.get("hits", [])[:3]]
        all_disease_terms = [t for t in all_disease_terms if t][:3]
        try:
            publications = await _pubmed_search(gene_symbol, all_disease_terms)
        except Exception:
            publications = []

    # ── Phase 3: Aggregate ALL results (external + local) ─────────
    disease_associations = []
    seen = set()

    # 1. External ClinVar diseases
    for d in clinvar_res.get("diseases", []):
        key = d["disease"].lower().strip()
        if key not in seen:
            seen.add(key)
            disease_associations.append(d)

    # 2. Local ClinVar VCF diseases
    for h in local_clinvar.get("hits", []):
        key = h["disease"].lower().strip()
        if key not in seen:
            seen.add(key)
            disease_associations.append({
                "disease": h["disease"],
                "clinical_significance": h.get("clinical_significance", ""),
                "gene": h.get("gene", ""),
                "rsid": h.get("rsid", ""),
                "consequence": h.get("consequence", ""),
                "impact": h.get("impact", ""),
                "source": "ClinVar VCF (Local)",
            })

    # 3. External GWAS diseases
    for a in gwas_res.get("associations", []):
        key = a["disease"].lower().strip()
        if key not in seen:
            seen.add(key)
            disease_associations.append({
                "disease": a["disease"],
                "pvalue": a.get("pvalue"),
                "gene": a.get("gene"),
                "study_id": a.get("study_id"),
                "pubmed_id": a.get("pubmed_id"),
                "risk_allele": a.get("risk_allele"),
                "source": "GWAS Catalog",
            })

    # 4. Local GWAS TSV diseases
    for h in local_gwas.get("hits", []):
        key = h["disease"].lower().strip()
        if key not in seen:
            seen.add(key)
            disease_associations.append({
                "disease": h["disease"],
                "pvalue": h.get("pvalue"),
                "gene": h.get("gene"),
                "study_id": h.get("study_id"),
                "pubmed_id": h.get("pubmed_id"),
                "risk_allele": h.get("risk_allele"),
                "or_value": h.get("or_value"),
                "risk_frequency": h.get("risk_frequency"),
                "source": "GWAS Catalog TSV (Local)",
            })

    # Build local dataset stats
    local_dataset_stats = {
        "clinvar_vcf": {"used": local_clinvar.get("found", False), "hits": len(local_clinvar.get("hits", []))},
        "gwas_tsv": {"used": local_gwas.get("found", False), "hits": len(local_gwas.get("hits", []))},
        "hpo_phenotypes": {"used": local_hpo.get("found", False), "hits": len(local_hpo.get("phenotypes", []))},
        "disease_names": {"used": local_disease_meta.get("found", False), "matches": len(local_disease_meta.get("metadata", {}))},
        "clinvar_conflicting": {"used": local_conflicting.get("found", False), "hits": len(local_conflicting.get("hits", []))},
        "chembl_compounds": {"used": local_chembl.get("found", False), "hits": len(local_chembl.get("compounds", []))},
    }
    local_total = sum(v["hits"] if "hits" in v else v.get("matches", 0) for v in local_dataset_stats.values())

    return {
        "variant_input": variant_input,
        "variant_display": variant_display,
        "resolved_rsid": resolved_rsid,
        "gene_info": {
            "gene_symbol": gene_symbol or "N/A",
            "full_name": gene_info.get("full_name", ""),
            "description": gene_info.get("description", ""),
            "gene_type": gene_info.get("type_of_gene", ""),
            "consequence": consequence or "N/A",
            "sift_prediction": sift or "N/A",
            "polyphen_prediction": polyphen or "N/A",
            "impact_level": impact or "N/A",
            "amino_acid_change": amino_acid or "N/A",
        },
        "clinical_significance": clinvar_res.get("clinical_significance") or "Not Available",
        "disease_associations": disease_associations,
        "gwas_findings": gwas_res.get("associations", []) + local_gwas.get("hits", []),
        "hpo_phenotypes": local_hpo.get("phenotypes", []),
        "disease_metadata": local_disease_meta.get("metadata", {}),
        "clinvar_conflicting": local_conflicting.get("hits", []),
        "chembl_compounds": local_chembl.get("compounds", []),
        "publications": publications,
        "local_dataset_stats": local_dataset_stats,
        "local_datasets_total_hits": local_total,
        "source_counts": {
            "clinvar_conditions": len(clinvar_res.get("diseases", [])),
            "clinvar_vcf_local": len(local_clinvar.get("hits", [])),
            "gwas_traits": len(gwas_res.get("associations", [])),
            "gwas_tsv_local": len(local_gwas.get("hits", [])),
            "hpo_phenotypes": len(local_hpo.get("phenotypes", [])),
            "publications": len(publications),
            "total_associations": len(disease_associations),
            "local_datasets_used": sum(1 for v in local_dataset_stats.values() if v.get("used", False)),
        },
    }
