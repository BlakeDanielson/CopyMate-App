"""Photo schemas for API requests and responses."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class PhotoStatus(str, Enum):
    """Enum for photo upload status."""
    PENDING_UPLOAD = "pending_upload"
    UPLOADED = "uploaded"
    FAILED = "failed"


class AIProcessingStatus(str, Enum):
    """Enum for AI processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PhotoBase(BaseModel):
    """Base schema for photo data."""
    storage_provider: str
    bucket: Optional[str] = None
    object_key: str 
    filename: str
    content_type: str
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class PhotoCreate(PhotoBase):
    """Schema for creating a new photo."""
    user_id: UUID
    status: Optional[PhotoStatus] = PhotoStatus.PENDING_UPLOAD
    ai_processing_status: Optional[AIProcessingStatus] = AIProcessingStatus.PENDING
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Validate that the content type is an image type."""
        if not v.startswith('image/'):
            raise ValueError('Content type must be an image type (e.g., image/jpeg, image/png)')
        return v
    
    @validator('storage_provider')
    def validate_storage_provider(cls, v):
        """Validate the storage provider."""
        allowed_providers = ['s3', 'gcs', 'local']
        if v not in allowed_providers:
            raise ValueError(f'Storage provider must be one of: {", ".join(allowed_providers)}')
        return v


class PhotoUpdate(BaseModel):
    """Schema for updating a photo."""
    status: Optional[PhotoStatus] = None
    ai_processing_status: Optional[AIProcessingStatus] = None
    detected_objects: Optional[Dict[str, Any]] = None
    detected_labels: Optional[Dict[str, Any]] = None
    face_details: Optional[Dict[str, Any]] = None
    ai_error_message: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        """Validate the photo status."""
        if v and v not in PhotoStatus.__members__.values():
            valid_statuses = [status.value for status in PhotoStatus]
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v
    
    @validator('ai_processing_status')
    def validate_ai_status(cls, v):
        """Validate the AI processing status."""
        if v and v not in AIProcessingStatus.__members__.values():
            valid_statuses = [status.value for status in AIProcessingStatus]
            raise ValueError(f'AI processing status must be one of: {", ".join(valid_statuses)}')
        return v


class PhotoRead(PhotoBase):
    """Schema for photo response."""
    id: UUID
    user_id: UUID
    status: PhotoStatus
    ai_processing_status: AIProcessingStatus
    detected_objects: Optional[Dict[str, Any]] = None
    detected_labels: Optional[Dict[str, Any]] = None
    face_details: Optional[Dict[str, Any]] = None
    ai_error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# For backward compatibility with existing code
PhotoResponse = PhotoRead