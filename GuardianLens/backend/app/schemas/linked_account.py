from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base properties (excluding sensitive tokens)
class LinkedAccountBase(BaseModel):
    provider: Optional[str] = None
    profile_id: Optional[int] = None
    # Potentially add scopes or expiry if needed by frontend

# Properties stored in DB (Internal use, includes tokens)
class LinkedAccountInDBBase(LinkedAccountBase):
    id: int
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# Properties to return to client (Avoid returning tokens)
class LinkedAccount(LinkedAccountBase):
    id: int
    provider: str
    # Add any other safe fields the client might need

# Schema for creating/updating internally (includes tokens)
class LinkedAccountCreate(BaseModel):
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: Optional[str] = None
    profile_id: int

class LinkedAccountUpdate(BaseModel):  # For token refresh
    access_token: str
    expires_at: Optional[datetime] = None
    # Potentially update scopes if they change during refresh
    scopes: Optional[str] = None