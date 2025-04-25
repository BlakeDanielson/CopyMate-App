"""Tests for the S3StorageService class."""

import io
import pytest
import boto3
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from backend.config import Settings
from backend.services.storage.base import StorageError
from backend.services.storage.s3_storage import S3StorageService


@pytest.fixture
def settings():
    """Fixture for settings with S3 storage configuration."""
    settings = Settings()
    settings.storage_backend = "s3"
    settings.storage_s3_bucket = "test-bucket"
    settings.storage_s3_region = "us-east-1"
    return settings


@pytest.fixture
def mock_s3_client():
    """Fixture for a mocked S3 client."""
    with patch("boto3.client") as mock_boto3_client:
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def storage_service(settings, mock_s3_client):
    """Fixture for an S3StorageService instance with mocked S3 client."""
    service = S3StorageService(settings)
    # The service's s3_client is already mocked through the mock_s3_client fixture
    return service


@pytest.mark.asyncio
async def test_upload_file(storage_service, mock_s3_client):
    """Test uploading a file to S3."""
    # Create a test file
    file_content = b"Test file content"
    file = io.BytesIO(file_content)
    
    # Generate a test key
    key = storage_service.generate_key(1, "test.txt")
    
    # Set up mock for file_exists check and presigned URL generation
    mock_s3_client.head_object.return_value = {}  # File exists
    mock_s3_client.generate_presigned_url.return_value = f"https://test-bucket.s3.amazonaws.com/{key}"
    
    # Upload the file
    url = await storage_service.upload_file(file, key, {"user_id": "1"}, "text/plain")
    
    # Verify that the upload was called with the correct arguments
    mock_s3_client.upload_fileobj.assert_called_once()
    # Extract call arguments
    call_args = mock_s3_client.upload_fileobj.call_args[0]
    call_kwargs = mock_s3_client.upload_fileobj.call_args[1]
    
    # Check call arguments
    assert call_args[0] == file
    assert call_args[1] == "test-bucket"
    assert call_args[2] == key
    assert call_kwargs["ExtraArgs"]["Metadata"] == {"user_id": "1"}
    assert call_kwargs["ExtraArgs"]["ContentType"] == "text/plain"
    
    # Check the returned URL
    assert url == f"https://test-bucket.s3.amazonaws.com/{key}"


@pytest.mark.asyncio
async def test_file_exists_true(storage_service, mock_s3_client):
    """Test checking if a file exists in S3 (file exists)."""
    key = "test.txt"
    
    # Mock successful head_object response
    mock_s3_client.head_object.return_value = {}
    
    # Check if file exists
    exists = await storage_service.file_exists(key)
    
    # Verify the head_object call
    mock_s3_client.head_object.assert_called_with(
        Bucket="test-bucket",
        Key=key
    )
    
    # File should exist
    assert exists is True


@pytest.mark.asyncio
async def test_file_exists_false(storage_service, mock_s3_client):
    """Test checking if a file exists in S3 (file doesn't exist)."""
    key = "test.txt"
    
    # Mock 404 response for head_object
    error_response = {
        "Error": {
            "Code": "404",
            "Message": "Not Found"
        }
    }
    mock_s3_client.head_object.side_effect = ClientError(error_response, "HeadObject")
    
    # Check if file exists
    exists = await storage_service.file_exists(key)
    
    # Verify the head_object call
    mock_s3_client.head_object.assert_called_with(
        Bucket="test-bucket",
        Key=key
    )
    
    # File should not exist
    assert exists is False


@pytest.mark.asyncio
async def test_file_exists_error(storage_service, mock_s3_client):
    """Test checking if a file exists in S3 (error case)."""
    key = "test.txt"
    
    # Mock an error that is not a 404
    error_response = {
        "Error": {
            "Code": "403",
            "Message": "Forbidden"
        }
    }
    mock_s3_client.head_object.side_effect = ClientError(error_response, "HeadObject")
    
    # Check should raise StorageError
    with pytest.raises(StorageError):
        await storage_service.file_exists(key)


