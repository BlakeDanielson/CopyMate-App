"""Tests for the photo service."""
import asyncio
import io
import uuid
from datetime import datetime
from typing import Any, Dict
from unittest import mock

import pytest
from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.photo import Photo, PhotoStatus
from backend.repositories.photo_repository import PhotoRepository
from backend.schemas.photo_upload import PhotoUploadForm
from backend.services.photo.exceptions import (
    InvalidPhotoError, 
    PhotoNotFoundError, 
    PhotoQuotaExceededError, 
    PhotoUploadError
)
from backend.services.photo.photo_service import PhotoServiceImpl
from backend.services.storage.base import StorageService


# Test data
TEST_USER_ID = 1
TEST_PHOTO_ID = str(uuid.uuid4())
TEST_FILENAME = "test_photo.jpg"
TEST_CONTENT_TYPE = "image/jpeg"
TEST_STORAGE_KEY = f"user_{TEST_USER_ID}/{TEST_PHOTO_ID}/{TEST_FILENAME}"


@pytest.fixture
def mock_photo_repository():
    """Create a mock photo repository."""
    repo = mock.AsyncMock(spec=PhotoRepository)
    return repo


@pytest.fixture
def mock_storage_service():
    """Create a mock storage service."""
    service = mock.AsyncMock(spec=StorageService)
    service.generate_key.return_value = TEST_STORAGE_KEY
    service.upload_file.return_value = f"https://example.com/{TEST_STORAGE_KEY}"
    service.get_file_url.return_value = f"https://example.com/{TEST_STORAGE_KEY}"
    return service


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return mock.AsyncMock(spec=AsyncSession)


@pytest.fixture
def photo_service(mock_photo_repository, mock_storage_service):
    """Create a photo service instance with mocked dependencies."""
    settings = mock.MagicMock()
    settings.storage_backend = "test"
    settings.storage_s3_bucket = "test-bucket"
    
    service = PhotoServiceImpl(
        photo_repository=mock_photo_repository,
        storage_service=mock_storage_service,
        settings=settings
    )
    return service


