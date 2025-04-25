from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user, get_password_hash
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.parent_user import ParentUserRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.schemas.user import (
    ParentUserCreate, ParentUserResponse, ParentUserUpdate
)


router = APIRouter(
    prefix="/parent_users",
    tags=["parent_users"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
parent_user_repo = ParentUserRepository()
audit_log_repo = AuditLogRepository()


@router.get("/", response_model=List[ParentUserResponse])
async def read_parent_users(
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None, min_length=3, description="Search term for name or email"),
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve parent users.
    
    Only admin users should be able to see all users.
    For now, we'll allow the current user to see all users,
    but in a production environment, this would be restricted.
    """
    if search:
        users = parent_user_repo.search_by_name_or_email(db, search_term=search, skip=skip, limit=limit)
    else:
        users = parent_user_repo.list(db, skip=skip, limit=limit)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="parent_user",
        resource_id=None,
        details={"count": len(users), "search": search if search else "none"}
    )
    
    return users


@router.get("/{user_id}", response_model=ParentUserResponse)
async def read_parent_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific parent user by ID.
    
    Users should only be able to access their own information,
    unless they have admin privileges.
    """
    # Check if the user is trying to access their own information
    if user_id != current_user.id:
        # In a production environment, check for admin privileges here
        pass
    
    db_user = parent_user_repo.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Parent user not found")
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="parent_user",
        resource_id=user_id,
        details={}
    )
    
    return db_user


@router.put("/{user_id}", response_model=ParentUserResponse)
async def update_parent_user(
    user_id: int,
    user_in: ParentUserUpdate,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Update a parent user.
    
    Users should only be able to update their own information,
    unless they have admin privileges.
    """
    # Check if the user is trying to update their own information
    if user_id != current_user.id:
        # In a production environment, check for admin privileges here
        pass
    
    db_user = parent_user_repo.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Parent user not found")
    
    # Handle password update separately
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        hashed_password = get_password_hash(update_data.pop("password"))
        update_data["hashed_password"] = hashed_password
    
    updated_user = parent_user_repo.update(db, db_obj=db_user, obj_in=update_data)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_UPDATED,
        parent_id=current_user.id,
        resource_type="parent_user",
        resource_id=user_id,
        details={"fields_updated": list(update_data.keys())}
    )
    
    return updated_user


@router.delete("/{user_id}", response_model=ParentUserResponse)
async def delete_parent_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Delete a parent user.
    
    Users should only be able to delete their own account,
    unless they have admin privileges.
    """
    # Check if the user is trying to delete their own account
    if user_id != current_user.id:
        # In a production environment, check for admin privileges here
        pass
    
    db_user = parent_user_repo.get(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Parent user not found")
    
    deleted_user = parent_user_repo.delete(db, id=user_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_DELETED,
        parent_id=current_user.id,
        resource_type="parent_user",
        resource_id=user_id,
        details={}
    )
    
    return deleted_user