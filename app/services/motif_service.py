"""
Functional motif analysis using PROSITE patterns.
Detects if a variant disrupts known protein domains and functional sites.

Integrates with InterPro/Pfam via external API for domain analysis.
"""

import httpx
from typing import Dict, List, Optional

INTERPRO_API = "https://www.ebi.ac.uk/interpro/api"

# Common PROSITE motif patterns (simplified)
# In production, download full PROSITE database from: https://prosite.expasy.org/
COMMON_MOTIFS = {
    "zinc_finger": {
        "pattern": r"C.{2,4}C.{12}H.{3,5}H",
        "description": "Zinc finger (C2H2 type)",
        "critical": True
    },
    "leucine_zipper": {
        "pattern": r"(L.{6}){4,}",
        "description": "Leucine zipper dimerization domain",
        "critical": True
    },
    "dna_binding": {
        "pattern": r"[RK].{0,2}[RK].{0,2}[RK]",
        "description": "Basic DNA-binding motif",
        "critical": True
    },
    "kinase": {
        "pattern": r"[LIVMFYC].K.[ST]",
        "description": "Protein kinase active site",
        "critical": True
    },
    "phosphorylation": {
        "pattern": r"[ST].{0,2}[DE]",
        "description": "Phosphorylation site (S/T-X-X-D/E)",
        "critical": False
    }
}


async def check_domain_disruption(
    gene_symbol: str,
    protein_position: Optional[int] = None,
    ref_aa: Optional[str] = None,
    alt_aa: Optional[str] = None
) -> Dict[str, any]:
    """
    Check if variant disrupts known protein domains.
    
    Args:
        gene_symbol: HGNC gene symbol (e.g., 'BRCA1')
        protein_position: Position in protein sequence
        ref_aa: Reference amino acid
        alt_aa: Alternate amino acid
    
    Returns:
        Dictionary with disrupted domains and severity
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Query InterPro for gene
            response = await client.get(
                f"{INTERPRO_API}/entry/",
                params={"keyword": gene_symbol}
            )
            
            if response.status_code != 200:
                return {
                    "domains_affected": [],
                    "disruption_risk": "UNKNOWN",
                    "note": "InterPro lookup failed"
                }
            
            data = response.json()
            results = data.get("results", [])
            
            disrupted = []
            for entry in results:
                entry_id = entry.get("metadata", {}).get("accession")
                entry_name = entry.get("metadata", {}).get("name")
                entry_type = entry.get("metadata", {}).get("type")
                
                if entry_type == "domain":
                    disrupted.append({
                        "domain_id": entry_id,
                        "domain_name": entry_name,
                        "type": entry_type
                    })
            
            risk_level = "HIGH" if disrupted else "LOW"
            
            return {
                "domains_affected": disrupted,
                "disruption_risk": risk_level,
                "note": f"Found {len(disrupted)} critical domains"
            }
    
    except Exception as e:
        return {
            "domains_affected": [],
            "disruption_risk": "ERROR",
            "note": f"Domain check error: {str(e)}"
        }


async def get_gene_domains(gene_symbol: str) -> List[Dict]:
    """Fetch all known domains for a gene."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{INTERPRO_API}/protein/",
                params={"gene": gene_symbol}
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = data.get("results", [])
            
            domains = []
            for result in results:
                proteins = result.get("proteins", [])
                for protein in proteins:
                    entry_protein_locations = protein.get("entry_protein_locations", [])
                    for location in entry_protein_locations:
                        domains.append({
                            "start": location.get("start"),
                            "end": location.get("end"),
                            "domain": location.get("location", {}).get("name"),
                            "accession": location.get("accession")
                        })
            
            return domains
    
    except Exception:
        return []


def is_position_in_critical_region(
    position: int,
    domains: List[Dict]
) -> bool:
    """Check if protein position falls within critical domain regions."""
    for domain in domains:
        start = domain.get("start")
        end = domain.get("end")
        
        if start and end and start <= position <= end:
            return True
    
    return False


async def analyze_variant_motif_impact(
    protein_sequence: str,
    variant_position: int,
    ref_aa: str,
    alt_aa: str,
    gene_symbol: str
) -> Dict:
    """
    Comprehensive motif disruption analysis.
    
    Returns:
        Dictionary with motif disruption details
    """
    # Check domain disruption
    domain_result = await check_domain_disruption(
        gene_symbol,
        variant_position,
        ref_aa,
        alt_aa
    )
    
    # Check known domains
    domains = await get_gene_domains(gene_symbol)
    in_critical_region = is_position_in_critical_region(variant_position, domains)
    
    return {
        "domain_disruption": domain_result,
        "in_critical_domain": in_critical_region,
        "affected_domains": domains,
        "severity": "HIGH" if in_critical_region else "LOW"
    }
