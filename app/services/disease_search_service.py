"""
Disease-based search service - Find variants, genes, and drugs associated with diseases
Uses local datasets: ClinVar, HPO, ChEMBL
"""

import pandas as pd
import os
from typing import Dict, List, Any, Optional
import asyncio


async def search_disease_associations(disease_name: str) -> Dict[str, Any]:
    """
    Comprehensive disease search using multiple local datasets.
    
    Args:
        disease_name: Disease name to search for
    
    Returns:
        Dictionary with disease associations from all available datasets
    """
    
    # Check if user is trying to input RSID or variant instead of disease name
    is_rsid = disease_name.startswith('rs') and disease_name[2:].isdigit()
    is_variant = ':' in disease_name and disease_name.count(':') >= 2
    
    results = {
        "query": disease_name,
        "is_rsid_input": is_rsid,
        "is_variant_input": is_variant,
        "variants": [],
        "genes": [],
        "phenotypes": [],
        "drugs": [],
        "disease_metadata": {},
        "summary": {},
        "warning": None
    }
    
    # Show warning if user is inputting RSID/variant
    if is_rsid:
        results["warning"] = "You entered an RSID. For variant searches, use the GENE VARIANT module instead."
        return results
    
    if is_variant:
        results["warning"] = "You entered a genomic variant. For variant searches, use the GENE VARIANT module instead."
        return results
    
    # Run all searches in parallel
    tasks = [
        _search_clinvar_by_disease(disease_name),
        _search_genes_by_disease(disease_name),
        _search_phenotypes_by_disease(disease_name),
        _search_drugs_by_disease(disease_name),
        _get_disease_metadata(disease_name),
    ]
    
    variant_hits, gene_hits, phenotype_hits, drug_hits, metadata = await asyncio.gather(*tasks)
    
    results["variants"] = variant_hits
    results["genes"] = gene_hits
    results["phenotypes"] = phenotype_hits
    results["drugs"] = drug_hits
    results["disease_metadata"] = metadata
    
    # Summary statistics
    results["summary"] = {
        "total_variants_found": len(variant_hits),
        "total_genes_found": len(gene_hits),
        "total_phenotypes_found": len(phenotype_hits),
        "total_drugs_found": len(drug_hits),
        "disease_sources": metadata.get("sources", [])
    }
    
    return results


