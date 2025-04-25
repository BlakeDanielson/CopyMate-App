from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from typing import List

class Settings(BaseSettings):
    # Example: Will load from .env file or environment variables
    PROJECT_NAME: str = "GuardianLens Backend"
    API_V1_STR: str = "/api/v1"

    # Database - Placeholder for local Docker setup initially
    # In deployed envs, this would point to Neon
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "app")
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

    # Redis (for Celery Broker & Cache) - Placeholder for local Docker setup
    REDIS_HOST: str = os.getenv("REDIS_HOST", "cache")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    CELERY_RESULT_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/1" # Use different DB for results

    # Add other settings as needed (JWT secrets, API keys, etc.)
    # SECRET_KEY: str = "YOUR_SECRET_KEY" # Load securely!
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env") # CHANGE THIS IN PRODUCTION VIA ENV VAR!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Example: 30 minutes

    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    # Ensure this matches the redirect URI registered in Google Cloud Console
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/youtube/auth/callback")
    YOUTUBE_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/youtube.readonly"
        # Add other scopes if needed later
    ]

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()