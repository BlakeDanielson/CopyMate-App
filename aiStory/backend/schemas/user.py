"""User schemas for API requests and responses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: Optional[str] = "user"
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`' for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str  # Can be username or email
    password: str


class User(UserBase):
    """Schema for user response."""
    id: int
    uuid: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    refresh_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    """Schema for decoded token data."""
    sub: str  # User ID
    exp: datetime
    
    
class RefreshToken(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str