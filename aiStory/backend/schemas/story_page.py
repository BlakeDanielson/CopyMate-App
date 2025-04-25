"""Schemas for StoryPage model."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field, validator

from .base import BaseSchema
from models.story_page import GenerationStatus


class StoryPageBase(BaseSchema):
    """Base schema for a story page."""
    
    page_number: int = Field(..., gt=0, description="The sequential number of this page in the story")
    text: Optional[str] = Field(None, description="The generated text content for this page")
    base_image_key: Optional[str] = Field(None, description="The storage key for the base generated image")
    personalized_image_key: Optional[str] = Field(None, description="The storage key for the personalized image")


class StoryPageCreate(StoryPageBase):
    """Schema for creating a new story page."""
    
    story_id: UUID = Field(..., description="The ID of the story this page belongs to")
    text_generation_status: Optional[str] = Field(
        default=GenerationStatus.PENDING.value,
        description="Status of text generation"
    )
    image_generation_status: Optional[str] = Field(
        default=GenerationStatus.PENDING.value, 
        description="Status of image generation"
    )
    personalization_status: Optional[str] = Field(
        default=GenerationStatus.PENDING.value,
        description="Status of image personalization"
    )
    
    @validator('text_generation_status', 'image_generation_status', 'personalization_status')
    def validate_status(cls, v):
        """Validate status values against the enum."""
        if v not in [status.value for status in GenerationStatus]:
            raise ValueError(f"Invalid status: {v}. Must be one of {[status.value for status in GenerationStatus]}")
        return v


class StoryPageUpdate(BaseSchema):
    """Schema for updating a story page."""
    
    text: Optional[str] = None
    base_image_key: Optional[str] = None
    personalized_image_key: Optional[str] = None
    text_generation_status: Optional[str] = None
    image_generation_status: Optional[str] = None
    personalization_status: Optional[str] = None
    
    @validator('text_generation_status', 'image_generation_status', 'personalization_status')
    def validate_status(cls, v):
        """Validate status values against the enum."""
        if v is not None and v not in [status.value for status in GenerationStatus]:
            raise ValueError(f"Invalid status: {v}. Must be one of {[status.value for status in GenerationStatus]}")
        return v


class StoryPageRead(StoryPageBase):
    """Schema for reading a story page, including all fields."""
    
    id: UUID
    story_id: UUID
    text_generation_status: str = Field(
        default=GenerationStatus.PENDING.value,
        description="Status of text generation"
    )
    image_generation_status: str = Field(
        default=GenerationStatus.PENDING.value,
        description="Status of image generation"
    )
    personalization_status: str = Field(
        default=GenerationStatus.PENDING.value,
        description="Status of image personalization"
    )
    created_at: datetime
    updated_at: datetime