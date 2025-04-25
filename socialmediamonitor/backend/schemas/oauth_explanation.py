from pydantic import BaseModel
from typing import List, Dict, Optional


class DataAccessItem(BaseModel):
    """Schema for a single data access item explanation."""
    data_type: str
    description: str
    example: Optional[str] = None
    is_required: bool = True


class OAuthExplanation(BaseModel):
    """Schema for OAuth process explanation."""
    platform: str
    title: str
    description: str
    data_accessed: List[DataAccessItem]
    process_steps: List[Dict[str, str]]
    privacy_notes: List[str]
    age_specific_info: Optional[Dict[str, str]] = None


class OAuthExplanationResponse(BaseModel):
    """Response schema for OAuth explanation."""
    explanation: OAuthExplanation