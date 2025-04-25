"""Refresh token model for JWT authentication."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.models.base import Base


class RefreshToken(Base):
    """Refresh token model for storing user refresh tokens."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column()
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Foreign key relationship
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    
    # Relationship to User model
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self) -> str:
        """String representation of the RefreshToken model."""
        return f"<RefreshToken {self.id} for user {self.user_id}>"