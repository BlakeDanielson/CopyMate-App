"""API routes for story management."""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.story import Story, StoryStatus
from backend.models.photo import Photo, PhotoStatus
from backend.schemas.story import StoryCreate, StoryRead
from backend.utils.auth import get_current_user
from backend.utils.database import get_db
from backend.services.tasks.celery_app import celery_app

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/stories",
    tags=["stories"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "Resource not found"},
        422: {"description": "Validation error"},
    }
)


@router.post(
    "",
    response_model=StoryRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create a new story",
    description="Create a new story using the user's uploaded photo. "
                "Story generation will be processed asynchronously."
)
async def create_story(
    data: StoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new story with the given child name, age, theme, and protagonist photo.
    
    The story generation is an asynchronous process. The endpoint will return
    a 202 Accepted response with the created story record, and the actual content
    will be generated in the background.
    
    Args:
        data: Story creation data
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        The created story record with an initial "pending" status
        
    Raises:
        HTTPException: If photo doesn't exist or doesn't belong to user
    """
    try:
        # Check if the photo exists and belongs to the user
        photo_id = data.protagonist_photo_id
        photo = await db.get(Photo, photo_id)
        
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Photo with ID {photo_id} not found"
            )
            
        if photo.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: The photo does not belong to the current user"
            )
            
        if photo.status != PhotoStatus.UPLOADED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Photo with ID {photo_id} is not ready for use (status: {photo.status})"
            )
        
        # Create the story record
        story = Story(
            user_id=current_user["id"],
            child_name=data.child_name,
            child_age=data.child_age,
            story_theme=data.story_theme,
            protagonist_photo_id=data.protagonist_photo_id,
            status=StoryStatus.PENDING.value
        )
        
        db.add(story)
        await db.commit()
        await db.refresh(story)
        
        # Start the story generation process in the background using Celery
        logger.info(f"Starting story generation task for story ID: {story.id}")
        generate_story.delay(str(story.id))
        
        # Prepare the response
        response = StoryRead.from_orm(story)
        response.message = "Story generation initiated. Check status using GET /v1/stories/{id}"
        
        return response
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error creating story: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating story"
        )


# Define Celery task for story generation
@celery_app.task(name="generate_story")
def generate_story(story_id: str):
    """
    Celery task to generate a story using AI services.
    
    In a real implementation, this would:
    1. Fetch the story record
    2. Use AI models to generate story content
    3. Update the story with the generated content
    4. Update the story status to completed
    
    Args:
        story_id: String representation of the story's UUID
    """
    # This is just a stub implementation for the MVP
    # The real implementation would call into AI services
    logger.info(f"Starting story generation for story ID: {story_id}")
    
    # In a real implementation, this would handle:
    # - Fetching data from DB
    # - Calling AI services to generate story
    # - Creating story pages
    # - Updating story status
    
    logger.info(f"Story generation completed for story ID: {story_id}")