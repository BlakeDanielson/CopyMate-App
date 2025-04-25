"""Tests for StoryPage schemas."""
import uuid
import pytest
from datetime import datetime
from pydantic import ValidationError

# Import our schemas
from schemas.story_page import (
    StoryPageBase,
    StoryPageCreate,
    StoryPageRead,
    StoryPageUpdate
)


class TestStoryPageSchema:
    """Test class for StoryPage schemas."""
    
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
        
        # Test validation for page number
        invalid_page_number_negative = valid_data.copy()
        invalid_page_number_negative["page_number"] = -1
        
        with pytest.raises(ValidationError):
            StoryPageBase(**invalid_page_number_negative)
            
        invalid_page_number_zero = valid_data.copy()
        invalid_page_number_zero["page_number"] = 0
        
        with pytest.raises(ValidationError):
            StoryPageBase(**invalid_page_number_zero)
        
        # Valid with minimal data
        minimal_data = {
            "page_number": 1,
        }
        
        minimal_page = StoryPageBase(**minimal_data)
        assert minimal_page.page_number == 1
        assert minimal_page.text is None
        assert minimal_page.base_image_key is None
        assert minimal_page.personalized_image_key is None
    
    def test_story_page_create_schema(self):
        """Test StoryPageCreate schema validation."""
        story_id = str(uuid.uuid4())
        
        # Valid data
        valid_data = {
            "story_id": story_id,
            "page_number": 1,
            "text": "Once upon a time in space...",
            "base_image_key": "stories/123/page1.jpg",
            "text_generation_status": "completed"
        }
        
        page_create = StoryPageCreate(**valid_data)
        assert str(page_create.story_id) == story_id
        assert page_create.page_number == 1
        assert page_create.text == "Once upon a time in space..."
        assert page_create.base_image_key == "stories/123/page1.jpg"
        assert page_create.text_generation_status == "completed"
        
        # Test missing required fields
        invalid_data_missing = {
            "page_number": 1,
            # Missing story_id which is required
        }
        
        with pytest.raises(ValidationError):
            StoryPageCreate(**invalid_data_missing)
        
        # Test invalid UUID
        invalid_uuid = valid_data.copy()
        invalid_uuid["story_id"] = "not-a-uuid"
        
        with pytest.raises(ValidationError):
            StoryPageCreate(**invalid_uuid)
        
        # Test invalid status value
        invalid_status = valid_data.copy()
        invalid_status["text_generation_status"] = "invalid_status"
        
        with pytest.raises(ValidationError):
            StoryPageCreate(**invalid_status)
    
    def test_story_page_update_schema(self):
        """Test StoryPageUpdate schema validation."""
        # Valid data - partial update
        valid_data = {
            "text": "Updated text content",
            "personalized_image_key": "stories/123/updated/page1.jpg",
            "text_generation_status": "completed"
        }
        
        page_update = StoryPageUpdate(**valid_data)
        assert page_update.text == "Updated text content"
        assert page_update.personalized_image_key == "stories/123/updated/page1.jpg"
        assert page_update.text_generation_status == "completed"
        
        # Test empty update (should be valid)
        empty_update = {}
        page_update = StoryPageUpdate(**empty_update)
        
        # Test invalid status values
        invalid_status = {
            "text_generation_status": "invalid_status"
        }
        
        with pytest.raises(ValidationError):
            StoryPageUpdate(**invalid_status)
            
        invalid_image_status = {
            "image_generation_status": "invalid_status"
        }
        
        with pytest.raises(ValidationError):
            StoryPageUpdate(**invalid_image_status)
            
        invalid_personalization_status = {
            "personalization_status": "invalid_status"
        }
        
        with pytest.raises(ValidationError):
            StoryPageUpdate(**invalid_personalization_status)
    
    def test_story_page_read_schema(self):
        """Test StoryPageRead schema."""
        # Create a valid story page response
        page_id = str(uuid.uuid4())
        story_id = str(uuid.uuid4())
        
        valid_data = {
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
        
        page_read = StoryPageRead(**valid_data)
        assert str(page_read.id) == page_id
        assert str(page_read.story_id) == story_id
        assert page_read.page_number == 1
        assert page_read.text == "Once upon a time in space..."
        assert page_read.base_image_key == "stories/123/page1.jpg"
        assert page_read.personalized_image_key == "stories/123/personalized/page1.jpg"
        assert page_read.text_generation_status == "completed"
        assert page_read.image_generation_status == "completed"
        assert page_read.personalization_status == "completed"
        
        # Test with minimal valid data
        minimal_data = {
            "id": page_id,
            "story_id": story_id,
            "page_number": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        minimal_page_read = StoryPageRead(**minimal_data)
        assert str(minimal_page_read.id) == page_id
        assert str(minimal_page_read.story_id) == story_id
        assert minimal_page_read.page_number == 1
        assert minimal_page_read.text is None
        assert minimal_page_read.base_image_key is None
        assert minimal_page_read.personalized_image_key is None
        assert minimal_page_read.text_generation_status == "pending"  # Default value
        
        # Test with invalid data
        invalid_data = valid_data.copy()
        invalid_data["page_number"] = -1  # Invalid page number
        
        with pytest.raises(ValidationError):
            StoryPageRead(**invalid_data)