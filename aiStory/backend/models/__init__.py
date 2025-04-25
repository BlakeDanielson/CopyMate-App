"""Models package for AI Story Creator.

This package contains SQLAlchemy ORM models that define the database schema.
All model classes should inherit from the Base class defined in base.py.
"""

# Import all models here for SQLAlchemy discovery
from .base import Base
from .user import User
from .photo import Photo
from .story import Story
from .story_page import StoryPage

__all__ = [
    "Base",
    "User",
    "Photo",
    "Story",
    "StoryPage",
]