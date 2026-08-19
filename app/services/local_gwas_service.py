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
        
        # Parse variant coordinates
        parts = variant.split(':')
        results = []
        
        # Search VCF
        if os.path.exists(vcf_path):
            try:
                with open(vcf_path, 'r') as f:
                    for line in f:
                        if line.startswith('##') or line.startswith('#'):
                            continue
                        
                        vparts = line.strip().split('\t')
                        if len(vparts) < 8:
                            continue
                        
                        # Match chromosome and position
                        if len(parts) >= 2:
                            try:
                                chrom_match = vparts[0] == parts[0] or vparts[0] == f"chr{parts[0]}"
                                pos_match = vparts[1] == parts[1]
                                
                                if chrom_match and pos_match:
                                    info = vparts[7] if len(vparts) > 7 else ""
                                    info_dict = {}
                                    for item in info.split(';'):
                                        if '=' in item:
                                            k, v = item.split('=', 1)
                                            info_dict[k] = v
                                    
                                    results.append({
                                        "chromosome": vparts[0],
                                        "position": vparts[1],
                                        "ref": vparts[3],
                                        "alt": vparts[4],
                                        "rsid": vparts[2],
                                        "gene": info_dict.get('SYMBOL', ''),
                                        "disease": info_dict.get('CLNDN', 'Unknown'),
                                        "clinical_significance": info_dict.get('CLNSIG', ''),
                                        "consequence": info_dict.get('Consequence', ''),
                                        "impact": info_dict.get('IMPACT', '')
                                    })
                            except:
                                pass
            except Exception as e:
                print(f"[LOCAL_GWAS ERROR] VCF search failed: {e}")
        
        # Search GWAS TSV
        if os.path.exists(gwas_path):
            try:
                df = pd.read_csv(gwas_path, sep='\t', low_memory=False, nrows=5000)
                if 'chr_id' in df.columns and 'chr_pos' in df.columns and len(parts) >= 2:
                    matches = df[(df['chr_id'].astype(str) == parts[0]) & 
                                (df['chr_pos'].astype(str) == parts[1])]
                    
                    for _, row in matches.head(10).iterrows():
                        results.append({
                            "chromosome": str(row.get('chr_id', '')),
                            "position": str(row.get('chr_pos', '')),
                            "ref": str(row.get('effect_allele', '')),
                            "alt": str(row.get('other_allele', '')),
                            "rsid": str(row.get('variant_id', '')),
                            "gene": str(row.get('mapped_gene', '')),
                            "disease": str(row.get('disease_trait', 'Unknown')),
                            "clinical_significance": f"p={row.get('p_value', 'N/A')}",
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


async def get_dataset_summary() -> Dict[str, Any]:
    """Get summary of all available local datasets."""
    summary = {
        "clinvar_vcf": {"exists": False, "rows": 0},
        "clinvar_tsv": {"exists": False, "rows": 0, "columns": []},
        "gwas_tsv": {"exists": False, "rows": 0, "columns": []},
        "hpo": {"exists": False, "rows": 0, "columns": []},
        "disease_names": {"exists": False, "rows": 0, "columns": []},
        "reference_gff": {"exists": False, "rows": 0},
        "reference_tsv": {"exists": False, "rows": 0}
    }
    
    try:
        # Check ClinVar VCF
        vcf_path = "data/datasets/clinvar/clinvar.vcf"
        if os.path.exists(vcf_path):
            summary["clinvar_vcf"]["exists"] = True
            with open(vcf_path) as f:
                summary["clinvar_vcf"]["rows"] = sum(1 for line in f if not line.startswith('#'))
    except:
        pass
    
    try:
        # Check ClinVar TSV (conflicting)
        clinvar_tsv = "data/datasets/clinvar/clinvar_conflicting.csv"
        if os.path.exists(clinvar_tsv):
            df = pd.read_csv(clinvar_tsv, nrows=1)
            summary["clinvar_tsv"]["exists"] = True
            summary["clinvar_tsv"]["columns"] = list(df.columns)
            with open(clinvar_tsv) as f:
                summary["clinvar_tsv"]["rows"] = sum(1 for _ in f) - 1
    except:
        pass
    
    try:
        # Check GWAS TSV
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"
        if os.path.exists(gwas_path):
            df = pd.read_csv(gwas_path, sep='\t', nrows=1)
            summary["gwas_tsv"]["exists"] = True
            summary["gwas_tsv"]["columns"] = list(df.columns)[:5]
            with open(gwas_path) as f:
                summary["gwas_tsv"]["rows"] = sum(1 for _ in f) - 1
    except:
        pass
    
    try:
        # Check HPO
        hpo_path = "data/datasets/hpo/genes_to_phenotype.csv"
        if os.path.exists(hpo_path):
            df = pd.read_csv(hpo_path, nrows=1)
            summary["hpo"]["exists"] = True
            summary["hpo"]["columns"] = list(df.columns)
            with open(hpo_path) as f:
                summary["hpo"]["rows"] = sum(1 for _ in f) - 1
    except:
        pass
    
    try:
        # Check disease names
        disease_path = "data/datasets/clinvar/disease_names.tsv"
        if os.path.exists(disease_path):
            df = pd.read_csv(disease_path, sep='\t', nrows=1)
            summary["disease_names"]["exists"] = True
            summary["disease_names"]["columns"] = list(df.columns)
            with open(disease_path) as f:
                summary["disease_names"]["rows"] = sum(1 for _ in f) - 1
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
                with open(gff_path) as f:
                    summary["reference_gff"]["rows"] += sum(1 for line in f if not line.startswith('#'))
    except:
        pass
    
    try:
        # Check TSV reference
        tsv_ref = "data/datasets/reference/humangenome.tsv"
        if os.path.exists(tsv_ref):
            df = pd.read_csv(tsv_ref, sep='\t', nrows=1)
            summary["reference_tsv"]["exists"] = True
            with open(tsv_ref) as f:
                summary["reference_tsv"]["rows"] = sum(1 for _ in f) - 1
    except:
        pass
    
    return summary