@pytest.mark.asyncio
async def test_get_file_url(storage_service, mock_s3_client):
    """Test getting a URL for a file in S3."""
    key = "test.txt"
    expected_url = f"https://test-bucket.s3.amazonaws.com/{key}"
    
    # Mock the file_exists check and presigned URL generation
    mock_s3_client.head_object.return_value = {}  # File exists
    mock_s3_client.generate_presigned_url.return_value = expected_url
    
    # Get the URL
    url = await storage_service.get_file_url(key)
    
    # Verify the generate_presigned_url call
    mock_s3_client.generate_presigned_url.assert_called_with(
        'get_object',
        Params={
            'Bucket': "test-bucket",
            'Key': key
        },
        ExpiresIn=3600
    )
    
    # Check the returned URL
    assert url == expected_url


@pytest.mark.asyncio
async def test_get_file_url_not_found(storage_service, mock_s3_client):
    """Test getting a URL for a non-existent file in S3."""
    key = "test.txt"
    
    # Mock 404 response for head_object (file doesn't exist)
    error_response = {
        "Error": {
            "Code": "404",
            "Message": "Not Found"
        }
    }
    mock_s3_client.head_object.side_effect = ClientError(error_response, "HeadObject")
    
    # Attempt to get the URL should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        await storage_service.get_file_url(key)


@pytest.mark.asyncio
async def test_delete_file(storage_service, mock_s3_client):
    """Test deleting a file from S3."""
    key = "test.txt"
    
    # Mock successful file_exists check
    mock_s3_client.head_object.return_value = {}  # File exists
    
    # Delete the file
    result = await storage_service.delete_file(key)
    
    # Verify the delete_object call
    mock_s3_client.delete_object.assert_called_with(
        Bucket="test-bucket",
        Key=key
    )
    
    # Check that the operation was successful
    assert result is True


@pytest.mark.asyncio
async def test_delete_nonexistent_file(storage_service, mock_s3_client):
    """Test deleting a non-existent file from S3."""
    key = "test.txt"
    
    # Mock 404 response for head_object (file doesn't exist)
    error_response = {
        "Error": {
            "Code": "404",
            "Message": "Not Found"
        }
    }
    mock_s3_client.head_object.side_effect = ClientError(error_response, "HeadObject")
    
    # Attempt to delete the file should return False
    result = await storage_service.delete_file(key)
    assert result is False
    
    # Verify that delete_object was not called
    mock_s3_client.delete_object.assert_not_called()


def test_generate_key(storage_service):
    """Test generating a storage key."""
    user_id = 1
    filename = "test.jpg"
    
    key = storage_service.generate_key(user_id, filename)
    
    # Check key format and properties
    assert str(user_id) in key
    assert key.endswith(".jpg")
    assert "/" in key  # Should include a date component


@pytest.mark.asyncio
async def test_boto3_import_error():
    """Test handling when boto3 is not available."""
    settings = Settings()
    settings.storage_backend = "s3"
    settings.storage_s3_bucket = "test-bucket"
    settings.storage_s3_region = "us-east-1"
    
    with patch("backend.services.storage.s3_storage.BOTO3_AVAILABLE", False):
        with pytest.raises(ImportError):
            S3StorageService(settings)


@pytest.mark.asyncio
async def test_missing_bucket_setting():
    """Test handling when bucket setting is missing."""
    settings = Settings()
    settings.storage_backend = "s3"
    settings.storage_s3_bucket = None
    settings.storage_s3_region = "us-east-1"
    
    with pytest.raises(StorageError):
        S3StorageService(settings)


@pytest.mark.asyncio
async def test_missing_region_setting():
    """Test handling when region setting is missing."""
    settings = Settings()
    settings.storage_backend = "s3"
    settings.storage_s3_bucket = "test-bucket"
    settings.storage_s3_region = None
    
    with pytest.raises(StorageError):
        S3StorageService(settings)