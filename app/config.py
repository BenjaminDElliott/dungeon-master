"""Configuration management for the Dungeon Master app."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file.

    All settings have sensible defaults suitable for development.
    """

    # Server
    app_name: str = "Dungeon Master"
    debug: bool = True

    # LLM / OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    llm_temperature: float = 0.8
    llm_max_tokens: int = 512

    # Database
    database_url: str = "sqlite:///./dungeon.db"

    # CORS
    cors_origins: list[str] = ["*"]

    model_config = {"env_prefix": "DM_"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Cached so that the app reads env vars once at startup.
    """
    return Settings()
