import time
from typing import Optional
from google import genai
from config.settings import settings
from providers.base import LLMProvider, LLMResponse

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key, model or settings.GEMINI_MODEL)
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def provider_name(self) -> str:
        return "Google Gemini"

    def model_name(self) -> str:
        return self._model or settings.GEMINI_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        if not self.is_configured():
            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                status="error",
                error="Gemini API Key is not configured. Please add your key in the BYOK settings."
            )

        start_time = time.perf_counter()
        try:
            # We initialize client with the active key
            client = genai.Client(api_key=self.api_key)
            # Use interactions.create per latest google-genai guidelines
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            interaction = client.interactions.create(
                model=self.model_name(),
                input=full_prompt
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            content = interaction.output_text or ""
            return LLMResponse(
                provider_name=self.provider_name(),
                model_name=self.model_name(),
                content=content,
                latency_ms=round(elapsed_ms, 2),
                status="success"
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            # Fallback to models.generate_content if interactions API behaves differently on some keys
            try:
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=self.model_name(),
                    contents=prompt
                )
                return LLMResponse(
                    provider_name=self.provider_name(),
                    model_name=self.model_name(),
                    content=response.text or "",
                    latency_ms=round(elapsed_ms, 2),
                    status="success"
                )
            except Exception as e_fallback:
                return LLMResponse(
                    provider_name=self.provider_name(),
                    model_name=self.model_name(),
                    latency_ms=round(elapsed_ms, 2),
                    status="error",
                    error=f"Gemini API Error: {str(e_fallback)}"
                )
