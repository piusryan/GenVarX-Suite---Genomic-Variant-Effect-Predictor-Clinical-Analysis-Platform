import httpx
from app.models import VariantAnnotation

ENSEMBL_VEP_URL = "https://rest.ensembl.org/vep/human/region"

# ── Predictor severity ranking (higher = more damaging) ──────────────
_SIFT_RANK = {"deleterious": 4, "deleterious_low_confidence": 3,
              "tolerated_low_confidence": 2, "tolerated": 1}
_POLYPHEN_RANK = {"probably_damaging": 4, "possibly_damaging": 3,
                  "benign": 2, "unknown": 1}


def _select_best_predictions(transcripts):
    """Scan EVERY transcript consequence and return the most damaging
    SIFT + PolyPhen predictions, plus the best gene_symbol and amino-acid
    change found anywhere in the list.
    """
    best_sift = "N/A"
    best_poly = "N/A"
    best_aa = "N/A"
    best_gene = "N/A"
    best_sift_rank = 0
    best_poly_rank = 0

    for tx in transcripts or []:
        if not isinstance(tx, dict):
            continue
        # Gene symbol (first hit wins — they're all usually the same)
        g = tx.get("gene_symbol")
        if g and isinstance(g, str) and best_gene == "N/A":
            best_gene = g
        # Amino-acid change (first useful one wins)
        aa = tx.get("amino_acids")
        if aa and isinstance(aa, str) and aa.strip() and best_aa == "N/A":
            best_aa = aa.strip()
        # SIFT — keep the most damaging one found across all transcripts
        sift = tx.get("sift_prediction")
        if sift and isinstance(sift, str) and sift.strip() not in ("N/A", ""):
            label = sift.lower().split("(")[0].strip() if "(" in sift else sift.lower().strip()
            rank = _SIFT_RANK.get(label, 0)
            if rank > best_sift_rank:
                best_sift_rank = rank
                best_sift = sift
        # PolyPhen — same logic
        poly = tx.get("polyphen_prediction")
        if poly and isinstance(poly, str) and poly.strip() not in ("N/A", ""):
            label = poly.lower().split("(")[0].strip() if "(" in poly else poly.lower().strip()
            rank = _POLYPHEN_RANK.get(label, 0)
            if rank > best_poly_rank:
                best_poly_rank = rank
                best_poly = poly

    return best_sift, best_poly, best_aa, best_gene


async def fetch_vep_annotation(variant_str: str) -> VariantAnnotation:
    # Parse coordinates
    try:
        clean_var = variant_str.replace("chr", "").strip()
        parts = clean_var.split(":")
        if len(parts) < 4:
            # Accept less tokens — caller may have passed chr:pos:ref only,
            # but strictly we need the 4-token form chr:pos:ref:alt.
            return VariantAnnotation(
                variant=variant_str,
                consequence="Invalid Variant Format (expected chr:pos:ref:alt)",
                impact_level="UNKNOWN",
                clinical_significance="Not Found in ClinVar",
                associated_diseases=[],
            )
        chrom, pos, ref, alt = parts[0], parts[1], parts[2], parts[3]
        formatted_region = f"{chrom}:{pos}-{pos}/{alt}"
    except Exception:
        return VariantAnnotation(
            variant=variant_str,
            consequence="Invalid Variant Format (expected chr:pos:ref:alt)",
            impact_level="UNKNOWN",
            clinical_significance="Not Found in ClinVar",
            associated_diseases=[],
        )

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "GenVarX-App/1.0",
    }

    # ── Retry loop: 2 attempts (12s, 14s) — fail fast, return clean fallback
    last_fail_reason = ""
    for attempt, timeout_s in enumerate((12.0, 14.0), start=1):
        try:
            async with httpx.AsyncClient(timeout=timeout_s, follow_redirects=True) as client:
                resp = await client.get(
                    f"{ENSEMBL_VEP_URL}/{formatted_region}",
                    headers=headers,
                )
                if resp.status_code != 200:
                    last_fail_reason = f"HTTP {resp.status_code}"
                    continue
                data = resp.json()
                if not data or not isinstance(data, list):
                    last_fail_reason = "Empty VEP response"
                    continue

                entry = data[0]
                most_severe = entry.get("most_severe_consequence", "unknown") or "unknown"
                transcripts = entry.get("transcript_consequences", []) or []
                primary_tx = transcripts[0] if transcripts else {}

                # ── Functional predictions across ALL transcripts ──
                sift_pred, polyphen_pred, aa_change, best_gene = _select_best_predictions(transcripts)

                # Fallback to primary transcript if scan returned nothing
                if sift_pred == "N/A":
                    sift_pred = primary_tx.get("sift_prediction") or "N/A"
                if polyphen_pred == "N/A":
                    polyphen_pred = primary_tx.get("polyphen_prediction") or "N/A"
                if aa_change == "N/A":
                    aa_change = primary_tx.get("amino_acids") or "N/A"
                if best_gene == "N/A":
                    best_gene = primary_tx.get("gene_symbol") or "N/A"

                # ── Impact level ──
                native_impact = (primary_tx.get("impact") or "").upper()
                if native_impact in ("HIGH", "MODERATE", "LOW"):
                    impact = native_impact
                else:
                    high_terms = ("stop_gained", "frameshift_variant",
                                  "splice_acceptor_variant", "splice_donor_variant",
                                  "start_lost", "stop_lost", "transcript_ablation")
                    if any(t in most_severe for t in high_terms):
                        impact = "HIGH"
                    elif "missense" in most_severe:
                        impact = "MODERATE"
                    else:
                        impact = "LOW"

                # ── ClinVar significance + rsID from colocated variants ──
                clin_sig = "Not Found in ClinVar"
                associated_diseases = []
                rs_id = None
                for var in entry.get("colocated_variants", []) or []:
                    var_id = var.get("id", "")
                    if not rs_id and isinstance(var_id, str) and var_id.startswith("rs"):
                        rs_id = var_id
                    sig_list = var.get("clin_sig") or []
                    if sig_list:
                        cleaned = []
                        for s in sig_list:
                            if s:
                                term = str(s).replace("_", " ").strip()
                                if term:
                                    cleaned.append(term.title() if term.islower() else term)
                        if cleaned:
                            clin_sig = " / ".join(cleaned)
                        if var_id:
                            associated_diseases.append(f"dbSNP / ClinVar ID: {var_id}")
                        if var.get("phenotype_or_disease"):
                            associated_diseases.append("ClinVar phenotype-associated variant")

                # Deduplicate while preserving insertion order
                seen = set()
                deduped = []
                for d in associated_diseases:
                    k = str(d).lower().strip()
                    if k and k not in seen:
                        seen.add(k)
                        deduped.append(d)

                return VariantAnnotation(
                    variant=variant_str,
                    rs_id=rs_id,
                    gene_symbol=best_gene,
                    consequence=most_severe,
                    sift_prediction=sift_pred,
                    polyphen_prediction=polyphen_pred,
                    amino_acid_change=aa_change,
                    impact_level=impact,
                    clinical_significance=clin_sig,
                    associated_diseases=deduped,
                )
        except httpx.TimeoutException:
            last_fail_reason = "Timeout"
            continue
        except httpx.RequestError as e:
            last_fail_reason = type(e).__name__
            continue
        except Exception as e:
            last_fail_reason = type(e).__name__
            continue

    # ── All attempts failed — return a clean fallback.
    #    CRITICAL: clinical_significance MUST be "Not Found in ClinVar" so the
    #    caller knows to use local VCF data instead of displaying "Timeout"/N/A.
    return VariantAnnotation(
        variant=variant_str,
        gene_symbol="N/A",
        consequence=f"VEP Unavailable ({last_fail_reason or 'Network'}) — Using Local Data",
        impact_level="UNKNOWN",
        clinical_significance="Not Found in ClinVar",
        associated_diseases=[],
    )
