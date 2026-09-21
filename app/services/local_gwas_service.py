"""
Local GWAS dataset service - searches against local datasets for disease associations.
This complements the external GWAS Catalog API with local data.
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional


async def search_local_disease_associations(variant: str, gene_symbol: Optional[str] = None) -> Dict[str, Any]:
    """
    Search local datasets for disease associations.
    
    Args:
        variant: Variant coordinates (CHR:POS:REF:ALT)
        gene_symbol: Associated gene symbol (optional)
    
    Returns:
        Dictionary with local findings
    """
    
    results = {
        "variant": variant,
        "gene_symbol": gene_symbol,
        "clinvar_hits": [],
        "hpo_phenotypes": [],
        "disease_names": [],
        "dataset_stats": {}
    }
    
    # Search ClinVar data
    clinvar_hits = await _search_clinvar(variant)
    results["clinvar_hits"] = clinvar_hits
    results["dataset_stats"]["clinvar"] = len(clinvar_hits)
    
    # Search HPO phenotypes if gene found
    if gene_symbol:
        hpo_phenotypes = await _search_hpo_phenotypes(gene_symbol)
        results["hpo_phenotypes"] = hpo_phenotypes
        results["dataset_stats"]["hpo"] = len(hpo_phenotypes)
    
    # Load disease names reference
    disease_names = await _load_disease_names()
    results["disease_names"] = disease_names[:20]  # First 20
    results["dataset_stats"]["disease_names"] = len(disease_names)
    
    return results


async def _search_clinvar(variant: str) -> List[Dict[str, Any]]:
    """Search ClinVar VCF and TSV datasets for variant information."""
    try:
        vcf_path = "data/datasets/clinvar/clinvar.vcf"
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"

        parts = variant.split(':')
        results = []

        def _clean_name(n):
            if not n:
                return None
            cleaned = n.strip().replace('_', ' ')
            low = cleaned.lower()
            if not cleaned or low in (
                'not provided', 'not specified', 'not_provided', 'not_specified',
                'unknown', '.', 'na', 'n/a'
            ):
                return None
            return cleaned

        def _clean_sig(s):
            return s.strip().replace('_', ' ') if s else ''

        # Search VCF
        if os.path.exists(vcf_path):
            try:
                with open(vcf_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        if line.startswith('#'):
                            continue
                        vparts = line.strip().split('\t')
                        if len(vparts) < 8:
                            continue
                        if len(parts) < 2:
                            continue
                        try:
                            chrom_match = vparts[0] == parts[0] or vparts[0] == f"chr{parts[0]}"
                            pos_match = vparts[1] == parts[1]
                            if not (chrom_match and pos_match):
                                continue

                            info = vparts[7] if len(vparts) > 7 else ""
                            info_dict = {}
                            for item in info.split(';'):
                                if '=' in item:
                                    k, v = item.split('=', 1)
                                    info_dict[k] = v

                            gene = info_dict.get('SYMBOL', '')
                            if not gene:
                                gi = info_dict.get('GENEINFO', '')
                                if gi and ':' in gi:
                                    gene = gi.split(':', 1)[0]

                            consequence = info_dict.get('Consequence', '')
                            mc = info_dict.get('MC', '')
                            if not consequence and mc and '|' in mc:
                                try:
                                    consequence = mc.split('|', 1)[1].replace('_', ' ')
                                except Exception:
                                    pass

                            rsid_val = ''
                            info_rs = info_dict.get('RS', '')
                            if info_rs:
                                first_rs = info_rs.split('|')[0]
                                rsid_val = f"rs{first_rs}"
                            else:
                                for vid in vparts[2].split(';'):
                                    if vid.lower().startswith('rs'):
                                        rsid_val = vid
                                        break
                            if not rsid_val:
                                rsid_val = vparts[2]

                            clin_sig = _clean_sig(info_dict.get('CLNSIG', ''))
                            impact = info_dict.get('IMPACT', '')

                            cldn_raw = info_dict.get('CLNDN', '')
                            disease_names: List[str] = []
                            if cldn_raw:
                                for raw_d in cldn_raw.split('|'):
                                    cd = _clean_name(raw_d)
                                    if cd:
                                        disease_names.append(cd)

                            if not disease_names:
                                results.append({
                                    "chromosome": vparts[0],
                                    "position": vparts[1],
                                    "ref": vparts[3],
                                    "alt": vparts[4],
                                    "rsid": rsid_val,
                                    "gene": gene,
                                    "disease": 'Unknown',
                                    "clinical_significance": clin_sig,
                                    "consequence": consequence,
                                    "impact": impact,
                                })
                            else:
                                for dname in disease_names:
                                    results.append({
                                        "chromosome": vparts[0],
                                        "position": vparts[1],
                                        "ref": vparts[3],
                                        "alt": vparts[4],
                                        "rsid": rsid_val,
                                        "gene": gene,
                                        "disease": dname,
                                        "clinical_significance": clin_sig,
                                        "consequence": consequence,
                                        "impact": impact,
                                    })
                        except Exception:
                            continue
            except Exception as e:
                print(f"[LOCAL_GWAS ERROR] VCF search failed: {e}")
        
        # Search GWAS TSV (full scan using the real uppercase column names)
        if os.path.exists(gwas_path):
            try:
                gwas_cols = lambda c: c in {
                    'CHR_ID', 'CHR_POS', 'SNPS', 'MAPPED_GENE', 'DISEASE/TRAIT',
                    'P-VALUE', 'STRONGEST SNP-RISK ALLELE'
                }
                df = pd.read_csv(gwas_path, sep='\t', low_memory=False,
                                 usecols=gwas_cols, dtype=str)
                if 'CHR_ID' in df.columns and 'CHR_POS' in df.columns and len(parts) >= 2:
                    matches = df[(df['CHR_ID'] == parts[0].replace('chr', '')) &
                                (df['CHR_POS'] == parts[1])]
                    
                    for _, row in matches.head(10).iterrows():
                        results.append({
                            "chromosome": str(row.get('CHR_ID', '')),
                            "position": str(row.get('CHR_POS', '')),
                            "ref": str(row.get('REF', '')),
                            "alt": str(row.get('ALT', '')),
                            "rsid": str(row.get('SNPS', '')).split(';')[0],
                            "gene": str(row.get('MAPPED_GENE', '')),
                            "disease": str(row.get('DISEASE/TRAIT', 'Unknown')),
                            "clinical_significance": f"p={row.get('P-VALUE', 'N/A')}",
                            "consequence": "",
                            "impact": "GWAS_SIGNAL"
                        })
            except Exception as e:
                print(f"[LOCAL_GWAS ERROR] GWAS search failed: {e}")
        
        return results[:20]
    
    except Exception as e:
        print(f"[LOCAL_GWAS ERROR] ClinVar search failed: {str(e)}")
        return []


async def _search_hpo_phenotypes(gene_symbol: str) -> List[Dict[str, Any]]:
    """Search HPO phenotypes for a gene from local CSV."""
    try:
        hpo_path = "data/datasets/hpo/genes_to_phenotype.csv"
        if not os.path.exists(hpo_path):
            return []
        
        # Read HPO data
        df = pd.read_csv(hpo_path, low_memory=False)
        
        # Find correct gene column name
        gene_col = None
        for col in df.columns:
            if col.lower() in ['gene_symbol', 'gene', 'symbol']:
                gene_col = col
                break
        
        if not gene_col:
            return []
        
        # Search for matching gene (case-insensitive)
        matches = df[df[gene_col].str.upper() == gene_symbol.upper()].head(15)
        
        results = []
        for _, row in matches.iterrows():
            results.append({
                "gene": str(row.get(gene_col, '')),
                "hpo_id": str(row.get('hpo_id', '')),
                "phenotype": str(row.get('hpo_name', '')),
                "frequency": str(row.get('frequency', '')),
                "disease_id": str(row.get('disease_id', ''))
            })
        
        return results
    
    except Exception as e:
        print(f"[LOCAL_GWAS ERROR] HPO search failed: {str(e)}")
        return []


async def _load_disease_names() -> List[Dict[str, str]]:
    """Load disease names reference."""
    try:
        disease_path = "data/datasets/clinvar/disease_names.tsv"
        if not os.path.exists(disease_path):
            return []
        
        # Read TSV with proper handling
        df = pd.read_csv(disease_path, sep='\t', low_memory=False)
        df.columns = [c.lstrip('#') for c in df.columns]
        
        # First 20 rows
        results = []
        for _, row in df.head(20).iterrows():
            results.append({
                "disease_name": str(row.get('DiseaseName', '')),
                "source": str(row.get('SourceName', '')),
                "concept_id": str(row.get('ConceptID', ''))
            })
        
        return results
    
    except Exception as e:
        print(f"[LOCAL_GWAS ERROR] Disease names loading failed: {str(e)}")
        return []


# Threshold above which we do not line-count a dataset on every request
_RAW_SCAN_LIMIT = 300 * 1024 * 1024  # 300 MB


def _file_size_mb(path: str) -> float:
    try:
        return round(os.path.getsize(path) / (1024 * 1024), 1)
    except Exception:
        return 0.0


def _count_rows(path: str, skip_hash: bool = False) -> int:
    """Count data rows in a file (safe for files below the raw scan limit)."""
    count = 0
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if skip_hash and line.startswith('#'):
                continue
            if line.strip():
                count += 1
    return max(count - 1, 0) if not skip_hash else count


async def get_dataset_summary() -> Dict[str, Any]:
    """Get summary of all available local datasets."""
    summary = {
        "clinvar_vcf": {"exists": False, "rows": None, "size_mb": 0},
        "clinvar_tsv": {"exists": False, "rows": None, "columns": [], "size_mb": 0},
        "gwas_tsv": {"exists": False, "rows": None, "columns": [], "size_mb": 0},
        "hpo": {"exists": False, "rows": None, "columns": [], "size_mb": 0},
        "disease_names": {"exists": False, "rows": None, "columns": [], "size_mb": 0},
        "reference_gff": {"exists": False, "rows": None, "size_mb": 0},
        "reference_tsv": {"exists": False, "rows": None, "columns": [], "size_mb": 0},
        "chembl": {"exists": False, "rows": None, "columns": [], "size_mb": 0}
    }

    try:
        # Check ClinVar VCF
        vcf_path = "data/datasets/clinvar/clinvar.vcf"
        if os.path.exists(vcf_path):
            summary["clinvar_vcf"]["exists"] = True
            summary["clinvar_vcf"]["size_mb"] = _file_size_mb(vcf_path)
            if os.path.getsize(vcf_path) <= _RAW_SCAN_LIMIT:
                summary["clinvar_vcf"]["rows"] = _count_rows(vcf_path, skip_hash=True)
    except:
        pass

    try:
        # Check ClinVar TSV (conflicting)
        clinvar_tsv = "data/datasets/clinvar/clinvar_conflicting.csv"
        if os.path.exists(clinvar_tsv):
            df = pd.read_csv(clinvar_tsv, nrows=1)
            summary["clinvar_tsv"]["exists"] = True
            summary["clinvar_tsv"]["columns"] = list(df.columns)
            summary["clinvar_tsv"]["size_mb"] = _file_size_mb(clinvar_tsv)
            if os.path.getsize(clinvar_tsv) <= _RAW_SCAN_LIMIT:
                summary["clinvar_tsv"]["rows"] = _count_rows(clinvar_tsv)
    except:
        pass

    try:
        # Check GWAS TSV
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"
        if os.path.exists(gwas_path):
            df = pd.read_csv(gwas_path, sep='\t', nrows=1)
            summary["gwas_tsv"]["exists"] = True
            summary["gwas_tsv"]["columns"] = list(df.columns)[:8]
            summary["gwas_tsv"]["size_mb"] = _file_size_mb(gwas_path)
            if os.path.getsize(gwas_path) <= _RAW_SCAN_LIMIT:
                summary["gwas_tsv"]["rows"] = _count_rows(gwas_path)
    except:
        pass

    try:
        # Check HPO
        hpo_path = "data/datasets/hpo/genes_to_phenotype.csv"
        if os.path.exists(hpo_path):
            df = pd.read_csv(hpo_path, nrows=1)
            summary["hpo"]["exists"] = True
            summary["hpo"]["columns"] = list(df.columns)
            summary["hpo"]["size_mb"] = _file_size_mb(hpo_path)
            if os.path.getsize(hpo_path) <= _RAW_SCAN_LIMIT:
                summary["hpo"]["rows"] = _count_rows(hpo_path)
    except:
        pass

    try:
        # Check disease names
        disease_path = "data/datasets/clinvar/disease_names.tsv"
        if os.path.exists(disease_path):
            df = pd.read_csv(disease_path, sep='\t', nrows=1)
            summary["disease_names"]["exists"] = True
            summary["disease_names"]["columns"] = list(df.columns)
            summary["disease_names"]["size_mb"] = _file_size_mb(disease_path)
            if os.path.getsize(disease_path) <= _RAW_SCAN_LIMIT:
                summary["disease_names"]["rows"] = _count_rows(disease_path)
    except:
        pass

    try:
        # Check GFF3 reference files
        gff_paths = [
            "data/datasets/reference/gencode.v50.annotation.gff3",
            "data/datasets/reference/gencode.v50.chr_patch_hapl_scaff.annotation.gff3"
        ]
        for gff_path in gff_paths:
            if os.path.exists(gff_path):
                summary["reference_gff"]["exists"] = True
                summary["reference_gff"]["size_mb"] += _file_size_mb(gff_path)
    except:
        pass

    try:
        # Check TSV reference
        tsv_ref = "data/datasets/reference/humangenome.tsv"
        if os.path.exists(tsv_ref):
            df = pd.read_csv(tsv_ref, sep='\t', nrows=1)
            summary["reference_tsv"]["exists"] = True
            summary["reference_tsv"]["columns"] = list(df.columns)
            summary["reference_tsv"]["size_mb"] = _file_size_mb(tsv_ref)
            if os.path.getsize(tsv_ref) <= _RAW_SCAN_LIMIT:
                summary["reference_tsv"]["rows"] = _count_rows(tsv_ref)
    except:
        pass

    try:
        # Check ChEMBL compounds (semicolon-delimited)
        chembl_path = "data/datasets/chembl/chembl_compounds.csv"
        if os.path.exists(chembl_path):
            df = pd.read_csv(chembl_path, sep=';', nrows=1)
            summary["chembl"]["exists"] = True
            summary["chembl"]["columns"] = list(df.columns)[:8]
            summary["chembl"]["size_mb"] = _file_size_mb(chembl_path)
    except:
        pass

    return summary