async def _search_clinvar_by_disease(disease_name: str) -> List[Dict[str, Any]]:
    """Search ClinVar VCF and TSV for variants associated with a disease."""
    try:
        vcf_path = "data/datasets/clinvar/clinvar.vcf"
        disease_tsv_path = "data/datasets/clinvar/disease_names.tsv"
        gwas_path = "data/datasets/clinvar/gwas-catalog-download-associations-v1.0-full.tsv"

        results = []
        disease_lower = disease_name.lower()

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

        # Search disease names TSV to find related RSIDs
        disease_rsids = set()
        if os.path.exists(disease_tsv_path):
            try:
                df = pd.read_csv(disease_tsv_path, sep='\t', low_memory=False)
                df.columns = [c.lstrip('#') for c in df.columns]
                if 'DiseaseName' in df.columns:
                    matches = df[df['DiseaseName'].str.lower().str.contains(disease_lower, na=False, regex=False)]
                    disease_rsids = set(matches.get('ConceptID', []).unique() if 'ConceptID' in matches.columns else [])
            except Exception as e:
                print(f"[DISEASE_SEARCH] Disease TSV search error: {e}")

        # Search VCF for matching diseases
        if os.path.exists(vcf_path):
            try:
                with open(vcf_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        if line.startswith('#'):
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

                        cldn_raw = info_dict.get('CLNDN', '')
                        disease_names = []
                        if cldn_raw:
                            for raw_d in cldn_raw.split('|'):
                                cd = _clean_name(raw_d)
                                if cd:
                                    disease_names.append(cd)

                        matched_diseases = [d for d in disease_names if disease_lower in d.lower()]
                        if not matched_diseases:
                            continue

                        gene = info_dict.get('SYMBOL', '')
                        if not gene:
                            gi = info_dict.get('GENEINFO', '')
                            if gi and ':' in gi:
                                gene = gi.split(':', 1)[0]
                        if not gene:
                            gene = 'Unknown'

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
                            for vid in parts[2].split(';'):
                                if vid.lower().startswith('rs'):
                                    rsid_val = vid
                                    break
                        if not rsid_val:
                            rsid_val = parts[2]

                        clin_sig = _clean_sig(info_dict.get('CLNSIG', '')) or 'Unknown'
                        impact = info_dict.get('IMPACT', '')

                        for dname in matched_diseases:
                            results.append({
                                "source": "ClinVar VCF",
                                "variant": f"{parts[0]}:{parts[1]}:{parts[3]}:{parts[4]}",
                                "rsid": rsid_val,
                                "gene": gene,
                                "disease": dname,
                                "clinical_significance": clin_sig,
                                "consequence": consequence,
                                "impact": impact,
                            })
                            if len(results) >= 30:
                                break
                        if len(results) >= 30:
                            break
            except Exception as e:
                print(f"[DISEASE_SEARCH] VCF search error: {e}")
        
        # Search GWAS TSV (full scan using the real uppercase column names)
        if os.path.exists(gwas_path):
            try:
                gwas_cols = lambda c: c in {
                    'CHR_ID', 'CHR_POS', 'SNPS', 'MAPPED_GENE', 'DISEASE/TRAIT',
                    'P-VALUE', 'STRONGEST SNP-RISK ALLELE'
                }
                df = pd.read_csv(gwas_path, sep='\t', low_memory=False,
                                 usecols=gwas_cols, dtype=str)
                if 'DISEASE/TRAIT' in df.columns:
                    matches = df[df['DISEASE/TRAIT'].str.lower().str.contains(disease_lower, na=False, regex=False)]
                    for _, row in matches.head(10).iterrows():
                        results.append({
                            "source": "GWAS Catalog",
                            "variant": f"{row.get('CHR_ID', '')}:{row.get('CHR_POS', '')}",
                            "rsid": str(row.get('SNPS', '')).split(';')[0],
                            "gene": str(row.get('MAPPED_GENE', 'Unknown')),
                            "disease": str(row.get('DISEASE/TRAIT', '')),
                            "clinical_significance": f"p={row.get('P-VALUE', 'N/A')}",
                            "consequence": "",
                            "impact": "GWAS_SIGNAL"
                        })
            except Exception as e:
                print(f"[DISEASE_SEARCH] GWAS search error: {e}")
        
        return results[:25]
    
    except Exception as e:
        print(f"[DISEASE_SEARCH] ClinVar search failed: {str(e)}")
        return []


async def _search_genes_by_disease(disease_name: str) -> List[Dict[str, Any]]:
    """Search HPO for genes associated with disease phenotypes."""
    try:
        hpo_path = "data/datasets/hpo/genes_to_phenotype.csv"
        if not os.path.exists(hpo_path):
            return []
        
        results = []
        disease_lower = disease_name.lower()
        
        df = pd.read_csv(hpo_path, low_memory=False)
        
        # Search for disease in various columns
        if 'disease_name' in df.columns:
            matches = df[df['disease_name'].str.lower().str.contains(disease_lower, na=False, regex=False)]
        elif 'gene_symbol' in df.columns:
            # Alternative: search by phenotype relevance
            matches = df[df.index.isin(df.index)]  # Will be filtered below
        else:
            return []
        
        seen_genes = set()
        for _, row in matches.head(30).iterrows():
            gene = str(row.get('gene_symbol', 'Unknown'))
            if gene not in seen_genes and gene != 'Unknown':
                seen_genes.add(gene)
                results.append({
                    "gene_symbol": gene,
                    "hpo_id": str(row.get('hpo_id', '')),
                    "phenotype": str(row.get('hpo_name', '')),
                    "disease_id": str(row.get('disease_id', '')),
                    "frequency": str(row.get('frequency', ''))
                })
        
        return results[:15]
    
    except Exception as e:
        print(f"[DISEASE_SEARCH] Gene search failed: {str(e)}")
        return []


async def _search_phenotypes_by_disease(disease_name: str) -> List[Dict[str, Any]]:
    """Search HPO phenotypes related to the disease."""
    try:
        hpo_path = "data/datasets/hpo/genes_to_phenotype.csv"
        if not os.path.exists(hpo_path):
            return []
        
        results = []
        disease_lower = disease_name.lower()
        
        df = pd.read_csv(hpo_path, low_memory=False)
        
        # Search for disease name in dataset
        if 'disease_name' in df.columns:
            matches = df[df['disease_name'].str.lower().str.contains(disease_lower, na=False, regex=False)]
            
            seen_phenotypes = set()
            for _, row in matches.head(20).iterrows():
                phenotype = str(row.get('hpo_name', 'Unknown'))
                if phenotype not in seen_phenotypes and phenotype != 'Unknown':
                    seen_phenotypes.add(phenotype)
                    results.append({
                        "hpo_id": str(row.get('hpo_id', '')),
                        "phenotype": phenotype,
                        "definition": "",  # Not in this dataset
                        "frequency": str(row.get('frequency', ''))
                    })
        
        return results
    
    except Exception as e:
        print(f"[DISEASE_SEARCH] Phenotype search failed: {str(e)}")
        return []


async def _search_drugs_by_disease(disease_name: str) -> List[Dict[str, Any]]:
    """Search ChEMBL for drugs that target genes associated with the disease."""
    try:
        chembl_path = "data/datasets/chembl/chembl.csv"
        if not os.path.exists(chembl_path):
            return []
        
        results = []
        disease_lower = disease_name.lower()
        
        df = pd.read_csv(chembl_path, low_memory=False)
        
        # Search for disease indication or target gene
        matches = []
        if 'indication' in df.columns:
            matches = df[df['indication'].str.lower().str.contains(disease_lower, na=False, regex=False)]
        
        # If no direct indication match, search by target
        if len(matches) == 0 and 'target_gene_symbol' in df.columns:
            # Get genes from disease search
            hpo_path = "data/datasets/hpo/genes_to_phenotype.csv"
            if os.path.exists(hpo_path):
                hpo_df = pd.read_csv(hpo_path, low_memory=False)
                if 'disease_name' in hpo_df.columns:
                    disease_genes = hpo_df[hpo_df['disease_name'].str.lower().str.contains(disease_lower, na=False, regex=False)]['gene_symbol'].unique()
                    if len(disease_genes) > 0:
                        matches = df[df['target_gene_symbol'].isin(disease_genes)]
        
        seen_drugs = set()
        for _, row in matches.head(20).iterrows():
            drug_id = str(row.get('chembl_id', 'Unknown'))
            if drug_id not in seen_drugs and drug_id != 'Unknown':
                seen_drugs.add(drug_id)
                results.append({
                    "chembl_id": drug_id,
                    "name": str(row.get('name', 'Unknown')),
                    "target_gene": str(row.get('target_gene_symbol', 'Unknown')),
                    "indication": str(row.get('indication', '')),
                    "max_phase": str(row.get('max_phase', 'Unknown')),
                    "compound_type": str(row.get('compound_type', ''))
                })
        
        return results
    
    except Exception as e:
        print(f"[DISEASE_SEARCH] Drug search failed: {str(e)}")
        return []


async def _get_disease_metadata(disease_name: str) -> Dict[str, Any]:
    """Get disease metadata from disease_names.tsv."""
    try:
        disease_path = "data/datasets/clinvar/disease_names.tsv"
        if not os.path.exists(disease_path):
            return {"found": False, "sources": []}
        
        df = pd.read_csv(disease_path, sep='\t', low_memory=False)
        df.columns = [c.lstrip('#') for c in df.columns]
        disease_lower = disease_name.lower()
        
        matches = df[df['DiseaseName'].str.lower() == disease_lower]
        
        if len(matches) == 0:
            # Try fuzzy match
            matches = df[df['DiseaseName'].str.lower().str.contains(disease_lower, na=False, regex=False)]
        
        if len(matches) > 0:
            row = matches.iloc[0]
            sources = df[df['DiseaseName'].str.lower() == disease_lower]['SourceName'].unique().tolist()
            
            return {
                "found": True,
                "official_name": str(row.get('DiseaseName', '')),
                "concept_id": str(row.get('ConceptID', '')),
                "sources": [str(s) for s in sources if pd.notna(s)],
                "category": str(row.get('Category', ''))
            }
        
        return {"found": False, "sources": []}
    
    except Exception as e:
        print(f"[DISEASE_SEARCH] Metadata retrieval failed: {str(e)}")
        return {"found": False, "sources": []}


async def get_available_diseases(limit: int = 100) -> List[str]:
    """Get list of available diseases from disease_names.tsv."""
    try:
        disease_path = "data/datasets/clinvar/disease_names.tsv"
        if not os.path.exists(disease_path):
            return []
        
        df = pd.read_csv(disease_path, sep='\t', low_memory=False)
        df.columns = [c.lstrip('#') for c in df.columns]
        
        # Filter to only actual diseases (not findings or responses)
        if 'Category' in df.columns:
            diseases = df[df['Category'] == 'Disease']['DiseaseName'].unique()
        else:
            diseases = df['DiseaseName'].unique()
        
        return [str(d) for d in diseases[:limit] if pd.notna(d)]
    
    except Exception as e:
        print(f"[DISEASE_SEARCH] Disease list retrieval failed: {str(e)}")
        return []
