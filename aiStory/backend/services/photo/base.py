"""Base interface for photo service."""
import abc
from typing import BinaryIO, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.photo import Photo, PhotoStatus
from backend.schemas.photo import PhotoResponse
from backend.schemas.photo_upload import PhotoListFilters, PhotoProcessingResult, PhotoUploadForm, PhotoUploadResponse


class PhotoService(abc.ABC):
    """Abstract interface for photo service operations."""
    
    @abc.abstractmethod
    async def upload_photo(
        self, 
        db: AsyncSession, 
        user_id: int, 
        upload_form: PhotoUploadForm
    ) -> PhotoUploadResponse:
        """Upload a photo for a user.
        
        Args:
            db: Database session
            user_id: ID of the user uploading the photo
            upload_form: Form containing the photo file and metadata
            
        Returns:
            PhotoUploadResponse with the photo ID and status
            
        Raises:
            PhotoUploadError: If the upload fails
            InvalidPhotoError: If the photo is invalid
            PhotoQuotaExceededError: If the user's photo quota is exceeded
        """
        pass
    
    @abc.abstractmethod
    async def get_photo_by_id(
        self, 
        db: AsyncSession, 
        photo_id: str
    ) -> Optional[PhotoResponse]:
        """Get a photo by its ID.
        
        Args:
            db: Database session
            photo_id: UUID of the photo
            
        Returns:
            PhotoResponse if found, None otherwise
            
        Raises:
            PhotoNotFoundError: If the photo is not found
        """
        pass
    
    @abc.abstractmethod
    async def get_photos_by_user(
        self, 
        db: AsyncSession, 
        user_id: int, 
        filters: Optional[PhotoListFilters] = None
    ) -> List[PhotoResponse]:
        """Get all photos for a user with optional filtering.
        
        Args:
            db: Database session
            user_id: ID of the user
            filters: Optional filters for the photos
            
        Returns:
            List of PhotoResponse objects
        """
        pass
    
    @abc.abstractmethod
    async def delete_photo(
        self, 
        db: AsyncSession, 
        photo_id: str, 
        user_id: Optional[int] = None
    ) -> bool:
        """Delete a photo.
        
        Args:
            db: Database session
            photo_id: UUID of the photo
            user_id: Optional user ID to verify ownership
            
        Returns:
            True if the photo was deleted, False otherwise
            
        Raises:
            PhotoNotFoundError: If the photo is not found
            PermissionError: If the user does not own the photo
        """
        pass
    
    @abc.abstractmethod
    async def update_photo_status(
        self, 
        db: AsyncSession, 
        photo_id: str, 
        status: PhotoStatus
    ) -> PhotoResponse:
        """Update the status of a photo.
        
        Args:
            db: Database session
            photo_id: UUID of the photo
            status: New status for the photo
            
        Returns:
            Updated PhotoResponse
            
        Raises:
            PhotoNotFoundError: If the photo is not found
        """
        pass
    
    @abc.abstractmethod
    async def process_photo(
        self, 
        db: AsyncSession, 
        photo_id: str
    ) -> PhotoProcessingResult:
        """Process a photo (AI processing, etc.).
        
        This method serves as a placeholder for future AI integration.
        It should update the photo's status to PROCESSING, perform any
        necessary processing, and then update the status to COMPLETED.
        
        Args:
            db: Database session
            photo_id: UUID of the photo
            
        Returns:
            PhotoProcessingResult with the processing results
            
        Raises:
            PhotoNotFoundError: If the photo is not found
            PhotoProcessingError: If processing fails
        """
        pass
    
    @abc.abstractmethod
    async def get_photo_url(
        self, 
        db: AsyncSession, 
        photo_id: str, 
        expires_in: Optional[int] = None
    ) -> str:
        """Get a URL for accessing a photo.
        
        Args:
            db: Database session
            photo_id: UUID of the photo
            expires_in: Optional expiration time in seconds for the URL
            
        Returns:
            URL to access the photo
            
        Raises:
            PhotoNotFoundError: If the photo is not found
            StorageError: If generating the URL fails
        """
        pass