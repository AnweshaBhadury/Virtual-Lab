"""
Central place for all settings. Everything is read from environment
variables (see .env.example). Using pydantic-settings means you get
clear errors if something required is missing.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Auth
    JWT_SECRET: str = "change-this-to-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database - SQLite file, works fully offline, no server needed
    DATABASE_URL: str = "sqlite:///./engitwin.db"

    # AI assistant
    AI_PROVIDER: str = "anthropic"  # "anthropic", "openai", or "local"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    LOCAL_AI_URL: str = "http://localhost:11434/api/generate"
    LOCAL_AI_MODEL: str = "llama3"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()