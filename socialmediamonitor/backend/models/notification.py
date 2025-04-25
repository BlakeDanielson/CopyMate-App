from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from backend.database import Base

class NotificationPreferences(Base):
    """
    Stores notification preferences for parent users.
    """
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parent_users.id", ondelete="CASCADE"), nullable=False)
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    scan_complete_notifications = Column(Boolean, default=True)
    new_flags_notifications = Column(Boolean, default=True)
    high_risk_notifications = Column(Boolean, default=True)
    account_change_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("ParentUser", back_populates="notification_preferences")
    
    # Indexes
    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )

class DeviceToken(Base):
    """
    Stores device tokens for push notifications.
    """
    __tablename__ = "device_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parent_users.id", ondelete="CASCADE"), nullable=False)
    device_token = Column(String(255), nullable=False, index=True)
    device_type = Column(String(50), nullable=False)  # 'ios', 'android', 'web'
    device_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    parent = relationship("ParentUser", back_populates="device_tokens")
    
    # Indexes
    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )