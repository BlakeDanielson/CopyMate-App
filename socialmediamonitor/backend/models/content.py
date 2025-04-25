from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime

from backend.database import Base
from backend.models.base import RiskCategory, AlertType, AuditActionType


class SubscribedChannel(Base):
    """
    Represents a YouTube channel that a child is subscribed to.
    """
    __tablename__ = "subscribed_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    linked_account_id = Column(Integer, ForeignKey("linked_accounts.id", ondelete="CASCADE"), nullable=False)
    channel_id = Column(String(255), nullable=False, index=True)  # Platform-specific channel identifier
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    subscriber_count = Column(Integer, nullable=True)
    video_count = Column(Integer, nullable=True)
    topic_details = Column(JSON, nullable=True)  # Stores topics associated with the channel
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    linked_account = relationship("LinkedAccount", back_populates="subscribed_channels")
    analyzed_videos = relationship("AnalyzedVideo", back_populates="channel", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="channel", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        # Composite index for efficient queries
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )


class AnalyzedVideo(Base):
    """
    Represents metadata for a YouTube video that has been analyzed.
    """
    __tablename__ = "analyzed_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("subscribed_channels.id", ondelete="CASCADE"), nullable=False)
    video_platform_id = Column(String(255), nullable=False, index=True)  # Platform-specific video identifier
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(String(20), nullable=True)  # ISO 8601 format
    view_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    channel = relationship("SubscribedChannel", back_populates="analyzed_videos")
    analysis_results = relationship("AnalysisResult", back_populates="video", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        # Composite index for efficient queries
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )


class AnalysisResult(Base):
    """
    Represents the result of analyzing a channel or video for potentially harmful content.
    """
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("subscribed_channels.id", ondelete="CASCADE"), nullable=True)
    video_id = Column(Integer, ForeignKey("analyzed_videos.id", ondelete="CASCADE"), nullable=True)
    risk_category = Column(Enum(RiskCategory), nullable=False)
    severity = Column(String(20), nullable=True)  # e.g., 'high', 'medium', 'low'
    flagged_text = Column(Text, nullable=True)  # The text snippet that triggered the flag
    keywords_matched = Column(JSON, nullable=True)  # Array of matched keywords
    confidence_score = Column(Float, nullable=True)  # For potential future ML models
    marked_not_harmful = Column(Boolean, default=False)  # Parent feedback
    marked_not_harmful_at = Column(DateTime(timezone=True), nullable=True)
    marked_not_harmful_by = Column(Integer, ForeignKey("parent_users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    channel = relationship("SubscribedChannel", back_populates="analysis_results")
    video = relationship("AnalyzedVideo", back_populates="analysis_results")
    
    # Indexes
    __table_args__ = (
        # Composite index for efficient queries
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )


class Alert(Base):
    """
    Represents a notification to be sent to the parent about analysis results.
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    child_profile_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    summary_data = Column(JSON, nullable=True)  # Summary information like number of flags
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    child_profile = relationship("ChildProfile", back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        # Composite index for efficient queries
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )


class AuditLog(Base):
    """
    Records significant system events, including user actions and data access.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parent_users.id"), nullable=True)
    action = Column(Enum(AuditActionType), nullable=False)
    resource_type = Column(String(100), nullable=True)  # Type of resource (e.g., "child_profile", "linked_account")
    resource_id = Column(Integer, nullable=True)  # ID of the affected resource
    details = Column(JSON, nullable=True)  # Additional information about the action
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6 address
    user_agent = Column(String(512), nullable=True)  # Browser/client info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("ParentUser", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        # Index for efficient audit trail queries
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )