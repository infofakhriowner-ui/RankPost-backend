# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # JWT settings
    JWT_SECRET: str  # Required, must be in .env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Encryption key
    FERNET_KEY_BASE64: str  # Required, must be in .env

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_IMAGE_MODEL: str = "gpt-image-1"

    # CORS settings (comma-separated string in .env)
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Database
    DATABASE_URL: str = "sqlite:///./rankpost.db"

    # Optional flags
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

    @property
    def cors_origins_list(self) -> List[str]:
        """Return the CORS origins as a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

# Load settings
settings = Settings()
