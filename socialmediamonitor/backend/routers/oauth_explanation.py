from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType, PlatformType
from backend.schemas.oauth_explanation import OAuthExplanationResponse, OAuthExplanation
from backend.utils.oauth_explanation import get_platform_explanation


router = APIRouter(
    prefix="/oauth-explanation",
    tags=["oauth-explanation"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
child_profile_repo = ChildProfileRepository()
audit_log_repo = AuditLogRepository()


@router.get("/{platform}/{child_profile_id}", response_model=OAuthExplanationResponse)
async def get_oauth_explanation(
    platform: str,
    child_profile_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get detailed explanation about the OAuth process and data accessed for a specific platform.
    
    This endpoint provides clear, age-appropriate explanations about the OAuth process,
    what data will be accessed, and how it will be used. This information should be
    displayed to both the parent and child before initiating the OAuth flow.
    
    Users should only be able to get explanations for their own children's profiles.
    """
    # Check if the child profile exists and belongs to the current user
    child_profile = child_profile_repo.get(db, id=child_profile_id)
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    if child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access information for your own children's profiles"
        )
    
    # Check if the platform is supported
    try:
        if platform.lower() not in [p.value for p in PlatformType]:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Get the platform-specific explanation
        explanation = get_platform_explanation(platform, child_profile)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESS,
        parent_id=current_user.id,
        resource_type="oauth_explanation",
        resource_id=None,
        details={
            "platform": platform,
            "child_profile_id": child_profile_id
        }
    )
    
    return {"explanation": explanation}