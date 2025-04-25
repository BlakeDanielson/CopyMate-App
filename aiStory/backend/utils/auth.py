"""Authentication utilities for password hashing and JWT token management."""
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.user import User
from backend.schemas.user import TokenData
from backend.utils.database import get_db

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 authentication scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash.
    
    Args:
        password: The plain text password
    
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access JWT token with an expiration time.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time, otherwise uses settings
    
    Returns:
        str: JWT access token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "token_type": "access"})
    
    # Add role to token if not already present and user_id is provided
    if "role" not in to_encode and "sub" in to_encode:
        # This is a simplification for testing; in production, you'd query the DB
        # We'll handle this during the get_current_user function where we have DB access
        pass
    
    # Create and return token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new refresh JWT token with an expiration time.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time, otherwise uses settings
    
    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode.update({"exp": expire, "token_type": "refresh"})
    
    # Create and return token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


# Alias for backward compatibility
create_jwt_token = create_access_token


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token.
    
    Args:
        token: The JWT token
    
    Returns:
        Dict: Token payload
    
    Raises:
        JWTError: If token is invalid
    """
    return jwt.decode(
        token, 
        settings.secret_key, 
        algorithms=[settings.algorithm]
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get the current authenticated user from a token.
    
    Args:
        token: JWT token from request
        db: Database session
    
    Returns:
        User: Current authenticated user
    
    Raises:
        HTTPException: If token is invalid or user is not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(sub=user_id, exp=datetime.fromtimestamp(payload.get("exp")))
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token type (must be access token)
    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_user_from_refresh_token(
    refresh_token: str,
    db: AsyncSession
) -> User:
    """Validate a refresh token and get the associated user.
    
    Args:
        refresh_token: JWT refresh token
        db: Database session
    
    Returns:
        User: User associated with the token
    
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = decode_jwt_token(refresh_token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("token_type")
        
        if user_id is None:
            raise credentials_exception
            
        # Verify this is a refresh token
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_data = TokenData(sub=user_id, exp=datetime.fromtimestamp(payload.get("exp")))
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    # Check if token is in database and not revoked
    from backend.models.refresh_token import RefreshToken
    refresh_token_query = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token,
            RefreshToken.user_id == user.id,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
    )
    db_refresh_token = refresh_token_query.scalar_one_or_none()
    
    if db_refresh_token is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def revoke_refresh_token(
    refresh_token: str,
    db: AsyncSession
) -> bool:
    """Revoke a refresh token.
    
    Args:
        refresh_token: JWT refresh token to revoke
        db: Database session
    
    Returns:
        bool: True if token was revoked, False otherwise
    """
    from backend.models.refresh_token import RefreshToken
    
    try:
        # Find token in database
        refresh_token_query = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.revoked == False
            )
        )
        db_refresh_token = refresh_token_query.scalar_one_or_none()
        
        if db_refresh_token is None:
            return False
        
        # Revoke token
        db_refresh_token.revoked = True
        await db.commit()
        return True
    except Exception:
        await db.rollback()
        return False


async def store_refresh_token(
    user_id: int,
    refresh_token: str,
    expires_at: datetime,
    db: AsyncSession
) -> bool:
    """Store a refresh token in the database.
    
    Args:
        user_id: User ID associated with the token
        refresh_token: JWT refresh token
        expires_at: Token expiration datetime
        db: Database session
        
    Returns:
        bool: True if token was stored, False otherwise
    """
    from backend.models.refresh_token import RefreshToken
    
    try:
        # Create new refresh token record
        db_refresh_token = RefreshToken(
            token=refresh_token,
            user_id=user_id,
            expires_at=expires_at,
            revoked=False
        )
        db.add(db_refresh_token)
        await db.commit()
        return True
    except Exception:
        await db.rollback()
        return False


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current active user.
    
    Args:
        current_user: User from get_current_user dependency
    
    Returns:
        User: Current active authenticated user
    
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account"
        )
    return current_user


def has_role(user: User, role: str) -> bool:
    """Check if a user has a specific role.
    
    Args:
        user: The user to check
        role: The role to check for
        
    Returns:
        bool: True if the user has the role, False otherwise
    """
    return user.role == role


def has_any_role(user: User, roles: List[str]) -> bool:
    """Check if a user has any of the specified roles.
    
    Args:
        user: The user to check
        roles: The list of roles to check for
        
    Returns:
        bool: True if the user has any of the roles, False otherwise
    """
    return user.role in roles


def require_role(role: str):
    """Dependency for requiring a specific role to access an endpoint.
    
    Args:
        role: The role required to access the endpoint
        
    Returns:
        Callable: A dependency that checks if the user has the required role
    """
    async def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not has_role(current_user, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized. Required role: {role}"
            )
        return current_user
    
    return role_dependency


def require_any_role(roles: List[str]):
    """Dependency for requiring any of the specified roles to access an endpoint.
    
    Args:
        roles: The list of roles that can access the endpoint
        
    Returns:
        Callable: A dependency that checks if the user has any of the required roles
    """
    async def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not has_any_role(current_user, roles):
            role_list = ", ".join(roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized. Required roles: {role_list}"
            )
        return current_user
    
    return role_dependency


async def authenticate_user(
    username_or_email: str,
    password: str,
    db: AsyncSession
) -> Optional[User]:
    """Authenticate a user by username/email and password.
    
    Args:
        username_or_email: Username or email
        password: Plain text password
        db: Database session
    
    Returns:
        Optional[User]: User if authentication successful, None otherwise
    """
    # Check if input is an email (contains @)
    if "@" in username_or_email:
        # Search by email
        result = await db.execute(select(User).where(User.email == username_or_email))
    else:
        # Search by username
        result = await db.execute(select(User).where(User.username == username_or_email))
    
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user