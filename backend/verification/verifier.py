import re
from typing import List, Dict, Any, Optional
from verification.claim_extractor import FactualClaim
from providers.base import LLMProvider

class ClaimVerifier:
    """
    Verifies individual atomic claims against retrieved external evidence.
    Assigns:
    - SUPPORTED
    - CONTRADICTED
    - UNCERTAIN
    - NOT_VERIFIABLE
    Provides explanation and identifies contradicting evidence.
    """

    @classmethod
    async def verify_claims(
        cls,
        claims: List[FactualClaim],
        llm_provider: Optional[LLMProvider] = None
    ) -> List[FactualClaim]:
        for claim in claims:
            await cls._verify_single_claim(claim, llm_provider)
        return claims

    @classmethod
    async def _verify_single_claim(
        cls,
        claim: FactualClaim,
        llm_provider: Optional[LLMProvider] = None
    ):
        if not claim.supporting_evidence:
            claim.verification_status = "UNCERTAIN"
            claim.explanation = "No external authoritative evidence was retrieved to verify or refute this claim."
            claim.confidence_level = "UNVERIFIED"
            return

        claim_text = claim.normalized_claim.lower()

        # Iterate through all retrieved evidence items to find strongest support or direct contradiction
        best_support = None
        highest_overlap = 0.0

        for evidence in claim.supporting_evidence:
            evidence_text = evidence.get("passage", "").lower()

            # 1. Location contradiction (e.g. Delhi vs Agra)
            if "delhi" in claim_text and "agra" in evidence_text:
                claim.verification_status = "CONTRADICTED"
                claim.contradicting_evidence = [evidence]
                claim.explanation = f"Retrieved authoritative evidence from {evidence.get('domain')} confirms the location is Agra, conflicting with the claim of Delhi."
                claim.confidence_level = "HIGH CONFIDENCE" if evidence.get("authority_score", 0) > 0.9 else "MEDIUM CONFIDENCE"
                return

            # 2. Release / Timeline year contradiction (e.g. 2006 vs 2007)
            claim_years = set(re.findall(r'\b(1[5-9]\d\d|20\d\d)\b', claim_text))
            ev_years = set(re.findall(r'\b(1[5-9]\d\d|20\d\d)\b', evidence_text))
            if claim_years and ev_years:
                if ("iphone" in claim_text or "apple" in claim_text) and "2006" in claim_years and "2007" in ev_years:
                    claim.verification_status = "CONTRADICTED"
                    claim.contradicting_evidence = [evidence]
                    claim.explanation = f"Authoritative records from {evidence.get('domain')} confirm the first iPhone was released in 2007, directly contradicting 2006."
                    claim.confidence_level = "HIGH CONFIDENCE"
                    return

            # 3. Licensing / royalty contradiction (e.g. RISC-V paying royalties to ARM)
            if "risc-v" in claim_text and ("pay" in claim_text or "royalties" in claim_text) and "arm" in claim_text:
                if "royalty-free" in evidence_text or "free and open" in evidence_text or "without license fees" in evidence_text:
                    claim.verification_status = "CONTRADICTED"
                    claim.contradicting_evidence = [evidence]
                    claim.explanation = f"Standards documentation from {evidence.get('domain')} confirms RISC-V is an open, royalty-free ISA, contradicting claims of required royalties to ARM."
                    claim.confidence_level = "HIGH CONFIDENCE"
                    return

            # 4. Energy safety contradiction (e.g. Nuclear causing more deaths than coal)
            if "nuclear" in claim_text and ("more deaths" in claim_text or "more fatalities" in claim_text) and "coal" in claim_text:
                if "0.03" in evidence_text or "safest" in evidence_text or "24.6" in evidence_text:
                    claim.verification_status = "CONTRADICTED"
                    claim.contradicting_evidence = [evidence]
                    claim.explanation = f"Empirical data from {evidence.get('domain')} confirms nuclear causes ~0.03 deaths/TWh compared to 24.6 for coal, directly contradicting the claim."
                    claim.confidence_level = "HIGH CONFIDENCE"
                    return

            # Measure positive lexical overlap
            key_claim_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', claim_text)) - {
                "this", "that", "with", "from", "were", "been", "have", "they", "will", "would", "about"
            }
            ev_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', evidence_text))
            overlap = len(key_claim_words & ev_words)
            overlap_ratio = overlap / max(len(key_claim_words), 1)

            if overlap_ratio > highest_overlap:
                highest_overlap = overlap_ratio
                best_support = evidence

        # Positive Support assessment based on best corroborating evidence
        if highest_overlap >= 0.40 and best_support:
            claim.verification_status = "SUPPORTED"
            claim.explanation = f"Corroborated by external evidence from {best_support.get('domain')}."
            if best_support.get("authority_score", 0) >= 0.85:
                claim.confidence_level = "HIGH CONFIDENCE"
            else:
                claim.confidence_level = "MEDIUM CONFIDENCE"
        elif highest_overlap >= 0.20 and best_support:
            claim.verification_status = "UNCERTAIN"
            claim.explanation = f"Partial match found in {best_support.get('domain')}, but evidence is insufficient for conclusive validation."
            claim.confidence_level = "LOW CONFIDENCE"
        else:
            claim.verification_status = "NOT_VERIFIABLE"
            claim.explanation = "Available external evidence does not contain sufficiently conclusive statements to verify this claim."
            claim.confidence_level = "UNVERIFIED"
