from typing import Any, List, Dict, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.coppa_verification import CoppaVerificationRepository
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.schemas.coppa_verification import (
    CoppaVerificationCreate, CoppaVerificationResponse, CoppaVerificationUpdate,
    CoppaVerificationRequest, CoppaVerificationResult, VerificationStatusEnum
)
from backend.utils.oauth import generate_authorization_url


router = APIRouter(
    prefix="/coppa-verification",
    tags=["coppa-verification"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
coppa_verification_repo = CoppaVerificationRepository()
child_profile_repo = ChildProfileRepository()
audit_log_repo = AuditLogRepository()


@router.post("/", response_model=CoppaVerificationResult)
async def create_coppa_verification(
    verification_in: CoppaVerificationRequest,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Create a new COPPA verification for a child under 13.
    
    This endpoint initiates the COPPA verification process for a child profile.
    It creates a verification record and returns the next steps.
    
    Users should only be able to create verifications for their own children's profiles.
    """
    # Check if the child profile exists and belongs to the current user
    child_profile = child_profile_repo.get(db, id=verification_in.child_profile_id)
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    if child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create verifications for your own children's profiles"
        )
    
    # Check if the child is under 13 (COPPA applies)
    if not child_profile.age or child_profile.age >= 13:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="COPPA verification is only required for children under 13"
        )
    
    # Check if there's already an active verification
    active_verification = coppa_verification_repo.get_active_verification(
        db, child_profile_id=child_profile.id, platform=verification_in.platform
    )
    
    if active_verification:
        # Generate authorization URL for the platform
        try:
            auth_data = generate_authorization_url(
                child_profile_id=child_profile.id,
                platform=verification_in.platform,
                parent_id=current_user.id
            )
            
            return CoppaVerificationResult(
                verification_id=str(active_verification.id),
                verification_status=VerificationStatusEnum.VERIFIED,
                message="Verification already active",
                authorization_url=auth_data["authorization_url"]
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # Check if there's a pending verification
    pending_verification = coppa_verification_repo.get_pending_verification(
        db, child_profile_id=child_profile.id, platform=verification_in.platform
    )
    
    if pending_verification:
        return CoppaVerificationResult(
            verification_id=str(pending_verification.id),
            verification_status=VerificationStatusEnum.PENDING,
            message="Verification is pending review",
            next_steps=["Wait for verification to be processed"]
        )
    
    # Create a new verification
    verification_data = CoppaVerificationCreate(
        child_profile_id=verification_in.child_profile_id,
        verification_method=verification_in.verification_method,
        parent_email=verification_in.parent_email,
        parent_full_name=verification_in.parent_full_name,
        parent_statement=verification_in.parent_statement,
        platform=verification_in.platform,
        verification_data=verification_in.verification_data
    )
    
    db_verification = coppa_verification_repo.create_verification(db, obj_in=verification_data)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_CREATED,
        parent_id=current_user.id,
        resource_type="coppa_verification",
        resource_id=db_verification.id,
        details={
            "platform": verification_in.platform,
            "verification_method": verification_in.verification_method.value,
            "child_profile_id": verification_in.child_profile_id
        }
    )
    
    # For demo purposes, automatically verify the verification
    # In a real implementation, this would be handled by an admin or automated verification process
    if verification_in.verification_method in ["credit_card", "digital_signature"]:
        db_verification = coppa_verification_repo.verify(
            db, 
            verification_id=db_verification.id,
            notes="Auto-verified for demo purposes"
        )
        
        # Generate authorization URL for the platform
        try:
            auth_data = generate_authorization_url(
                child_profile_id=child_profile.id,
                platform=verification_in.platform,
                parent_id=current_user.id
            )
            
            return CoppaVerificationResult(
                verification_id=str(db_verification.id),
                verification_status=VerificationStatusEnum.VERIFIED,
                message="Verification successful",
                authorization_url=auth_data["authorization_url"]
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # For other verification methods, return pending status
    return CoppaVerificationResult(
        verification_id=str(db_verification.id),
        verification_status=VerificationStatusEnum.PENDING,
        message="Verification submitted and pending review",
        next_steps=["Wait for verification to be processed"]
    )


@router.get("/{verification_id}", response_model=CoppaVerificationResponse)
async def read_coppa_verification(
    verification_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific COPPA verification by ID.
    
    Users should only be able to access verifications for their own children's profiles.
    """
    db_verification = coppa_verification_repo.get(db, id=verification_id)
    if db_verification is None:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    # Check if the verification is for one of the current user's children
    child_profile = child_profile_repo.get(db, id=db_verification.child_profile_id)
    if not child_profile or child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access verifications for your own children's profiles"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="coppa_verification",
        resource_id=verification_id,
        details={}
    )
    
    return db_verification


@router.get("/child/{child_profile_id}", response_model=List[CoppaVerificationResponse])
async def read_coppa_verifications_for_child(
    child_profile_id: int,
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get all COPPA verifications for a child profile.
    
    Users should only be able to access verifications for their own children's profiles.
    """
    # Check if the child profile exists and belongs to the current user
    child_profile = child_profile_repo.get(db, id=child_profile_id)
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    if child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access verifications for your own children's profiles"
        )
    
    verifications = coppa_verification_repo.get_verifications_for_child(
        db, child_profile_id=child_profile_id, platform=platform
    )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="coppa_verification",
        resource_id=None,
        details={
            "child_profile_id": child_profile_id,
            "platform": platform if platform else "all",
            "count": len(verifications)
        }
    )
    
    return verifications


@router.get("/status/{child_profile_id}/{platform}", response_model=CoppaVerificationResult)
async def check_verification_status(
    child_profile_id: int,
    platform: str,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Check the COPPA verification status for a child profile and platform.
    
    Users should only be able to check verifications for their own children's profiles.
    """
    # Check if the child profile exists and belongs to the current user
    child_profile = child_profile_repo.get(db, id=child_profile_id)
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    if child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only check verifications for your own children's profiles"
        )
    
    # Check if the child is under 13 (COPPA applies)
    if not child_profile.age or child_profile.age >= 13:
        # For children 13+, no COPPA verification is required
        # Generate authorization URL for the platform
        try:
            auth_data = generate_authorization_url(
                child_profile_id=child_profile.id,
                platform=platform,
                parent_id=current_user.id
            )
            
            return CoppaVerificationResult(
                verification_id="not_required",
                verification_status=VerificationStatusEnum.VERIFIED,
                message="COPPA verification not required for children 13 or older",
                authorization_url=auth_data["authorization_url"]
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # Check if there's an active verification
    active_verification = coppa_verification_repo.get_active_verification(
        db, child_profile_id=child_profile.id, platform=platform
    )
    
    if active_verification:
        # Generate authorization URL for the platform
        try:
            auth_data = generate_authorization_url(
                child_profile_id=child_profile.id,
                platform=platform,
                parent_id=current_user.id
            )
            
            return CoppaVerificationResult(
                verification_id=str(active_verification.id),
                verification_status=VerificationStatusEnum.VERIFIED,
                message="Verification active",
                authorization_url=auth_data["authorization_url"]
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # Check if there's a pending verification
    pending_verification = coppa_verification_repo.get_pending_verification(
        db, child_profile_id=child_profile.id, platform=platform
    )
    
    if pending_verification:
        return CoppaVerificationResult(
            verification_id=str(pending_verification.id),
            verification_status=VerificationStatusEnum.PENDING,
            message="Verification is pending review",
            next_steps=["Wait for verification to be processed"]
        )
    
    # No verification found
    return CoppaVerificationResult(
        verification_id="none",
        verification_status=VerificationStatusEnum.PENDING,
        message="No verification found",
        next_steps=["Create a new verification"]
    )