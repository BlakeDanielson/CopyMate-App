"""Celery tasks for AI image processing."""
import logging
import asyncio
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.tasks.celery_app import celery_app
from backend.utils.database import get_async_session_factory
from backend.models.photo import AIProcessingStatus
from backend.repositories.photo_repository import PhotoRepository
from backend.services.ai_processing import AIService, AIProcessingError
from backend.services.storage.factory import get_storage_service

# Configure logger
logger = logging.getLogger(__name__)


async def _process_photo_async(photo_id: int, storage_path: str) -> Dict[str, Any]:
    """
    Process a photo with AI processing service (async version).
    
    Args:
        photo_id: The ID of the photo to process
        storage_path: The storage path for the photo
        
    Returns:
        The AI processing results
    """
    # Initialize repositories and services
    photo_repo = PhotoRepository()
    storage_service = get_storage_service()
    ai_service = AIService(storage_service)
    
    # Create an async database session
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        session: AsyncSession
        async with session.begin():
            try:
                # Update photo status to "processing"
                logger.info(f"Updating photo {photo_id} status to processing")
                await photo_repo.update_ai_status(
                    session, photo_id, AIProcessingStatus.PROCESSING
                )
                
                # Process the photo using AI service
                # This is a synchronous call in an async context, but it's ok
                logger.info(f"Processing photo {photo_id} at path {storage_path}")
                try:
                    results = ai_service.process_photo(photo_id, storage_path)
                except Exception as e:
                    logger.error(f"Error during AI processing: {str(e)}")
                    if isinstance(e, AIProcessingError):
                        raise
                    else:
                        raise AIProcessingError(f"Unexpected error during processing: {str(e)}")
                
                # Update photo with AI results
                logger.info(f"Updating photo {photo_id} with AI results")
                await photo_repo.update_ai_results(
                    session, 
                    photo_id, 
                    results,
                    ai_provider_used=results.get('provider')
                )
                
                return results
            
            except AIProcessingError as e:
                logger.error(f"AI processing error for photo {photo_id}: {str(e)}")
                # Update photo with error status
                await photo_repo.update_ai_error(
                    session,
                    photo_id,
                    str(e),
                    ai_provider_used=getattr(e, 'provider_name', None)
                )
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error processing photo {photo_id}: {str(e)}")
                # Update photo with error status
                await photo_repo.update_ai_error(
                    session,
                    photo_id,
                    f"Unexpected error: {str(e)}"
                )
                raise


@celery_app.task(bind=True, name="process_photo", max_retries=3)
def process_photo(self, photo_id: int, storage_path: str) -> Dict[str, Any]:
    """
    Celery task to process a photo with AI.
    
    Args:
        self: The Celery task instance
        photo_id: The ID of the photo to process
        storage_path: The storage path for the photo
        
    Returns:
        The AI processing results
    """
    logger.info(f"Running AI processing task for photo {photo_id}")
    
    try:
        # Run the async function in the event loop
        return asyncio.run(_process_photo_async(photo_id, storage_path))
        
    except Exception as e:
        logger.error(f"Error in process_photo task for photo {photo_id}: {str(e)}")
        # Retry the task with exponential backoff
        retry_countdown = 60 * (2 ** self.request.retries)  # 60s, 120s, 240s
        self.retry(exc=e, countdown=retry_countdown)


@celery_app.task(name="enqueue_pending_photos")
def enqueue_pending_photos(limit: int = 10) -> int:
    """
    Celery task to find and enqueue pending photos for AI processing.
    
    This task can be scheduled to run periodically to pick up any photos
    that were missed during normal upload processing.
    
    Args:
        limit: Maximum number of photos to enqueue
        
    Returns:
        Number of photos enqueued
    """
    async def _get_and_enqueue_photos():
        photo_repo = PhotoRepository()
        count = 0
        
        # Create an async database session
        session_factory = get_async_session_factory()
        async with session_factory() as session:
            session: AsyncSession
            try:
                # Get photos pending AI processing
                pending_photos = await photo_repo.get_pending_ai_processing(session, limit)
                
                for photo in pending_photos:
                    # Enqueue each photo for processing
                    storage_path = f"{photo.storage_provider}/{photo.bucket_name}/{photo.storage_key}"
                    process_photo.delay(photo.id, storage_path)
                    count += 1
                    
                    logger.info(f"Enqueued photo {photo.id} for AI processing")
                    
                return count
            except Exception as e:
                logger.error(f"Error enqueuing pending photos: {str(e)}")
                raise
    
    try:
        return asyncio.run(_get_and_enqueue_photos())
    except Exception as e:
        logger.error(f"Failed to enqueue pending photos: {str(e)}")
        return 0