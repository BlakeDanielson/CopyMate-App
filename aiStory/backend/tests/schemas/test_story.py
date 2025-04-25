"""Tests for Story schemas."""
import uuid
import pytest
from datetime import datetime
from pydantic import ValidationError

# Import our schemas
from schemas.story import StoryBase, StoryCreate, StoryRead, StoryUpdate
from schemas.story_page import StoryPageRead


class TestStorySchema:
    """Test class for Story schemas."""
    
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
        
        # Test missing required fields
        invalid_data_missing = {
            "child_name": "Test Child"
            # Missing other required fields
        }
        
        with pytest.raises(ValidationError):
            StoryBase(**invalid_data_missing)
        
        # Test child_age validation
        invalid_age_too_young = valid_data.copy()
        invalid_age_too_young["child_age"] = 0
        
        with pytest.raises(ValidationError):
            StoryBase(**invalid_age_too_young)
        
        invalid_age_too_old = valid_data.copy()
        invalid_age_too_old["child_age"] = 18
        
        with pytest.raises(ValidationError):
            StoryBase(**invalid_age_too_old)
        
        # Test story_theme validation
        invalid_theme = valid_data.copy()
        invalid_theme["story_theme"] = "invalid_theme"
        
        with pytest.raises(ValidationError):
            StoryBase(**invalid_theme)
    
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
        assert str(story_create.user_id) == valid_data["user_id"]
        assert str(story_create.protagonist_photo_id) == valid_data["protagonist_photo_id"]
        assert story_create.child_name == "Test Child"
        assert story_create.child_age == 8
        assert story_create.story_theme == "space_adventure"
        assert story_create.title == "Space Journey"
        
        # Test missing required fields
        invalid_data_missing = {
            "child_name": "Test Child",
            "child_age": 8,
            "story_theme": "space_adventure"
            # Missing user_id and protagonist_photo_id
        }
        
        with pytest.raises(ValidationError):
            StoryCreate(**invalid_data_missing)
        
        # Test invalid UUID
        invalid_uuid = valid_data.copy()
        invalid_uuid["user_id"] = "not-a-uuid"
        
        with pytest.raises(ValidationError):
            StoryCreate(**invalid_uuid)
    
    def test_story_update_schema(self):
        """Test StoryUpdate schema validation."""
        # Valid data - partial update
        valid_data = {
            "title": "Updated Title",
            "status": "processing"
        }
        
        story_update = StoryUpdate(**valid_data)
        assert story_update.title == "Updated Title"
        assert story_update.status == "processing"
        
        # Test empty update (should be valid)
        empty_update = {}
        story_update = StoryUpdate(**empty_update)
        
        # Test invalid status value
        invalid_status = {
            "status": "invalid_status"
        }
        
        with pytest.raises(ValidationError):
            StoryUpdate(**invalid_status)
    
    def test_story_read_schema(self):
        """Test StoryRead schema."""
        # Create a valid story response with no pages
        story_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        photo_id = str(uuid.uuid4())
        
        valid_data = {
            "id": story_id,
            "user_id": user_id,
            "protagonist_photo_id": photo_id,
            "child_name": "Test Child",
            "child_age": 8,
            "story_theme": "space_adventure",
            "title": "Space Journey",
            "status": "pending",
            "error_message": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "pages": []
        }
        
        story_read = StoryRead(**valid_data)
        assert str(story_read.id) == story_id
        assert str(story_read.user_id) == user_id
        assert str(story_read.protagonist_photo_id) == photo_id
        assert story_read.child_name == "Test Child"
        assert story_read.child_age == 8
        assert story_read.story_theme == "space_adventure"
        assert story_read.title == "Space Journey"
        assert story_read.status == "pending"
        assert story_read.error_message is None
        assert len(story_read.pages) == 0
        
        # Create a valid story response with pages
        page_id = str(uuid.uuid4())
        valid_data_with_pages = valid_data.copy()
        valid_data_with_pages["pages"] = [
            {
                "id": page_id,
                "story_id": story_id,
                "page_number": 1,
                "text": "Once upon a time in space...",
                "base_image_key": "stories/123/page1.jpg",
                "personalized_image_key": "stories/123/personalized/page1.jpg",
                "text_generation_status": "completed",
                "image_generation_status": "completed",
                "personalization_status": "completed",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        story_read_with_pages = StoryRead(**valid_data_with_pages)
        assert len(story_read_with_pages.pages) == 1
        assert str(story_read_with_pages.pages[0].id) == page_id
        assert story_read_with_pages.pages[0].page_number == 1
        assert story_read_with_pages.pages[0].text == "Once upon a time in space..."
        
        # Test with invalid page data
        invalid_page_data = valid_data.copy()
        invalid_page_data["pages"] = [
            {
                "id": page_id,
                "story_id": story_id,
                "page_number": -1,  # Invalid page number
                "text": "Once upon a time in space..."
            }
        ]
        
        with pytest.raises(ValidationError):
            StoryRead(**invalid_page_data)