"""Story model for the application."""
import uuid
from typing import List, Optional
from enum import Enum

from sqlalchemy import Column, String, Integer, ForeignKey, Text, UniqueConstraint
from sqlalchemy.sql import text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

from .base import Base


class StoryStatus(str, Enum):
    """Enum for story generation status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Story(Base):
    """Story model for storing user-created stories."""
    
    __tablename__ = "stories"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    # Foreign key relationship with User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Child information
    child_name: Mapped[str] = mapped_column(String, nullable=False)
    child_age: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Story information
    story_theme: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Foreign key relationship with Photo (protagonist)
    protagonist_photo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("photos.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Story content
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(
        String, 
        default=StoryStatus.PENDING.value,
        nullable=False,
        index=True
    )
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Inherit timestamps from Base class
    
    # Relationships
    user = relationship("User", back_populates="stories")
    protagonist_photo = relationship("Photo")
    pages = relationship("StoryPage", back_populates="story", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="story", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the Story model."""
        return f"<Story {self.id} - {self.title or 'Untitled'}>"