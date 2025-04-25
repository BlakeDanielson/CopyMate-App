from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.linked_account import LinkedAccountRepository
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType, PlatformType
from backend.schemas.linked_account import (
    LinkedAccountCreate, LinkedAccountResponse, LinkedAccountUpdate,
    LinkedAccountInitiate, OAuthInitiateResponse
)
from backend.celery_worker import perform_account_scan
from backend.utils.oauth import generate_authorization_url
from backend.utils.oauth_revocation import revoke_oauth_token
from backend.repositories.coppa_verification import CoppaVerificationRepository
from backend.schemas.coppa_verification import VerificationStatusEnum


router = APIRouter(
    prefix="/linked_accounts",
    tags=["linked_accounts"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
linked_account_repo = LinkedAccountRepository()
child_profile_repo = ChildProfileRepository()
audit_log_repo = AuditLogRepository()
coppa_verification_repo = CoppaVerificationRepository()


@router.post("/", response_model=LinkedAccountResponse)
async def create_linked_account(
    account_in: LinkedAccountCreate,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Create a new linked social media account.
    
    Users should only be able to link accounts to their own children's profiles.
    """
    # Check if the child profile exists and belongs to the current user
    child_profile = child_profile_repo.get(db, id=account_in.child_profile_id)
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    if child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only link accounts to your own children's profiles"
        )
    
    # Create the linked account
    db_account = linked_account_repo.create(db, obj_in=account_in)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_CREATED,
        parent_id=current_user.id,
        resource_type="linked_account",
        resource_id=db_account.id,
        details={
            "platform": db_account.platform,
            "platform_username": db_account.platform_username,
            "child_profile_id": db_account.child_profile_id
        }
    )
    
    return db_account


@router.get("/", response_model=List[LinkedAccountResponse])
async def read_linked_accounts(
    skip: int = 0,
    limit: int = 100,
    child_profile_id: int = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve linked accounts.
    
    Users should only be able to see accounts linked to their own children's profiles.
    """
    # If child_profile_id is provided, check if it belongs to the current user
    if child_profile_id:
        child_profile = child_profile_repo.get(db, id=child_profile_id)
        if not child_profile or child_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access accounts linked to your own children's profiles"
            )
        
        accounts = linked_account_repo.list(
            db, skip=skip, limit=limit, child_profile_id=child_profile_id
        )
    else:
        # Get all linked accounts for all of the current user's children
        child_profiles = child_profile_repo.list(db, parent_id=current_user.id)
        child_profile_ids = [profile.id for profile in child_profiles]
        
        if not child_profile_ids:
            return []
        
        accounts = []
        for profile_id in child_profile_ids:
            profile_accounts = linked_account_repo.list(
                db, skip=skip, limit=limit, child_profile_id=profile_id
            )
            accounts.extend(profile_accounts)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="linked_account",
        resource_id=None,
        details={
            "count": len(accounts),
            "child_profile_id": child_profile_id if child_profile_id else "all"
        }
    )
    
    return accounts


@router.get("/{account_id}", response_model=LinkedAccountResponse)
async def read_linked_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific linked account by ID.
    
    Users should only be able to access accounts linked to their own children's profiles.
    """
    db_account = linked_account_repo.get(db, id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Linked account not found")
    
    # Check if the account is linked to one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_account.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access accounts linked to your own children's profiles"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="linked_account",
        resource_id=account_id,
        details={}
    )
    
    return db_account


@router.put("/{account_id}", response_model=LinkedAccountResponse)
async def update_linked_account(
    account_id: int,
    account_in: LinkedAccountUpdate,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Update a linked account.
    
    Users should only be able to update accounts linked to their own children's profiles.
    """
    db_account = linked_account_repo.get(db, id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Linked account not found")
    
    # Check if the account is linked to one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_account.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update accounts linked to your own children's profiles"
        )
    
    # If child_profile_id is provided, check if it belongs to the current user
    update_data = account_in.dict(exclude_unset=True)
    if "child_profile_id" in update_data:
        new_profile = child_profile_repo.get(db, id=update_data["child_profile_id"])
        if not new_profile or new_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only link accounts to your own children's profiles"
            )
    
    updated_account = linked_account_repo.update(db, db_obj=db_account, obj_in=update_data)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_UPDATED,
        parent_id=current_user.id,
        resource_type="linked_account",
        resource_id=account_id,
        details={"fields_updated": list(update_data.keys())}
    )
    
    return updated_account


