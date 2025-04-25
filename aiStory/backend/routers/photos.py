"""Photo API endpoints."""
import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, Form, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.photo import Photo, PhotoStatus
from backend.repositories.photo_repository import PhotoRepository
from backend.schemas.photo import PhotoResponse
from backend.schemas.photo_upload import (
    PhotoListFilters,
    PhotoProcessingResult,
    PhotoUploadForm,
    PhotoUploadResponse,
    PhotoUploadUrlRequest,
    PhotoUploadUrlResponse
)
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
from backend.services.photo.factory import PhotoServiceFactory
from backend.utils.auth import get_current_user
from backend.utils.database import get_db


logger = logging.getLogger(__name__)

# Configure router with prefix and tags
router = APIRouter(
    prefix="/photos",
    tags=["photos"],
    dependencies=[Depends(get_current_user)]  # All endpoints require authentication
)

# Get limiter instance from app state
limiter = Limiter(key_func=get_remote_address)


async def get_photo_service() -> PhotoService:
    """Dependency for getting the photo service."""
    return PhotoServiceFactory.get_photo_service()


@router.post(
    "/upload", 
    response_model=PhotoUploadResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new photo",
    description="Upload a new photo. The file must be an image with a valid content type.",
    dependencies=[Depends(limiter.limit("10/minute"))]  # Rate limiting for uploads
)
async def upload_photo(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service)
):
    """Upload a new photo.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Photo file to upload
        description: Optional description
        tags: Optional comma-separated tags
        db: Database session
        current_user: Current authenticated user
        photo_service: Photo service
        
    Returns:
        PhotoUploadResponse with photo ID and status
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Create form data
        upload_form = PhotoUploadForm(file=file, description=description, tags=tags)
        
        # Upload photo
        upload_response = await photo_service.upload_photo(
            db=db, 
            user_id=current_user.id, 
            upload_form=upload_form
        )
        
        # Start processing in background (non-blocking)
        try:
            await photo_service.start_processing_photo_async(
                db=db,
                photo_id=upload_response.photo_id,
                background_tasks=background_tasks
            )
        except Exception as e:
            # Don't fail the upload if background processing setup fails
            # Just log the error
            logger.error(f"Failed to start background processing: {str(e)}")
        
        return upload_response
        
    except PhotoQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except InvalidPhotoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PhotoUploadError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{photo_id}", 
    response_model=PhotoResponse,
    summary="Get photo by ID",
    description="Retrieve a photo by its ID"
)
async def get_photo(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service)
):
    """Get a photo by ID.
    
    Args:
        photo_id: UUID of the photo
        db: Database session
        current_user: Current authenticated user
        photo_service: Photo service
        
    Returns:
        PhotoResponse with photo details
        
    Raises:
        HTTPException: If photo is not found or user is not authorized
    """
    try:
        photo = await photo_service.get_photo_by_id(db, photo_id)
        
        # Check if user is authorized to view this photo
        if photo.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this photo"
            )
        
        return photo
        
    except PhotoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "", 
    response_model=List[PhotoResponse],
    summary="Get user photos",
    description="Retrieve photos for the current user with optional filtering"
)
async def get_user_photos(
    status: Optional[PhotoStatus] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service)
):
    """Get photos for the current user with optional filtering.
    
    Args:
        status: Optional filter by photo status
        page: Page number (1-based)
        page_size: Number of items per page
        db: Database session
        current_user: Current authenticated user
        photo_service: Photo service
        
    Returns:
        List of PhotoResponse objects
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Create filters
        filters = PhotoListFilters(
            status=status,
            page=page,
            page_size=page_size
        )
        
        # Get photos
        return await photo_service.get_photos_by_user(db, current_user.id, filters)
        
    except PhotoServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete photo",
    description="Delete a photo by ID"
)
async def delete_photo(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service)
):
    """Delete a photo.
    
    Args:
        photo_id: UUID of the photo
        db: Database session
        current_user: Current authenticated user
        photo_service: Photo service
        
    Raises:
        HTTPException: If deletion fails or user is not authorized
    """
    try:
        # Delete with user ID check to ensure ownership
        await photo_service.delete_photo(db, photo_id, current_user.id)
        
    except PhotoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except PhotoServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch(
    "/{photo_id}/process",
    response_model=PhotoProcessingResult,
    summary="Process photo",
    description="Trigger processing of a photo"
)
async def process_photo(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service)
):
    """Process a photo (generate thumbnails, apply AI, etc.).
    
    Args:
        photo_id: UUID of the photo
        db: Database session
        current_user: Current authenticated user
        photo_service: Photo service
        
    Returns:
        PhotoProcessingResult with processing results
        
    Raises:
        HTTPException: If processing fails or user is not authorized
    """
    try:
        # First check if photo exists and user owns it
        photo = await photo_service.get_photo_by_id(db, photo_id)
        
        # Check if user is authorized to process this photo
        if photo.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to process this photo"
            )
        
        # Process photo
        return await photo_service.process_photo(db, photo_id)
        
    except PhotoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PhotoProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{photo_id}/url",
    response_model=str,
    summary="Get photo URL",
    description="Get a URL for accessing a photo"
)
async def get_photo_url(
    photo_id: str,
    expires_in: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service)
):
    """Get a URL for accessing a photo.
    
    Args:
        photo_id: UUID of the photo
        expires_in: Optional expiration time in seconds
        db: Database session
        current_user: Current authenticated user
        photo_service: Photo service
        
    Returns:
        URL to access the photo
        
    Raises:
        HTTPException: If URL generation fails or user is not authorized
    """
    try:
        # First check if photo exists and user owns it
        photo = await photo_service.get_photo_by_id(db, photo_id)
        
        # Check if user is authorized to get URL for this photo
        if photo.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this photo"
            )
        
        # Get URL
        return await photo_service.get_photo_url(db, photo_id, expires_in)
        
    except PhotoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/{photo_id}/ai-processing",
    response_model=dict,
    summary="Get AI processing status",
    description="Get the AI processing status and results for a photo"
)
async def get_ai_processing_status(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service)
):
    """Get the AI processing status and results for a photo.
    
    Args:
        photo_id: UUID of the photo
        db: Database session
        current_user: Current authenticated user
        photo_service: Photo service
        
    Returns:
        Dictionary containing AI processing status and results
        
    Raises:
        HTTPException: If retrieval fails or user is not authorized
    """
    try:
        # First check if photo exists and user owns it
        photo = await photo_service.get_photo_by_id(db, photo_id)
        
        # Check if user is authorized to access this photo
        if photo.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this photo's AI processing information"
            )
        
        # Get AI processing status and results
        return await photo_service.get_ai_processing_status(db, photo_id)
        
    except PhotoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PhotoServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/upload-url",
    response_model=PhotoUploadUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate pre-signed URL for photo upload",
    description="Generate a pre-signed URL for directly uploading a photo to storage"
)
async def get_photo_upload_url(
    request: PhotoUploadUrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    photo_service: PhotoService = Depends(get_photo_service)
):
    """Generate a pre-signed URL for photo upload.
    
    Args:
        request: Request containing filename and content_type
        db: Database session
        current_user: Current authenticated user
        photo_service: Photo service
        
    Returns:
        PhotoUploadUrlResponse with upload URL and photo details
        
    Raises:
        HTTPException: If generation fails or validation errors occur
    """
    try:
        # Generate a unique object key (storage path)
        object_key = f"user_{current_user.id}/{uuid.uuid4()}/{request.filename}"
        
        # Create a photo record with pending_upload status
        photo = Photo(
            user_id=current_user.id,
            storage_provider=settings.storage_provider,
            bucket=settings.storage_bucket,
            object_key=object_key,
            filename=request.filename,
            content_type=request.content_type,
            status=PhotoStatus.PENDING_UPLOAD.value
        )
        
        # Save to database
        db.add(photo)
        await db.commit()
        await db.refresh(photo)
        
        # Generate pre-signed URL
        storage_service = await photo_service.get_storage_service()
        presigned_data = await storage_service.generate_presigned_upload_url(
            bucket=settings.storage_bucket,
            object_key=object_key,
            content_type=request.content_type,
            metadata={"user_id": str(current_user.id)}
        )
        
        # Return response
        return PhotoUploadUrlResponse(
            upload_url=presigned_data["url"],
            photo_id=str(photo.id),
            object_key=object_key,
            fields=presigned_data.get("fields")
        )
        
    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except StorageError as e:
        # Storage service errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error generating upload URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )