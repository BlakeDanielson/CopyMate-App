"""Photo repository interface and implementation."""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.photo import Photo, PhotoStatus, AIProcessingStatus
from backend.repositories.base import ItemNotFoundError, DatabaseError
from backend.repositories.sqlalchemy_base import SQLAlchemyRepository

# Configure logger
logger = logging.getLogger(__name__)


class PhotoRepository(SQLAlchemyRepository[Photo]):
    """SQLAlchemy implementation of photo repository."""
    
    def __init__(self):
        """Initialize the repository with the Photo model."""
        super().__init__(Photo)
    
    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Optional[Photo]:
        """Get a photo by UUID.
        
        Args:
            db: Database session
            uuid: Photo UUID
            
        Returns:
            The photo if found, None otherwise
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            return await self.get_by_field(db, "uuid", uuid)
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving photo with uuid {uuid}: {e}")
            raise DatabaseError(f"Error retrieving photo with uuid {uuid}: {e}")
    
    async def list_by_user_id(self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Photo]:
        """List photos for a specific user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of photos for the user
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            statement = select(self.model).where(self.model.user_id == user_id).offset(skip).limit(limit)
            result = await db.execute(statement)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error listing photos for user {user_id}: {e}")
            raise DatabaseError(f"Error listing photos for user {user_id}: {e}")
    
    async def list_by_status(
        self, db: AsyncSession, status: PhotoStatus, skip: int = 0, limit: int = 100
    ) -> List[Photo]:
        """List photos with a specific status.
        
        Args:
            db: Database session
            status: Photo status
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of photos with the specified status
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            statement = select(self.model).where(self.model.status == status.value).offset(skip).limit(limit)
            result = await db.execute(statement)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error listing photos with status {status.value}: {e}")
            raise DatabaseError(f"Error listing photos with status {status.value}: {e}")
    
    async def update_status(self, db: AsyncSession, id: int, status: PhotoStatus) -> Photo:
        """Update the status of a photo.
        
        Args:
            db: Database session
            id: Photo ID
            status: New photo status
            
        Returns:
            The updated photo
            
        Raises:
            ItemNotFoundError: If the photo is not found
            DatabaseError: If a database error occurs
        """
        try:
            return await self.update(db, id, {"status": status.value})
        except (ItemNotFoundError, DatabaseError):
            # Re-raise these exceptions
            raise
    
    async def update_status_by_uuid(self, db: AsyncSession, uuid: str, status: PhotoStatus) -> Photo:
        """Update the status of a photo by UUID.
        
        Args:
            db: Database session
            uuid: Photo UUID
            status: New photo status
            
        Returns:
            The updated photo
            
        Raises:
            ItemNotFoundError: If the photo is not found
            DatabaseError: If a database error occurs
        """
        try:
            # First get the photo by UUID
            photo = await self.get_by_uuid(db, uuid)
            if not photo:
                raise ItemNotFoundError(f"Photo with uuid {uuid} not found")
            
            # Update the status
            return await self.update(db, photo.id, {"status": status.value})
        except (ItemNotFoundError, DatabaseError):
            # Re-raise these exceptions
            raise
    
    async def count_by_user_id(self, db: AsyncSession, user_id: int) -> int:
        """Count the total number of photos for a specific user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Total count of photos for the user
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            statement = select(self.model).where(self.model.user_id == user_id)
            result = await db.execute(statement)
            return len(list(result.scalars().all()))
        except SQLAlchemyError as e:
            logger.error(f"Database error counting photos for user {user_id}: {e}")
            raise DatabaseError(f"Error counting photos for user {user_id}: {e}")
    
    async def count_by_status(self, db: AsyncSession, status: PhotoStatus) -> int:
        """Count the total number of photos with a specific status.
        
        Args:
            db: Database session
            status: Photo status
            
        Returns:
            Total count of photos with the specified status
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            statement = select(self.model).where(self.model.status == status.value)
            result = await db.execute(statement)
            return len(list(result.scalars().all()))
        except SQLAlchemyError as e:
            logger.error(f"Database error counting photos with status {status.value}: {e}")
            raise DatabaseError(f"Error counting photos with status {status.value}: {e}")
            
    # AI Processing Methods
    
    async def list_by_ai_status(
        self, db: AsyncSession, ai_status: AIProcessingStatus, skip: int = 0, limit: int = 100
    ) -> List[Photo]:
        """List photos with a specific AI processing status.
        
        Args:
            db: Database session
            ai_status: AI processing status
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of photos with the specified AI processing status
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            statement = select(self.model).where(
                self.model.ai_processing_status == ai_status.value
            ).offset(skip).limit(limit)
            result = await db.execute(statement)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error listing photos with AI status {ai_status.value}: {e}")
            raise DatabaseError(f"Error listing photos with AI status {ai_status.value}: {e}")
    
    async def update_ai_status(
        self, db: AsyncSession, id: int, ai_status: AIProcessingStatus
    ) -> Photo:
        """Update the AI processing status of a photo.
        
        Args:
            db: Database session
            id: Photo ID
            ai_status: New AI processing status
            
        Returns:
            The updated photo
            
        Raises:
            ItemNotFoundError: If the photo is not found
            DatabaseError: If a database error occurs
        """
        try:
            return await self.update(db, id, {"ai_processing_status": ai_status.value})
        except (ItemNotFoundError, DatabaseError):
            # Re-raise these exceptions
            raise
    
    async def update_ai_results(
        self, db: AsyncSession, id: int, ai_results: Dict[str, Any], 
        ai_status: AIProcessingStatus = AIProcessingStatus.COMPLETED, 
        ai_provider_used: Optional[str] = None
    ) -> Photo:
        """Update the AI processing results of a photo.
        
        Args:
            db: Database session
            id: Photo ID
            ai_results: AI processing results
            ai_status: New AI processing status (default: COMPLETED)
            ai_provider_used: Name of the AI provider used
            
        Returns:
            The updated photo
            
        Raises:
            ItemNotFoundError: If the photo is not found
            DatabaseError: If a database error occurs
        """
        try:
            update_data = {
                "ai_results": ai_results,
                "ai_processing_status": ai_status.value,
            }
            
            if ai_provider_used:
                update_data["ai_provider_used"] = ai_provider_used
                
            return await self.update(db, id, update_data)
        except (ItemNotFoundError, DatabaseError):
            # Re-raise these exceptions
            raise
    
    async def update_ai_error(
        self, db: AsyncSession, id: int, error_message: str, 
        ai_provider_used: Optional[str] = None
    ) -> Photo:
        """Update the photo with AI processing error information.
        
        Args:
            db: Database session
            id: Photo ID
            error_message: Error message
            ai_provider_used: Name of the AI provider that generated the error
            
        Returns:
            The updated photo
            
        Raises:
            ItemNotFoundError: If the photo is not found
            DatabaseError: If a database error occurs
        """
        try:
            update_data = {
                "ai_processing_status": AIProcessingStatus.FAILED.value,
                "ai_error_message": error_message
            }
            
            if ai_provider_used:
                update_data["ai_provider_used"] = ai_provider_used
                
            return await self.update(db, id, update_data)
        except (ItemNotFoundError, DatabaseError):
            # Re-raise these exceptions
            raise
    
    async def get_pending_ai_processing(
        self, db: AsyncSession, limit: int = 10
    ) -> List[Photo]:
        """Get photos pending AI processing.
        
        Args:
            db: Database session
            limit: Maximum number of photos to return
            
        Returns:
            List of photos pending AI processing
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            statement = select(self.model).where(
                self.model.ai_processing_status == AIProcessingStatus.PENDING.value,
                self.model.status == PhotoStatus.UPLOADED.value
            ).limit(limit)
            result = await db.execute(statement)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving photos pending AI processing: {e}")
            raise DatabaseError(f"Error retrieving photos pending AI processing: {e}")