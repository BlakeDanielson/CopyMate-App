"""Tests for the LocalStorageService class."""

import io
import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch

from backend.config import Settings
from backend.services.storage.base import StorageError
from backend.services.storage.local_storage import LocalStorageService


@pytest.fixture
def settings():
    """Fixture for settings with local storage configuration."""
    test_storage_path = Path("./test_uploads").resolve()
    settings = Settings()
    settings.storage_backend = "local"
    settings.storage_local_path = str(test_storage_path)
    return settings


@pytest.fixture
def storage_service(settings):
    """Fixture for a LocalStorageService instance."""
    # Create a fresh test directory
    test_storage_path = Path(settings.storage_local_path).resolve()
    if test_storage_path.exists():
        shutil.rmtree(test_storage_path)
    os.makedirs(test_storage_path, exist_ok=True)
    
    service = LocalStorageService(settings)
    
    yield service
    
    # Clean up after tests
    if test_storage_path.exists():
        shutil.rmtree(test_storage_path)


@pytest.mark.asyncio
async def test_upload_file(storage_service):
    """Test uploading a file to local storage."""
    # Create a test file
    file_content = b"Test file content"
    file = io.BytesIO(file_content)
    
    # Generate a test key
    key = storage_service.generate_key(1, "test.txt")
    
    # Upload the file
    url = await storage_service.upload_file(file, key)
    
    # Check that the file exists
    file_path = Path(storage_service.storage_path) / key
    assert file_path.exists()
    
    # Check that the content was correctly written
    with open(file_path, "rb") as f:
        stored_content = f.read()
    assert stored_content == file_content
    
    # Check that the URL is correct
    assert url == f"/uploads/{key}"


@pytest.mark.asyncio
async def test_file_exists(storage_service):
    """Test checking if a file exists."""
    # Generate a test key
    key = storage_service.generate_key(1, "test.txt")
    file_path = Path(storage_service.storage_path) / key
    
    # File should not exist initially
    assert not await storage_service.file_exists(key)
    
    # Create the file
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, "w") as f:
        f.write("Test content")
    
    # Now the file should exist
    assert await storage_service.file_exists(key)


@pytest.mark.asyncio
async def test_get_file_url(storage_service):
    """Test getting a URL for a file."""
    # Generate a test key
    key = storage_service.generate_key(1, "test.txt")
    file_path = Path(storage_service.storage_path) / key
    
    # Create the file
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, "w") as f:
        f.write("Test content")
    
    # Get the URL
    url = await storage_service.get_file_url(key)
    
    # Check that the URL is correct
    assert url == f"/uploads/{key}"


@pytest.mark.asyncio
async def test_get_file_url_not_found(storage_service):
    """Test getting a URL for a non-existent file."""
    key = "non-existent-file.txt"
    
    # Attempt to get the URL should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        await storage_service.get_file_url(key)


@pytest.mark.asyncio
async def test_delete_file(storage_service):
    """Test deleting a file."""
    # Generate a test key
    key = storage_service.generate_key(1, "test.txt")
    file_path = Path(storage_service.storage_path) / key
    
    # Create the file
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, "w") as f:
        f.write("Test content")
    
    # Delete the file
    result = await storage_service.delete_file(key)
    
    # Check that the operation was successful
    assert result is True
    
    # Check that the file no longer exists
    assert not file_path.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_file(storage_service):
    """Test deleting a non-existent file."""
    key = "non-existent-file.txt"
    
    # Attempt to delete the file should return False
    result = await storage_service.delete_file(key)
    assert result is False


def test_generate_key(storage_service):
    """Test generating a storage key."""
    user_id = 1
    filename = "test.jpg"
    
    key = storage_service.generate_key(user_id, filename)
    
    # Check key format and properties
    assert str(user_id) in key
    assert key.endswith(".jpg")
    assert "/" in key  # Should include a date component