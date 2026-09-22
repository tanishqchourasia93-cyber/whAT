from fastapi import APIRouter
from evaluation.runner import EvaluationRunner

router = APIRouter(prefix="/api/eval", tags=["evaluation"])

@router.post("/run")
async def run_evaluation_suite():
    """
    Executes the standard hallucination detection evaluation dataset
    and outputs academic metrics and architecture comparisons.
    """
    results = await EvaluationRunner.run_evaluation()
    return results
