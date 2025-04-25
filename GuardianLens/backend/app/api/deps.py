from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core import security
from app.config import settings
from app.db.session import AsyncSessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token" # Point to the token endpoint
)

async def get_db() -> Generator[AsyncSession, None, None]:
    """Dependency that provides an async database session."""
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.ParentUser:
    """Dependency to get the current user from JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenData(username=payload.get("sub")) # Validate payload structure
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.crud_user.get_user_by_email(db, email=token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Optional: Add dependencies for active user, superuser etc. later
# def get_current_active_user(...) -> models.ParentUser: ...