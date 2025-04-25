from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Add imports:
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from app.config import settings

# ... (keep existing pwd_context and functions)

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Add authenticate function (moved from crud_user suggestion)
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import ParentUser
from app.crud import crud_user # Assuming __init__ makes it available

async def authenticate(db: AsyncSession, *, email: str, password: str) -> Optional[ParentUser]:
   user = await crud_user.get_user_by_email(db, email=email)
   if not user:
       return None
   if not verify_password(password, user.hashed_password):
       return None
   # Optional: Check if user is active
   # if not user.is_active:
   #     return None
   return user