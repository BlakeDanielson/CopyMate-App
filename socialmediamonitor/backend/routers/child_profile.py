from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.parent_user import ParentUserRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.schemas.user import (
    ChildProfileCreate, ChildProfileResponse, ChildProfileUpdate, ChildProfileWithLinkedAccounts
)


router = APIRouter(
    prefix="/child_profiles",
    tags=["child_profiles"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
child_profile_repo = ChildProfileRepository()
parent_user_repo = ParentUserRepository()
audit_log_repo = AuditLogRepository()


@router.post("/", response_model=ChildProfileResponse)
async def create_child_profile(
    profile_in: ChildProfileCreate,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Create a new child profile.
    
    Users should only be able to create profiles for their own children.
    """
    # Ensure the parent_id matches the current user's ID
    if profile_in.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create profiles for your own children"
        )
    
    # Create the child profile
    db_profile = child_profile_repo.create(db, obj_in=profile_in)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_CREATED,
        parent_id=current_user.id,
        resource_type="child_profile",
        resource_id=db_profile.id,
        details={"display_name": db_profile.display_name}
    )
    
    return db_profile


@router.get("/", response_model=List[ChildProfileResponse])
async def read_child_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve child profiles.
    
    Users should only be able to see their own children's profiles.
    """
    # Get only the profiles belonging to the current user
    profiles = child_profile_repo.list(
        db, skip=skip, limit=limit, parent_id=current_user.id
    )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="child_profile",
        resource_id=None,
        details={"count": len(profiles)}
    )
    
    return profiles


@router.get("/{profile_id}", response_model=ChildProfileWithLinkedAccounts)
async def read_child_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific child profile by ID.
    
    Users should only be able to access their own children's profiles.
    """
    db_profile = child_profile_repo.get(db, id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    # Check if the profile belongs to the current user
    if db_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own children's profiles"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="child_profile",
        resource_id=profile_id,
        details={}
    )
    
    return db_profile


@router.put("/{profile_id}", response_model=ChildProfileResponse)
async def update_child_profile(
    profile_id: int,
    profile_in: ChildProfileUpdate,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Update a child profile.
    
    Users should only be able to update their own children's profiles.
    """
    db_profile = child_profile_repo.get(db, id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    # Check if the profile belongs to the current user
    if db_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own children's profiles"
        )
    
    # If parent_id is provided, ensure it matches the current user's ID
    update_data = profile_in.dict(exclude_unset=True)
    if "parent_id" in update_data and update_data["parent_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update profiles to be under your own account"
        )
    
    updated_profile = child_profile_repo.update(db, db_obj=db_profile, obj_in=update_data)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_UPDATED,
        parent_id=current_user.id,
        resource_type="child_profile",
        resource_id=profile_id,
        details={"fields_updated": list(update_data.keys())}
    )
    
    return updated_profile


@router.delete("/{profile_id}", response_model=ChildProfileResponse)
async def delete_child_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Delete a child profile.
    
    Users should only be able to delete their own children's profiles.
    """
    db_profile = child_profile_repo.get(db, id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Child profile not found")
    
    # Check if the profile belongs to the current user
    if db_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own children's profiles"
        )
    
    deleted_profile = child_profile_repo.delete(db, id=profile_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_DELETED,
        parent_id=current_user.id,
        resource_type="child_profile",
        resource_id=profile_id,
        details={"display_name": deleted_profile.display_name}
    )
    
    return deleted_profile