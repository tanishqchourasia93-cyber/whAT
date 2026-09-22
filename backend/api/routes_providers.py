import time
from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from config.settings import settings
from security.key_manager import mask_api_key, KeyManager
from providers.factory import ProviderFactory

router = APIRouter(prefix="/api/providers", tags=["providers"])

class ProviderStatusItem(BaseModel):
    id: str
    name: str
    default_model: str
    requires_key: bool
    is_configured: bool
    masked_key: Optional[str] = None
    description: str

class TestKeyRequest(BaseModel):
    provider_id: str
    api_key: str

class TestKeyResponse(BaseModel):
    provider_id: str
    status: str
    latency_ms: float
    message: str

@router.get("/status")
async def get_providers_status() -> Dict[str, Any]:
    system_providers = [
        {
            "id": "gemini",
            "name": "Google Gemini",
            "default_model": settings.GEMINI_MODEL,
            "requires_key": True,
            "is_configured": bool(settings.GEMINI_API_KEY),
            "masked_key": mask_api_key(settings.GEMINI_API_KEY),
            "description": "Google's flagship multimodal reasoning and research models."
        },
        {
            "id": "openai",
            "name": "OpenAI",
            "default_model": settings.OPENAI_MODEL,
            "requires_key": True,
            "is_configured": bool(settings.OPENAI_API_KEY),
            "masked_key": mask_api_key(settings.OPENAI_API_KEY),
            "description": "OpenAI GPT-4o and GPT-4o-mini reasoning models."
        },
        {
            "id": "anthropic",
            "name": "Anthropic Claude",
            "default_model": settings.ANTHROPIC_MODEL,
            "requires_key": True,
            "is_configured": bool(settings.ANTHROPIC_API_KEY),
            "masked_key": mask_api_key(settings.ANTHROPIC_API_KEY),
            "description": "Anthropic Claude 3.5 Sonnet advanced analytical models."
        },
        {
            "id": "groq",
            "name": "Groq LLaMA",
            "default_model": settings.GROQ_MODEL,
            "requires_key": True,
            "is_configured": bool(settings.GROQ_API_KEY),
            "masked_key": mask_api_key(settings.GROQ_API_KEY),
            "description": "Ultra-low latency inference for LLaMA 3.3 70B."
        },
        {
            "id": "mock_gpt",
            "name": "Simulated GPT-4o (Test/Demo)",
            "default_model": "simulated-gpt-4o",
            "requires_key": False,
            "is_configured": True,
            "masked_key": "Demo-Included",
            "description": "Deterministic multi-model testing persona (zero credit cost)."
        },
        {
            "id": "mock_gemini",
            "name": "Simulated Gemini (Test/Demo)",
            "default_model": "simulated-gemini-3.8",
            "requires_key": False,
            "is_configured": True,
            "masked_key": "Demo-Included",
            "description": "Deterministic multi-model testing persona (zero credit cost)."
        },
        {
            "id": "mock_claude",
            "name": "Simulated Claude (Test/Demo)",
            "default_model": "simulated-claude-3.5",
            "requires_key": False,
            "is_configured": True,
            "masked_key": "Demo-Included",
            "description": "Deterministic multi-model testing persona (zero credit cost)."
        }
    ]

    return {
        "providers": system_providers,
        "security_policy": {
            "byok_storage": "Encrypted or Client-Side Session Storage",
            "billing_notice": "Using personal API keys will incur standard usage charges from the respective model provider."
        }
    }

@router.post("/test", response_model=TestKeyResponse)
async def test_provider_key(req: TestKeyRequest):
    start = time.perf_counter()
    provider = ProviderFactory.get_provider(
        req.provider_id,
        user_keys={req.provider_id: req.api_key},
        allow_demo_fallback=False
    )

    if not provider.is_configured():
        return TestKeyResponse(
            provider_id=req.provider_id,
            status="error",
            latency_ms=0.0,
            message="Provided API key is empty or invalid format."
        )

    # Lightweight test ping
    try:
        res = await provider.generate("Ping! Respond with the single word 'OK'.")
        latency = round((time.perf_counter() - start) * 1000, 1)
        if res.status == "success":
            return TestKeyResponse(
                provider_id=req.provider_id,
                status="success",
                latency_ms=latency,
                message="Connection successful! Provider is ready."
            )
        else:
            return TestKeyResponse(
                provider_id=req.provider_id,
                status="error",
                latency_ms=latency,
                message=res.error or "Authentication failed."
            )
    except Exception as e:
        latency = round((time.perf_counter() - start) * 1000, 1)
        return TestKeyResponse(
            provider_id=req.provider_id,
            status="error",
            latency_ms=latency,
            message=f"Connection error: {str(e)}"
        )
