"""
Centralized app configuration.
Keeping this separate means nothing else in the codebase touches
os.environ directly - one source of truth for settings.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"

    class Config:
        env_file = ".env"


settings = Settings()
