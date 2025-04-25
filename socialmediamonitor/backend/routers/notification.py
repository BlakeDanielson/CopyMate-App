from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.notification import NotificationPreferencesRepository, DeviceTokenRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.services.notification_service import NotificationService
from backend.schemas.notification import (
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
    DeviceRegistrationBase,
    DeviceRegistrationResponse,
    NotificationTestRequest,
    NotificationTestResponse
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
notification_prefs_repo = NotificationPreferencesRepository()
device_token_repo = DeviceTokenRepository()
audit_log_repo = AuditLogRepository()


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get notification preferences for the current user.
    If preferences don't exist, create default preferences.
    """
    preferences = notification_prefs_repo.get_by_parent_id(db, current_user.id)
    
    if not preferences:
        # Create default preferences
        preferences = notification_prefs_repo.create_default_preferences(db, current_user.id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="notification_preferences",
        details={}
    )
    
    return preferences


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    preferences_in: NotificationPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Update notification preferences for the current user.
    """
    # Update preferences
    updated_preferences = notification_prefs_repo.update_preferences(
        db, 
        current_user.id, 
        preferences_in.dict(exclude_unset=True)
    )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_UPDATED,
        parent_id=current_user.id,
        resource_type="notification_preferences",
        details={"fields_updated": list(preferences_in.dict(exclude_unset=True).keys())}
    )
    
    return updated_preferences


@router.get("/devices", response_model=List[DeviceRegistrationResponse])
async def get_registered_devices(
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get all registered devices for the current user.
    """
    devices = device_token_repo.get_by_parent_id(db, current_user.id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="device_tokens",
        details={"count": len(devices)}
    )
    
    return devices


@router.post("/devices", response_model=DeviceRegistrationResponse)
async def register_device(
    device_in: DeviceRegistrationBase,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Register a device for push notifications.
    """
    # Register device
    device = device_token_repo.register_device(
        db,
        parent_id=current_user.id,
        device_token=device_in.device_token,
        device_type=device_in.device_type,
        device_name=device_in.device_name
    )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_CREATED,
        parent_id=current_user.id,
        resource_type="device_token",
        details={"device_type": device_in.device_type}
    )
    
    return device


@router.delete("/devices/{device_token}")
async def unregister_device(
    device_token: str,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Unregister a device for push notifications.
    """
    # Check if device exists and belongs to the current user
    device = device_token_repo.get_by_token(db, device_token)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if device.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only unregister your own devices"
        )
    
    # Unregister device
    device_token_repo.unregister_device(db, device_token)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_DELETED,
        parent_id=current_user.id,
        resource_type="device_token",
        details={"device_token": device_token}
    )
    
    return {"status": "success", "message": "Device unregistered successfully"}


@router.post("/test", response_model=NotificationTestResponse)
async def test_notification(
    test_request: NotificationTestRequest,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Send a test notification to the current user.
    """
    result = {"success": False, "message": "Unknown notification type", "details": {}}
    
    if test_request.notification_type == "email":
        # Send test email
        if not current_user.email:
            raise HTTPException(status_code=400, detail="User has no email address")
        
        email_result = NotificationService.send_email(
            recipient_email=current_user.email,
            subject="GuardianLens Test Notification",
            html_content=f"""
            <html>
            <body>
                <h2>Test Notification</h2>
                <p>This is a test notification from GuardianLens.</p>
                <p>If you received this, your email notifications are working correctly.</p>
            </body>
            </html>
            """
        )
        
        result = {
            "success": email_result,
            "message": "Test email sent successfully" if email_result else "Failed to send test email",
            "details": {"email": current_user.email}
        }
        
    elif test_request.notification_type == "push":
        # Get user's devices
        devices = device_token_repo.get_by_parent_id(db, current_user.id)
        
        if not devices:
            raise HTTPException(status_code=400, detail="User has no registered devices")
        
        # Send test push notification to all devices
        success_count = 0
        for device in devices:
            push_result = NotificationService.send_push_notification(
                device_token=device.device_token,
                title="GuardianLens Test Notification",
                body="This is a test notification from GuardianLens.",
                data={"type": "test"}
            )
            
            if push_result:
                success_count += 1
        
        result = {
            "success": success_count > 0,
            "message": f"Test push notification sent to {success_count}/{len(devices)} devices",
            "details": {"total_devices": len(devices), "success_count": success_count}
        }
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.SYSTEM_ACTION,
        parent_id=current_user.id,
        resource_type="notification_test",
        details={
            "notification_type": test_request.notification_type,
            "success": result["success"]
        }
    )
    
    return result