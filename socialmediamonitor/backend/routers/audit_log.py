from typing import Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.schemas.audit_log import (
    AuditLogResponse
)


router = APIRouter(
    prefix="/audit_logs",
    tags=["audit_logs"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
audit_log_repo = AuditLogRepository()


@router.get("/", response_model=List[AuditLogResponse])
async def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve audit logs.
    
    Users should only be able to see their own audit logs.
    In a production environment, this would be restricted to admin users or users with specific permissions.
    """
    # Build filter criteria
    filter_criteria = {"parent_id": current_user.id}
    
    # Add action type filter if provided
    if action_type:
        try:
            action_type_enum = AuditActionType[action_type.upper()]
            filter_criteria["action"] = action_type_enum
        except KeyError:
            # Invalid action type, ignore the filter
            pass
    
    # Add resource type filter if provided
    if resource_type:
        filter_criteria["resource_type"] = resource_type
    
    # Add resource ID filter if provided
    if resource_id is not None:
        filter_criteria["resource_id"] = resource_id
    
    # Add date range filters if provided
    date_filters = {}
    if start_date:
        date_filters["created_at__gte"] = start_date
    
    if end_date:
        date_filters["created_at__lte"] = end_date
    
    # Get audit logs based on filters
    logs = audit_log_repo.list_with_date_filter(
        db, skip=skip, limit=limit, date_filters=date_filters, **filter_criteria
    )
    
    return logs


@router.get("/{log_id}", response_model=AuditLogResponse)
async def read_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific audit log by ID.
    
    Users should only be able to access their own audit logs.
    """
    db_log = audit_log_repo.get(db, id=log_id)
    if db_log is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    # Check if the log belongs to the current user
    if db_log.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own audit logs"
        )
    
    return db_log


@router.get("/summary/recent_activity", response_model=dict)
async def get_recent_activity_summary(
    days: int = Query(7, ge=1, le=30, description="Number of days to include in the summary"),
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a summary of recent activity from the audit logs.
    
    This endpoint provides aggregated statistics about user activity.
    """
    # Calculate the start date
    start_date = datetime.now() - timedelta(days=days)
    
    # Get counts by action type
    action_counts = audit_log_repo.count_by_action_type(
        db, parent_id=current_user.id, start_date=start_date
    )
    
    # Get counts by resource type
    resource_counts = audit_log_repo.count_by_resource_type(
        db, parent_id=current_user.id, start_date=start_date
    )
    
    # Get counts by day
    daily_counts = audit_log_repo.count_by_day(
        db, parent_id=current_user.id, start_date=start_date
    )
    
    return {
        "period_days": days,
        "total_actions": sum(count for _, count in action_counts),
        "action_counts": {str(action.value): count for action, count in action_counts},
        "resource_counts": resource_counts,
        "daily_counts": daily_counts
    }