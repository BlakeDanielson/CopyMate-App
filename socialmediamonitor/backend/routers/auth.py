from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.auth import (
    Token, authenticate_user, create_access_token, 
    get_current_active_user, get_password_hash
)
from backend.config import settings
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.parent_user import ParentUserRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.schemas.user import ParentUserCreate, ParentUserResponse


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)

# Initialize repositories
parent_user_repo = ParentUserRepository()
audit_log_repo = AuditLogRepository()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login timestamp
    parent_user_repo.update_last_login(db, user.id)
    
    # Log login action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.USER_LOGIN,
        parent_id=user.id,
        resource_type="parent_user",
        resource_id=user.id,
        details={"method": "password"}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=ParentUserResponse)
async def register_user(
    user_in: ParentUserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new parent user.
    """
    # Check if user with this email already exists
    existing_user = parent_user_repo.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.dict(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    
    db_user = parent_user_repo.create(db, obj_in=user_data)
    
    # Log user registration
    audit_log_repo.log_action(
        db,
        action=AuditActionType.USER_REGISTERED,
        parent_id=db_user.id,
        resource_type="parent_user",
        resource_id=db_user.id,
        details={}
    )
    
    return db_user


@router.get("/me", response_model=ParentUserResponse)
async def read_users_me(
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get current user information.
    """
    return current_user