from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class NotificationPreferencesBase(BaseModel):
    """Base schema for notification preferences."""
    email_enabled: bool = True
    push_enabled: bool = True
    scan_complete_notifications: bool = True
    new_flags_notifications: bool = True
    high_risk_notifications: bool = True
    account_change_notifications: bool = True
    
class NotificationPreferencesCreate(NotificationPreferencesBase):
    """Schema for creating notification preferences."""
    parent_id: int
    
class NotificationPreferencesUpdate(BaseModel):
    """Schema for updating notification preferences."""
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    scan_complete_notifications: Optional[bool] = None
    new_flags_notifications: Optional[bool] = None
    high_risk_notifications: Optional[bool] = None
    account_change_notifications: Optional[bool] = None
    
class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Schema for notification preferences response."""
    id: int
    parent_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        
class DeviceRegistrationBase(BaseModel):
    """Base schema for device registration."""
    device_token: str
    device_type: str = Field(..., description="Device type (e.g., 'ios', 'android', 'web')")
    device_name: Optional[str] = None
    
class DeviceRegistrationCreate(DeviceRegistrationBase):
    """Schema for registering a device."""
    parent_id: int
    
class DeviceRegistrationResponse(DeviceRegistrationBase):
    """Schema for device registration response."""
    id: int
    parent_id: int
    created_at: datetime
    last_used_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        
class NotificationTestRequest(BaseModel):
    """Schema for testing notifications."""
    notification_type: str = Field(..., description="Type of notification to test (email, push)")
    
class NotificationTestResponse(BaseModel):
    """Schema for notification test response."""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None