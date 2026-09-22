import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "VeriAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Default LLM Models
    GEMINI_MODEL: str = "gemini-3.8-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Optional System API Keys (fallback if user has not provided BYOK)
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    # Verification settings
    MAX_CLAIMS_TO_VERIFY: int = 10
    SEARCH_RESULTS_PER_CLAIM: int = 4
    SIMULATE_DELAY_SECS: float = 0.5

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
