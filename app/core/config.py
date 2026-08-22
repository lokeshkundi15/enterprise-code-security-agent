import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Code Review & Security Agent"
    ENVIRONMENT: str = "development"
    
    # LLM API Keys
    GROQ_API_KEY: str = ""
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    
    # GitHub Webhook Security
    WEBHOOK_SECRET: str = "dev_webhook_secret_key"
    GITHUB_TOKEN: Optional[str] = None
    
    # Persistence
    DB_PATH: str = "data/agent_state.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()