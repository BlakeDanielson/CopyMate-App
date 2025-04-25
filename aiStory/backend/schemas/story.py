"""Schemas for Story model."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Union
from uuid import UUID

from pydantic import Field, validator

from .base import BaseSchema
from .story_page import StoryPageRead
from models.story import StoryStatus


class StoryTheme(str, Enum):
    """Enum for story themes."""
    SPACE_ADVENTURE = "space_adventure"
    FAIRY_TALE = "fairy_tale"
    JUNGLE_EXPEDITION = "jungle_expedition"
    OCEAN_EXPLORATION = "ocean_exploration"
    DINOSAUR_TIME = "dinosaur_time"
    SUPERHERO = "superhero"


class StoryBase(BaseSchema):
    """Base schema for a story."""
    
    child_name: str = Field(..., min_length=1, max_length=50, description="Name of the child protagonist")
    child_age: int = Field(..., ge=1, le=17, description="Age of the child protagonist")
    story_theme: str = Field(..., description="Theme of the story")
    title: Optional[str] = Field(None, description="Title of the story")
    
    @validator('story_theme')
    def validate_theme(cls, v):
        """Validate that the theme is one of our predefined options."""
        if v not in [theme.value for theme in StoryTheme]:
            raise ValueError(f"Invalid theme: {v}. Must be one of {[theme.value for theme in StoryTheme]}")
        return v


class StoryCreate(StoryBase):
    """Schema for creating a new story."""
    
    user_id: UUID = Field(..., description="ID of the user creating the story")
    protagonist_photo_id: UUID = Field(..., description="ID of the photo to use for personalization")
    status: Optional[str] = Field(
        default=StoryStatus.PENDING.value,
        description="Status of the story generation process"
    )
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status value against the enum."""
        if v not in [status.value for status in StoryStatus]:
            raise ValueError(f"Invalid status: {v}. Must be one of {[status.value for status in StoryStatus]}")
        return v


class StoryUpdate(BaseSchema):
    """Schema for updating a story."""
    
    title: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status value against the enum."""
        if v is not None and v not in [status.value for status in StoryStatus]:
            raise ValueError(f"Invalid status: {v}. Must be one of {[status.value for status in StoryStatus]}")
        return v


class StoryRead(StoryBase):
    """Schema for reading a story, including all fields and nested pages."""
    
    id: UUID
    user_id: UUID
    protagonist_photo_id: UUID
    status: str = Field(default=StoryStatus.PENDING.value)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    pages: List[StoryPageRead] = Field(default_factory=list)