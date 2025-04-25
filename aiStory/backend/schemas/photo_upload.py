"""Schemas for photo upload and related operations."""
import mimetypes
import uuid
from enum import Enum
from typing import List, Optional, Set, Dict, Any

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field, validator

from backend.models.photo import PhotoStatus, AIProcessingStatus


# Set of allowed image MIME types
ALLOWED_IMAGE_TYPES: Set[str] = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/tiff',
    'image/svg+xml',
    'image/heic',
    'image/heif',
}

# Maximum file size in bytes (10MB)
MAX_FILE_SIZE: int = 10 * 1024 * 1024


class PhotoUploadResponse(BaseModel):
    """Response schema for photo upload."""
    photo_id: str
    status: PhotoStatus
    message: str


class PhotoUploadForm:
    """Form for uploading photos.
    
    This is a class rather than a Pydantic model because we need to handle
    file uploads using FastAPI's File() and Form() dependencies.
    """
    
    def __init__(
        self,
        file: UploadFile = File(..., description="The photo file to upload"),
        description: Optional[str] = Form(None, description="Optional description of the photo"),
        tags: Optional[str] = Form(None, description="Optional comma-separated tags")
    ):
        """Initialize the photo upload form.
        
        Args:
            file: The photo file to upload
            description: Optional description of the photo
            tags: Optional comma-separated tags
        """
        self.file = file
        self.description = description
        self.tags = tags.split(',') if tags else []
        
    async def validate(self) -> None:
        """Validate the uploaded file.
        
        Raises:
            ValueError: If the file is not a valid image or exceeds the size limit
        """
        # Check content type
        content_type = self.file.content_type or mimetypes.guess_type(self.file.filename)[0]
        if not content_type or content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(
                f"Unsupported file type: {content_type}. "
                f"Supported types: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        # Check file size
        # Get the file size by seeking to the end and getting position
        await self.file.seek(0)  # Go to start
        file_content = await self.file.read()
        file_size = len(file_content)
        await self.file.seek(0)  # Reset position after reading
        
        if file_size > MAX_FILE_SIZE:
            max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
            raise ValueError(
                f"File size ({file_size / (1024 * 1024):.2f}MB) exceeds the maximum "
                f"allowed size of {max_size_mb:.2f}MB"
            )


class PhotoProcessingResult(BaseModel):
    """Result of photo processing."""
    photo_id: str
    status: PhotoStatus
    ai_status: Optional[AIProcessingStatus] = None
    processed_url: Optional[str] = None
    thumbnails: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    ai_provider_used: Optional[str] = None


class AIProcessingResponse(BaseModel):
    """Response schema for AI processing results."""
    photo_id: str
    ai_processing_status: AIProcessingStatus
    ai_provider_used: Optional[str] = None
    ai_results: Optional[Dict[str, Any]] = None
    ai_error_message: Optional[str] = None


class PhotoListFilters(BaseModel):
    """Filters for listing photos."""
    status: Optional[PhotoStatus] = None
    ai_processing_status: Optional[AIProcessingStatus] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    tags: Optional[List[str]] = None
    page: int = 1
    page_size: int = 20


class PhotoUploadUrlRequest(BaseModel):
    """Request schema for obtaining a pre-signed URL for photo upload."""
    filename: str = Field(..., description="The filename of the photo to upload")
    content_type: str = Field(..., description="The content type of the photo file")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Validate that the content type is an image type."""
        if v not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Content type must be one of: {', '.join(ALLOWED_IMAGE_TYPES)}")
        return v


class PhotoUploadUrlResponse(BaseModel):
    """Response schema for pre-signed URL generation."""
    upload_url: str = Field(..., description="The pre-signed URL for uploading the photo")
    photo_id: str = Field(..., description="UUID of the created Photo record")
    object_key: str = Field(..., description="The key/path within the storage bucket")
    fields: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Any additional fields needed for the upload (e.g., for S3 POST policy)"
    )