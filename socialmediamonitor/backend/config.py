import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # API settings
    api_title: str = "GuardianLens API"
    api_description: str = "API for GuardianLens social media monitoring tool"
    api_version: str = "0.1.0"
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/socialmediamonitor")
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Celery settings
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    
    # YouTube API settings
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY")
    youtube_client_id: str = os.getenv("YOUTUBE_CLIENT_ID")
    youtube_client_secret: str = os.getenv("YOUTUBE_CLIENT_SECRET")
    youtube_redirect_uri: str = os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:8000/api/v1/oauth/callback")
    
    # Email notification settings
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    email_sender: str = os.getenv("EMAIL_SENDER", "notifications@guardianlens.com")
    email_enabled: bool = os.getenv("EMAIL_ENABLED", "False").lower() == "true"
    
    # Push notification settings
    fcm_api_key: str = os.getenv("FCM_API_KEY", "")  # Firebase Cloud Messaging API key
    push_enabled: bool = os.getenv("PUSH_ENABLED", "False").lower() == "true"
    
    # Authentication settings
    secret_key: str = os.getenv("SECRET_KEY", "supersecretkey")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings instance
settings = Settings()