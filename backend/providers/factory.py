from typing import Dict, Optional, List
from providers.base import LLMProvider
from providers.gemini_provider import GeminiProvider
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.groq_provider import GroqProvider
from providers.mock_provider import MockLLMProvider
from security.key_manager import KeyManager

class ProviderFactory:
    """
    Creates and configures LLM providers dynamically based on:
    - User-provided BYOK keys
    - System environment fallbacks
    - Simulated test/demo fallback options
    """

    AVAILABLE_PROVIDERS = [
        {"id": "gemini", "name": "Google Gemini", "default_model": "gemini-3.8-flash", "requires_key": True},
        {"id": "openai", "name": "OpenAI", "default_model": "gpt-4o-mini", "requires_key": True},
        {"id": "anthropic", "name": "Anthropic Claude", "default_model": "claude-3-5-sonnet-20241022", "requires_key": True},
        {"id": "groq", "name": "Groq LLaMA", "default_model": "llama-3.3-70b-versatile", "requires_key": True},
        {"id": "mock_gpt", "name": "Simulated GPT-4o (Test/Demo)", "default_model": "simulated-gpt-4o", "requires_key": False},
        {"id": "mock_gemini", "name": "Simulated Gemini (Test/Demo)", "default_model": "simulated-gemini-3.8", "requires_key": False},
        {"id": "mock_claude", "name": "Simulated Claude (Test/Demo)", "default_model": "simulated-claude-3.5", "requires_key": False},
    ]

    @classmethod
    def get_provider(
        cls,
        provider_id: str,
        user_keys: Optional[Dict[str, str]] = None,
        header_key: Optional[str] = None,
        allow_demo_fallback: bool = True
    ) -> LLMProvider:
        pid = provider_id.lower().strip()

        # Simulated providers
        if pid == "mock_gpt" or pid == "simulated_gpt":
            return MockLLMProvider(persona="gpt")
        elif pid == "mock_gemini" or pid == "simulated_gemini":
            return MockLLMProvider(persona="gemini")
        elif pid == "mock_claude" or pid == "simulated_claude":
            return MockLLMProvider(persona="claude")

        # Resolve real key
        key = KeyManager.resolve_key(pid, user_keys=user_keys, header_key=header_key)

        if "gemini" in pid or "google" in pid:
            if not key and allow_demo_fallback:
                return MockLLMProvider(persona="gemini")
            return GeminiProvider(api_key=key)

        elif "openai" in pid:
            if not key and allow_demo_fallback:
                return MockLLMProvider(persona="gpt")
            return OpenAIProvider(api_key=key)

        elif "anthropic" in pid or "claude" in pid:
            if not key and allow_demo_fallback:
                return MockLLMProvider(persona="claude")
            return AnthropicProvider(api_key=key)

        elif "groq" in pid:
            if not key and allow_demo_fallback:
                return MockLLMProvider(persona="groq")
            return GroqProvider(api_key=key)

        # Default fallback
        return MockLLMProvider(persona="gpt")
