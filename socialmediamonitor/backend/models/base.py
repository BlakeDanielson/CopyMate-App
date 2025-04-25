from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from backend.database import Base

# Enum types
class PlatformType(enum.Enum):
    YOUTUBE = "youtube"
    # Future platforms can be added here

class RiskCategory(enum.Enum):
    HATE_SPEECH = "hate_speech"
    SELF_HARM = "self_harm"
    GRAPHIC_VIOLENCE = "graphic_violence"
    EXPLICIT_CONTENT = "explicit_content"
    BULLYING = "bullying"
    DANGEROUS_CHALLENGES = "dangerous_challenges"
    MISINFORMATION = "misinformation"

class AlertType(enum.Enum):
    SCAN_COMPLETE = "scan_complete"
    NEW_FLAGS = "new_flags"
    HIGH_RISK = "high_risk"
    ACCOUNT_CHANGE = "account_change"

class AuditActionType(enum.Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PROFILE_CREATE = "profile_create"
    PROFILE_UPDATE = "profile_update"
    PROFILE_DELETE = "profile_delete"
    ACCOUNT_LINK = "account_link"
    ACCOUNT_UNLINK = "account_unlink"
    MARK_NOT_HARMFUL = "mark_not_harmful"
    DATA_ACCESS = "data_access"
    SCAN_TRIGGERED = "scan_triggered"
    SYSTEM_ERROR = "system_error"