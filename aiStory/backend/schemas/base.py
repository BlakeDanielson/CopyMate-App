"""Base schemas and common schema utilities."""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configurations."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM mode (from_orm)
        populate_by_name=True,  # Allow populating by field name and alias
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
        }
    )


# Define TypeVar for use with generic models
T = TypeVar('T')


class PaginatedResponse(BaseSchema, Generic[T]):
    """Standard paginated response format."""
    
    data: List[T]
    meta: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total": 0,
            "page": 1,
            "per_page": 10,
            "pages": 1,
        }
    )
    links: Dict[str, Optional[str]] = Field(
        default_factory=lambda: {
            "self": None,
            "next": None,
            "prev": None,
        }
    )


class ErrorResponse(BaseSchema):
    """Standard error response format."""
    
    error: Dict[str, Any] = Field(
        default_factory=lambda: {
            "code": "UNKNOWN_ERROR",
            "message": "An unknown error occurred",
            "details": {},
        }
    )