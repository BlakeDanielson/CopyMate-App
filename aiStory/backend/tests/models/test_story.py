"""Tests for the Story model."""
import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from sqlalchemy import select

from models.user import User
from models.photo import Photo
# These imports for our models and schemas
from models.story import Story, StoryStatus
from schemas.story import StoryBase, StoryCreate, StoryRead
from tests.test_database import test_db

# Helper function for creating test user and photo
async def create_test_user_and_photo(session):
    """Create and return a test user and photo for use in tests."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="fakehashedpassword"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    photo = Photo(
        user_id=user.id,
        storage_provider="s3",
        bucket="test-bucket",
        object_key="users/1234/photo123.jpg",
        filename="profile.jpg",
        content_type="image/jpeg"
    )
    
    session.add(photo)
    await session.commit()
    await session.refresh(photo)
    
    return user, photo


class TestStoryModel:
    """Test class for Story model."""
    
    @pytest.mark.asyncio
    async def test_create_story(self, test_db):
        """Test creating a Story instance."""
        # Create test user and photo first
        user, photo = await create_test_user_and_photo(test_db)
        
        # Create a story instance
        story = Story(
            user_id=user.id,
            child_name="Test Child",
            child_age=8,
            story_theme="space_adventure",
            protagonist_photo_id=photo.id,
            title="Space Journey"
        )
        
        test_db.add(story)
        await test_db.commit()
        await test_db.refresh(story)
        
        # Assertions
        assert story.id is not None
        assert story.user_id == user.id
        assert story.child_name == "Test Child"
        assert story.child_age == 8
        assert story.story_theme == "space_adventure"
        assert story.protagonist_photo_id == photo.id
        assert story.title == "Space Journey"
        assert story.status == "pending"  # Default status
        assert story.error_message is None
        assert story.created_at is not None
        assert story.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_story_relationships(self, test_db):
        """Test the relationships between Story, User, and Photo models."""
        # Create test user and photo
        user, photo = await create_test_user_and_photo(test_db)
        
        # Create a story for the user
        story = Story(
            user_id=user.id,
            child_name="Test Child",
            child_age=8,
            story_theme="space_adventure",
            protagonist_photo_id=photo.id,
            title="Space Journey"
        )
        
        test_db.add(story)
        await test_db.commit()
        await test_db.refresh(story)
        
        # Test relationship - story to user
        assert story.user.id == user.id
        assert story.protagonist_photo.id == photo.id
        
        # Test relationship - create a page for the story
        from backend.models.story_page import StoryPage
        
        page = StoryPage(
            story_id=story.id,
            page_number=1,
            text="Once upon a time in space..."
        )
        
        test_db.add(page)
        await test_db.commit()
        
        # Test relationship - story to pages
        assert len(story.pages) == 1
        assert story.pages[0].page_number == 1
    
    @pytest.mark.asyncio
    async def test_story_required_fields(self, test_db):
        """Test that required fields are enforced."""
        # Attempt to create a story without required fields
        story = Story()
        
        test_db.add(story)
        
        # Expect an integrity error
        with pytest.raises(IntegrityError):
            await test_db.commit()
        
        await test_db.rollback()
    
    @pytest.mark.asyncio
    async def test_story_status_enum(self, test_db):
        """Test that the status field accepts valid values from the enum."""
        # Create test user and photo
        user, photo = await create_test_user_and_photo(test_db)
        
        # Create a story with various status values
        for status in ["pending", "processing", "completed", "failed"]:
            story = Story(
                user_id=user.id,
                child_name="Test Child",
                child_age=8,
                story_theme="space_adventure",
                protagonist_photo_id=photo.id,
                status=status
            )
            
            test_db.add(story)
            await test_db.commit()
            await test_db.refresh(story)
            
            assert story.status == status
            await test_db.delete(story)
            await test_db.commit()


class TestStorySchema:
    """Test class for Story Pydantic schemas."""
    
    def test_story_base_schema(self):
        """Test StoryBase schema validation."""
        # Valid data
        valid_data = {
            "child_name": "Test Child",
            "child_age": 8,
            "story_theme": "space_adventure",
            "title": "Space Journey"
        }
        
        story_base = StoryBase(**valid_data)
        assert story_base.child_name == "Test Child"
        assert story_base.child_age == 8
        assert story_base.story_theme == "space_adventure"
        assert story_base.title == "Space Journey"
        
        # Invalid data - missing required fields
        invalid_data = {
            "child_name": "Test Child"
            # Missing other required fields
        }
        
        with pytest.raises(ValidationError):
            StoryBase(**invalid_data)
        
        # Invalid data - age out of range
        invalid_age_data = valid_data.copy()
        invalid_age_data["child_age"] = -1
        
        with pytest.raises(ValidationError):
            StoryBase(**invalid_age_data)
    
    def test_story_create_schema(self):
        """Test StoryCreate schema validation."""
        # Valid data
        valid_data = {
            "user_id": str(uuid.uuid4()),
            "protagonist_photo_id": str(uuid.uuid4()),
            "child_name": "Test Child",
            "child_age": 8,
            "story_theme": "space_adventure",
            "title": "Space Journey"
        }
        
        story_create = StoryCreate(**valid_data)
        assert story_create.user_id is not None
        assert story_create.child_name == "Test Child"
        
        # Test validation for theme
        invalid_theme_data = valid_data.copy()
        invalid_theme_data["story_theme"] = "invalid_theme"
        
        with pytest.raises(ValidationError):
            StoryCreate(**invalid_theme_data)
    
    def test_story_read_schema(self):
        """Test StoryRead schema."""
        # Create a valid story response
        valid_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "protagonist_photo_id": str(uuid.uuid4()),
            "child_name": "Test Child",
            "child_age": 8,
            "story_theme": "space_adventure", 
            "title": "Space Journey",
            "status": "pending",
            "error_message": None,
            "created_at": "2025-04-22T17:45:00Z",
            "updated_at": "2025-04-22T17:46:00Z",
            "pages": []
        }
        
        story_read = StoryRead(**valid_data)
        assert story_read.id == valid_data["id"]
        assert story_read.user_id == valid_data["user_id"]
        assert story_read.child_name == "Test Child"
        assert story_read.status == "pending"
        assert len(story_read.pages) == 0
        
        # Test with pages
        data_with_pages = valid_data.copy()
        data_with_pages["pages"] = [
            {
                "id": str(uuid.uuid4()),
                "story_id": valid_data["id"],
                "page_number": 1,
                "text": "Once upon a time...",
                "base_image_key": "stories/123/page1.jpg",
                "personalized_image_key": "stories/123/personalized/page1.jpg",
                "text_generation_status": "completed",
                "image_generation_status": "completed",
                "personalization_status": "completed",
                "created_at": "2025-04-22T17:45:00Z",
                "updated_at": "2025-04-22T17:46:00Z"
            }
        ]
        
        story_read_with_pages = StoryRead(**data_with_pages)
        assert len(story_read_with_pages.pages) == 1
        assert story_read_with_pages.pages[0].page_number == 1