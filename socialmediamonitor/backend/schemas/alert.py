from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from backend.models.base import AlertType

class AlertBase(BaseModel):
    child_profile_id: int
    alert_type: AlertType
    title: str
    message: str
    summary_data: Optional[Any] = None
    is_read: bool = False

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True