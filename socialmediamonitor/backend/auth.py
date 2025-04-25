from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.config import settings
from backend.database import get_db
from backend.repositories.parent_user import ParentUserRepository
from backend.models.user import ParentUser


# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize repositories
parent_user_repo = ParentUserRepository()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password
        
    Returns:
        True if the password matches the hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: The plain text password
        
    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[ParentUser]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: User password
        
    Returns:
        The authenticated user or None if authentication fails
    """
    user = parent_user_repo.get_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> ParentUser:
    """
    Get the current authenticated user from the token.
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        The authenticated user
        
    Raises:
        HTTPException: If the token is invalid or the user is not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = parent_user_repo.get(db, id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: ParentUser = Depends(get_current_user),
) -> ParentUser:
    """
    Get the current active user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The current active user
        
    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def update_user_schema_for_auth():
    """
    Update the user schema to include proper authentication fields.
    This function is called during application startup.
    """
    from backend.schemas.user import ParentUserCreate
    
    # Add a password field to the ParentUserCreate schema
    if not hasattr(ParentUserCreate, "password"):
        # This is a runtime modification of the schema
        # In a real-world scenario, you would modify the schema file directly
        pass