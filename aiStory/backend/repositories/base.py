"""Base repository interface defining common CRUD operations."""
import abc
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.base import Base

# Generic type variable for models
ModelType = TypeVar("ModelType", bound=Base)


class RepositoryError(Exception):
    """Base class for repository exceptions."""
    pass


class ItemNotFoundError(RepositoryError):
    """Exception raised when an item is not found."""
    pass


class DatabaseError(RepositoryError):
    """Exception raised when a database error occurs."""
    pass


class Repository(Generic[ModelType], abc.ABC):
    """Abstract base class for all repositories."""
    
    @abc.abstractmethod
    async def create(self, db: AsyncSession, obj_data: Dict[str, Any]) -> ModelType:
        """Create a new item in the repository.
        
        Args:
            db: Database session
            obj_data: Dictionary of data to create the item with
            
        Returns:
            The created item
            
        Raises:
            DatabaseError: If a database error occurs
        """
        pass
    
    @abc.abstractmethod
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get an item by ID.
        
        Args:
            db: Database session
            id: Item ID
            
        Returns:
            The item if found, None otherwise
            
        Raises:
            DatabaseError: If a database error occurs
        """
        pass
    
    @abc.abstractmethod
    async def get_by_field(self, db: AsyncSession, field: str, value: Any) -> Optional[ModelType]:
        """Get an item by a specific field.
        
        Args:
            db: Database session
            field: Field name
            value: Field value
            
        Returns:
            The item if found, None otherwise
            
        Raises:
            DatabaseError: If a database error occurs
        """
        pass
    
    @abc.abstractmethod
    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """List items in the repository.
        
        Args:
            db: Database session
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of items
            
        Raises:
            DatabaseError: If a database error occurs
        """
        pass
    
    @abc.abstractmethod
    async def update(self, db: AsyncSession, id: Any, obj_data: Dict[str, Any]) -> ModelType:
        """Update an item.
        
        Args:
            db: Database session
            id: Item ID
            obj_data: Dictionary of data to update the item with
            
        Returns:
            The updated item
            
        Raises:
            ItemNotFoundError: If the item is not found
            DatabaseError: If a database error occurs
        """
        pass
    
    @abc.abstractmethod
    async def delete(self, db: AsyncSession, id: Any) -> None:
        """Delete an item.
        
        Args:
            db: Database session
            id: Item ID
            
        Raises:
            ItemNotFoundError: If the item is not found
            DatabaseError: If a database error occurs
        """
        pass