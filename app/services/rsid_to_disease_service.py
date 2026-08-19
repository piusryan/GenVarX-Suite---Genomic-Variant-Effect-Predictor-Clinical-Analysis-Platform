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
    VCF format has ID column containing RS IDs.
    """
    try:
        vcf_path = "data/datasets/clinvar/clinvar.vcf"
        if not os.path.exists(vcf_path):
            return []
        
        results = []
        
        # Read VCF file (skip header lines starting with ##)
        with open(vcf_path, 'r') as f:
            for line in f:
                # Skip comment lines
                if line.startswith('##'):
                    continue
                
                # Parse header
                if line.startswith('#CHROM'):
                    headers = line.strip().split('\t')
                    continue
                
                # Parse data lines
                if line.startswith('#') or not line.strip():
                    continue
                
                parts = line.strip().split('\t')
                if len(parts) < 8:
                    continue
                
                # VCF columns: CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO
                chrom = parts[0]
                pos = parts[1]
                variant_ids = parts[2]  # Can be multiple IDs separated by ;
                ref = parts[3]
                alt = parts[4]
                info = parts[7] if len(parts) > 7 else ""
                
                # Check if this RSID matches
                if rsid in variant_ids.split(';'):
                    # Extract disease info from INFO field
                    disease_info = _parse_vcf_info(info, chrom, pos, ref, alt, rsid)
                    results.append(disease_info)
        
        return results
    
    except Exception as e:
        print(f"[RSID_DISEASE] VCF search error: {e}")
        return []


async def _search_gwas_by_rsid(rsid: str) -> List[Dict[str, Any]]:
    """
    Search GWAS TSV for variants matching RSID.
    GWAS has columns like: variant_id, disease_trait, risk_allele, p_value, etc.
    """
    try:
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"
        if not os.path.exists(gwas_path):
            return []
        
        results = []
        
        # Read TSV - only load relevant columns
        try:
            df = pd.read_csv(gwas_path, sep='\t', low_memory=False, 
                           usecols=['variant_id', 'disease_trait', 'risk_allele', 'p_value', 'mapped_gene', 'chr_id', 'chr_pos'])
        except:
            # Try with different column names
            df = pd.read_csv(gwas_path, sep='\t', low_memory=False, nrows=1000)
        
        # Search for RSID
        if 'variant_id' in df.columns:
            matches = df[df['variant_id'].astype(str).str.contains(rsid, na=False, case=False)]
            
            for _, row in matches.iterrows():
                disease_info = {
                    "source": "GWAS Catalog",
                    "rsid": rsid,
                    "variant": f"{row.get('chr_id', '')}:{row.get('chr_pos', '')}",
                    "disease": str(row.get('disease_trait', 'Unknown')),
                    "gene": str(row.get('mapped_gene', 'Unknown')),
                    "clinical_significance": f"p={row.get('p_value', 'N/A')}",
                    "consequence": "",
                    "impact": "GWAS_SIGNAL",
                    "review_status": "GWAS_CATALOG",
                    "conflicting": False
                }
                results.append(disease_info)
        
        return results[:50]
    
    except Exception as e:
        print(f"[RSID_DISEASE] GWAS search error: {e}")
        return []


def _parse_vcf_info(info_str: str, chrom: str, pos: str, ref: str, alt: str, rsid: str) -> Dict[str, Any]:
    """
    Parse VCF INFO field to extract disease and clinical significance.
    INFO format: CLNDN=disease_name;CLNSIG=clinical_sig;SYMBOL=gene_symbol
    """
    info_dict = {}
    for item in info_str.split(';'):
        if '=' in item:
            key, val = item.split('=', 1)
            info_dict[key] = val
    
    return {
        "source": "ClinVar VCF",
        "rsid": rsid,
        "variant": f"{chrom}:{pos}:{ref}:{alt}",
        "disease": info_dict.get('CLNDN', 'Unknown'),
        "gene": info_dict.get('SYMBOL', 'Unknown'),
        "clinical_significance": info_dict.get('CLNSIG', 'Unknown'),
        "consequence": info_dict.get('Consequence', ''),
        "impact": info_dict.get('IMPACT', ''),
        "review_status": info_dict.get('CLNREVSTAT', ''),
        "conflicting": False
    }


async def get_rsid_gene_disease_mapping() -> Dict[str, Any]:
    """
    Get complete RSID to Gene to Disease mapping from VCF and GWAS.
    Returns summary statistics about available mappings.
    """
    try:
        vcf_path = "data/datasets/clinvar/clinvar.vcf"
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"
        
        mapping = {}
        unique_rsids = 0
        unique_genes = 0
        unique_diseases = 0
        
        # Parse VCF
        if os.path.exists(vcf_path):
            try:
                with open(vcf_path, 'r') as f:
                    for line in f:
                        if line.startswith('##') or line.startswith('#'):
                            continue
                        
                        parts = line.strip().split('\t')
                        if len(parts) < 8:
                            continue
                        
                        variant_ids = parts[2].split(';')
                        info = parts[7]
                        
                        info_dict = {}
                        for item in info.split(';'):
                            if '=' in item:
                                key, val = item.split('=', 1)
                                info_dict[key] = val
                        
                        gene = info_dict.get('SYMBOL', 'Unknown')
                        disease = info_dict.get('CLNDN', 'Unknown')
                        
                        for rsid in variant_ids:
                            if rsid.startswith('rs'):
                                if rsid not in mapping:
                                    mapping[rsid] = {"genes": set(), "diseases": set()}
                                    unique_rsids += 1
                                
                                if gene != 'Unknown':
                                    mapping[rsid]["genes"].add(gene)
                                if disease != 'Unknown':
                                    mapping[rsid]["diseases"].add(disease)
            except Exception as e:
                print(f"[RSID_DISEASE] VCF mapping error: {e}")
        
        # Parse GWAS TSV
        if os.path.exists(gwas_path):
            try:
                df = pd.read_csv(gwas_path, sep='\t', low_memory=False, nrows=10000)
                
                if 'variant_id' in df.columns and 'disease_trait' in df.columns:
                    for _, row in df.iterrows():
                        variant_ids = str(row.get('variant_id', '')).split(';')
                        disease = str(row.get('disease_trait', 'Unknown'))
                        gene = str(row.get('mapped_gene', 'Unknown'))
                        
                        for rsid in variant_ids:
                            if rsid.startswith('rs'):
                                if rsid not in mapping:
                                    mapping[rsid] = {"genes": set(), "diseases": set()}
                                    unique_rsids += 1
                                
                                if gene != 'Unknown':
                                    mapping[rsid]["genes"].add(gene)
                                if disease != 'Unknown':
                                    mapping[rsid]["diseases"].add(disease)
            except Exception as e:
                print(f"[RSID_DISEASE] GWAS mapping error: {e}")
        
        # Convert sets to lists
        for rsid in mapping:
            mapping[rsid]["genes"] = list(mapping[rsid]["genes"])
            mapping[rsid]["diseases"] = list(mapping[rsid]["diseases"])
        
        return {
            "available": True,
            "total_unique_rsids": unique_rsids,
            "total_unique_genes": len(set().union(*[set(v["genes"]) for v in mapping.values()])),
            "total_unique_diseases": len(set().union(*[set(v["diseases"]) for v in mapping.values()])),
            "mapping_sample": {k: v for k, v in list(mapping.items())[:10]},
            "data_source": "ClinVar VCF + GWAS TSV"
        }
    
    except Exception as e:
        print(f"[RSID_DISEASE] Mapping retrieval failed: {str(e)}")
        return {"error": str(e), "available": False}
