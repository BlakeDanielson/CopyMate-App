from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class VerificationMethodEnum(str, Enum):
    """Enum for COPPA verification methods."""
    CREDIT_CARD = "credit_card"
    GOVERNMENT_ID = "government_id"
    DIGITAL_SIGNATURE = "digital_signature"
    PHONE_VERIFICATION = "phone_verification"
    EMAIL_VERIFICATION = "email_verification"


class VerificationStatusEnum(str, Enum):
    """Enum for COPPA verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class CoppaVerificationBase(BaseModel):
    """Base schema for COPPA verification."""
    child_profile_id: int
    verification_method: VerificationMethodEnum
    parent_email: EmailStr
    parent_full_name: str
    parent_statement: bool = Field(..., description="Parent statement of consent")
    platform: str = Field(..., description="Platform being linked (e.g., 'youtube')")


class CoppaVerificationCreate(CoppaVerificationBase):
    """Schema for creating a COPPA verification."""
    verification_data: Dict[str, Any] = Field(
        ..., 
        description="Method-specific verification data (e.g., last 4 digits of credit card)"
    )
    
    @validator('parent_statement')
    def validate_parent_statement(cls, v):
        """Validate that the parent has agreed to the statement."""
        if not v:
            raise ValueError("Parent must agree to the consent statement")
        return v


class CoppaVerificationUpdate(BaseModel):
    """Schema for updating a COPPA verification."""
    verification_status: Optional[VerificationStatusEnum] = None
    verification_notes: Optional[str] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class CoppaVerificationResponse(CoppaVerificationBase):
    """Response schema for COPPA verification."""
    id: int
    verification_status: VerificationStatusEnum
    verification_notes: Optional[str] = None
    created_at: datetime
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class CoppaVerificationRequest(BaseModel):
    """Request schema for initiating COPPA verification."""
    child_profile_id: int
    platform: str
    verification_method: VerificationMethodEnum
    parent_email: EmailStr
    parent_full_name: str
    parent_statement: bool
    verification_data: Dict[str, Any]


class CoppaVerificationResult(BaseModel):
    """Result schema for COPPA verification."""
    verification_id: str
    verification_status: VerificationStatusEnum
    message: str
    next_steps: Optional[List[str]] = None
    authorization_url: Optional[str] = None