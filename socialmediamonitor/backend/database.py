import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Configuration settings for database connection."""
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/socialmediamonitor")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = DatabaseSettings()

# Create SQLAlchemy engine
engine = create_engine(settings.database_url)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Dependency for FastAPI to get a database session.
    Yields a session and ensures it's closed when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()