from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from backend.models.base import AuditActionType

class AuditLogBase(BaseModel):
    parent_id: Optional[int] = None
    action: AuditActionType
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True