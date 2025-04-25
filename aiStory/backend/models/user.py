"""User model for the application."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class User(Base):
    """User model for authentication and authorization."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String, default=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    
    # Authentication fields
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    
    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    profile_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Status fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Role-based authorization
    role: Mapped[str] = mapped_column(String, default="user")
    
    # Timestamps
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
        
    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User {self.username}>"