"""Implementation of the photo service."""
import asyncio
import io
import logging
import uuid
from typing import BinaryIO, List, Optional, Union

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings, get_settings
from backend.models.photo import Photo, PhotoStatus, AIProcessingStatus
from backend.repositories.photo_repository import PhotoRepository
from backend.schemas.photo import PhotoResponse
from backend.schemas.photo_upload import PhotoListFilters, PhotoProcessingResult, PhotoUploadForm, PhotoUploadResponse
from backend.services.photo.base import PhotoService
from backend.services.photo.exceptions import (
    InvalidPhotoError, 
    PhotoNotFoundError, 
    PhotoProcessingError, 
    PhotoQuotaExceededError, 
    PhotoServiceError, 
    PhotoUploadError,
    StorageError
)
from backend.services.storage.base import StorageService, StorageError as BaseStorageError
from backend.services.storage.factory import StorageServiceFactory
from backend.services.tasks.ai_processing_tasks import process_photo as process_photo_task


logger = logging.getLogger(__name__)


class PhotoServiceImpl(PhotoService):
    """Photo service implementation."""
    
    def __init__(
        self, 
        photo_repository: PhotoRepository,
        storage_service: Optional[StorageService] = None,
        settings: Optional[Settings] = None
    ):
        """Initialize the photo service.
        
        Args:
            photo_repository: Repository for photo database operations
            storage_service: Service for file storage operations
            settings: Application settings
        """
        self.photo_repository = photo_repository
        self.settings = settings or get_settings()
        
        # If storage service is not provided, get it from the factory
        if storage_service is None:
            self.storage_service = StorageServiceFactory.get_storage_service(self.settings)
        else:
            self.storage_service = storage_service
    
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
        try:
            # Validate the uploaded file
            await upload_form.validate()
            
            # Check user quotas
            photo_count = await self.photo_repository.count_by_user_id(db, user_id)
            max_photos = 100  # This could be part of settings or user plan
            if photo_count >= max_photos:
                raise PhotoQuotaExceededError(
                    f"User has reached the maximum number of photos allowed ({max_photos})"
                )
            
            # Generate a unique storage key
            filename = upload_form.file.filename
            content_type = upload_form.file.content_type
            storage_key = self.storage_service.generate_key(user_id, filename)
            
            # Read file content
            file_content = await upload_form.file.read()
            file_io = io.BytesIO(file_content)
            
            # Upload to storage
            try:
                # Set initial status to PENDING
                photo_uuid = str(uuid.uuid4())
                
                # Create the photo record in database with PENDING status
                photo_data = {
                    "uuid": photo_uuid,
                    "user_id": user_id,
                    "storage_provider": self.settings.storage_backend,
                    "bucket_name": self.settings.storage_s3_bucket or "local",
                    "storage_key": storage_key,
                    "original_filename": filename,
                    "content_type": content_type,
                    "status": PhotoStatus.PENDING.value,
                    "ai_processing_status": AIProcessingStatus.PENDING.value
                }
                
                # Create the photo in the database
                photo = await self.photo_repository.create(db, photo_data)
                
                # Upload to storage
                await self.storage_service.upload_file(
                    file=file_io, 
                    key=storage_key,
                    content_type=content_type,
                    metadata={"user_id": str(user_id), "photo_uuid": photo_uuid}
                )
                
                # Update status to UPLOADED
                photo = await self.photo_repository.update_status(
                    db, photo.id, PhotoStatus.UPLOADED
                )
                
                # Enqueue AI processing task
                storage_path = f"{photo.storage_provider}/{photo.bucket_name}/{photo.storage_key}"
                process_photo_task.delay(photo.id, storage_path)
                
                logger.info(f"Enqueued AI processing task for photo {photo.id} ({photo_uuid})")
                
                return PhotoUploadResponse(
                    photo_id=photo.uuid,
                    status=PhotoStatus(photo.status),
                    message="Photo uploaded successfully and queued for AI processing"
                )
                
            except BaseStorageError as e:
                # If storage upload fails, we need to clean up any partial uploads
                logger.error(f"Storage error during photo upload: {str(e)}")
                if photo := await self.photo_repository.get_by_uuid(db, photo_uuid):
                    await self.photo_repository.update_status(
                        db, photo.id, PhotoStatus.FAILED
                    )
                raise PhotoUploadError(f"Failed to upload photo to storage: {str(e)}")
            
        except ValueError as e:
            # This catches validation errors from upload_form.validate()
            logger.error(f"Invalid photo upload: {str(e)}")
            raise InvalidPhotoError(str(e))
            
        except Exception as e:
            logger.error(f"Unexpected error during photo upload: {str(e)}", exc_info=True)
            raise PhotoUploadError(f"Photo upload failed: {str(e)}")
    
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
        try:
            photo = await self.photo_repository.get_by_uuid(db, photo_id)
            if not photo:
                raise PhotoNotFoundError(f"Photo with ID {photo_id} not found")
            
            # Convert to PhotoResponse
            return PhotoResponse.model_validate(photo)
            
        except Exception as e:
            if isinstance(e, PhotoNotFoundError):
                raise
            logger.error(f"Error retrieving photo {photo_id}: {str(e)}")
            raise PhotoServiceError(f"Failed to retrieve photo: {str(e)}")
    
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
        try:
            # Set default filters if none provided
            if filters is None:
                filters = PhotoListFilters()
                
            # Calculate pagination
            skip = (filters.page - 1) * filters.page_size
            limit = filters.page_size
            
            # Get photos from repository
            photos = await self.photo_repository.list_by_user_id(db, user_id, skip, limit)
            
            # Convert to responses
            return [PhotoResponse.model_validate(photo) for photo in photos]
            
        except Exception as e:
            logger.error(f"Error retrieving photos for user {user_id}: {str(e)}")
            raise PhotoServiceError(f"Failed to retrieve photos: {str(e)}")
    
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
        try:
            photo = await self.photo_repository.get_by_uuid(db, photo_id)
            if not photo:
                raise PhotoNotFoundError(f"Photo with ID {photo_id} not found")
            
            # Check ownership if user_id is provided
            if user_id is not None and photo.user_id != user_id:
                raise PermissionError(f"User {user_id} does not own photo {photo_id}")
            
            # Delete from storage
            try:
                await self.storage_service.delete_file(photo.storage_key)
            except BaseStorageError as e:
                logger.error(f"Error deleting photo {photo_id} from storage: {str(e)}")
                # Continue with database deletion even if storage deletion fails
                # This ensures we don't have orphaned database records
            
            # Delete from database
            await self.photo_repository.delete(db, photo.id)
            
            return True
            
        except Exception as e:
            if isinstance(e, (PhotoNotFoundError, PermissionError)):
                raise
            logger.error(f"Error deleting photo {photo_id}: {str(e)}")
            raise PhotoServiceError(f"Failed to delete photo: {str(e)}")
    
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
        try:
            # Update the status
            photo = await self.photo_repository.update_status_by_uuid(db, photo_id, status)
            if not photo:
                raise PhotoNotFoundError(f"Photo with ID {photo_id} not found")
            
            # Convert to response
            return PhotoResponse.model_validate(photo)
            
        except Exception as e:
            if isinstance(e, PhotoNotFoundError):
                raise
            logger.error(f"Error updating photo {photo_id} status: {str(e)}")
            raise PhotoServiceError(f"Failed to update photo status: {str(e)}")
    
    async def process_photo(
        self, 
        db: AsyncSession, 
        photo_id: str
    ) -> PhotoProcessingResult:
        """Process a photo (AI processing, etc.).
        
        This method now triggers the Celery task for async AI processing.
        If you need immediate processing, this method will wait for the task to complete.
        
        Args:
            db: Database session
            photo_id: UUID of the photo
            
        Returns:
            PhotoProcessingResult with the processing results
            
        Raises:
            PhotoNotFoundError: If the photo is not found
            PhotoProcessingError: If processing fails
        """
        try:
            # Get the photo
            photo = await self.photo_repository.get_by_uuid(db, photo_id)
            if not photo:
                raise PhotoNotFoundError(f"Photo with ID {photo_id} not found")
            
            # Check if already completed
            if photo.ai_processing_status == AIProcessingStatus.COMPLETED.value:
                # Get URL to the processed photo
                processed_url = await self.storage_service.get_file_url(photo.storage_key)
                
                # Return the existing result
                return PhotoProcessingResult(
                    photo_id=photo.uuid,
                    status=PhotoStatus(photo.status),
                    processed_url=processed_url,
                    thumbnails=[],  # Will be populated in future versions
                    metadata=photo.ai_results or {}
                )
            
            # Enqueue the processing task if not already in progress
            if photo.ai_processing_status not in [AIProcessingStatus.PROCESSING.value, AIProcessingStatus.COMPLETED.value]:
                # Update to processing status
                photo = await self.photo_repository.update_ai_status(
                    db, photo.id, AIProcessingStatus.PROCESSING
                )
                
                # Trigger the Celery task
                storage_path = f"{photo.storage_provider}/{photo.bucket_name}/{photo.storage_key}"
                task_result = process_photo_task.delay(photo.id, storage_path)
                
                logger.info(f"Triggered immediate AI processing for photo {photo_id}, task ID: {task_result.id}")
                
                # For now, we don't wait for the task to complete
                # In a real application, you might want to add an option to wait
            
            # Get URL to the photo
            processed_url = await self.storage_service.get_file_url(photo.storage_key)
            
            # Return current status
            return PhotoProcessingResult(
                photo_id=photo.uuid,
                status=PhotoStatus(photo.status),
                ai_status=AIProcessingStatus(photo.ai_processing_status),
                processed_url=processed_url,
                thumbnails=[],
                metadata=photo.ai_results or {}
            )
            
        except Exception as e:
            if isinstance(e, PhotoNotFoundError):
                raise
            logger.error(f"Error processing photo {photo_id}: {str(e)}")
            
            # Try to update status to FAILED if possible
            try:
                if photo:
                    await self.photo_repository.update_ai_status(
                        db, photo.id, AIProcessingStatus.FAILED
                    )
            except Exception as update_err:
                logger.error(f"Failed to update photo AI status to FAILED: {str(update_err)}")
            
            raise PhotoProcessingError(f"Failed to process photo: {str(e)}")
    
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
        try:
            # Get the photo
            photo = await self.photo_repository.get_by_uuid(db, photo_id)
            if not photo:
                raise PhotoNotFoundError(f"Photo with ID {photo_id} not found")
            
            # Get URL from storage service
            return await self.storage_service.get_file_url(photo.storage_key, expires_in)
            
        except BaseStorageError as e:
            logger.error(f"Storage error getting URL for photo {photo_id}: {str(e)}")
            raise StorageError(f"Failed to get photo URL: {str(e)}")
            
        except Exception as e:
            if isinstance(e, (PhotoNotFoundError, StorageError)):
                raise
            logger.error(f"Error getting URL for photo {photo_id}: {str(e)}")
            raise PhotoServiceError(f"Failed to get photo URL: {str(e)}")
    
    async def start_processing_photo_async(
        self,
        db: AsyncSession,
        photo_id: str,
        background_tasks: BackgroundTasks
    ) -> None:
        """Start asynchronous processing of a photo.
        
        This method now uses Celery tasks for processing instead of FastAPI background tasks.
        
        Args:
            db: Database session
            photo_id: UUID of the photo
            background_tasks: FastAPI BackgroundTasks object (kept for backward compatibility)
            
        Raises:
            PhotoNotFoundError: If the photo is not found
        """
        # Get the photo first to ensure it exists
        photo = await self.photo_repository.get_by_uuid(db, photo_id)
        if not photo:
            raise PhotoNotFoundError(f"Photo with ID {photo_id} not found")
        
        # Update status to processing
        await self.photo_repository.update_ai_status(
            db, photo.id, AIProcessingStatus.PROCESSING
        )
        
        # Enqueue the task
        storage_path = f"{photo.storage_provider}/{photo.bucket_name}/{photo.storage_key}"
        process_photo_task.delay(photo.id, storage_path)
        
        logger.info(f"Enqueued AI processing task for photo {photo.id} ({photo_id})")
    
    async def get_ai_processing_status(
        self,
        db: AsyncSession,
        photo_id: str
    ) -> dict:
        """Get the AI processing status and results for a photo.
        
        Args:
            db: Database session
            photo_id: UUID of the photo
            
        Returns:
            Dictionary with AI processing status and results
            
        Raises:
            PhotoNotFoundError: If the photo is not found
        """
        photo = await self.photo_repository.get_by_uuid(db, photo_id)
        if not photo:
            raise PhotoNotFoundError(f"Photo with ID {photo_id} not found")
        
        result = {
            "photo_id": photo.uuid,
            "ai_processing_status": photo.ai_processing_status,
            "ai_provider_used": photo.ai_provider_used,
            "ai_results": photo.ai_results
        }
        
        # Add error message if failed
        if photo.ai_processing_status == AIProcessingStatus.FAILED.value:
            result["ai_error_message"] = photo.ai_error_message
            
        return result
        
    async def get_storage_service(self) -> StorageService:
        """Get the storage service used by this photo service.
        
        Returns:
            The storage service instance
        """
        return self.storage_service