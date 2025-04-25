from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING, List

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import ParentUser  # Import for type hinting relationship
    from .linked_account import LinkedAccount  # Import for type hinting

class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # Example length
    # Add other relevant fields like date_of_birth, avatar_url etc. if needed
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)

    # Foreign Key to ParentUser
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("parent_users.id"), nullable=False)

    # Relationship to ParentUser (bi-directional)
    parent: Mapped["ParentUser"] = relationship(back_populates="child_profiles")

    # Relationship to LinkedAccount (bi-directional)
    linked_accounts: Mapped[List["LinkedAccount"]] = relationship(
        "LinkedAccount", back_populates="profile", cascade="all, delete-orphan"
    )