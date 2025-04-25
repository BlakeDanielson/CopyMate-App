"""Tests for the Photo model."""
import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID

from backend.models.photo import Photo, PhotoStatus, AIProcessingStatus
from backend.models.user import User
from backend.schemas.photo import PhotoBase, PhotoCreate, PhotoRead, PhotoUpdate
from backend.tests.test_database import test_db

# Helper function for creating a test user
async def create_test_user(session):
    """Create and return a test user for use in tests."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="fakehashedpassword"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


class TestPhotoModel:
    """Test class for Photo model."""

    @pytest.mark.asyncio
    async def test_create_photo(self, test_db):
        """Test creating a Photo instance."""
        # Create a test user first
        user = await create_test_user(test_db)
        
        # Create a photo instance
        photo = Photo(
            user_id=user.id,
            storage_provider="s3",
            bucket="test-bucket",
            object_key="users/1234/photo123.jpg",
            filename="profile.jpg",
            content_type="image/jpeg"
        )
        
        test_db.add(photo)
        await test_db.commit()
        await test_db.refresh(photo)
        
        # Assertions
        assert photo.id is not None
        assert photo.user_id == user.id
        assert photo.storage_provider == "s3"
        assert photo.bucket == "test-bucket"
        assert photo.object_key == "users/1234/photo123.jpg"
        assert photo.filename == "profile.jpg"
        assert photo.content_type == "image/jpeg"
        assert photo.status == "pending_upload"  # Default status
        assert photo.ai_processing_status == "pending"  # Default status
        assert photo.created_at is not None
        assert photo.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_photo_user_relationship(self, test_db):
        """Test the relationship between Photo and User models."""
        # Create a test user
        user = await create_test_user(test_db)
        
        # Create a photo for the user
        photo = Photo(
            user_id=user.id,
            storage_provider="s3",
            bucket="test-bucket",
            object_key="users/1234/photo123.jpg",
            filename="profile.jpg",
            content_type="image/jpeg"
        )
        
        test_db.add(photo)
        await test_db.commit()
        
        # Test relationship - user to photos
        assert len(user.photos) == 1
        assert user.photos[0].id == photo.id
        
        # Test relationship - photo to user
        assert photo.user.id == user.id
    
    @pytest.mark.asyncio
    async def test_photo_required_fields(self, test_db):
        """Test that required fields are enforced."""
        # Attempt to create a photo without required fields
        photo = Photo()
        
        test_db.add(photo)
        
        # Expect an integrity error
        with pytest.raises(IntegrityError):
            await test_db.commit()
        
        await test_db.rollback()
    
    @pytest.mark.asyncio
    async def test_photo_ai_fields(self, test_db):
        """Test the AI-related fields."""
        # Create a test user
        user = await create_test_user(test_db)
        
        # Create a photo with AI data
        photo = Photo(
            user_id=user.id,
            storage_provider="s3",
            bucket="test-bucket",
            object_key="users/1234/photo123.jpg",
            filename="profile.jpg",
            content_type="image/jpeg",
            detected_objects={"objects": [{"name": "person", "confidence": 0.98}]},
            detected_labels={"labels": [{"name": "outdoors", "confidence": 0.85}]},
            face_details={"faces": [{"boundingBox": {"width": 0.5, "height": 0.5, "left": 0.25, "top": 0.25}}]},
            ai_processing_status="completed"
        )
        
        test_db.add(photo)
        await test_db.commit()
        await test_db.refresh(photo)
        
        # Assertions for AI fields
        assert photo.detected_objects["objects"][0]["name"] == "person"
        assert photo.detected_labels["labels"][0]["name"] == "outdoors"
        assert photo.face_details["faces"][0]["boundingBox"]["width"] == 0.5
        assert photo.ai_processing_status == "completed"


class TestPhotoSchema:
    """Test class for Photo Pydantic schemas."""
    
    def test_photo_base_schema(self):
        """Test PhotoBase schema validation."""
        # Valid data
        valid_data = {
            "storage_provider": "s3",
            "bucket": "test-bucket",
            "object_key": "users/1234/photo123.jpg",
            "filename": "profile.jpg",
            "content_type": "image/jpeg"
        }
        
        photo_base = PhotoBase(**valid_data)
        assert photo_base.storage_provider == "s3"
        assert photo_base.bucket == "test-bucket"
        assert photo_base.object_key == "users/1234/photo123.jpg"
        assert photo_base.filename == "profile.jpg"
        assert photo_base.content_type == "image/jpeg"
        
        # Invalid data - missing required fields
        invalid_data = {
            "storage_provider": "s3",
            # Missing other required fields
        }
        
        with pytest.raises(ValidationError):
            PhotoBase(**invalid_data)
    
    def test_photo_create_schema(self):
        """Test PhotoCreate schema validation."""
        # Valid data
        valid_data = {
            "storage_provider": "s3",
            "bucket": "test-bucket",
            "object_key": "users/1234/photo123.jpg",
            "filename": "profile.jpg",
            "content_type": "image/jpeg",
            "user_id": str(uuid.uuid4())
        }
        
        photo_create = PhotoCreate(**valid_data)
        assert photo_create.storage_provider == "s3"
        assert photo_create.user_id is not None
        
        # Test validation for storage provider
        invalid_provider_data = valid_data.copy()
        invalid_provider_data["storage_provider"] = "invalid_provider"
        
        with pytest.raises(ValidationError):
            PhotoCreate(**invalid_provider_data)
        
        # Test validation for content type
        invalid_content_type = valid_data.copy()
        invalid_content_type["content_type"] = "application/pdf"
        
        with pytest.raises(ValidationError):
            PhotoCreate(**invalid_content_type)
    
    def test_photo_update_schema(self):
        """Test PhotoUpdate schema validation."""
        # Valid data - only updating status
        valid_data = {
            "status": "uploaded"
        }
        
        photo_update = PhotoUpdate(**valid_data)
        assert photo_update.status == PhotoStatus.UPLOADED
        
        # Invalid data - invalid status value
        invalid_data = {
            "status": "invalid_status"  # Not a valid status
        }
        
        with pytest.raises(ValidationError):
            PhotoUpdate(**invalid_data)
    
    def test_photo_read_schema(self):
        """Test PhotoRead schema."""
        # Create a valid photo response
        valid_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "storage_provider": "s3",
            "bucket": "test-bucket",
            "object_key": "users/1234/photo123.jpg",
            "filename": "profile.jpg",
            "content_type": "image/jpeg",
            "status": "pending_upload",
            "ai_processing_status": "pending",
            "detected_objects": {"objects": [{"name": "person", "confidence": 0.98}]},
            "detected_labels": {"labels": [{"name": "outdoors", "confidence": 0.85}]},
            "face_details": {"faces": [{"boundingBox": {"width": 0.5, "height": 0.5, "left": 0.25, "top": 0.25}}]},
            "created_at": "2025-04-22T17:45:00Z",
            "updated_at": "2025-04-22T17:46:00Z"
        }
        
        photo_read = PhotoRead(**valid_data)
        assert photo_read.id == valid_data["id"]
        assert photo_read.user_id == valid_data["user_id"]
        assert photo_read.storage_provider == valid_data["storage_provider"]
        assert photo_read.status == PhotoStatus.PENDING_UPLOAD
        assert photo_read.detected_objects["objects"][0]["name"] == "person"