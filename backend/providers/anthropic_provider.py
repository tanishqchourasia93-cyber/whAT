import time
from typing import Optional
import httpx
from config.settings import settings
from providers.base import LLMProvider, LLMResponse

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key, model or settings.ANTHROPIC_MODEL)

    def provider_name(self) -> str:
        return "Anthropic Claude"

    def model_name(self) -> str:
        return self._model or settings.ANTHROPIC_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        if not self.is_configured():
            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                status="error",
                error="Anthropic API Key is not configured. Please add your key in the BYOK settings."
            )

        start_time = time.perf_counter()
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": self.model_name(),
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                payload["system"] = system_prompt

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            text_blocks = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
            content = "\n".join(text_blocks)

            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                content=content,
                latency_ms=round(elapsed_ms, 2),
                status="success"
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                latency_ms=round(elapsed_ms, 2),
                status="error",
                error=f"Anthropic API Error: {str(e)}"
            )
