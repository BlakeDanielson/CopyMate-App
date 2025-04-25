"""Photo model for the application."""
import uuid
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, String, ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP

from .base import Base


class PhotoStatus(str, Enum):
    """Enum for photo status."""
    PENDING_UPLOAD = "pending_upload"
    UPLOADED = "uploaded"
    FAILED = "failed"


class AIProcessingStatus(str, Enum):
    """Enum for AI processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Photo(Base):
    """Photo model for storing user-uploaded images."""
    
    __tablename__ = "photos"
    
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
    
    # Storage information
    storage_provider: Mapped[str] = mapped_column(String, nullable=False)
    bucket: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    object_key: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    
    # File information
    filename: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(
        String, 
        default=PhotoStatus.PENDING_UPLOAD.value,
        nullable=False,
        index=True
    )
    
    # AI Processing fields
    ai_processing_status: Mapped[str] = mapped_column(
        String,
        default=AIProcessingStatus.PENDING.value,
        nullable=True,
        index=True
    )
    
    ai_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # JSON fields for AI processing results
    detected_objects = Column(JSONB, nullable=True, index=True)
    detected_labels = Column(JSONB, nullable=True, index=True)
    face_details = Column(JSONB, nullable=True)
    
    # Timestamps are inherited from Base class
    created_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )
    
    # Relationships
    user = relationship("User", back_populates="photos")
    
    def __repr__(self) -> str:
        """String representation of the Photo model."""
        return f"<Photo {self.id} - {self.filename}>"