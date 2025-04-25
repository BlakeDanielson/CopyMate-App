"""Tests for the StoryPage model."""
import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from sqlalchemy import select

from models.user import User
from models.photo import Photo
# These imports for our models and schemas
from models.story import Story
from models.story_page import StoryPage, GenerationStatus
from schemas.story_page import StoryPageBase, StoryPageCreate, StoryPageRead
from tests.test_database import test_db


# Helper function for creating test user, photo and story
async def create_test_story(session):
    """Create and return a test user, photo and story for use in tests."""
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
    
    story = Story(
        user_id=user.id,
        child_name="Test Child",
        child_age=8,
        story_theme="space_adventure",
        protagonist_photo_id=photo.id,
        title="Space Journey"
    )
    
    session.add(story)
    await session.commit()
    await session.refresh(story)
    
    return user, photo, story


class TestStoryPageModel:
    """Test class for StoryPage model."""
    
    @pytest.mark.asyncio
    async def test_create_story_page(self, test_db):
        """Test creating a StoryPage instance."""
        # Create test user, photo and story first
        _, _, story = await create_test_story(test_db)
        
        # Create a story page instance
        page = StoryPage(
            story_id=story.id,
            page_number=1,
            text="Once upon a time in space...",
            base_image_key="stories/123/page1.jpg",
            personalized_image_key="stories/123/personalized/page1.jpg"
        )
        
        test_db.add(page)
        await test_db.commit()
        await test_db.refresh(page)
        
        # Assertions
        assert page.id is not None
        assert page.story_id == story.id
        assert page.page_number == 1
        assert page.text == "Once upon a time in space..."
        assert page.base_image_key == "stories/123/page1.jpg"
        assert page.personalized_image_key == "stories/123/personalized/page1.jpg"
        assert page.text_generation_status == "pending"  # Default status
        assert page.image_generation_status == "pending"  # Default status
        assert page.personalization_status == "pending"  # Default status
        assert page.created_at is not None
        assert page.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_story_page_relationship(self, test_db):
        """Test the relationship between StoryPage and Story models."""
        # Create test user, photo and story
        _, _, story = await create_test_story(test_db)
        
        # Create a page for the story
        page = StoryPage(
            story_id=story.id,
            page_number=1,
            text="Once upon a time in space..."
        )
        
        test_db.add(page)
        await test_db.commit()
        await test_db.refresh(page)
        
        # Test relationship - page to story
        assert page.story.id == story.id
        
        # Test relationship - story to pages
        assert len(story.pages) == 1
        assert story.pages[0].id == page.id
    
    @pytest.mark.asyncio
    async def test_story_page_required_fields(self, test_db):
        """Test that required fields are enforced."""
        # Attempt to create a page without required fields
        page = StoryPage()
        
        test_db.add(page)
        
        # Expect an integrity error
        with pytest.raises(IntegrityError):
            await test_db.commit()
        
        await test_db.rollback()
    
    @pytest.mark.asyncio
    async def test_story_page_unique_constraint(self, test_db):
        """Test that the unique constraint on (story_id, page_number) is enforced."""
        # Create test user, photo and story
        _, _, story = await create_test_story(test_db)
        
        # Create first page
        page1 = StoryPage(
            story_id=story.id,
            page_number=1,
            text="Page one content"
        )
        
        test_db.add(page1)
        await test_db.commit()
        
        # Try to create another page with the same page number
        page2 = StoryPage(
            story_id=story.id,
            page_number=1,  # Same page number as page1
            text="Duplicate page number"
        )
        
        test_db.add(page2)
        
        # Expect an integrity error
        with pytest.raises(IntegrityError):
            await test_db.commit()
        
        await test_db.rollback()
        
        # Should be able to create a page with a different page number
        page3 = StoryPage(
            story_id=story.id,
            page_number=2,  # Different page number
            text="Page two content"
        )
        
        test_db.add(page3)
        await test_db.commit()
        
        # Check both pages exist
        pages = await test_db.execute(select(StoryPage).where(StoryPage.story_id == story.id))
        pages = pages.scalars().all()
        assert len(pages) == 2
    
    @pytest.mark.asyncio
    async def test_generation_status_enum(self, test_db):
        """Test that the status fields accept valid values from the enum."""
        # Create test user, photo and story
        _, _, story = await create_test_story(test_db)
        
        # Create a page with various status values
        for status in ["pending", "processing", "completed", "failed"]:
            page = StoryPage(
                story_id=story.id,
                page_number=len(story.pages) + 1,
                text="Test page",
                text_generation_status=status,
                image_generation_status=status,
                personalization_status=status
            )
            
            test_db.add(page)
            await test_db.commit()
            await test_db.refresh(page)
            
            assert page.text_generation_status == status
            assert page.image_generation_status == status
            assert page.personalization_status == status


class TestStoryPageSchema:
    """Test class for StoryPage Pydantic schemas."""
    
    def test_story_page_base_schema(self):
        """Test StoryPageBase schema validation."""
        # Valid data
        valid_data = {
            "page_number": 1,
            "text": "Once upon a time in space...",
            "base_image_key": "stories/123/page1.jpg",
            "personalized_image_key": "stories/123/personalized/page1.jpg"
        }
        
        page_base = StoryPageBase(**valid_data)
        assert page_base.page_number == 1
        assert page_base.text == "Once upon a time in space..."
        assert page_base.base_image_key == "stories/123/page1.jpg"
        assert page_base.personalized_image_key == "stories/123/personalized/page1.jpg"
        
        # Invalid data - negative page number
        invalid_data = valid_data.copy()
        invalid_data["page_number"] = -1
        
        with pytest.raises(ValidationError):
            StoryPageBase(**invalid_data)
    
    def test_story_page_create_schema(self):
        """Test StoryPageCreate schema validation."""
        # Valid data
        valid_data = {
            "story_id": str(uuid.uuid4()),
            "page_number": 1,
            "text": "Once upon a time in space..."
        }
        
        page_create = StoryPageCreate(**valid_data)
        assert page_create.story_id is not None
        assert page_create.page_number == 1
        
        # Test validation for text generation status
        invalid_status_data = valid_data.copy()
        invalid_status_data["text_generation_status"] = "invalid_status"
        
        with pytest.raises(ValidationError):
            StoryPageCreate(**invalid_status_data)
    
    def test_story_page_read_schema(self):
        """Test StoryPageRead schema."""
        # Create a valid story page response
        valid_data = {
            "id": str(uuid.uuid4()),
            "story_id": str(uuid.uuid4()),
            "page_number": 1,
            "text": "Once upon a time in space...",
            "base_image_key": "stories/123/page1.jpg",
            "personalized_image_key": "stories/123/personalized/page1.jpg",
            "text_generation_status": "completed",
            "image_generation_status": "completed",
            "personalization_status": "completed",
            "created_at": "2025-04-22T17:45:00Z",
            "updated_at": "2025-04-22T17:46:00Z"
        }
        
        page_read = StoryPageRead(**valid_data)
        assert page_read.id == valid_data["id"]
        assert page_read.story_id == valid_data["story_id"]
        assert page_read.page_number == 1
        assert page_read.text == "Once upon a time in space..."
        assert page_read.text_generation_status == "completed"