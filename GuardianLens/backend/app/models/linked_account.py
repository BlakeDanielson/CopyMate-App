from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING, Optional

from app.db.base_class import Base

if TYPE_CHECKING:
    from .profile import ChildProfile  # Import for type hinting relationship

class LinkedAccount(Base):
    __tablename__ = "linked_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # e.g., 'youtube'
    # Store encrypted tokens in production! Placeholder as plain text for now.
    # Consider using libraries like sqlalchemy-utils EncryptedType or Fernet manually.
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Refresh token might not always be present
    expires_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)  # Store expiry time
    scopes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Store granted scopes as space-separated string or JSON

    # Foreign Key to ChildProfile
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("child_profiles.id"), nullable=False)

    # Relationship to ChildProfile
    profile: Mapped["ChildProfile"] = relationship(back_populates="linked_accounts")