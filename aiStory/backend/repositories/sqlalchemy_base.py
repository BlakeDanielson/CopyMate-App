"""SQLAlchemy base repository implementation."""
import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, cast

from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.base import Base
from backend.repositories.base import Repository, ItemNotFoundError, DatabaseError

# Configure logger
logger = logging.getLogger(__name__)

# Generic type variable for models
ModelType = TypeVar("ModelType", bound=Base)


class SQLAlchemyRepository(Repository[ModelType], Generic[ModelType]):
    """Base SQLAlchemy repository implementation."""
    
    def __init__(self, model: Type[ModelType]):
        """Initialize the repository with a model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
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
        try:
            # Create a new model instance with the provided data
            db_obj = self.model(**obj_data)
            
            # Add to session and flush to get the ID
            db.add(db_obj)
            await db.flush()
            
            # Return the created object
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise DatabaseError(f"Integrity error creating {self.model.__name__}: {e}")
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error creating {self.model.__name__}: {e}")
            raise DatabaseError(f"Error creating {self.model.__name__}: {e}")
    
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
        try:
            statement = select(self.model).where(self.model.id == id)
            result = await db.execute(statement)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Error retrieving {self.model.__name__} with id {id}: {e}")
    
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
        try:
            # Get the column by name
            if not hasattr(self.model, field):
                raise ValueError(f"Field {field} does not exist on model {self.model.__name__}")
            
            column = getattr(self.model, field)
            
            # Query the database
            statement = select(self.model).where(column == value)
            result = await db.execute(statement)
            return result.scalars().first()
        except ValueError as e:
            # Re-raise ValueError for invalid field names
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving {self.model.__name__} with {field}={value}: {e}")
            raise DatabaseError(f"Error retrieving {self.model.__name__} with {field}={value}: {e}")
    
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
        try:
            statement = select(self.model).offset(skip).limit(limit)
            result = await db.execute(statement)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error listing {self.model.__name__}: {e}")
            raise DatabaseError(f"Error listing {self.model.__name__}: {e}")
    
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
        try:
            # First get the item to update
            db_obj = await self.get(db, id)
            if not db_obj:
                raise ItemNotFoundError(f"{self.model.__name__} with id {id} not found")
            
            # Update the object with new data
            for key, value in obj_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            # Add to session and flush
            db.add(db_obj)
            await db.flush()
            
            # Return the updated object
            return db_obj
        except ItemNotFoundError:
            # Re-raise ItemNotFoundError
            raise
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error updating {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Integrity error updating {self.model.__name__} with id {id}: {e}")
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error updating {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Error updating {self.model.__name__} with id {id}: {e}")
    
    async def delete(self, db: AsyncSession, id: Any) -> None:
        """Delete an item.
        
        Args:
            db: Database session
            id: Item ID
            
        Raises:
            ItemNotFoundError: If the item is not found
            DatabaseError: If a database error occurs
        """
        try:
            # First check if the item exists
            db_obj = await self.get(db, id)
            if not db_obj:
                raise ItemNotFoundError(f"{self.model.__name__} with id {id} not found")
            
            # Delete the object
            await db.delete(db_obj)
            await db.flush()
        except ItemNotFoundError:
            # Re-raise ItemNotFoundError
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Error deleting {self.model.__name__} with id {id}: {e}")
    
    async def count(self, db: AsyncSession) -> int:
        """Count the total number of items in the repository.
        
        Args:
            db: Database session
            
        Returns:
            Total count of items
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            statement = select(func.count()).select_from(self.model)
            result = await db.execute(statement)
            return result.scalar() or 0
        except SQLAlchemyError as e:
            logger.error(f"Database error counting {self.model.__name__}: {e}")
            raise DatabaseError(f"Error counting {self.model.__name__}: {e}")