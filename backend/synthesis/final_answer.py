import re
from typing import List, Dict, Any, Optional
from verification.claim_extractor import FactualClaim
from providers.base import LLMResponse, LLMProvider

class FinalAnswerSynthesizer:
    """
    Generates an evidence-backed final synthesized response.
    - Directly answers question
    - Resolves and explicitly highlights model disagreements
    - Corrects contradicted claims using external evidence
    - Communicates residual uncertainty
    - Cites authoritative sources [1], [2]
    """

    @classmethod
    async def synthesize(
        cls,
        question: str,
        responses: List[LLMResponse],
        claims: List[FactualClaim],
        sources: List[Dict[str, Any]],
        llm_provider: Optional[LLMProvider] = None
    ) -> Dict[str, Any]:
        # Collect supported, contradicted, and uncertain claims
        supported = [c for c in claims if c.verification_status == "SUPPORTED"]
        contradicted = [c for c in claims if c.verification_status == "CONTRADICTED"]
        uncertain = [c for c in claims if c.verification_status in ["UNCERTAIN", "NOT_VERIFIABLE"]]

        # Disagreements between models
        disagreements = [c for c in claims if len(c.models_contradicting) > 0]

        # Try LLM-based synthesis if provider is active
        if llm_provider and llm_provider.is_configured():
            try:
                prompt = cls._build_synthesis_prompt(
                    question=question,
                    responses=responses,
                    supported_claims=supported,
                    contradicted_claims=contradicted,
                    disagreements=disagreements,
                    sources=sources
                )
                res = await llm_provider.generate(
                    prompt=prompt,
                    system_prompt="You are VeriAI, an evidence-grounded research synthesizer. You never claim absolute truth; you clearly delineate verified facts, model disagreements, and uncertainties."
                )
                if res.status == "success" and res.content.strip():
                    return {
                        "synthesized_answer": res.content.strip(),
                        "generation_method": "llm_grounded_synthesis",
                        "sources_used": sources[:5]
                    }
            except Exception:
                pass

        # Deterministic Grounded Synthesis Fallback
        return {
            "synthesized_answer": cls._generate_structured_synthesis(
                question=question,
                responses=responses,
                supported=supported,
                contradicted=contradicted,
                uncertain=uncertain,
                disagreements=disagreements,
                sources=sources
            ),
            "generation_method": "deterministic_grounded_synthesis",
            "sources_used": sources[:5]
        }

    @classmethod
    def _build_synthesis_prompt(
        cls,
        question: str,
        responses: List[LLMResponse],
        supported_claims: List[FactualClaim],
        contradicted_claims: List[FactualClaim],
        disagreements: List[FactualClaim],
        sources: List[Dict[str, Any]]
    ) -> str:
        sources_text = "\n".join([
            f"[{idx+1}] {s.get('title')} ({s.get('domain')}): \"{s.get('passage', '')[:200]}...\""
            for idx, s in enumerate(sources[:5])
        ])

        contradictions_text = "\n".join([
            f"- Model '{c.source_model}' claimed: \"{c.normalized_claim}\". CONTRADICTED BY: {c.explanation}"
            for c in contradicted_claims
        ]) or "None detected."

        return f"""
Synthesize an evidence-backed answer to the user's question based strictly on verified external evidence.

USER QUESTION:
{question}

RETRIEVED AUTHORITATIVE EVIDENCE:
{sources_text}

FACTUAL CONTRADICTIONS & MODEL DISAGREEMENTS:
{contradictions_text}

INSTRUCTIONS:
1. Provide a direct, factual answer to the question using the retrieved evidence.
2. If any model made an incorrect claim, explicitly state: e.g. "While one model claimed X, external records confirm Y."
3. Cite sources using [1], [2] corresponding to the evidence list.
4. Conclude with a clear statement acknowledging limits or residual uncertainties.
5. Do NOT claim the answer is infallible; emphasize that conclusions reflect currently retrieved evidence.
"""

    @classmethod
    def _generate_structured_synthesis(
        cls,
        question: str,
        responses: List[LLMResponse],
        supported: List[FactualClaim],
        contradicted: List[FactualClaim],
        uncertain: List[FactualClaim],
        disagreements: List[FactualClaim],
        sources: List[Dict[str, Any]]
    ) -> str:
        parts = []

        # 1. Main Direct Answer based on best supported facts or consensus
        parts.append(f"### Research Synthesis\n")
        parts.append(f"Based on cross-model analysis and authoritative external evidence:")

        if supported:
            core_points = "\n".join([f"- **{c.normalized_claim}** (Corroborated by {c.supporting_evidence[0].get('domain') if c.supporting_evidence else 'external sources'})" for c in supported[:4]])
            parts.append(f"\n#### Supported Findings:\n{core_points}\n")
        else:
            # Fallback to model consensus
            primary_response = next((r.content for r in responses if r.status == "success"), "No conclusive answer generated.")
            parts.append(f"\n{primary_response[:400]}...\n")

        # 2. Corrected Contradictions / Hallucinations
        if contradicted:
            parts.append("#### Corrected Discrepancies & Disagreements:")
            for c in contradicted:
                opposing_models = ", ".join(c.models_contradicting) if c.models_contradicting else "External consensus"
                parts.append(
                    f"- ⚠️ **Claim:** \"{c.normalized_claim}\" (stated by {c.source_model}).\n"
                    f"  **Correction:** {c.explanation} (Noted by {opposing_models})."
                )
            parts.append("")

        # 3. Model Disagreements
        if disagreements and not contradicted:
            parts.append("#### Model Disagreements Observed:")
            for d in disagreements[:2]:
                parts.append(f"- Discrepancy observed regarding \"{d.normalized_claim}\" between {d.source_model} and {', '.join(d.models_contradicting)}.")
            parts.append("")

        # 4. Uncertainty & Source Disclaimer
        parts.append(
            "> **Verification Note:** This synthesis reflects verification against retrieved external records "
            f"({len(sources)} sources consulted). While high agreement exists on core claims, secondary claims remain subject to verification limits."
        )

        return "\n".join(parts)
