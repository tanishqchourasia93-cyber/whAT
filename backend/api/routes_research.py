import asyncio
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from providers.factory import ProviderFactory
from providers.base import LLMResponse
from verification.claim_extractor import ClaimExtractor, FactualClaim
from verification.claim_comparator import ClaimComparator
from research.retrieval import EvidenceRetriever
from verification.verifier import ClaimVerifier
from verification.scoring import VerificationMetrics
from synthesis.final_answer import FinalAnswerSynthesizer

router = APIRouter(prefix="/api/research", tags=["research"])

class ResearchRequest(BaseModel):
    question: str
    mode: str = Field("deep", description="quick | verify | deep")
    providers: List[str] = Field(default_factory=lambda: ["mock_gpt", "mock_gemini", "mock_claude"])
    api_keys: Optional[Dict[str, str]] = Field(default_factory=dict)
    allow_demo_fallback: bool = True

class ResearchResponse(BaseModel):
    question: str
    mode: str
    duration_ms: float
    model_responses: List[LLMResponse]
    claims: List[FactualClaim] = Field(default_factory=list)
    verification_metrics: Dict[str, Any] = Field(default_factory=dict)
    synthesized_answer: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    pipeline_stages: List[Dict[str, Any]] = Field(default_factory=list)

@router.post("", response_model=ResearchResponse)
async def execute_research(
    req: ResearchRequest,
    x_gemini_api_key: Optional[str] = Header(None),
    x_openai_api_key: Optional[str] = Header(None),
    x_anthropic_api_key: Optional[str] = Header(None),
    x_groq_api_key: Optional[str] = Header(None)
):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    start_total = time.perf_counter()
    header_keys = {
        "gemini": x_gemini_api_key,
        "openai": x_openai_api_key,
        "anthropic": x_anthropic_api_key,
        "groq": x_groq_api_key
    }

    # Merge header keys with body api_keys
    effective_keys = dict(req.api_keys or {})
    for k, v in header_keys.items():
        if v and not effective_keys.get(k):
            effective_keys[k] = v

    selected_providers = req.providers if req.providers else ["gemini", "openai", "claude"]
    if req.mode == "quick":
        selected_providers = selected_providers[:1]

    # Instantiate provider instances
    provider_instances = [
        ProviderFactory.get_provider(
            p_id,
            user_keys=effective_keys,
            header_key=effective_keys.get(p_id),
            allow_demo_fallback=req.allow_demo_fallback
        )
        for p_id in selected_providers
    ]

    pipeline_stages = []

    # STAGE 1: Parallel Model Query Dispatch
    # If one model fails or has no key, the other models proceed gracefully
    async def run_single(p):
        try:
            return await p.generate(req.question)
        except Exception as e:
            return LLMResponse(
                provider_name=p.provider_name(),
                model_name=p.model_name(),
                status="error",
                error=str(e)
            )

    t0 = time.perf_counter()
    responses: List[LLMResponse] = await asyncio.gather(*(run_single(p) for p in provider_instances))
    pipeline_stages.append({
        "stage": "Parallel Model Queries",
        "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
        "status": "completed",
        "detail": f"Received {sum(1 for r in responses if r.status == 'success')} successful responses."
    })

    successful_responses = [r for r in responses if r.status == "success"]
    if not successful_responses:
        raise HTTPException(
            status_code=500,
            detail="All selected LLM providers failed to generate responses. Please verify your API keys or use the demo simulator."
        )

    # If Quick Mode: Return immediately with basic synthesis
    if req.mode == "quick":
        elapsed_total = (time.perf_counter() - start_total) * 1000
        primary = successful_responses[0]
        return ResearchResponse(
            question=req.question,
            mode="quick",
            duration_ms=round(elapsed_total, 1),
            model_responses=responses,
            claims=[],
            verification_metrics={},
            synthesized_answer=primary.content,
            sources=[],
            pipeline_stages=pipeline_stages
        )

    # STAGE 2: Claim Extraction
    t1 = time.perf_counter()
    claims: List[FactualClaim] = await ClaimExtractor.extract_claims(successful_responses)
    pipeline_stages.append({
        "stage": "Claim Extraction",
        "duration_ms": round((time.perf_counter() - t1) * 1000, 1),
        "status": "completed",
        "detail": f"Extracted {len(claims)} discrete atomic factual claims."
    })

    # STAGE 3: Cross-Model Comparison & Disagreement Detection
    t2 = time.perf_counter()
    model_names = [r.provider_name for r in successful_responses]
    claims = ClaimComparator.compare_and_cluster_claims(claims, model_names)
    disagreements_count = sum(1 for c in claims if len(c.models_contradicting) > 0)
    pipeline_stages.append({
        "stage": "Cross-Model Disagreement Detection",
        "duration_ms": round((time.perf_counter() - t2) * 1000, 1),
        "status": "completed",
        "detail": f"Identified {disagreements_count} direct cross-model discrepancies."
    })

    # If Verify Mode (only verify cross-model claims without web search)
    all_sources = []
    if req.mode == "verify":
        # Calculate basic metrics without external web
        for c in claims:
            if len(c.models_contradicting) > 0:
                c.verification_status = "UNCERTAIN"
                c.explanation = f"Cross-model conflict detected: claimed by {c.source_model}, contested by {', '.join(c.models_contradicting)}."
            else:
                c.verification_status = "SUPPORTED" if len(c.models_supporting) > 1 else "UNCERTAIN"
                c.explanation = f"Supported by consensus of {', '.join(c.models_supporting)}."

        metrics = VerificationMetrics.calculate_summary(claims)
        synthesis_result = await FinalAnswerSynthesizer.synthesize(
            question=req.question,
            responses=successful_responses,
            claims=claims,
            sources=[],
            llm_provider=provider_instances[0] if provider_instances[0].is_configured() else None
        )
        elapsed_total = (time.perf_counter() - start_total) * 1000
        return ResearchResponse(
            question=req.question,
            mode="verify",
            duration_ms=round(elapsed_total, 1),
            model_responses=responses,
            claims=claims,
            verification_metrics=metrics,
            synthesized_answer=synthesis_result["synthesized_answer"],
            sources=[],
            pipeline_stages=pipeline_stages
        )

    # STAGE 4: External Evidence Retrieval
    t3 = time.perf_counter()
    claims = await EvidenceRetriever.retrieve_evidence_for_claims(claims, max_claims_to_check=10)
    
    # Collect all unique sources
    source_map = {}
    for c in claims:
        for ev in c.supporting_evidence:
            url = ev["url"]
            if url not in source_map:
                source_map[url] = ev
    all_sources = list(source_map.values())
    pipeline_stages.append({
        "stage": "External Evidence Retrieval",
        "duration_ms": round((time.perf_counter() - t3) * 1000, 1),
        "status": "completed",
        "detail": f"Retrieved and ranked passages from {len(all_sources)} authoritative sources."
    })

    # STAGE 5: Claim Verification against External Evidence
    t4 = time.perf_counter()
    claims = await ClaimVerifier.verify_claims(claims)
    pipeline_stages.append({
        "stage": "Evidence-Claim Verification",
        "duration_ms": round((time.perf_counter() - t4) * 1000, 1),
        "status": "completed",
        "detail": "Verified all claims against evidence passages."
    })

    # STAGE 6: Hallucination Analysis & Confidence Scoring
    metrics = VerificationMetrics.calculate_summary(claims)

    # STAGE 7: Final Evidence-Backed Synthesis
    t5 = time.perf_counter()
    synthesis_result = await FinalAnswerSynthesizer.synthesize(
        question=req.question,
        responses=successful_responses,
        claims=claims,
        sources=all_sources,
        llm_provider=provider_instances[0] if provider_instances[0].is_configured() else None
    )
    pipeline_stages.append({
        "stage": "Final Answer Synthesis",
        "duration_ms": round((time.perf_counter() - t5) * 1000, 1),
        "status": "completed",
        "detail": "Synthesized evidence-grounded final answer with citations and uncertainty indicators."
    })

    elapsed_total = (time.perf_counter() - start_total) * 1000

    return ResearchResponse(
        question=req.question,
        mode="deep",
        duration_ms=round(elapsed_total, 1),
        model_responses=responses,
        claims=claims,
        verification_metrics=metrics,
        synthesized_answer=synthesis_result["synthesized_answer"],
        sources=all_sources,
        pipeline_stages=pipeline_stages
    )
