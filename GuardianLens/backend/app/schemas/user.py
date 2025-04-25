from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8) # Enforce min length
    full_name: str

# Properties to receive via API on update (optional for now)
class UserUpdate(UserBase):
    password: Optional[str] = None

# Properties stored in DB
class UserInDBBase(UserBase):
    id: int
    # Add fields from the model that should be readable
    email: EmailStr
    full_name: str

    model_config = { # Use model_config for Pydantic v2
        "from_attributes": True # Renamed from orm_mode
    }

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

# Additional properties to return to client
class User(UserInDBBase):
    pass # Inherits readable fields from UserInDBBase