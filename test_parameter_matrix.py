import asyncio
import time
import json
from api.routes_research import execute_research, ResearchRequest
from documents.parser import DocumentParser
from documents.chunker import DocumentChunker

# Add backend directory to path if needed
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

async def test_modes():
    print("\n=======================================================")
    print("TEST SUITE 1: PARAMETER VARIATION BY RESEARCH MODE")
    print("=======================================================")
    question = "Where is the Taj Mahal located, who commissioned it, and when was it completed?"
    
    for mode in ["quick", "verify", "deep"]:
        print(f"\n---> Running with mode='{mode}' (Providers: mock_gpt, mock_gemini, mock_claude)")
        start = time.perf_counter()
        req = ResearchRequest(
            question=question,
            mode=mode,
            providers=["mock_gpt", "mock_gemini", "mock_claude"]
        )
        res = await execute_research(req)
        elapsed = round((time.perf_counter() - start) * 1000, 1)

        print(f"  [Result] Mode: {res.mode}")
        print(f"  [Result] Latency: {elapsed}ms (Pipeline reported: {res.duration_ms}ms)")
        print(f"  [Result] Models Queried: {len(res.model_responses)}")
        print(f"  [Result] Claims Extracted: {len(res.claims)}")
        if res.verification_metrics:
            vm = res.verification_metrics
            print(f"  [Result] Verification Metrics: Supported={vm.get('supported')}, Contradicted={vm.get('contradicted')}, Uncertain={vm.get('uncertain')}")
            print(f"  [Result] Overall Confidence: {vm.get('overall_confidence')}")
        print(f"  [Result] Sources Retrieved: {len(res.sources)}")
        print(f"  [Result] Synthesis Sample: {res.synthesized_answer[:150]}...")

async def test_provider_scaling():
    print("\n=======================================================")
    print("TEST SUITE 2: PARAMETER VARIATION BY PROVIDER COMBINATION")
    print("=======================================================")
    question = "When was the original Apple iPhone officially released for sale to the public?"
    
    provider_sets = [
        ("Single Provider (Baseline)", ["mock_gpt"]),
        ("Dual Providers (Pairwise Comparison)", ["mock_gpt", "mock_gemini"]),
        ("Tri-Providers (Consensus & Outlier Detection)", ["mock_gpt", "mock_gemini", "mock_claude"])
    ]

    for label, providers in provider_sets:
        print(f"\n---> Running {label}: {providers}")
        req = ResearchRequest(
            question=question,
            mode="deep",
            providers=providers
        )
        res = await execute_research(req)
        print(f"  [Result] Models Active: {len(res.model_responses)}")
        print(f"  [Result] Claims Extracted: {len(res.claims)}")
        contradictions = [c for c in res.claims if c.verification_status == "CONTRADICTED"]
        print(f"  [Result] Contradictions Flagged: {len(contradictions)}")
        for c in contradictions:
            print(f"    * Flagged: '{c.normalized_claim}' (Model: {c.source_model})")
            print(f"      Reason: {c.explanation}")
        if res.verification_metrics:
            print(f"  [Result] Support Ratio: {res.verification_metrics.get('support_ratio')}%")
            print(f"  [Result] System Confidence: {res.verification_metrics.get('overall_confidence')}")

async def test_domain_diversity():
    print("\n=======================================================")
    print("TEST SUITE 3: PARAMETER VARIATION ACROSS DIVERSE KNOWLEDGE DOMAINS")
    print("=======================================================")
    
    test_domains = [
        {
            "domain": "Computer Architecture & Open Hardware",
            "question": "What are the architectural licensing differences and advantages of RISC-V over ARM?",
        },
        {
            "domain": "Quantitative Energy Physics & Public Health",
            "question": "Is nuclear energy empirically safer than fossil fuels per terawatt-hour produced?",
        },
        {
            "domain": "Subjective / Non-Empirical Query",
            "question": "Which painting in the world is objectively the most beautiful?",
        }
    ]

    for item in test_domains:
        print(f"\n---> Testing Domain: {item['domain']}")
        print(f"     Prompt: '{item['question']}'")
        req = ResearchRequest(
            question=item['question'],
            mode="deep",
            providers=["mock_gpt", "mock_gemini", "mock_claude"]
        )
        res = await execute_research(req)
        print(f"  [Result] Extracted Claims: {len(res.claims)}")
        if res.verification_metrics:
            vm = res.verification_metrics
            print(f"  [Result] Grounding Telemetry: Supported={vm.get('supported')}, Contradicted={vm.get('contradicted')}, Uncertain={vm.get('uncertain')}")
            print(f"  [Result] Summary: {vm.get('summary_statement')}")
            print(f"  [Result] Confidence Level: {vm.get('overall_confidence')}")
        if res.sources:
            print(f"  [Result] Top Source: {res.sources[0].get('title')} ({res.sources[0].get('domain')}) - Auth: {res.sources[0].get('authority_score')}")

async def test_document_grounding_parameters():
    print("\n=======================================================")
    print("TEST SUITE 4: DOCUMENT GROUNDING PARAMETER VARIATIONS")
    print("=======================================================")
    
    sample_doc = """
    TECHNICAL SPECIFICATION & BENCHMARK REPORT v4.2
    Project: Antigravity Autonomous Engine
    Date: September 2026

    1. Architecture Overview:
    The Antigravity system executes autonomous multi-agent pipelines with distributed state machines.
    All modules communicate over encrypted gRPC channels with zero plaintext token serialization.

    2. Quantitative Performance Metrics:
    Benchmarking over 10,000 synthetic queries demonstrates that query latency decreased by 41.5%
    compared to the v3.8 legacy architecture. Memory consumption stabilized at 320MB per worker instance.
    The false-positive hallucination rate was measured at 0.02% across verified encyclopedic tests.

    3. Safety and Deployment Constraints:
    High-risk database drop and KMS key destruction operations require mandatory two-party authorization.
    All model checkpoints adhere to strict SHA-256 integrity verification before runtime execution.
    """

    queries = [
        ("Supported Factual Query", "Does this document indicate query latency decreased by over 40%?"),
        ("Unrelated / Out of Scope Query", "What are the rules of professional cricket in Australia?")
    ]

    chunks = DocumentChunker.chunk_document(sample_doc, chunk_size=300, overlap=50)
    print(f"Document parsed: {len(sample_doc)} chars, segmented into {len(chunks)} overlapping chunks.")

    for label, q in queries:
        print(f"\n---> Testing: {label}")
        print(f"     Query: '{q}'")
        matches = DocumentChunker.find_relevant_passages(q, chunks, top_k=2)
        if matches:
            top = matches[0]
            status = "SUPPORTED" if top["score"] >= 0.3 else "PARTIALLY_SUPPORTED"
            print(f"  [Result] Status: {status} (Relevance Score: {top['score']})")
            print(f"  [Result] Matched Passage: \"{top['passage'][:120]}...\"")
        else:
            print(f"  [Result] Status: NOT_FOUND (Relevance Score: 0.0)")

async def main():
    print("#######################################################")
    print("  VERIAI MULTI-PARAMETER AUTOMATED TEST SUITE")
    print("#######################################################")
    
    t_start = time.perf_counter()
    await test_modes()
    await test_provider_scaling()
    await test_domain_diversity()
    await test_document_grounding_parameters()
    t_end = time.perf_counter()

    print("\n#######################################################")
    print(f"  ALL PARAMETER MATRIX TESTS COMPLETED IN {round(t_end - t_start, 2)}s")
    print("#######################################################")

if __name__ == "__main__":
    asyncio.run(main())
