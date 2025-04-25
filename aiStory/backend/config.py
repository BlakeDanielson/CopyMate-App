"""Configuration settings for the AI Story Creator backend."""
import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Find project root directory (one level up from backend)
ROOT_DIR = Path(__file__).parent.parent.resolve()


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings.
    
    This class manages all configuration settings for the application, sourced
    from environment variables with appropriate defaults where applicable.
    Environment variables are prefixed with 'aistory_'.
    """
    # Core application settings
    app_name: str = "AI Story Creator"
    debug: bool = False
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Environment settings
    environment: Environment = Environment.DEVELOPMENT
    
    # Database
    database_url: Optional[PostgresDsn] = None
    database_url_test: Optional[PostgresDsn] = None
    database_url_dev: Optional[PostgresDsn] = None
    database_url_prod: Optional[PostgresDsn] = None
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False
    db_echo_pool: bool = False
    db_pool_recycle: int = 300  # Recycle connections after 5 minutes
    db_pool_pre_ping: bool = True  # Enable connection health checks
    
    # Security
    secret_key: str  # Used for JWT encoding/decoding - MUST be set via AISTORY_SECRET_KEY env var
    access_token_expire_minutes: int = 60  # 1 hour
    refresh_token_expire_days: int = 7  # 7 days
    algorithm: str = "HS256"
    
    # CORS
    cors_origins: List[AnyHttpUrl] = []
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    auth_rate_limit_requests_per_minute: int = 10
    
    # Cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 60
    
    # Logging
    log_level: str = "INFO"
    
    # AI Service
    ai_service_url: Optional[AnyHttpUrl] = None
    ai_service_api_key: Optional[str] = None
    
    # File storage
    storage_backend: str = "local"  # Options: local, s3
    storage_local_path: str = "./uploads"
    storage_s3_bucket: Optional[str] = None
    storage_s3_region: Optional[str] = None
    storage_s3_access_key_id: Optional[str] = None
    storage_s3_secret_access_key: Optional[str] = None
    storage_s3_endpoint_url: Optional[str] = None  # Optional for custom S3-compatible storage
    
    # Celery settings for asynchronous task processing
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    celery_concurrency: int = 2
    
    # AI Processing settings
    ai_provider_type: str = "local"  # Options: local, aws_rekognition, google_vision
    
    # AWS settings
    aws_region: Optional[str] = None  # Required for AWS Rekognition
    
    # AWS Rekognition settings
    rekognition_max_labels: int = 10  # Maximum number of labels to return
    rekognition_min_confidence: float = 75.0  # Minimum confidence level (percentage)
    
    @field_validator("rekognition_max_labels")
    def validate_rekognition_max_labels(cls, v: int) -> int:
        """Validate that rekognition_max_labels is within acceptable boundaries.
        
        A valid value is between 1 and 100 to prevent potential abuse (e.g., DoS, cost escalation).
        """
        if v < 1 or v > 100:
            raise ValueError(
                "rekognition_max_labels must be between 1 and 100"
            )
        return v
    
    @field_validator("rekognition_min_confidence")
    def validate_rekognition_min_confidence(cls, v: float) -> float:
        """Validate that rekognition_min_confidence is within acceptable boundaries.
        
        A valid value is between 0 and 100 to prevent potential abuse.
        """
        if v < 0 or v > 100:
            raise ValueError(
                "rekognition_min_confidence must be between 0 and 100"
            )
        return v
    
    model_config = SettingsConfigDict(
        # Look for .env file in project root directory
        env_file=os.path.join(ROOT_DIR, '.env'),
        env_file_encoding='utf-8',
        env_prefix='aistory_',
        extra='ignore',
        case_sensitive=False,
    )
    
    @field_validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        """Validate that the secret key is sufficiently secure.
        
        A secure key should be at least 32 characters long and not use the default value.
        """
        default_key_patterns = [
            "CHANGE_ME",
            "your-secret-key",
            "secret-key",
            "secretkey",
            "changeme",
        ]
        
        if len(v) < 32:
            raise ValueError(
                "Secret key is too short. It should be at least 32 characters long. "
                "Generate a secure key using: openssl rand -hex 32"
            )
            
        # Check if the key contains any default patterns
        if any(pattern.lower() in v.lower() for pattern in default_key_patterns):
            raise ValueError(
                "Secret key appears to be a default or placeholder value. "
                "Please change it to a secure random value. "
                "Generate a secure key using: openssl rand -hex 32"
            )
            
        return v
    
    @field_validator("cors_origins", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string to list if provided as comma-separated string."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @field_validator("database_url", "database_url_test", "database_url_dev", "database_url_prod", mode="before")
    def assemble_db_connection(cls, v: Optional[str]) -> Optional[str]:
        """Ensure DB URL is properly formatted for SQLAlchemy."""
        if isinstance(v, str) and v.startswith("postgres://"):
            # Replace 'postgres://' with 'postgresql://' for SQLAlchemy 2.0+
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL based on the current environment."""
        if self.environment == Environment.TESTING and self.database_url_test:
            return str(self.database_url_test)
        elif self.environment == Environment.DEVELOPMENT and self.database_url_dev:
            return str(self.database_url_dev)
        elif self.environment == Environment.PRODUCTION and self.database_url_prod:
            return str(self.database_url_prod)
        elif self.database_url:
            return str(self.database_url)
        else:
            # Default to SQLite in-memory database
            return "sqlite+aiosqlite:///:memory:"


# Create a global instance of the settings
settings = Settings()


def get_settings() -> Settings:
    """Return the settings object as a dependency."""
    return settings