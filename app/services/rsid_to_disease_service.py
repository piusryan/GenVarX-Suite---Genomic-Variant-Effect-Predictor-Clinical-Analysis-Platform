"""
RSID to Disease Mapping Service
Maps variant RSIDs to associated diseases using ClinVar VCF and GWAS TSV datasets
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional
import asyncio


# Cache for VCF data
_vcf_cache = None
_gwas_cache = None

# Cache for resolved RSID -> variant/gene lookups so the ~1.9 GB ClinVar VCF
# is not rescanned line-by-line on every request.
_resolve_cache: Dict[str, Dict[str, Any]] = {}
_RESOLVE_CACHE_MAX = 200

# Cache for RSID -> disease association lookups (also VCF + GWAS scans).
_diseases_by_rsid_cache: Dict[str, Dict[str, Any]] = {}
_DISEASES_CACHE_MAX = 100


async def get_diseases_by_rsid(rsid: str) -> Dict[str, Any]:
    """
    Get all diseases associated with a given RSID.
    
    Args:
        rsid: Single RSID (e.g., 'rs3093017')
    
    Returns:
        Dictionary with disease associations for the RSID
    """
    
    # Validate RSID format
    if not rsid.startswith('rs'):
        return {
            "rsid": rsid,
            "error": "Invalid RSID format. RSID must start with 'rs' (e.g., rs3093017)",
            "diseases": [],
            "total_diseases": 0
        }

    rsid_lower = rsid.lower()
    cached = _diseases_by_rsid_cache.get(rsid_lower)
    if cached is not None:
        return dict(cached)

    results = {
        "rsid": rsid,
        "diseases": [],
        "variants": [],
        "total_diseases": 0,
        "summary": {},
        "error": None
    }
    
    # Search in ClinVar VCF and GWAS TSV
    diseases = await _search_by_rsid(rsid)
    
    results["diseases"] = diseases
    results["total_diseases"] = len(diseases)
    
    # Generate summary
    if diseases:
        results["summary"] = {
            "total_associations": len(diseases),
            "clinical_significances": list(set([d.get("clinical_significance", "Unknown") for d in diseases])),
            "genes_involved": list(set([d.get("gene", "Unknown") for d in diseases if d.get("gene")])),
            "data_source": "ClinVar VCF + GWAS TSV"
        }

    if len(_diseases_by_rsid_cache) >= _DISEASES_CACHE_MAX:
        _diseases_by_rsid_cache.pop(next(iter(_diseases_by_rsid_cache)))
    _diseases_by_rsid_cache[rsid_lower] = dict(results)

    return results


async def get_diseases_by_rsids(rsids: List[str]) -> Dict[str, Any]:
    """
    Get diseases associated with multiple RSIDs (batch query).
    
    Args:
        rsids: List of RSIDs
    
    Returns:
        Dictionary with disease associations for each RSID
    """
    
    results = {
        "total_rsids": len(rsids),
        "rsids_processed": 0,
        "rsids_found": 0,
        "results": {},
        "summary": {}
    }
    
    # Process each RSID
    tasks = [get_diseases_by_rsid(rsid) for rsid in rsids]
    disease_results = await asyncio.gather(*tasks)
    
    rsids_with_diseases = 0
    all_diseases = []
    
    for result in disease_results:
        rsid = result["rsid"]
        results["results"][rsid] = result
        results["rsids_processed"] += 1
        
        if result.get("diseases"):
            rsids_with_diseases += 1
            all_diseases.extend(result["diseases"])
    
    results["rsids_found"] = rsids_with_diseases
    
    # Generate overall summary
    results["summary"] = {
        "total_rsids_queried": len(rsids),
        "rsids_with_disease_associations": rsids_with_diseases,
        "total_disease_associations": len(all_diseases),
        "unique_diseases": len(set([d.get("disease") for d in all_diseases])),
        "unique_genes": len(set([d.get("gene") for d in all_diseases if d.get("gene")])),
        "coverage_percentage": f"{(rsids_with_diseases / len(rsids) * 100):.1f}%" if rsids else "0%"
    }
    
    return results


async def _search_by_rsid(rsid: str) -> List[Dict[str, Any]]:
    """
    Search for RSID in both VCF and GWAS TSV files.
    """
    results = []
    
    # Search VCF file
    vcf_results = await _search_vcf_by_rsid(rsid)
    results.extend(vcf_results)
    
    # Search GWAS TSV file
    gwas_results = await _search_gwas_by_rsid(rsid)
    results.extend(gwas_results)
    
    return results


async def _search_vcf_by_rsid(rsid: str) -> List[Dict[str, Any]]:
    """
    Search ClinVar VCF file for variants matching RSID.
    NOTE: RS IDs are stored in INFO field as RS=1234567, NOT in the ID column.
          The ID column contains ClinVar Variation IDs (e.g., 3385321).
    """
    try:
        vcf_path = "data/datasets/clinvar/clinvar.vcf"
        if not os.path.exists(vcf_path):
            return []

        rsid_lower = rsid.lower()
        rsid_num = rsid_lower[2:] if rsid_lower.startswith('rs') else rsid_lower
        results = []
        info_dict_cache = {}

        with open(vcf_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.startswith('##'):
                    continue
                if line.startswith('#CHROM') or line.startswith('#'):
                    continue
                if not line.strip():
                    continue

                parts = line.strip().split('\t')
                if len(parts) < 8:
                    continue

                chrom = parts[0]
                pos = parts[1]
                ref = parts[3]
                alt = parts[4]
                info = parts[7]

                info_dict_cache.clear()
                for item in info.split(';'):
                    if '=' in item:
                        k, v = item.split('=', 1)
                        info_dict_cache[k] = v

                info_rs = info_dict_cache.get('RS', '')
                match = False
                matched_rs = rsid
                if info_rs:
                    info_rs_ids = info_rs.split('|')
                    for irs in info_rs_ids:
                        if irs == rsid_num or f"rs{irs}" == rsid_lower:
                            match = True
                            matched_rs = f"rs{irs}"
                            break

                if not match:
                    id_col = parts[2]
                    id_ids = id_col.split(';')
                    for vid in id_ids:
                        if vid.lower() == rsid_lower:
                            match = True
                            matched_rs = rsid
                            break

                if match:
                    disease_entries = _parse_vcf_info_multi(
                        info_dict_cache, chrom, pos, ref, alt, matched_rs
                    )
                    results.extend(disease_entries)

        return results

    except Exception as e:
        print(f"[RSID_DISEASE] VCF search error: {e}")
        return []


async def _search_gwas_by_rsid(rsid: str) -> List[Dict[str, Any]]:
    """
    Search GWAS TSV for variants matching RSID.
    Actual GWAS Catalog TSV columns:
      SNPS, DISEASE/TRAIT, P-VALUE, MAPPED_GENE, CHR_ID, CHR_POS,
      STRONGEST SNP-RISK ALLELE, STUDY, PUBMEDID, OR or BETA
    """
    try:
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"
        if not os.path.exists(gwas_path):
            return []

        results = []

        try:
            df = pd.read_csv(
                gwas_path, sep='\t', low_memory=False, dtype=str,
                usecols=['SNPS', 'DISEASE/TRAIT', 'P-VALUE', 'MAPPED_GENE',
                         'CHR_ID', 'CHR_POS', 'STRONGEST SNP-RISK ALLELE',
                         'STUDY', 'PUBMEDID', 'OR or BETA']
            )
        except Exception:
            try:
                df = pd.read_csv(gwas_path, sep='\t', low_memory=False, dtype=str, nrows=50000)
            except Exception:
                return []

        snp_col = 'SNPS' if 'SNPS' in df.columns else None
        for alt in ('variant_id', 'SNPS', 'snp_id', 'SNP_ID_CURRENT'):
            if alt in df.columns:
                snp_col = alt
                break
        if not snp_col:
            return []

        matches = df[df[snp_col].astype(str).str.contains(rsid, na=False, case=False)]

        disease_col = 'DISEASE/TRAIT' if 'DISEASE/TRAIT' in df.columns else (
            'disease_trait' if 'disease_trait' in df.columns else None
        )
        pval_col = 'P-VALUE' if 'P-VALUE' in df.columns else (
            'p_value' if 'p_value' in df.columns else None
        )
        gene_col = 'MAPPED_GENE' if 'MAPPED_GENE' in df.columns else (
            'mapped_gene' if 'mapped_gene' in df.columns else None
        )
        chr_col = 'CHR_ID' if 'CHR_ID' in df.columns else (
            'chr_id' if 'chr_id' in df.columns else None
        )
        pos_col = 'CHR_POS' if 'CHR_POS' in df.columns else (
            'chr_pos' if 'chr_pos' in df.columns else None
        )
        risk_col = 'STRONGEST SNP-RISK ALLELE' if 'STRONGEST SNP-RISK ALLELE' in df.columns else (
            'risk_allele' if 'risk_allele' in df.columns else None
        )
        study_col = 'STUDY' if 'STUDY' in df.columns else None
        pmid_col = 'PUBMEDID' if 'PUBMEDID' in df.columns else None
        or_col = 'OR or BETA' if 'OR or BETA' in df.columns else None

        for _, row in matches.iterrows():
            chrom = str(row[chr_col]) if chr_col and chr_col in row.index else ''
            pos_val = str(row[pos_col]) if pos_col and pos_col in row.index else ''
            disease = str(row[disease_col]) if disease_col and disease_col in row.index and pd.notna(row[disease_col]) else 'Unknown'
            gene = str(row[gene_col]) if gene_col and gene_col in row.index and pd.notna(row[gene_col]) else 'Unknown'
            pval = str(row[pval_col]) if pval_col and pval_col in row.index and pd.notna(row[pval_col]) else 'N/A'
            risk = str(row[risk_col]) if risk_col and risk_col in row.index and pd.notna(row[risk_col]) else ''
            study = str(row[study_col]) if study_col and study_col in row.index and pd.notna(row[study_col]) else ''
            pmid = str(row[pmid_col]) if pmid_col and pmid_col in row.index and pd.notna(row[pmid_col]) else ''
            orval = str(row[or_col]) if or_col and or_col in row.index and pd.notna(row[or_col]) else ''

            disease_info = {
                "source": "GWAS Catalog",
                "rsid": rsid,
                "variant": f"{chrom}:{pos_val}" if chrom and pos_val else '',
                "disease": disease if disease else 'Unknown',
                "gene": gene if gene else 'Unknown',
                "clinical_significance": f"p={pval}",
                "consequence": '',
                "impact": "GWAS_SIGNAL",
                "review_status": "GWAS_CATALOG",
                "conflicting": False,
                "study_accession": study[:60] if study else '',
                "pubmed_id": pmid if pmid else '',
                "strongest_allele": risk if risk else '',
                "or_value": orval if orval else ''
            }
            results.append(disease_info)

        return results[:50]

    except Exception as e:
        print(f"[RSID_DISEASE] GWAS search error: {e}")
        return []


def _clean_disease_name(name: str) -> Optional[str]:
    """
    Clean a disease name from VCF:
      - Replace underscores with spaces
      - Skip 'not_provided', 'not_specified', 'Unknown'
      - Strip whitespace
    Returns cleaned name or None if it should be skipped.
    """
    if not name:
        return None
    cleaned = name.strip().replace('_', ' ')
    lower = cleaned.lower()
    if not cleaned or lower in ('not provided', 'not specified', 'not_provided', 'not_specified', 'unknown', '.', 'na', 'n/a'):
        return None
    return cleaned


def _clean_clinsig(sig: str) -> str:
    """Clean clinical significance string: replace underscores with spaces."""
    if not sig:
        return ''
    return sig.strip().replace('_', ' ')


def _parse_vcf_info_multi(info_dict: Dict[str, str], chrom: str, pos: str, ref: str, alt: str, rsid: str) -> List[Dict[str, Any]]:
    """
    Parse VCF INFO dict and return a list of disease entries (one per disease in CLNDN).
    CLNDN can contain multiple diseases separated by '|'.
    SYMBOL (gene) can come from GENEINFO or MC as fallback.
    """
    gene = info_dict.get('SYMBOL', '')
    if not gene:
        geneinfo = info_dict.get('GENEINFO', '')
        if geneinfo and ':' in geneinfo:
            gene = geneinfo.split(':', 1)[0]

    clnsig = _clean_clinsig(info_dict.get('CLNSIG', ''))
    revstat = _clean_clinsig(info_dict.get('CLNREVSTAT', ''))
    consequence = info_dict.get('Consequence', '')
    impact = info_dict.get('IMPACT', '')

    mc = info_dict.get('MC', '')
    if not consequence and mc and '|' in mc:
        try:
            consequence = mc.split('|', 1)[1].replace('_', ' ')
        except Exception:
            pass

    cldn = info_dict.get('CLNDN', '')
    disease_names = []
    if cldn:
        for raw in cldn.split('|'):
            cleaned = _clean_disease_name(raw)
            if cleaned:
                disease_names.append(cleaned)

    if not disease_names:
        return []

    entries = []
    for dname in disease_names:
        entries.append({
            "source": "ClinVar VCF",
            "rsid": rsid,
            "variant": f"{chrom}:{pos}:{ref}:{alt}",
            "disease": dname,
            "gene": gene if gene else 'Unknown',
            "clinical_significance": clnsig if clnsig else 'Unknown',
            "consequence": consequence,
            "impact": impact,
            "review_status": revstat,
            "conflicting": False
        })
    return entries


def _parse_vcf_info(info_str: str, chrom: str, pos: str, ref: str, alt: str, rsid: str) -> Dict[str, Any]:
    """Backward-compatible wrapper: returns first disease entry or default."""
    info_dict = {}
    for item in info_str.split(';'):
        if '=' in item:
            key, val = item.split('=', 1)
            info_dict[key] = val
    multi = _parse_vcf_info_multi(info_dict, chrom, pos, ref, alt, rsid)
    if multi:
        return multi[0]
    return {
        "source": "ClinVar VCF",
        "rsid": rsid,
        "variant": f"{chrom}:{pos}:{ref}:{alt}",
        "disease": "Unknown",
        "gene": _parse_vcf_info.__defaults__ and 'Unknown' or 'Unknown',
        "clinical_significance": "Unknown",
        "consequence": "",
        "impact": "",
        "review_status": "",
        "conflicting": False
    }


async def get_rsid_gene_disease_mapping() -> Dict[str, Any]:
    """
    Get complete RSID to Gene to Disease mapping from VCF and GWAS.
    Returns summary statistics about available mappings.
    Correctly extracts RS from INFO field (VCF) and uses actual TSV column names.
    """
    try:
        vcf_path = "data/datasets/clinvar/clinvar.vcf"
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"

        mapping: Dict[str, Any] = {}
        unique_rsids = 0

        if os.path.exists(vcf_path):
            try:
                info_dict_cache: Dict[str, str] = {}
                with open(vcf_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        if line.startswith('#'):
                            continue
                        parts = line.strip().split('\t')
                        if len(parts) < 8:
                            continue

                        info = parts[7]
                        info_dict_cache.clear()
                        for item in info.split(';'):
                            if '=' in item:
                                key, val = item.split('=', 1)
                                info_dict_cache[key] = val

                        gene_raw = info_dict_cache.get('SYMBOL', '')
                        if not gene_raw:
                            gi = info_dict_cache.get('GENEINFO', '')
                            if gi and ':' in gi:
                                gene_raw = gi.split(':', 1)[0]

                        cldn_raw = info_dict_cache.get('CLNDN', '')
                        diseases_cleaned: List[str] = []
                        if cldn_raw:
                            for raw in cldn_raw.split('|'):
                                cd = _clean_disease_name(raw)
                                if cd:
                                    diseases_cleaned.append(cd)

                        rs_candidates: List[str] = []
                        rs_val = info_dict_cache.get('RS', '')
                        if rs_val:
                            for r in rs_val.split('|'):
                                if r:
                                    rs_candidates.append(f"rs{r}")
                        for vid in parts[2].split(';'):
                            if vid.lower().startswith('rs'):
                                rs_candidates.append(vid)

                        for rsid in rs_candidates:
                            if rsid not in mapping:
                                mapping[rsid] = {"genes": set(), "diseases": set()}
                                unique_rsids += 1
                            if gene_raw and gene_raw != 'Unknown':
                                mapping[rsid]["genes"].add(gene_raw)
                            for dname in diseases_cleaned:
                                mapping[rsid]["diseases"].add(dname)
            except Exception as e:
                print(f"[RSID_DISEASE] VCF mapping error: {e}")

        if os.path.exists(gwas_path):
            try:
                gwas_cols = None
                test_df = pd.read_csv(gwas_path, sep='\t', low_memory=False, nrows=1)
                all_cols = list(test_df.columns)
                col_map = {}
                for src, candidates in [
                    ('snp', ['SNPS', 'variant_id', 'snp_id', 'SNP_ID_CURRENT']),
                    ('disease', ['DISEASE/TRAIT', 'disease_trait', 'Disease/Trait']),
                    ('gene', ['MAPPED_GENE', 'mapped_gene', 'Mapped Gene'])
                ]:
                    for cand in candidates:
                        if cand in all_cols:
                            col_map[src] = cand
                            break
                if 'snp' in col_map:
                    gwas_cols = [col_map['snp']]
                    for k in ('disease', 'gene'):
                        if k in col_map:
                            gwas_cols.append(col_map[k])

                if gwas_cols:
                    for chunk in pd.read_csv(gwas_path, sep='\t', low_memory=False, dtype=str,
                                             usecols=gwas_cols, chunksize=50000):
                        snp_col = col_map['snp']
                        disease_col = col_map.get('disease')
                        gene_col = col_map.get('gene')
                        for _, row in chunk.iterrows():
                            snp_field = str(row.get(snp_col, '')) if pd.notna(row.get(snp_col, '')) else ''
                            diseases_field = str(row.get(disease_col, 'Unknown')) if disease_col and pd.notna(row.get(disease_col, 'Unknown')) else 'Unknown'
                            gene_field = str(row.get(gene_col, 'Unknown')) if gene_col and pd.notna(row.get(gene_col, 'Unknown')) else 'Unknown'

                            variant_ids = snp_field.split(';') if snp_field else []
                            for rsid in variant_ids:
                                rsid = rsid.strip()
                                if rsid.lower().startswith('rs'):
                                    if rsid not in mapping:
                                        mapping[rsid] = {"genes": set(), "diseases": set()}
                                        unique_rsids += 1
                                    if gene_field and gene_field != 'Unknown':
                                        mapping[rsid]["genes"].add(gene_field)
                                    if diseases_field and diseases_field != 'Unknown':
                                        for single_d in diseases_field.split('|'):
                                            dclean = _clean_disease_name(single_d)
                                            if dclean:
                                                mapping[rsid]["diseases"].add(dclean)
            except Exception as e:
                print(f"[RSID_DISEASE] GWAS mapping error: {e}")

        all_genes: set = set()
        all_diseases: set = set()
        for v in mapping.values():
            all_genes.update(v["genes"])
            all_diseases.update(v["diseases"])
            v["genes"] = list(v["genes"])
            v["diseases"] = list(v["diseases"])

        sample_items = list(mapping.items())[:10]
        sample = {k: v for k, v in sample_items}

        return {
            "available": True,
            "total_unique_rsids": unique_rsids,
            "total_unique_genes": len(all_genes),
            "total_unique_diseases": len(all_diseases),
            "mapping_sample": sample,
            "data_source": "ClinVar VCF + GWAS TSV"
        }

    except Exception as e:
        print(f"[RSID_DISEASE] Mapping retrieval failed: {str(e)}")
        return {"error": str(e), "available": False}


async def resolve_rsid_to_variant(rsid: str) -> Dict[str, Any]:
    """
    Resolve a pure RSID string (e.g. 'rs28934576') to a full chr:pos:ref:alt
    coordinate, gene, and other metadata using:
      1. ClinVar VCF (INFO RS= field + chrom/pos/ref/alt + GENEINFO gene)
      2. GWAS TSV (CHR_ID/CHR_POS + MAPPED_GENE) as fallback

    Returns dict with keys:
        - variant: 'chr:pos:ref:alt' or None if not found
        - chromosome, position, ref, alt
        - rsid: canonical RSID
        - gene_symbol (or None)
        - source: 'ClinVar VCF' | 'GWAS Catalog' | None
        - clinical_significance, diseases[], consequence, impact (if VCF found)
    """
    out = {
        "variant": None,
        "chromosome": None,
        "position": None,
        "ref": None,
        "alt": None,
        "rsid": (rsid or "").strip(),
        "gene_symbol": None,
        "source": None,
        "clinical_significance": None,
        "diseases": [],
        "consequence": None,
        "impact": None,
    }
    if not rsid or not str(rsid).strip().lower().startswith("rs"):
        return out

    rsid_lower = rsid.strip().lower()
    rsid_num = rsid_lower[2:] if rsid_lower.startswith("rs") else rsid_lower

    cached = _resolve_cache.get(rsid_lower)
    if cached is not None:
        return dict(cached)

    def _cache_and_return(o):
        if len(_resolve_cache) >= _RESOLVE_CACHE_MAX:
            _resolve_cache.pop(next(iter(_resolve_cache)))
        _resolve_cache[rsid_lower] = dict(o)
        return o

    vcf_path = "data/datasets/clinvar/clinvar.vcf"
    gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"

    def _clean_name(n):
        if not n: return None
        cleaned = n.strip().replace('_', ' ')
        low = cleaned.lower()
        if not cleaned or low in ('not provided','not specified','not_provided','not_specified','unknown','.','na','n/a'):
            return None
        return cleaned

    # ---- 1. ClinVar VCF search (RS= field) ----
    if os.path.exists(vcf_path):
        try:
            with open(vcf_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) < 8:
                        continue
                    info = parts[7]
                    info_dict = {}
                    for item in info.split(';'):
                        if '=' in item:
                            k, v = item.split('=', 1)
                            info_dict[k] = v

                    matched = False
                    info_rs = info_dict.get('RS', '')
                    if info_rs:
                        for irs in info_rs.split('|'):
                            if irs == rsid_num or f"rs{irs}" == rsid_lower:
                                matched = True
                                break
                    if not matched:
                        for vid in parts[2].split(';'):
                            if vid.lower() == rsid_lower:
                                matched = True
                                break

                    if matched:
                        chrom = parts[0].replace('chr', '')
                        pos = parts[1]
                        ref = parts[3]
                        alt = parts[4]
                        gene = info_dict.get('SYMBOL', '')
                        if not gene:
                            gi = info_dict.get('GENEINFO', '')
                            if gi and ':' in gi:
                                gene = gi.split(':', 1)[0]
                        clinsig_raw = info_dict.get('CLNSIG', '')
                        clin_sig = clinsig_raw.strip().replace('_', ' ') if clinsig_raw else ''

                        consequence = info_dict.get('Consequence', '')
                        mc = info_dict.get('MC', '')
                        if not consequence and mc and '|' in mc:
                            try:
                                consequence = mc.split('|', 1)[1].replace('_', ' ')
                            except Exception:
                                pass

                        impact = info_dict.get('IMPACT', '') or None

                        diseases = []
                        cldn_raw = info_dict.get('CLNDN', '')
                        if cldn_raw:
                            for raw_d in cldn_raw.split('|'):
                                cd = _clean_name(raw_d)
                                if cd:
                                    diseases.append(cd)

                        out.update({
                            "variant": f"{chrom}:{pos}:{ref}:{alt}",
                            "chromosome": chrom,
                            "position": pos,
                            "ref": ref,
                            "alt": alt,
                            "gene_symbol": gene or None,
                            "source": "ClinVar VCF",
                            "clinical_significance": clin_sig or None,
                            "diseases": diseases,
                            "consequence": consequence or None,
                            "impact": impact,
                        })
                        return _cache_and_return(out)
        except Exception as e:
            print(f"[RSID_RESOLVER] VCF lookup failed for {rsid}: {e}")

    # ---- 2. Fallback: GWAS TSV (CHR_ID + CHR_POS + MAPPED_GENE) ----
    if os.path.exists(gwas_path):
        try:
            col_map = {}
            test_df = pd.read_csv(gwas_path, sep='\t', low_memory=False, nrows=1)
            test_cols = list(test_df.columns)
            for src, cands in [
                ('snp', ['SNPS','variant_id','snp_id','SNP_ID_CURRENT']),
                ('chr', ['CHR_ID','chr_id','CHR','chromosome','Chr']),
                ('pos', ['CHR_POS','pos','POS','chr_pos','Position']),
                ('gene', ['MAPPED_GENE','mapped_gene','Mapped Gene','Gene']),
            ]:
                for cand in cands:
                    if cand in test_cols:
                        col_map[src] = cand
                        break
            if 'snp' in col_map:
                use_cols = [col_map['snp']]
                for k in ('chr','pos','gene'):
                    if k in col_map:
                        use_cols.append(col_map[k])

                for chunk in pd.read_csv(gwas_path, sep='\t', low_memory=False, dtype=str,
                                         usecols=use_cols, chunksize=100000):
                    snp_col = col_map['snp']
                    chr_col = col_map.get('chr')
                    pos_col = col_map.get('pos')
                    gene_col = col_map.get('gene')
                    for _, row in chunk.iterrows():
                        snp_raw = str(row.get(snp_col, '')) if pd.notna(row.get(snp_col, '')) else ''
                        if not snp_raw:
                            continue
                        for rs_token in snp_raw.replace('x',';').split(';'):
                            rs_tok = rs_token.strip()
                            if rs_tok.lower() == rsid_lower:
                                chrom = str(row.get(chr_col, '')) if chr_col and pd.notna(row.get(chr_col, '')) else ''
                                pos = str(row.get(pos_col, '')) if pos_col and pd.notna(row.get(pos_col, '')) else ''
                                gene = str(row.get(gene_col, '')) if gene_col and pd.notna(row.get(gene_col, '')) else ''
                                if chrom and pos:
                                    chrom = str(chrom).replace('chr','')
                                    out.update({
                                        "variant": f"{chrom}:{pos}",
                                        "chromosome": chrom,
                                        "position": pos,
                                        "ref": None,
                                        "alt": None,
                                        "gene_symbol": gene or None,
                                        "source": "GWAS Catalog",
                                    })
                                    return _cache_and_return(out)
        except Exception as e:
            print(f"[RSID_RESOLVER] GWAS fallback failed for {rsid}: {e}")

    # ───── 3. Region fallback: if we still have NO bases but the GWAS TSV gave
    #          us CHR_ID + CHR_POS, open the ClinVar VCF and lift REF/ALT from
    #          the first row spanning that position. This is what feeds the
    #          helix glyph (base letters) for rsIDs whose ClinVar row used a
    #          different RS= token or whose VEP call was network-blocked.
    if (not out.get("variant") or not out.get("alt")) and (out.get("chromosome") and out.get("position")):
        try:
            if os.path.exists(vcf_path):
                with open(vcf_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        if line.startswith('#') or not line.strip():
                            continue
                        _c = line.strip().split('\t')
                        if len(_c) < 8:
                            continue
                        _chrom = str(_c[0]).replace('chr', '')
                        if _chrom != str(out.get("chromosome", "")).replace('chr', ''):
                            continue
                        try:
                            _pos = int(_c[1])
                        except Exception:
                            continue
                        if abs(_pos - int(out.get("position", 0))) > 3:
                            continue
                        ref_c, alt_c = (_c[3], _c[4])
                        if not ref_c or ref_c in ('.', '-') or not alt_c or alt_c in ('.', '-'):
                            continue
                        out["variant"] = f"{_chrom}:{_pos}:{ref_c}:{alt_c}"
                        out["position"] = str(_pos)
                        out["ref"] = ref_c
                        out["alt"] = alt_c
                        break
        except Exception as e:
            print(f"[RSID_RESOLVER] Region fallback failed for {rsid}: {e}")

    return _cache_and_return(out)
