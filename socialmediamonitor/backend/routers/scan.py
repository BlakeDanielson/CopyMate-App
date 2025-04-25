from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.linked_account import LinkedAccountRepository
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.celery_worker import perform_account_scan


router = APIRouter(
    prefix="/scans",
    tags=["scans"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
linked_account_repo = LinkedAccountRepository()
child_profile_repo = ChildProfileRepository()
audit_log_repo = AuditLogRepository()


@router.post("/trigger/{linked_account_id}", response_model=Dict[str, Any])
async def trigger_account_scan(
    linked_account_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Trigger a scan for a linked account.
    
    Users should only be able to trigger scans for their own children's linked accounts.
    """
    # Get the linked account
    linked_account = linked_account_repo.get(db, id=linked_account_id)
    if not linked_account:
        raise HTTPException(status_code=404, detail="Linked account not found")
    
    # Get the child profile
    child_profile = child_profile_repo.get(db, id=linked_account.child_profile_id)
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    # Check if the user has access to the child profile
    if child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only trigger scans for your own children's linked accounts"
        )
    
    # Queue the scan task
    task = perform_account_scan.delay(linked_account_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.SCAN_TRIGGERED,
        parent_id=current_user.id,
        resource_type="linked_account",
        resource_id=linked_account_id,
        details={
            "task_id": task.id,
            "platform": linked_account.platform
        }
    )
    
    return {
        "status": "success",
        "message": "Scan triggered successfully",
        "task_id": task.id,
        "linked_account_id": linked_account_id
    }


@router.post("/trigger-all", response_model=Dict[str, Any])
async def trigger_all_accounts_scan(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Trigger scans for all linked accounts belonging to the current user's children.
    """
    # Get all child profiles for the current user
    child_profiles = child_profile_repo.list(db, parent_id=current_user.id)
    if not child_profiles:
        return {
            "status": "success",
            "message": "No child profiles found",
            "accounts_scanned": 0
        }
    
    # Get all linked accounts for these child profiles
    linked_accounts = []
    for profile in child_profiles:
        profile_accounts = linked_account_repo.list(db, child_profile_id=profile.id)
        linked_accounts.extend(profile_accounts)
    
    if not linked_accounts:
        return {
            "status": "success",
            "message": "No linked accounts found",
            "accounts_scanned": 0
        }
    
    # Queue scan tasks for all linked accounts
    task_ids = []
    for account in linked_accounts:
        task = perform_account_scan.delay(account.id)
        task_ids.append(task.id)
        
        # Log the action for each account
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SCAN_TRIGGERED,
            parent_id=current_user.id,
            resource_type="linked_account",
            resource_id=account.id,
            details={
                "task_id": task.id,
                "platform": account.platform
            }
        )
    
    return {
        "status": "success",
        "message": f"Scans triggered for {len(linked_accounts)} accounts",
        "accounts_scanned": len(linked_accounts),
        "task_ids": task_ids
    }