@router.delete("/{account_id}", response_model=LinkedAccountResponse)
async def delete_linked_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Delete a linked account.
    
    Users should only be able to delete accounts linked to their own children's profiles.
    """
    db_account = linked_account_repo.get(db, id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Linked account not found")
    
    # Check if the account is linked to one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_account.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete accounts linked to your own children's profiles"
        )
    
    deleted_account = linked_account_repo.delete(db, id=account_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_DELETED,
        parent_id=current_user.id,
        resource_type="linked_account",
        resource_id=account_id,
        details={
            "platform": deleted_account.platform,
            "platform_username": deleted_account.platform_username
        }
    )
    
    return deleted_account


@router.post("/{account_id}/unlink", status_code=status.HTTP_200_OK)
async def unlink_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Unlink a social media account by revoking OAuth tokens and deactivating the account.
    
    This endpoint revokes the OAuth tokens with the platform provider and
    deactivates the linked account in the database. The account record is not
    deleted, but marked as inactive.
    
    Users should only be able to unlink accounts linked to their own children's profiles.
    """
    # Get the linked account
    db_account = linked_account_repo.get(db, id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Linked account not found")
    
    # Check if the account is linked to one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_account.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only unlink accounts linked to your own children's profiles"
        )
    
    # Revoke the OAuth tokens
    try:
        # Try to revoke the access token
        if db_account.access_token:
            revoke_oauth_token(db_account.platform, db_account.access_token, "access_token")
        
        # Try to revoke the refresh token
        if db_account.refresh_token:
            revoke_oauth_token(db_account.platform, db_account.refresh_token, "refresh_token")
    except ValueError as e:
        # Log the error but continue with deactivation
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=current_user.id,
            resource_type="oauth",
            resource_id=account_id,
            details={
                "error": str(e),
                "action": "token_revocation"
            }
        )
    
    # Deactivate the account
    deactivated_account = linked_account_repo.update(
        db,
        db_obj=db_account,
        obj_in={
            "is_active": False,
            "updated_at": datetime.utcnow()
        }
    )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.ACCOUNT_UNLINK,
        parent_id=current_user.id,
        resource_type="linked_account",
        resource_id=account_id,
        details={
            "platform": deactivated_account.platform,
            "platform_username": deactivated_account.platform_username
        }
    )
    
    return {
        "status": "success",
        "message": "Account successfully unlinked",
        "account_id": account_id,
        "platform": deactivated_account.platform,
        "unlinked_at": datetime.utcnow().isoformat()
    }


@router.post("/{account_id}/scan", status_code=status.HTTP_202_ACCEPTED)
async def trigger_account_scan(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Trigger a scan for a linked account.
    
    Users should only be able to scan accounts linked to their own children's profiles.
    """
    db_account = linked_account_repo.get(db, id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Linked account not found")
    
    # Check if the account is linked to one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_account.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only scan accounts linked to your own children's profiles"
        )
    
    # Log the scan triggering
    audit_log_repo.log_action(
        db,
        action=AuditActionType.SCAN_TRIGGERED,
        parent_id=current_user.id,
        resource_type="linked_account",
        resource_id=account_id,
        details={"trigger_type": "manual"}
    )
    
    # Queue the Celery task
    task = perform_account_scan.delay(account_id)
    
    return {
        "message": "Account scan task queued", 
        "task_id": task.id,
        "linked_account_id": account_id
    }


@router.post("/initiate-linking", response_model=OAuthInitiateResponse)
async def initiate_account_linking(
    account_init: LinkedAccountInitiate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Initiate the OAuth flow for linking a social media account.
    
    This endpoint generates an authorization URL that the user should be redirected to.
    After authorization, the user will be redirected back to the application's callback URL.
    
    Users should only be able to initiate linking for their own children's profiles.
    """
    # Check if the child profile exists and belongs to the current user
    child_profile = child_profile_repo.get(db, id=account_init.child_profile_id)
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    if child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only link accounts to your own children's profiles"
        )
    
    # Check if COPPA verification is required
    if child_profile.age is not None and child_profile.age < 13:
        # Child is under 13, check for active COPPA verification
        active_verification = coppa_verification_repo.get_active_verification(
            db,
            child_profile_id=child_profile.id,
            platform=account_init.platform.value
        )
        
        if not active_verification:
            # No active verification, return error with guidance
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="COPPA verification required for children under 13. Please complete the verification process first."
            )
    
    # Generate the authorization URL
    try:
        auth_data = generate_authorization_url(
            child_profile_id=account_init.child_profile_id,
            platform=account_init.platform.value,
            parent_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.ACCOUNT_LINK,
        parent_id=current_user.id,
        resource_type="child_profile",
        resource_id=child_profile.id,
        details={
            "platform": account_init.platform.value,
            "action": "initiate_linking"
        }
    )
    
    return auth_data