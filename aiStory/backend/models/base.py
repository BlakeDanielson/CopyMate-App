"""Base model for SQLAlchemy models."""
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    # Use lowercase table names derived from class names
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate a table name from the class name."""
        return cls.__name__.lower()
    
    # Common columns for all models
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}