from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class ParentUserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ParentUserCreate(ParentUserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class ParentUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength if provided"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class ParentUserInDB(ParentUserBase):
    id: int
    hashed_password: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ParentUserResponse(ParentUserBase):
    id: int
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ChildProfileBase(BaseModel):
    display_name: str
    age: Optional[int] = Field(None, ge=0, le=18)
    notes: Optional[str] = None


class ChildProfileCreate(ChildProfileBase):
    parent_id: int


class ChildProfileUpdate(ChildProfileBase):
    display_name: Optional[str] = None
    parent_id: Optional[int] = None


class ChildProfileInDB(ChildProfileBase):
    id: int
    parent_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ChildProfileResponse(ChildProfileBase):
    id: int
    parent_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ChildProfileWithLinkedAccounts(ChildProfileResponse):
    linked_accounts: List = []

    class Config:
        orm_mode = True