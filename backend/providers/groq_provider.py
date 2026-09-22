import time
from typing import Optional
import httpx
from config.settings import settings
from providers.base import LLMProvider, LLMResponse

class GroqProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key, model or settings.GROQ_MODEL)

    def provider_name(self) -> str:
        return "Groq LLaMA"

    def model_name(self) -> str:
        return self._model or settings.GROQ_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        if not self.is_configured():
            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                status="error",
                error="Groq API Key is not configured. Please add your key in the BYOK settings."
            )

        start_time = time.perf_counter()
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model_name(),
                "messages": messages,
                "temperature": 0.2
            }

            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            content = data["choices"][0]["message"]["content"] or ""

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
                error=f"Groq API Error: {str(e)}"
            )
