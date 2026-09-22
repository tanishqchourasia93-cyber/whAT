from typing import Optional, Dict
from config.settings import settings

def mask_api_key(key: Optional[str]) -> Optional[str]:
    """
    Returns a masked version of the API key for safe UI display.
    Example: sk-1234567890abcdef -> sk-...cdef
    """
    if not key:
        return None
    key = key.strip()
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"

class KeyManager:
    """
    Manages BYOK (Bring Your Own Key) resolution.
    Prioritizes request-level keys provided by the user,
    falling back to system environment variables if present.
    Ensures keys are never logged in plaintext.
    """

    @staticmethod
    def resolve_key(
        provider: str,
        user_keys: Optional[Dict[str, str]] = None,
        header_key: Optional[str] = None
    ) -> Optional[str]:
        # 1. Header takes highest precedence
        if header_key and header_key.strip():
            return header_key.strip()

        # 2. Body-provided user keys
        if user_keys and provider in user_keys and user_keys[provider]:
            k = user_keys[provider].strip()
            if k:
                return k

        # 3. System environment fallback
        provider_lower = provider.lower()
        if "gemini" in provider_lower or "google" in provider_lower:
            return settings.GEMINI_API_KEY
        elif "openai" in provider_lower:
            return settings.OPENAI_API_KEY
        elif "anthropic" in provider_lower or "claude" in provider_lower:
            return settings.ANTHROPIC_API_KEY
        elif "groq" in provider_lower:
            return settings.GROQ_API_KEY
        return None
