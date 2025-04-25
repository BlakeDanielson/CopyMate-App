"""StoryPage model for the application."""
import uuid
from typing import Optional
from enum import Enum

from sqlalchemy import Column, String, Integer, ForeignKey, Text, UniqueConstraint
from sqlalchemy.sql import text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

from .base import Base


class GenerationStatus(str, Enum):
    """Enum for generation status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class StoryPage(Base):
    """StoryPage model for storing pages of a story."""
    
    __tablename__ = "story_pages"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    # Foreign key relationship with Story
    story_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("stories.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Page information
    page_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Content
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_image_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    personalized_image_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Generation status
    text_generation_status: Mapped[str] = mapped_column(
        String, 
        default=GenerationStatus.PENDING.value,
        nullable=True,
        index=True
    )
    
    image_generation_status: Mapped[str] = mapped_column(
        String, 
        default=GenerationStatus.PENDING.value,
        nullable=True,
        index=True
    )
    
    personalization_status: Mapped[str] = mapped_column(
        String, 
        default=GenerationStatus.PENDING.value,
        nullable=True,
        index=True
    )
    
    # Inherit timestamps from Base class
    
    # Relationships
    story = relationship("Story", back_populates="pages")
    
    # Unique constraint to ensure page numbers are unique within a story
    __table_args__ = (
        UniqueConstraint("story_id", "page_number", name="uix_story_page_number"),
    )
    
    def __repr__(self) -> str:
        """String representation of the StoryPage model."""
        return f"<StoryPage {self.id} - Story: {self.story_id}, Page: {self.page_number}>"