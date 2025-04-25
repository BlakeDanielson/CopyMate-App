from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func  # For count
from typing import Optional, List, Any

from app.models.profile import ChildProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate

async def get_profile(db: AsyncSession, *, profile_id: int, parent_id: int) -> Optional[ChildProfile]:
    """Gets a specific profile by ID, ensuring it belongs to the parent."""
    result = await db.execute(
        select(ChildProfile)
        .filter(ChildProfile.id == profile_id, ChildProfile.parent_id == parent_id)
    )
    return result.scalars().first()

async def get_profiles_by_parent(
    db: AsyncSession, *, parent_id: int, skip: int = 0, limit: int = 100
) -> List[ChildProfile]:
    """Gets all profiles belonging to a specific parent."""
    result = await db.execute(
        select(ChildProfile)
        .filter(ChildProfile.parent_id == parent_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_profiles_count_by_parent(db: AsyncSession, *, parent_id: int) -> int:
    """Counts profiles belonging to a specific parent."""
    result = await db.execute(
        select(func.count(ChildProfile.id))
        .filter(ChildProfile.parent_id == parent_id)
    )
    return result.scalar_one()

async def create_profile(db: AsyncSession, *, obj_in: ProfileCreate, parent_id: int) -> ChildProfile:
    """Creates a new profile linked to a parent."""
    db_obj_data = obj_in.model_dump()
    db_obj = ChildProfile(**db_obj_data, parent_id=parent_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_profile(
    db: AsyncSession, *, db_obj: ChildProfile, obj_in: ProfileUpdate | dict[str, Any]
) -> ChildProfile:
    """Updates an existing profile."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)  # Only update provided fields

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_profile(db: AsyncSession, *, profile_id: int, parent_id: int) -> Optional[ChildProfile]:
    """Removes a profile by ID, ensuring it belongs to the parent."""
    result = await db.execute(
        select(ChildProfile)
        .filter(ChildProfile.id == profile_id, ChildProfile.parent_id == parent_id)
    )
    db_obj = result.scalars().first()
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj  # Return the deleted object or None