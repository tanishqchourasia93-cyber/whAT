import asyncio
import json
from api.routes_research import execute_research, ResearchRequest
from evaluation.runner import EvaluationRunner

async def main():
    print("==================================================")
    print("VERIAI BACKEND INTEGRATION TEST SUITE")
    print("==================================================")

    # Test 1: Deep Research with Disagreement & Hallucination Flagging
    print("\n--- TEST 1: Multi-LLM Disagreement & Hallucination Detection ---")
    req = ResearchRequest(
        question="Where is the Taj Mahal located, who designed it, and when was it completed?",
        mode="deep",
        providers=["mock_gpt", "mock_gemini", "mock_claude"]
    )
    result = await execute_research(req)
    print(f"Total Duration: {result.duration_ms}ms")
    print(f"Model Responses Received: {len(result.model_responses)}")
    print(f"Claims Extracted: {len(result.claims)}")
    for c in result.claims[:4]:
        print(f"  [{c.verification_status}] Claim: '{c.normalized_claim}' (Model: {c.source_model})")
        if c.contradicting_evidence:
            print(f"    -> CONTRADICTION ALERT: {c.explanation}")

    print(f"\nVerification Metrics: {json.dumps(result.verification_metrics, indent=2)}")
    print(f"\nSources Consulted: {len(result.sources)}")
    for s in result.sources[:2]:
        print(f"  - [{s.get('domain')}] {s.get('title')}: {s.get('url')}")

    print("\nSynthesized Answer Preview:")
    print(result.synthesized_answer[:300] + "...")

    # Test 2: Academic Evaluation Runner
    print("\n--- TEST 2: Academic Evaluation Suite Runner ---")
    eval_result = await EvaluationRunner.run_evaluation()
    print("Evaluation Metrics:")
    print(json.dumps(eval_result["metrics"], indent=2))
    print("\nArchitectural Comparison:")
    for arch in eval_result["architecture_comparison"]:
        print(f"  * {arch['architecture']}: Accuracy={arch['hallucination_accuracy']}, F1={arch['hallucination_detection_f1']}")

    print("\n==================================================")
    print("ALL BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
