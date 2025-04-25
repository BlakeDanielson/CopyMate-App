from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum

class PlatformEnum(str, Enum):
    YOUTUBE = "youtube"
    # Add more platforms as needed

class LinkedAccountBase(BaseModel):
    child_profile_id: int
    platform: str
    platform_account_id: str
    platform_username: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    metadata: Optional[Any] = None
    is_active: bool = True

class LinkedAccountCreate(LinkedAccountBase):
    pass

class LinkedAccountResponse(LinkedAccountBase):
    id: int
    last_scan_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class LinkedAccountUpdate(BaseModel):
    platform_username: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    metadata: Optional[Any] = None
    is_active: Optional[bool] = None

class LinkedAccountInitiate(BaseModel):
    """Schema for initiating the account linking process."""
    child_profile_id: int
    platform: PlatformEnum = Field(..., description="The platform to link (e.g., 'youtube')")
    
class OAuthState(BaseModel):
    """Schema for OAuth state data."""
    child_profile_id: int
    platform: str
    parent_id: int
    timestamp: datetime
    
class OAuthInitiateResponse(BaseModel):
    """Response schema for OAuth initiation."""
    authorization_url: str
    state: str