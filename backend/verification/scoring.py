from typing import List, Dict, Any
from verification.claim_extractor import FactualClaim

class VerificationMetrics:
    @classmethod
    def calculate_summary(cls, claims: List[FactualClaim]) -> Dict[str, Any]:
        total = len(claims)
        if total == 0:
            return {
                "total_claims": 0,
                "supported": 0,
                "contradicted": 0,
                "uncertain": 0,
                "not_verifiable": 0,
                "summary_statement": "No claims were extracted for verification.",
                "support_ratio": 0.0,
                "contradiction_ratio": 0.0,
                "overall_confidence": "UNVERIFIED"
            }

        supported = sum(1 for c in claims if c.verification_status == "SUPPORTED")
        contradicted = sum(1 for c in claims if c.verification_status == "CONTRADICTED")
        uncertain = sum(1 for c in claims if c.verification_status == "UNCERTAIN")
        not_verifiable = sum(1 for c in claims if c.verification_status == "NOT_VERIFIABLE")

        summary_statement = (
            f"{supported} of {total} analyzed claims were supported by the retrieved evidence, "
            f"while {contradicted} were contradicted and {uncertain + not_verifiable} were unverified or uncertain."
        )

        support_ratio = round((supported / total) * 100, 1)
        contradiction_ratio = round((contradicted / total) * 100, 1)

        # Calculate overall system confidence
        if contradicted > 0:
            overall_confidence = "LOW CONFIDENCE"
        elif supported >= total * 0.7:
            overall_confidence = "HIGH CONFIDENCE"
        elif supported > 0:
            overall_confidence = "MEDIUM CONFIDENCE"
        else:
            overall_confidence = "UNVERIFIED"

        return {
            "total_claims": total,
            "supported": supported,
            "contradicted": contradicted,
            "uncertain": uncertain,
            "not_verifiable": not_verifiable,
            "summary_statement": summary_statement,
            "support_ratio": support_ratio,
            "contradiction_ratio": contradiction_ratio,
            "overall_confidence": overall_confidence,
            "calculation_note": "Metric represents proportion of extracted atomic claims corroborated by retrieved external passages. It is not an absolute measure of truth."
        }
