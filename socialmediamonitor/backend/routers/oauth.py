from typing import Any, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.linked_account import LinkedAccountRepository
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType, PlatformType
from backend.schemas.linked_account import LinkedAccountCreate, LinkedAccountResponse
from backend.utils.oauth import decode_state_token, exchange_code_for_tokens


router = APIRouter(
    prefix="/oauth",
    tags=["oauth"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
linked_account_repo = LinkedAccountRepository()
child_profile_repo = ChildProfileRepository()
audit_log_repo = AuditLogRepository()


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State token from OAuth initiation"),
    error: str = Query(None, description="Error message from OAuth provider"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Handle OAuth callback from external platforms.
    
    This endpoint is called by the OAuth provider after the user authorizes or denies the application.
    If authorized, it exchanges the authorization code for access and refresh tokens,
    then creates a new linked account.
    """
    # Check for OAuth errors
    if error:
        # Log the error
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=None,  # We don't know the parent ID yet
            resource_type="oauth",
            resource_id=None,
            details={
                "error": error,
                "state": state
            }
        )
        
        # Return an error page or redirect to an error page
        return {
            "status": "error",
            "message": f"Authorization denied or error occurred: {error}",
            "redirect_to": "/account-linking-error"  # Frontend should handle this redirect
        }
    
    # Validate the state token
    try:
        state_data = decode_state_token(state)
        child_profile_id = state_data["child_profile_id"]
        platform = state_data["platform"]
        parent_id = state_data["parent_id"]
    except ValueError as e:
        # Log the error
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=None,
            resource_type="oauth",
            resource_id=None,
            details={
                "error": str(e),
                "state": state
            }
        )
        
        # Return an error
        return {
            "status": "error",
            "message": "Invalid or expired state token",
            "redirect_to": "/account-linking-error"
        }
    
    # Check if the child profile exists
    child_profile = child_profile_repo.get(db, id=child_profile_id)
    if not child_profile:
        # Log the error
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=parent_id,
            resource_type="oauth",
            resource_id=None,
            details={
                "error": "Child profile not found",
                "child_profile_id": child_profile_id
            }
        )
        
        # Return an error
        return {
            "status": "error",
            "message": "Child profile not found",
            "redirect_to": "/account-linking-error"
        }
    
    # Check if the child profile belongs to the parent
    if child_profile.parent_id != parent_id:
        # Log the error
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=parent_id,
            resource_type="oauth",
            resource_id=None,
            details={
                "error": "Child profile does not belong to parent",
                "child_profile_id": child_profile_id,
                "parent_id": parent_id
            }
        )
        
        # Return an error
        return {
            "status": "error",
            "message": "Unauthorized access",
            "redirect_to": "/account-linking-error"
        }
    
    # Exchange the authorization code for tokens
    try:
        token_data = exchange_code_for_tokens(platform, code)
    except Exception as e:
        # Log the error
        audit_log_repo.log_action(
            db,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=parent_id,
            resource_type="oauth",
            resource_id=None,
            details={
                "error": str(e),
                "platform": platform,
                "child_profile_id": child_profile_id
            }
        )
        
        # Return an error
        return {
            "status": "error",
            "message": f"Failed to exchange authorization code for tokens: {str(e)}",
            "redirect_to": "/account-linking-error"
        }
    
    # Create a new linked account
    account_data = LinkedAccountCreate(
        child_profile_id=child_profile_id,
        platform=platform,
        platform_account_id=token_data["platform_account_id"],
        platform_username=token_data["platform_username"],
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_expiry=token_data["token_expiry"],
        metadata=token_data["metadata"],
        is_active=True
    )
    
    # Check if an account with this platform and platform_account_id already exists
    existing_accounts = linked_account_repo.list(
        db, 
        child_profile_id=child_profile_id,
        platform=platform
    )
    
    for account in existing_accounts:
        if account.platform_account_id == token_data["platform_account_id"]:
            # Update the existing account instead of creating a new one
            update_data = {
                "access_token": token_data["access_token"],
                "refresh_token": token_data["refresh_token"],
                "token_expiry": token_data["token_expiry"],
                "metadata": token_data["metadata"],
                "is_active": True
            }
            db_account = linked_account_repo.update(db, db_obj=account, obj_in=update_data)
            
            # Log the action
            audit_log_repo.log_action(
                db,
                action=AuditActionType.ACCOUNT_LINK,
                parent_id=parent_id,
                resource_type="linked_account",
                resource_id=db_account.id,
                details={
                    "platform": platform,
                    "platform_username": token_data["platform_username"],
                    "action": "updated"
                }
            )
            
            # Return success with detailed information for dashboard display
            return {
                "status": "success",
                "message": "Account successfully linked",
                "redirect_to": f"/dashboard/child/{child_profile_id}",
                "linked_account": {
                    "id": db_account.id,
                    "platform": platform,
                    "platform_username": token_data["platform_username"],
                    "platform_account_id": token_data["platform_account_id"],
                    "child_profile_id": child_profile_id,
                    "is_new": False,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
    
    # Create a new linked account
    db_account = linked_account_repo.create(db, obj_in=account_data)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.ACCOUNT_LINK,
        parent_id=parent_id,
        resource_type="linked_account",
        resource_id=db_account.id,
        details={
            "platform": platform,
            "platform_username": token_data["platform_username"],
            "action": "created"
        }
    )
    
    # Return success with detailed information for dashboard display
    return {
        "status": "success",
        "message": "Account successfully linked",
        "redirect_to": f"/dashboard/child/{child_profile_id}",
        "linked_account": {
            "id": db_account.id,
            "platform": platform,
            "platform_username": token_data["platform_username"],
            "platform_account_id": token_data["platform_account_id"],
            "child_profile_id": child_profile_id,
            "is_new": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    }