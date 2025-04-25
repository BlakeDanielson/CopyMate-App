from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from backend.database import Base
from backend.models.base import PlatformType

class ParentUser(Base):
    """
    Represents a parent user account in the system.
    """
    __tablename__ = "parent_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to ChildProfile
    child_profiles = relationship("ChildProfile", back_populates="parent", cascade="all, delete-orphan")
    
    # Relationship to AuditLog
    audit_logs = relationship("AuditLog", back_populates="parent", cascade="all, delete-orphan")
    
    # Relationship to NotificationPreferences
    notification_preferences = relationship("NotificationPreferences", back_populates="parent", cascade="all, delete-orphan", uselist=False)
    
    # Relationship to DeviceToken
    device_tokens = relationship("DeviceToken", back_populates="parent", cascade="all, delete-orphan")


class ChildProfile(Base):
    """
    Represents a child profile created by a parent user.
    """
    __tablename__ = "child_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parent_users.id", ondelete="CASCADE"), nullable=False)
    display_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)  # For COPPA compliance checks
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("ParentUser", back_populates="child_profiles")
    linked_accounts = relationship("LinkedAccount", back_populates="child_profile", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="child_profile", cascade="all, delete-orphan")
    coppa_verifications = relationship("CoppaVerification", back_populates="child_profile", cascade="all, delete-orphan")


class LinkedAccount(Base):
    """
    Represents a social media account linked to a child profile.
    For the MVP, only YouTube platform is supported.
    """
    __tablename__ = "linked_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    child_profile_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)  # Using string to allow for easy expansion beyond the enum
    platform_account_id = Column(String(255), nullable=False)  # External ID from the platform
    platform_username = Column(String(255), nullable=True)
    access_token = Column(String(255), nullable=False)  # Encrypted OAuth token
    refresh_token = Column(String(255), nullable=True)  # Encrypted OAuth refresh token
    token_expiry = Column(DateTime(timezone=True), nullable=True)
    platform_metadata = Column(JSON, nullable=True)  # Additional platform-specific information
    is_active = Column(Boolean, default=True)
    last_scan_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    child_profile = relationship("ChildProfile", back_populates="linked_accounts")
    subscribed_channels = relationship("SubscribedChannel", back_populates="linked_account", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        # Composite index for efficient queries
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )