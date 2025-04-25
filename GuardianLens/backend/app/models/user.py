from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column # Use Mapped/mapped_column for modern SQLAlchemy
from typing import List, TYPE_CHECKING # If using relationships

from app.db.base_class import Base

if TYPE_CHECKING:
    from .profile import ChildProfile  # Import for type hinting

class ParentUser(Base):
    __tablename__ = "parent_users" # Use plural table name convention

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True) # Example length
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False) # Store hash, not plain text
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)

    # Relationship to child profiles
    child_profiles: Mapped[List["ChildProfile"]] = relationship(
        "ChildProfile", back_populates="parent", cascade="all, delete-orphan"
    )