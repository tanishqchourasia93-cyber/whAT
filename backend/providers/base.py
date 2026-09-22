from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class LLMResponse(BaseModel):
    provider_name: str
    model_name: str
    content: str = ""
    latency_ms: float = 0.0
    token_count: Optional[int] = None
    cost_estimate_usd: Optional[float] = None
    status: str = "success"  # "success" | "error"
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM Providers.
    Provides uniform interface for all models (Gemini, OpenAI, Claude, Groq, Mock).
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self._model = model

    @abstractmethod
    def provider_name(self) -> str:
        """Name of provider (e.g. Google Gemini, OpenAI, Anthropic Claude)."""
        pass

    @abstractmethod
    def model_name(self) -> str:
        """Name of the specific model (e.g. gemini-3.8-flash, gpt-4o)."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if provider has valid credentials to make requests."""
        pass

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        """Generate response asynchronously."""
        pass
