from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Profile, status_code=status.HTTP_201_CREATED)
async def create_child_profile(
    *,
    db: AsyncSession = Depends(deps.get_db),
    profile_in: schemas.ProfileCreate,
    current_user: models.ParentUser = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new child profile for the current parent user.
    """
    profile = await crud.crud_profile.create_profile(
        db=db, obj_in=profile_in, parent_id=current_user.id
    )
    return profile

@router.get("/", response_model=List[schemas.Profile]) # Return a list directly for simplicity, or use Profiles schema
async def read_child_profiles(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.ParentUser = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve child profiles for the current parent user.
    """
    # Optional: Add count for pagination headers if needed
    # total = await crud.crud_profile.get_profiles_count_by_parent(db, parent_id=current_user.id)
    profiles = await crud.crud_profile.get_profiles_by_parent(
        db, parent_id=current_user.id, skip=skip, limit=limit
    )
    return profiles

@router.put("/{profile_id}", response_model=schemas.Profile)
async def update_child_profile(
    *,
    db: AsyncSession = Depends(deps.get_db),
    profile_id: int,
    profile_in: schemas.ProfileUpdate,
    current_user: models.ParentUser = Depends(deps.get_current_user),
) -> Any:
    """
    Update a child profile belonging to the current parent user.
    """
    profile = await crud.crud_profile.get_profile(
        db=db, profile_id=profile_id, parent_id=current_user.id
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found or not owned by user",
        )
    profile = await crud.crud_profile.update_profile(
        db=db, db_obj=profile, obj_in=profile_in
    )
    return profile

@router.delete("/{profile_id}", response_model=schemas.Profile) # Or return status 204
async def delete_child_profile(
    *,
    db: AsyncSession = Depends(deps.get_db),
    profile_id: int,
    current_user: models.ParentUser = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a child profile belonging to the current parent user.
    """
    profile = await crud.crud_profile.remove_profile(
        db=db, profile_id=profile_id, parent_id=current_user.id
    )
    if not profile:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found or not owned by user",
        )
    # Optionally return status 204 No Content instead of the deleted object
    return profile