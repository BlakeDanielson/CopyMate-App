from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List, Any

from app.models.linked_account import LinkedAccount
from app.schemas.linked_account import LinkedAccountCreate, LinkedAccountUpdate

async def get_linked_account(db: AsyncSession, *, linked_account_id: int) -> Optional[LinkedAccount]:
    """Gets a linked account by its ID."""
    result = await db.execute(
        select(LinkedAccount).filter(LinkedAccount.id == linked_account_id)
    )
    return result.scalars().first()

async def get_linked_account_by_profile(
    db: AsyncSession, *, profile_id: int, provider: str = "youtube" # Default or specify provider
) -> Optional[LinkedAccount]:
    """Gets the linked account for a specific profile and provider."""
    result = await db.execute(
        select(LinkedAccount)
        .filter(LinkedAccount.profile_id == profile_id, LinkedAccount.provider == provider)
    )
    return result.scalars().first()

async def create_or_update_linked_account(
    db: AsyncSession, *, obj_in: LinkedAccountCreate
) -> LinkedAccount:
    """Creates a new linked account or updates it if it already exists for the profile/provider."""
    # Check if an account already exists for this profile and provider
    existing_account = await get_linked_account_by_profile(
        db, profile_id=obj_in.profile_id, provider=obj_in.provider
    )

    if existing_account:
        # Update existing account
        update_data = obj_in.model_dump(exclude={"profile_id", "provider"}) # Don't update profile_id or provider
        for field, value in update_data.items():
             setattr(existing_account, field, value)
        db_obj = existing_account
    else:
        # Create new account
        db_obj_data = obj_in.model_dump()
        db_obj = LinkedAccount(**db_obj_data)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_linked_account_tokens(
    db: AsyncSession, *, db_obj: LinkedAccount, obj_in: LinkedAccountUpdate
) -> LinkedAccount:
    """Specifically updates tokens for an existing linked account (e.g., after refresh)."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_linked_account(db: AsyncSession, *, linked_account_id: int) -> Optional[LinkedAccount]:
    """Removes a linked account by ID."""
    result = await db.execute(
        select(LinkedAccount).filter(LinkedAccount.id == linked_account_id)
    )
    db_obj = result.scalars().first()
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj

async def remove_linked_account_by_profile(db: AsyncSession, *, profile_id: int, provider: str = "youtube") -> Optional[LinkedAccount]:
    """Removes the linked account for a specific profile and provider."""
    db_obj = await get_linked_account_by_profile(db, profile_id=profile_id, provider=provider)
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj