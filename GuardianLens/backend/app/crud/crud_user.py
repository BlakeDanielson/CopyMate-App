from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Use select for modern SQLAlchemy
from typing import Optional, Any

from app.core.security import get_password_hash, verify_password
from app.models.user import ParentUser
from app.schemas.user import UserCreate, UserUpdate # Assuming UserUpdate exists

async def get_user_by_email(db: AsyncSession, *, email: str) -> Optional[ParentUser]:
    """Gets a user by email."""
    result = await db.execute(select(ParentUser).filter(ParentUser.email == email))
    return result.scalars().first()

async def get_user(db: AsyncSession, *, user_id: int) -> Optional[ParentUser]:
    """Gets a user by ID."""
    result = await db.execute(select(ParentUser).filter(ParentUser.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, *, obj_in: UserCreate) -> ParentUser:
    """Creates a new user."""
    hashed_password = get_password_hash(obj_in.password)
    # Create a dictionary excluding the plain password
    db_obj_data = obj_in.model_dump(exclude={"password"})
    db_obj = ParentUser(**db_obj_data, hashed_password=hashed_password)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# Optional: Add update user function if needed later
# async def update_user(db: AsyncSession, *, db_obj: ParentUser, obj_in: UserUpdate | dict[str, Any]) -> ParentUser:
#     ...

# Optional: Add authenticate user function here or in a separate auth module
# async def authenticate(db: AsyncSession, *, email: str, password: str) -> Optional[ParentUser]:
#    user = await get_user_by_email(db, email=email)
#    if not user:
#        return None
#    if not verify_password(password, user.hashed_password):
#        return None
#    return user