@pytest.fixture
def sample_photo():
    """Create a sample photo entity."""
    return Photo(
        id=1,
        uuid=TEST_PHOTO_ID,
        user_id=TEST_USER_ID,
        storage_provider="test",
        bucket_name="test-bucket",
        storage_key=TEST_STORAGE_KEY,
        original_filename=TEST_FILENAME,
        content_type=TEST_CONTENT_TYPE,
        status=PhotoStatus.UPLOADED.value,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_upload_form():
    """Create a mock upload form."""
    file = mock.AsyncMock(spec=UploadFile)
    file.filename = TEST_FILENAME
    file.content_type = TEST_CONTENT_TYPE
    
    # Mock the read method to return some binary data
    async def mock_read():
        return b"test file content"
    
    file.read.side_effect = mock_read
    
    # Create an actual PhotoUploadForm with the mocked file
    form = PhotoUploadForm(file=file)
    
    # Mock the validate method
    async def mock_validate():
        return None
    
    form.validate = mock_validate
    
    return form


@pytest.mark.asyncio
async def test_upload_photo_success(
    photo_service, mock_db_session, mock_upload_form, mock_photo_repository, sample_photo
):
    """Test successful photo upload."""
    # Setup
    mock_photo_repository.count_by_user_id.return_value = 5  # Below quota
    mock_photo_repository.create.return_value = sample_photo
    mock_photo_repository.update_status.return_value = sample_photo
    
    # Execute
    result = await photo_service.upload_photo(
        db=mock_db_session,
        user_id=TEST_USER_ID,
        upload_form=mock_upload_form
    )
    
    # Assert
    assert result.photo_id == TEST_PHOTO_ID
    assert result.status == PhotoStatus.UPLOADED
    mock_photo_repository.create.assert_called_once()
    mock_photo_repository.update_status.assert_called_once()


@pytest.mark.asyncio
async def test_upload_photo_quota_exceeded(
    photo_service, mock_db_session, mock_upload_form, mock_photo_repository
):
    """Test photo upload with quota exceeded."""
    # Setup
    mock_photo_repository.count_by_user_id.return_value = 100  # At quota limit
    
    # Execute & Assert
    with pytest.raises(PhotoQuotaExceededError):
        await photo_service.upload_photo(
            db=mock_db_session,
            user_id=TEST_USER_ID,
            upload_form=mock_upload_form
        )


@pytest.mark.asyncio
async def test_upload_photo_storage_error(
    photo_service, mock_db_session, mock_upload_form, mock_photo_repository, 
    mock_storage_service, sample_photo
):
    """Test photo upload with storage error."""
    # Setup
    mock_photo_repository.count_by_user_id.return_value = 5  # Below quota
    mock_photo_repository.create.return_value = sample_photo
    mock_photo_repository.get_by_uuid.return_value = sample_photo
    
    # Make the storage service throw an error
    mock_storage_service.upload_file.side_effect = Exception("Storage error")
    
    # Execute & Assert
    with pytest.raises(PhotoUploadError):
        await photo_service.upload_photo(
            db=mock_db_session,
            user_id=TEST_USER_ID,
            upload_form=mock_upload_form
        )
    
    # Verify the photo status was updated to FAILED
    mock_photo_repository.update_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_photo_by_id_success(
    photo_service, mock_db_session, mock_photo_repository, sample_photo
):
    """Test getting a photo by ID successfully."""
    # Setup
    mock_photo_repository.get_by_uuid.return_value = sample_photo
    
    # Execute
    result = await photo_service.get_photo_by_id(
        db=mock_db_session,
        photo_id=TEST_PHOTO_ID
    )
    
    # Assert
    assert result.id == TEST_PHOTO_ID
    assert result.user_id == TEST_USER_ID
    mock_photo_repository.get_by_uuid.assert_called_once_with(mock_db_session, TEST_PHOTO_ID)


@pytest.mark.asyncio
async def test_get_photo_by_id_not_found(
    photo_service, mock_db_session, mock_photo_repository
):
    """Test getting a photo by ID that doesn't exist."""
    # Setup
    mock_photo_repository.get_by_uuid.return_value = None
    
    # Execute & Assert
    with pytest.raises(PhotoNotFoundError):
        await photo_service.get_photo_by_id(
            db=mock_db_session,
            photo_id=TEST_PHOTO_ID
        )


@pytest.mark.asyncio
async def test_get_photos_by_user(
    photo_service, mock_db_session, mock_photo_repository, sample_photo
):
    """Test getting photos by user."""
    # Setup
    mock_photo_repository.list_by_user_id.return_value = [sample_photo, sample_photo]
    
    # Execute
    results = await photo_service.get_photos_by_user(
        db=mock_db_session,
        user_id=TEST_USER_ID
    )
    
    # Assert
    assert len(results) == 2
    assert results[0].id == TEST_PHOTO_ID
    assert results[1].id == TEST_PHOTO_ID
    mock_photo_repository.list_by_user_id.assert_called_once()


@pytest.mark.asyncio
async def test_delete_photo_success(
    photo_service, mock_db_session, mock_photo_repository, 
    mock_storage_service, sample_photo
):
    """Test deleting a photo successfully."""
    # Setup
    mock_photo_repository.get_by_uuid.return_value = sample_photo
    
    # Execute
    result = await photo_service.delete_photo(
        db=mock_db_session,
        photo_id=TEST_PHOTO_ID,
        user_id=TEST_USER_ID
    )
    
    # Assert
    assert result is True
    mock_storage_service.delete_file.assert_called_once_with(TEST_STORAGE_KEY)
    mock_photo_repository.delete.assert_called_once_with(mock_db_session, sample_photo.id)


@pytest.mark.asyncio
async def test_delete_photo_not_found(
    photo_service, mock_db_session, mock_photo_repository
):
    """Test deleting a photo that doesn't exist."""
    # Setup
    mock_photo_repository.get_by_uuid.return_value = None
    
    # Execute & Assert
    with pytest.raises(PhotoNotFoundError):
        await photo_service.delete_photo(
            db=mock_db_session,
            photo_id=TEST_PHOTO_ID,
            user_id=TEST_USER_ID
        )


@pytest.mark.asyncio
async def test_delete_photo_unauthorized(
    photo_service, mock_db_session, mock_photo_repository, sample_photo
):
    """Test deleting a photo with incorrect user ID."""
    # Setup
    mock_photo_repository.get_by_uuid.return_value = sample_photo
    
    # Execute & Assert
    with pytest.raises(PermissionError):
        await photo_service.delete_photo(
            db=mock_db_session,
            photo_id=TEST_PHOTO_ID,
            user_id=999  # Different user ID
        )


@pytest.mark.asyncio
async def test_update_photo_status(
    photo_service, mock_db_session, mock_photo_repository, sample_photo
):
    """Test updating a photo's status."""
    # Setup
    updated_photo = sample_photo
    updated_photo.status = PhotoStatus.PROCESSING.value
    mock_photo_repository.update_status_by_uuid.return_value = updated_photo
    
    # Execute
    result = await photo_service.update_photo_status(
        db=mock_db_session,
        photo_id=TEST_PHOTO_ID,
        status=PhotoStatus.PROCESSING
    )
    
    # Assert
    assert result.status == PhotoStatus.PROCESSING
    mock_photo_repository.update_status_by_uuid.assert_called_once_with(
        mock_db_session, TEST_PHOTO_ID, PhotoStatus.PROCESSING
    )


@pytest.mark.asyncio
async def test_process_photo(
    photo_service, mock_db_session, mock_photo_repository, 
    mock_storage_service, sample_photo
):
    """Test processing a photo."""
    # Setup
    processing_photo = sample_photo
    processing_photo.status = PhotoStatus.PROCESSING.value
    
    completed_photo = sample_photo
    completed_photo.status = PhotoStatus.COMPLETED.value
    
    mock_photo_repository.get_by_uuid.return_value = sample_photo
    mock_photo_repository.update_status_by_uuid.side_effect = [
        processing_photo,  # First call for PROCESSING
        completed_photo    # Second call for COMPLETED
    ]
    
    # Replace asyncio.sleep to avoid waiting in the test
    with mock.patch('asyncio.sleep', return_value=None):
        # Execute
        result = await photo_service.process_photo(
            db=mock_db_session,
            photo_id=TEST_PHOTO_ID
        )
    
    # Assert
    assert result.photo_id == TEST_PHOTO_ID
    assert result.status == PhotoStatus.COMPLETED
    assert result.processed_url == f"https://example.com/{TEST_STORAGE_KEY}"
    mock_photo_repository.update_status_by_uuid.assert_called_with(
        mock_db_session, TEST_PHOTO_ID, PhotoStatus.COMPLETED
    )


@pytest.mark.asyncio
async def test_get_photo_url(
    photo_service, mock_db_session, mock_photo_repository, 
    mock_storage_service, sample_photo
):
    """Test getting a photo URL."""
    # Setup
    mock_photo_repository.get_by_uuid.return_value = sample_photo
    
    # Execute
    url = await photo_service.get_photo_url(
        db=mock_db_session,
        photo_id=TEST_PHOTO_ID
    )
    
    # Assert
    assert url == f"https://example.com/{TEST_STORAGE_KEY}"
    mock_storage_service.get_file_url.assert_called_once_with(TEST_STORAGE_KEY, None)


@pytest.mark.asyncio
async def test_start_processing_photo_async(
    photo_service, mock_db_session, mock_photo_repository, sample_photo
):
    """Test starting asynchronous photo processing."""
    # Setup
    mock_photo_repository.get_by_uuid.return_value = sample_photo
    background_tasks = mock.MagicMock(spec=BackgroundTasks)
    
    # Execute
    await photo_service.start_processing_photo_async(
        db=mock_db_session,
        photo_id=TEST_PHOTO_ID,
        background_tasks=background_tasks
    )
    
    # Assert
    background_tasks.add_task.assert_called_once()
    assert background_tasks.add_task.call_args[0][0] == photo_service._process_photo_background_task
    assert background_tasks.add_task.call_args[0][1] == TEST_PHOTO_ID