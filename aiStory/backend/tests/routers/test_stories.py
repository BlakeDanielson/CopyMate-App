"""Tests for story creation endpoints."""
import json
import uuid
from datetime import datetime
from unittest import mock
from typing import Dict, Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.main import app
from backend.models.user import User
from backend.models.photo import Photo
from backend.models.story import Story, StoryStatus
from backend.schemas.story import StoryTheme
from backend.tests.test_database import test_db, test_engine, test_settings
from backend.utils.auth import create_access_token, get_password_hash


class TestStoryEndpoints:
    """Tests for story creation and retrieval endpoints."""
    
    async def create_test_user(self, test_db):
        """Helper to create a test user."""
        user = User(
            email="testuser@example.com",
            username="testuser",
            hashed_password=get_password_hash("Password123!"),
            role="user"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user
    
    async def create_test_photo(self, test_db, user_id):
        """Helper to create a test photo for the user."""
        photo = Photo(
            user_id=user_id,
            filename="test_photo.jpg",
            storage_key="test_key",
            bucket_name="test_bucket",
            storage_provider="local",
            status="uploaded",
            ai_processing_status="completed"  # Photo should be processed to use in story
        )
        test_db.add(photo)
        await test_db.commit()
        await test_db.refresh(photo)
        return photo
    
    def create_token_for_user(self, user):
        """Helper to create an access token for a user."""
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )
        return access_token
    
    @pytest.mark.asyncio
    async def test_create_story_unauthorized(self, test_db):
        """Test that story creation requires authentication."""
        story_data = {
            "child_name": "Alex",
            "child_age": 5,
            "story_theme": StoryTheme.SPACE_ADVENTURE.value,
            "protagonist_photo_id": str(uuid.uuid4())
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/stories",
                json=story_data
            )
            
            # Verify unauthorized response
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_story_invalid_data(self, test_db):
        """Test that story creation validates input data."""
        # Create a user and get token
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        
        # Missing required fields
        invalid_data = {
            "child_name": "Alex",
            # Missing child_age
            "story_theme": StoryTheme.SPACE_ADVENTURE.value,
            # Missing protagonist_photo_id
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/stories",
                json=invalid_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify validation error
            assert response.status_code == 422
            assert "validation error" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_create_story_invalid_theme(self, test_db):
        """Test that story creation validates the theme."""
        # Create a user and get token
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        photo = await self.create_test_photo(test_db, user.id)
        
        # Invalid theme
        invalid_data = {
            "child_name": "Alex",
            "child_age": 5,
            "story_theme": "invalid_theme",
            "protagonist_photo_id": str(photo.id)
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/stories",
                json=invalid_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify validation error
            assert response.status_code == 422
            assert "invalid theme" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_create_story_invalid_photo_id(self, test_db):
        """Test that story creation validates the photo ID belongs to the user."""
        # Create a user and get token
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        
        # Create another user with a photo
        other_user = User(
            email="otheruser@example.com",
            username="otheruser",
            hashed_password=get_password_hash("Password123!"),
            role="user"
        )
        test_db.add(other_user)
        await test_db.commit()
        await test_db.refresh(other_user)
        
        other_photo = await self.create_test_photo(test_db, other_user.id)
        
        # Try to use another user's photo
        story_data = {
            "child_name": "Alex",
            "child_age": 5,
            "story_theme": StoryTheme.SPACE_ADVENTURE.value,
            "protagonist_photo_id": str(other_photo.id)
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/stories",
                json=story_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify forbidden response
            assert response.status_code == 403
            assert "access denied" in response.text.lower() or "not authorized" in response.text.lower()
    
    @pytest.mark.asyncio
    @mock.patch("backend.routers.stories.generate_story.delay")
    async def test_create_story_success(self, mock_generate_story, test_db):
        """Test successful story creation with all required fields."""
        # Create a user and get token
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        photo = await self.create_test_photo(test_db, user.id)
        
        # Valid story data
        story_data = {
            "child_name": "Alex",
            "child_age": 5,
            "story_theme": StoryTheme.SPACE_ADVENTURE.value,
            "protagonist_photo_id": str(photo.id)
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/stories",
                json=story_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify success response
            assert response.status_code == 202
            data = response.json()
            
            # Verify response structure
            assert "id" in data
            assert data["user_id"] == str(user.id)
            assert data["child_name"] == story_data["child_name"]
            assert data["child_age"] == story_data["child_age"]
            assert data["story_theme"] == story_data["story_theme"]
            assert data["protagonist_photo_id"] == story_data["protagonist_photo_id"]
            assert data["status"] == StoryStatus.PENDING.value
            assert "created_at" in data
            assert "updated_at" in data
            assert "message" in data
            
            # Verify story was saved to database
            statement = select(Story).where(Story.id == uuid.UUID(data["id"]))
            result = await test_db.execute(statement)
            story = result.scalar_one_or_none()
            
            assert story is not None
            assert story.user_id == user.id
            assert story.child_name == story_data["child_name"]
            assert story.child_age == story_data["child_age"]
            assert story.story_theme == story_data["story_theme"]
            assert story.protagonist_photo_id == uuid.UUID(story_data["protagonist_photo_id"])
            assert story.status == StoryStatus.PENDING.value
            
            # Check that the Celery task was called to start story generation
            mock_generate_story.assert_called_once()
            args = mock_generate_story.call_args[0]
            # First argument should be the story ID as a string
            assert args[0] == data["id"]