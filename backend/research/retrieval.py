import asyncio
from typing import List, Dict, Any
from verification.claim_extractor import FactualClaim
from research.query_analyzer import QueryAnalyzer
from research.search import WebSearchEngine

class EvidenceRetriever:
    """
    Coordinates evidence retrieval and passage ranking for extracted claims.
    """

    @classmethod
    async def retrieve_evidence_for_claims(
        cls,
        claims: List[FactualClaim],
        max_claims_to_check: int = 10
    ) -> List[FactualClaim]:
        # Filter high/medium priority claims
        prioritized_claims = sorted(
            claims,
            key=lambda c: (1 if c.importance == "high" else 2, 0 if len(c.models_contradicting) > 0 else 1)
        )[:max_claims_to_check]

        async def process_single_claim(claim: FactualClaim):
            queries = QueryAnalyzer.generate_verification_queries(claim.normalized_claim, claim.category)
            combined_evidence: List[Dict[str, Any]] = []

            for q in queries:
                results = await WebSearchEngine.search(q, max_results=3)
                combined_evidence.extend(results)

            # Deduplicate by URL
            unique_evidence = {}
            for ev in combined_evidence:
                url = ev["url"]
                if url not in unique_evidence or ev.get("authority_score", 0) > unique_evidence[url].get("authority_score", 0):
                    unique_evidence[url] = ev

            ranked = sorted(
                list(unique_evidence.values()),
                key=lambda x: x.get("authority_score", 0.5),
                reverse=True
            )
            # Store in claim
            claim.supporting_evidence = ranked[:3]

        # Concurrently retrieve evidence for claims
        await asyncio.gather(*(process_single_claim(c) for c in prioritized_claims))
        return claims
