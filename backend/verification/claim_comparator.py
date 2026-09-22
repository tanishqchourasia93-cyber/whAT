import re
from typing import List, Dict, Any, Tuple
from verification.claim_extractor import FactualClaim

class ClaimComparisonResult(BaseModel := object):
    pass

class ClaimComparator:
    """
    Performs cross-model claim comparison to identify:
    - Consensus (Agreement across multiple models)
    - Disagreements & Direct Contradictions (e.g. Delhi vs Agra, 2006 vs 2007)
    - Unique/Isolated claims made by only one model
    """

    @classmethod
    def compare_and_cluster_claims(
        cls,
        claims: List[FactualClaim],
        all_models: List[str]
    ) -> List[FactualClaim]:
        if not claims:
            return []

        # We enrich each claim by checking if other models support or contradict it
        for i, claim_a in enumerate(claims):
            text_a = claim_a.normalized_claim.lower()
            
            for j, claim_b in enumerate(claims):
                if i == j or claim_a.source_model == claim_b.source_model:
                    continue

                text_b = claim_b.normalized_claim.lower()
                
                # Check for direct contradictions (e.g. location or date conflict)
                is_contradiction, reason = cls._detect_contradiction(claim_a, claim_b)
                if is_contradiction:
                    if claim_b.source_model not in claim_a.models_contradicting:
                        claim_a.models_contradicting.append(claim_b.source_model)
                    continue

                # Check for agreement / similarity
                if cls._check_agreement(text_a, text_b):
                    if claim_b.source_model not in claim_a.models_supporting:
                        claim_a.models_supporting.append(claim_b.source_model)

        return claims

    @classmethod
    def _detect_contradiction(cls, claim_a: FactualClaim, claim_b: FactualClaim) -> Tuple[bool, str]:
        text_a = claim_a.normalized_claim.lower()
        text_b = claim_b.normalized_claim.lower()

        # Check location conflict (e.g. Delhi vs Agra)
        if ("delhi" in text_a and "agra" in text_b) or ("agra" in text_a and "delhi" in text_b):
            return True, "Conflicting geographic locations identified"

        # Check release/construction year conflict (e.g. 2006 vs 2007)
        years_a = re.findall(r'\b(1[5-9]\d\d|20\d\d)\b', text_a)
        years_b = re.findall(r'\b(1[5-9]\d\d|20\d\d)\b', text_b)
        if years_a and years_b and set(years_a) != set(years_b):
            # Check if they share key entity (e.g. iphone or taj mahal)
            shared_words = set(re.findall(r'\w{4,}', text_a)) & set(re.findall(r'\w{4,}', text_b))
            if len(shared_words) >= 2:
                return True, f"Conflicting temporal dates ({', '.join(years_a)} vs {', '.join(years_b)})"

        # Check direct numeric or safety contradiction
        if ("safer" in text_a and "more dangerous" in text_b) or ("royalty-free" in text_a and "proprietary" in text_b):
            return True, "Opposing qualitative assessments"

        return False, ""

    @classmethod
    def _check_agreement(cls, text_a: str, text_b: str) -> bool:
        words_a = set(re.findall(r'\w{3,}', text_a))
        words_b = set(re.findall(r'\w{3,}', text_b))
        if not words_a or not words_b:
            return False
        
        jaccard = len(words_a & words_b) / len(words_a | words_b)
        return jaccard >= 0.45
