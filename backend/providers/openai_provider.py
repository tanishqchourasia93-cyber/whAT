import time
from typing import Optional
from openai import AsyncOpenAI
from config.settings import settings
from providers.base import LLMProvider, LLMResponse

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key, model or settings.OPENAI_MODEL)
        self.client = None
        if self.api_key:
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def provider_name(self) -> str:
        return "OpenAI"

    def model_name(self) -> str:
        return self._model or settings.OPENAI_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        if not self.is_configured():
            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                status="error",
                error="OpenAI API Key is not configured. Please add your key in the BYOK settings."
            )

        start_time = time.perf_counter()
        try:
            client = AsyncOpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            completion = await client.chat.completions.create(
                model=self.model_name(),
                messages=messages,
                temperature=0.2
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            content = completion.choices[0].message.content or ""
            tokens = completion.usage.total_tokens if completion.usage else None

            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                content=content,
                latency_ms=round(elapsed_ms, 2),
                token_count=tokens,
                status="success"
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                latency_ms=round(elapsed_ms, 2),
                status="error",
                error=f"OpenAI API Error: {str(e)}"
            )
