from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.alert import AlertRepository
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType, AlertType
from backend.schemas.alert import (
    AlertResponse, AlertCreate, AlertUpdate
)


router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
alert_repo = AlertRepository()
child_profile_repo = ChildProfileRepository()
audit_log_repo = AuditLogRepository()


@router.get("/", response_model=List[AlertResponse])
async def read_alerts(
    skip: int = 0,
    limit: int = 100,
    child_profile_id: Optional[int] = None,
    alert_type: Optional[str] = None,
    read: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve alerts.
    
    Users should only be able to see alerts for their own children's profiles.
    """
    # Build filter criteria
    filter_criteria = {}
    
    # If child_profile_id is provided, check if it belongs to the current user
    if child_profile_id:
        child_profile = child_profile_repo.get(db, id=child_profile_id)
        if not child_profile or child_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access alerts for your own children's profiles"
            )
        
        filter_criteria["child_profile_id"] = child_profile_id
    else:
        # Get all child profiles for the current user
        child_profiles = child_profile_repo.list(db, parent_id=current_user.id)
        child_profile_ids = [profile.id for profile in child_profiles]
        
        if not child_profile_ids:
            return []
        
        # We'll filter by child profile IDs in the query
        # But we need to handle this specially since we have multiple IDs
    
    # Add alert type filter if provided
    if alert_type:
        try:
            alert_type_enum = AlertType[alert_type.upper()]
            filter_criteria["alert_type"] = alert_type_enum
        except KeyError:
            # Invalid alert type, ignore the filter
            pass
    
    # Add read status filter if provided
    if read is not None:
        filter_criteria["is_read"] = read
    
    # Get alerts based on filters
    if "child_profile_id" in filter_criteria:
        # Simple case: filtering by a single child profile
        alerts = alert_repo.list(db, skip=skip, limit=limit, **filter_criteria)
    else:
        # Complex case: filtering by multiple child profiles
        alerts = []
        for profile_id in child_profile_ids:
            profile_filter = filter_criteria.copy()
            profile_filter["child_profile_id"] = profile_id
            profile_alerts = alert_repo.list(db, skip=skip, limit=limit, **profile_filter)
            alerts.extend(profile_alerts)
            
            # Respect the limit across all profiles
            if len(alerts) >= limit:
                alerts = alerts[:limit]
                break
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="alert",
        resource_id=None,
        details={
            "count": len(alerts),
            "child_profile_id": child_profile_id if child_profile_id else "all",
            "alert_type": alert_type if alert_type else "all",
            "read": read if read is not None else "all"
        }
    )
    
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def read_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific alert by ID.
    
    Users should only be able to access alerts for their own children's profiles.
    """
    db_alert = alert_repo.get(db, id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if the alert belongs to one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_alert.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access alerts for your own children's profiles"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="alert",
        resource_id=alert_id,
        details={}
    )
    
    return db_alert


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_in: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Update an alert.
    
    Users should only be able to update alerts for their own children's profiles.
    This is primarily used to mark alerts as read.
    """
    db_alert = alert_repo.get(db, id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if the alert belongs to one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_alert.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update alerts for your own children's profiles"
        )
    
    # Update the alert
    update_data = alert_in.dict(exclude_unset=True)
    updated_alert = alert_repo.update(db, db_obj=db_alert, obj_in=update_data)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_UPDATED,
        parent_id=current_user.id,
        resource_type="alert",
        resource_id=alert_id,
        details={"fields_updated": list(update_data.keys())}
    )
    
    return updated_alert


@router.delete("/{alert_id}", response_model=AlertResponse)
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Delete an alert.
    
    Users should only be able to delete alerts for their own children's profiles.
    """
    db_alert = alert_repo.get(db, id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if the alert belongs to one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_alert.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete alerts for your own children's profiles"
        )
    
    # Delete the alert
    deleted_alert = alert_repo.delete(db, id=alert_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_DELETED,
        parent_id=current_user.id,
        resource_type="alert",
        resource_id=alert_id,
        details={"alert_type": str(deleted_alert.alert_type.value)}
    )
    
    return deleted_alert


@router.post("/mark_all_read", response_model=dict)
async def mark_all_alerts_read(
    child_profile_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Mark all alerts as read for a child profile or all child profiles.
    
    Users should only be able to update alerts for their own children's profiles.
    """
    # If child_profile_id is provided, check if it belongs to the current user
    if child_profile_id:
        child_profile = child_profile_repo.get(db, id=child_profile_id)
        if not child_profile or child_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update alerts for your own children's profiles"
            )
        
        # Mark all alerts as read for this child profile
        count = alert_repo.mark_all_read(db, child_profile_id=child_profile_id)
    else:
        # Get all child profiles for the current user
        child_profiles = child_profile_repo.list(db, parent_id=current_user.id)
        child_profile_ids = [profile.id for profile in child_profiles]
        
        if not child_profile_ids:
            return {"marked_read_count": 0}
        
        # Mark all alerts as read for all child profiles
        count = 0
        for profile_id in child_profile_ids:
            count += alert_repo.mark_all_read(db, child_profile_id=profile_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_UPDATED,
        parent_id=current_user.id,
        resource_type="alert",
        resource_id=None,
        details={
            "action": "mark_all_read",
            "child_profile_id": child_profile_id if child_profile_id else "all",
            "count": count
        }
    )
    
    return {"marked_read_count": count}