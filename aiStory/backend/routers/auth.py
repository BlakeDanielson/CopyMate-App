"""Authentication router for user registration and login."""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.user import User
from backend.models.refresh_token import RefreshToken
from backend.schemas.user import RefreshToken as RefreshTokenSchema, Token, User as UserSchema, UserCreate, UserLogin
from backend.utils.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_user_from_refresh_token,
    revoke_refresh_token,
    store_refresh_token
)
from backend.utils.database import get_db

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Rate limit settings
AUTH_RATE_LIMIT = f"{settings.auth_rate_limit_requests_per_minute}/minute"


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_RATE_LIMIT)
async def register_user(
    request: Request,
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Token: Access token and user data
        
    Raises:
        HTTPException: If user already exists or validation fails
    """
    # Check if email already exists
    email_result = await db.execute(select(User).where(User.email == user_data.email))
    if email_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed: User details conflict."
        )
    
    # Check if username already exists
    username_result = await db.execute(select(User).where(User.username == user_data.username))
    if username_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed: User details conflict."
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user"
        )
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    # Generate refresh token
    refresh_token = create_refresh_token(
        data={"sub": str(new_user.id)},
        expires_delta=timedelta(days=settings.refresh_token_expire_days)
    )
    
    # Store refresh token in database
    token_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    await store_refresh_token(new_user.id, refresh_token, token_expires, db)
    
    # Create user response model
    user_response = UserSchema.model_validate(new_user)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/login", response_model=Token)
@limiter.limit(AUTH_RATE_LIMIT)
async def login_user(
    request: Request,
    form_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login user and return JWT token.
    
    Args:
        form_data: Login credentials
        db: Database session
        
    Returns:
        Token: Access token and user data
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = await authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login timestamp
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    # Generate refresh token
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.refresh_token_expire_days)
    )
    
    # Store refresh token in database
    token_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    await store_refresh_token(user.id, refresh_token, token_expires, db)
    
    # Create user response model
    user_response = UserSchema.model_validate(user)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/refresh", response_model=Token)
@limiter.limit(AUTH_RATE_LIMIT)
async def refresh_token(
    request: Request,
    refresh_token_data: RefreshTokenSchema,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token using a valid refresh token.
    
    Args:
        request: FastAPI request object
        refresh_token_data: Refresh token data
        db: Database session
        
    Returns:
        Token: New access token, refresh token, and user data
        
    Raises:
        HTTPException: If refresh token is invalid or revoked
    """
    try:
        # Validate refresh token and get user
        user = await get_user_from_refresh_token(refresh_token_data.refresh_token, db)
        
        # Revoke old refresh token
        await revoke_refresh_token(refresh_token_data.refresh_token, db)
        
        # Generate new access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        # Generate new refresh token
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=settings.refresh_token_expire_days)
        )
        
        # Store new refresh token in database
        token_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        await store_refresh_token(user.id, new_refresh_token, token_expires, db)
        
        # Create user response model
        user_response = UserSchema.model_validate(user)
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh access token",
            headers={"WWW-Authenticate": "Bearer"},
        )