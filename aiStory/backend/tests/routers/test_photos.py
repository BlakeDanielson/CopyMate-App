"""Integration tests for photo API endpoints."""
import io
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.main import app
from backend.models.photo import Photo, PhotoStatus
from backend.models.user import User
from backend.schemas.photo_upload import PhotoUploadResponse
from backend.tests.test_database import test_db, test_engine, test_settings
from backend.utils.auth import create_access_token, get_password_hash


class TestPhotoEndpoints:
    """Integration tests for photo API endpoints."""
    
    # Test data
    TEST_PHOTO_FILENAME = "test_photo.jpg"
    TEST_PHOTO_CONTENT = b"dummy image content"
    TEST_PHOTO_MIMETYPE = "image/jpeg"
    
    async def create_test_user(self, test_db, role="user"):
        """Helper to create a test user with the specified role."""
        user = User(
            email=f"{role}@example.com",
            username=f"{role}user",
            hashed_password=get_password_hash("Password123!"),
            role=role
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user
    
    def create_token_for_user(self, user, expires_delta=None):
        """Helper to create an access token for a user."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=15)
        
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=expires_delta
        )
        return access_token
    
    async def create_test_photo(self, test_db, user_id):
        """Helper to create a test photo in the database."""
        photo = Photo(
            uuid="test-photo-uuid",
            user_id=user_id,
            original_filename=self.TEST_PHOTO_FILENAME,
            storage_provider="test_provider",
            bucket_name="test_bucket",
            storage_key="test_key",
            content_type=self.TEST_PHOTO_MIMETYPE,
            status=PhotoStatus.UPLOADED.value
        )
        test_db.add(photo)
        await test_db.commit()
        await test_db.refresh(photo)
        return photo
    
    @pytest.mark.asyncio
    async def test_upload_photo(self, test_db, monkeypatch):
        """Test successful photo upload endpoint."""
        # Create a user and get token
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        
        # Create test file
        test_file = io.BytesIO(self.TEST_PHOTO_CONTENT)
        
        # We need to mock the storage service to avoid actual uploads
        # This is a simplified mock that just returns success
        # In a real test, we'd use a more robust mocking approach
        from backend.services.photo.photo_service import PhotoServiceImpl
        original_upload_file = PhotoServiceImpl.upload_photo
        
        async def mock_upload_photo(*args, **kwargs):
            return PhotoUploadResponse(
                photo_id="test-photo-uuid",
                status=PhotoStatus.UPLOADED,
                message="Photo uploaded successfully"
            )
        
        # Apply the mock
        monkeypatch.setattr(PhotoServiceImpl, "upload_photo", mock_upload_photo)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/photos/upload",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"file": (self.TEST_PHOTO_FILENAME, test_file, self.TEST_PHOTO_MIMETYPE)},
                data={"description": "Test photo", "tags": "test,photo"}
            )
            
            # Restore original method
            monkeypatch.setattr(PhotoServiceImpl, "upload_photo", original_upload_file)
            
            # Verify response
            assert response.status_code == 201
            data = response.json()
            assert data["photo_id"] == "test-photo-uuid"
            assert data["status"] == PhotoStatus.UPLOADED.value
    
    @pytest.mark.asyncio
    async def test_get_photo_by_id(self, test_db, monkeypatch):
        """Test get photo by ID endpoint."""
        # Create a user and photo
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        photo = await self.create_test_photo(test_db, user.id)
        
        # We need to mock the storage service method that gets photo URLs
        from backend.services.storage.base import StorageService
        original_get_file_url = StorageService.get_file_url
        
        async def mock_get_file_url(*args, **kwargs):
            return "https://example.com/test-photo.jpg"
        
        # Apply the mock
        monkeypatch.setattr(StorageService, "get_file_url", mock_get_file_url)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/photos/{photo.uuid}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Restore original method
            monkeypatch.setattr(StorageService, "get_file_url", original_get_file_url)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == photo.uuid
            assert data["user_id"] == user.id
            assert data["status"] == PhotoStatus.UPLOADED.value
    
    @pytest.mark.asyncio
    async def test_list_photos(self, test_db):
        """Test list photos endpoint."""
        # Create a user and multiple photos
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        
        # Create multiple test photos
        for i in range(3):
            photo = Photo(
                uuid=f"test-photo-uuid-{i}",
                user_id=user.id,
                original_filename=f"test_photo_{i}.jpg",
                storage_provider="test_provider",
                bucket_name="test_bucket",
                storage_key=f"test_key_{i}",
                content_type=self.TEST_PHOTO_MIMETYPE,
                status=PhotoStatus.UPLOADED.value
            )
            test_db.add(photo)
        
        await test_db.commit()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/photos",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            
            # Test pagination
            response = await client.get(
                f"{settings.api_prefix}/photos?page=1&page_size=2",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify pagination
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
    
    @pytest.mark.asyncio
    async def test_delete_photo(self, test_db, monkeypatch):
        """Test delete photo endpoint."""
        # Create a user and photo
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        photo = await self.create_test_photo(test_db, user.id)
        
        # Mock the storage service delete method
        from backend.services.storage.base import StorageService
        original_delete_file = StorageService.delete_file
        
        async def mock_delete_file(*args, **kwargs):
            return True
        
        # Apply the mock
        monkeypatch.setattr(StorageService, "delete_file", mock_delete_file)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                f"{settings.api_prefix}/photos/{photo.uuid}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Restore original method
            monkeypatch.setattr(StorageService, "delete_file", original_delete_file)
            
            # Verify response
            assert response.status_code == 204
            
            # Verify photo is deleted from db
            result = await test_db.execute(select(Photo).where(Photo.uuid == photo.uuid))
            assert result.scalar_one_or_none() is None
    
    @pytest.mark.asyncio
    async def test_process_photo(self, test_db, monkeypatch):
        """Test process photo endpoint."""
        # Create a user and photo
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        photo = await self.create_test_photo(test_db, user.id)
        
        # Mock the storage service get_file_url method
        from backend.services.storage.base import StorageService
        original_get_file_url = StorageService.get_file_url
        
        async def mock_get_file_url(*args, **kwargs):
            return "https://example.com/test-photo-processed.jpg"
        
        # Apply the mock
        monkeypatch.setattr(StorageService, "get_file_url", mock_get_file_url)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.patch(
                f"{settings.api_prefix}/photos/{photo.uuid}/process",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Restore original method
            monkeypatch.setattr(StorageService, "get_file_url", original_get_file_url)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["photo_id"] == photo.uuid
            assert data["status"] == PhotoStatus.COMPLETED.value
            assert data["processed_url"] == "https://example.com/test-photo-processed.jpg"
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, test_db):
        """Test unauthorized access to photo endpoints."""
        # Create two users
        user1 = await self.create_test_user(test_db, "user1")
        user2 = await self.create_test_user(test_db, "user2")
        
        # Create token for user2
        access_token = self.create_token_for_user(user2)
        
        # Create photo for user1
        photo = await self.create_test_photo(test_db, user1.id)
        
        # Try to access user1's photo with user2's token
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/photos/{photo.uuid}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify forbidden
            assert response.status_code == 403
            
            # Try to delete user1's photo with user2's token
            response = await client.delete(
                f"{settings.api_prefix}/photos/{photo.uuid}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify forbidden
            assert response.status_code == 403
            
            # Try to process user1's photo with user2's token
            response = await client.patch(
                f"{settings.api_prefix}/photos/{photo.uuid}/process",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify forbidden
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_photo_not_found(self, test_db):
        """Test handling of non-existent photos."""
        # Create a user
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        
        # Non-existent photo ID
        non_existent_id = "non-existent-photo-uuid"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Try to get non-existent photo
            response = await client.get(
                f"{settings.api_prefix}/photos/{non_existent_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify not found
            assert response.status_code == 404
            
            # Try to delete non-existent photo
            response = await client.delete(
                f"{settings.api_prefix}/photos/{non_existent_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify not found
            assert response.status_code == 404
            
            # Try to process non-existent photo
            response = await client.patch(
                f"{settings.api_prefix}/photos/{non_existent_id}/process",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify not found
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, test_db, monkeypatch):
        """Test rate limiting for photo uploads."""
        # This test is a placeholder - in a real test environment,
        # you'd need a more sophisticated setup to properly test rate limiting
        
        # Mock limiter to force rate limit exceeded
        from fastapi import HTTPException, status
        from slowapi.errors import RateLimitExceeded
        
        # Create a user
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        
        # This is a simplified approach - in reality testing rate limiting
        # would require more sophisticated setup with the ability to
        # simulate multiple requests and track limiter state
        
        # For now, we'll just ensure the endpoint exists and returns expected status code
        # for a normal request (tested in test_upload_photo)
        
        # In a complete test, you would make multiple requests in quick succession
        # and verify that after N requests, you start getting 429 responses
        
    @pytest.mark.asyncio
    async def test_get_upload_url_unauthorized(self, test_db):
        """Test that the upload URL endpoint requires authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/photos/upload-url",
                json={"filename": "test.jpg", "content_type": "image/jpeg"}
            )
            # Verify unauthorized
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_upload_url_success(self, test_db, monkeypatch):
        """Test successful generation of a pre-signed upload URL."""
        # Create a user and get token
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        
        # We need to mock the storage service that generates pre-signed URLs
        from backend.services.storage.base import StorageService
        
        # Define the mock pre-signed URL
        mock_url = "https://storage.example.com/bucket-name/unique-object-key?signature=abc123"
        mock_fields = {
            "Content-Type": "image/jpeg",
            "x-amz-meta-user-id": str(user.id)
        }
        
        # Mock the generate_presigned_upload_url method
        async def mock_generate_url(*args, **kwargs):
            return {
                "url": mock_url,
                "fields": mock_fields
            }
        
        # Apply the mock
        monkeypatch.setattr(StorageService, "generate_presigned_upload_url", mock_generate_url)
        
        # Make request
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/photos/upload-url",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"filename": "test.jpg", "content_type": "image/jpeg"}
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert "upload_url" in data
            assert "photo_id" in data
            assert "object_key" in data
            assert "fields" in data
            assert data["upload_url"] == mock_url
            assert data["fields"] == mock_fields
            
            # Verify a photo record was created
            result = await test_db.execute(
                select(Photo).where(Photo.id == data["photo_id"])
            )
            photo = result.scalar_one_or_none()
            assert photo is not None
            assert photo.user_id == user.id
            assert photo.filename == "test.jpg"
            assert photo.content_type == "image/jpeg"
            assert photo.status == PhotoStatus.PENDING_UPLOAD.value
    
    @pytest.mark.asyncio
    async def test_get_upload_url_validation_failure(self, test_db):
        """Test validation failures when requesting an upload URL."""
        # Create a user and get token
        user = await self.create_test_user(test_db)
        access_token = self.create_token_for_user(user)
        
        # Test missing filename
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/photos/upload-url",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"content_type": "image/jpeg"}
            )
            # Verify bad request
            assert response.status_code in (400, 422)
        
        # Test missing content_type
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/photos/upload-url",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"filename": "test.jpg"}
            )
            # Verify bad request
            assert response.status_code in (400, 422)
        
        # Test invalid content_type
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"{settings.api_prefix}/photos/upload-url",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"filename": "test.jpg", "content_type": "invalid/type"}
            )
            # Verify bad request
            assert response.status_code in (400, 422)