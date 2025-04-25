from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app import crud, schemas
from app.api import deps # We'll create deps.py next
from app.core.security import create_access_token, authenticate
from app.models.user import ParentUser # Needed for response_model

router = APIRouter()

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: AsyncSession = Depends(deps.get_db), # Use get_db from deps
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await crud.crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud.crud_user.create_user(db, obj_in=user_in)
    return user

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Optional: Check if user is active
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(subject=user.email) # Use email as subject
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }