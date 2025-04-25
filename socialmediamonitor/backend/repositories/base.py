from typing import Generic, TypeVar, Type, List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from backend.database import Base

# Type variables for generic repository
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository with common CRUD operations.
    """
    def __init__(self, model: Type[ModelType]):
        """
        Initialize the repository with a SQLAlchemy model.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Database session
            id: ID of the record to get
            
        Returns:
            The found record or None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by(self, db: Session, **kwargs) -> Optional[ModelType]:
        """
        Get a single record by arbitrary filters.
        
        Args:
            db: Database session
            **kwargs: Filter conditions as keyword arguments
            
        Returns:
            The found record or None
        """
        query = db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first()

    def list(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        **kwargs
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            **kwargs: Filter conditions as keyword arguments
            
        Returns:
            List of matching records
        """
        query = db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Data to create the record with (Pydantic model or dict)
            
        Returns:
            The created record
        """
        try:
            if isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                obj_data = obj_in.dict(exclude_unset=True)
                
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    def update(
        self, 
        db: Session, 
        *, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session
            db_obj: Database object to update
            obj_in: Data to update with (Pydantic model or dict)
            
        Returns:
            The updated record
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
                
            for field in update_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, update_data[field])
                    
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Delete a record by ID.
        
        Args:
            db: Database session
            id: ID of the record to delete
            
        Returns:
            The deleted record or None if not found
        """
        try:
            obj = db.query(self.model).get(id)
            if obj is None:
                return None
                
            db.delete(obj)
            db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    def count(self, db: Session, **kwargs) -> int:
        """
        Count records with optional filtering.
        
        Args:
            db: Database session
            **kwargs: Filter conditions as keyword arguments
            
        Returns:
            Count of matching records
        """
        query = db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.count()