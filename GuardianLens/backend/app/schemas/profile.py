from pydantic import BaseModel
from typing import Optional
from datetime import date

# Shared properties
class ProfileBase(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None

# Properties to receive via API on creation
class ProfileCreate(ProfileBase):
    name: str  # Make name required on creation

# Properties to receive via API on update
class ProfileUpdate(ProfileBase):
    pass  # All fields optional for update

# Properties stored in DB
class ProfileInDBBase(ProfileBase):
    id: int
    name: str
    parent_id: int  # Include parent_id

    model_config = {
        "from_attributes": True
    }

# Additional properties to return to client
class Profile(ProfileInDBBase):
    pass  # Inherits readable fields

# Schema for reading multiple profiles (e.g., in a list)
class Profiles(BaseModel):
    profiles: list[Profile]
    total: int