from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime, timedelta

from backend.database import Base
from backend.schemas.coppa_verification import VerificationMethodEnum, VerificationStatusEnum


class CoppaVerification(Base):
    """
    Represents a COPPA verification record for children under 13.
    """
    __tablename__ = "coppa_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    child_profile_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    verification_method = Column(Enum(VerificationMethodEnum), nullable=False)
    verification_status = Column(Enum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING, nullable=False)
    verification_notes = Column(Text, nullable=True)
    parent_email = Column(String(255), nullable=False)
    parent_full_name = Column(String(255), nullable=False)
    parent_statement = Column(Boolean, default=False, nullable=False)
    platform = Column(String(50), nullable=False)
    verification_data = Column(JSON, nullable=True)  # Encrypted or hashed sensitive data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    child_profile = relationship("ChildProfile", back_populates="coppa_verifications")
    
    @classmethod
    def create_with_expiry(cls, **kwargs):
        """
        Create a new COPPA verification with an expiry date.
        
        By default, verifications expire after 1 year.
        """
        if "verification_status" not in kwargs:
            kwargs["verification_status"] = VerificationStatusEnum.PENDING
            
        if kwargs.get("verification_status") == VerificationStatusEnum.VERIFIED:
            kwargs["verified_at"] = datetime.utcnow()
            
            # Set expiry date to 1 year from verification
            if "expires_at" not in kwargs:
                kwargs["expires_at"] = datetime.utcnow() + timedelta(days=365)
                
        return cls(**kwargs)
    
    def is_valid(self):
        """
        Check if the verification is valid.
        
        A verification is valid if it's verified and not expired.
        """
        if self.verification_status != VerificationStatusEnum.VERIFIED:
            return False
            
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
            
        return True