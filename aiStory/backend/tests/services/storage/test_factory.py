"""Tests for the StorageServiceFactory class."""

import pytest
from unittest.mock import patch

from backend.config import Settings
from backend.services.storage.base import StorageService, StorageError
from backend.services.storage.local_storage import LocalStorageService
from backend.services.storage.s3_storage import S3StorageService
from backend.services.storage.factory import StorageServiceFactory


@pytest.fixture
def reset_factory():
    """Fixture to reset the factory's singleton instance before and after each test."""
    StorageServiceFactory.reset()
    yield
    StorageServiceFactory.reset()


@pytest.fixture
def local_settings():
    """Fixture for settings with local storage configuration."""
    settings = Settings()
    settings.storage_backend = "local"
    settings.storage_local_path = "./uploads"
    return settings


@pytest.fixture
def s3_settings():
    """Fixture for settings with S3 storage configuration."""
    settings = Settings()
    settings.storage_backend = "s3"
    settings.storage_s3_bucket = "test-bucket"
    settings.storage_s3_region = "us-east-1"
    return settings


def test_get_local_storage_service(local_settings, reset_factory):
    """Test that the factory returns a LocalStorageService when configured for local storage."""
    service = StorageServiceFactory.get_storage_service(local_settings)
    
    assert isinstance(service, LocalStorageService)
    assert service.provider == "local"
    assert service.bucket_name == "local"


@patch("backend.services.storage.s3_storage.BOTO3_AVAILABLE", True)
@patch("backend.services.storage.s3_storage.boto3.client")
def test_get_s3_storage_service(mock_client, s3_settings, reset_factory):
    """Test that the factory returns an S3StorageService when configured for S3 storage."""
    service = StorageServiceFactory.get_storage_service(s3_settings)
    
    assert isinstance(service, S3StorageService)
    assert service.provider == "s3"
    assert service.bucket_name == "test-bucket"
    assert service.region == "us-east-1"


def test_unsupported_storage_backend(reset_factory):
    """Test that the factory raises a StorageError for unsupported storage backends."""
    settings = Settings()
    settings.storage_backend = "unsupported"
    
    with pytest.raises(StorageError) as excinfo:
        StorageServiceFactory.get_storage_service(settings)
    
    assert "Unsupported storage backend" in str(excinfo.value)


def test_singleton_pattern(local_settings, reset_factory):
    """Test that the factory implements the Singleton pattern correctly."""
    service1 = StorageServiceFactory.get_storage_service(local_settings)
    service2 = StorageServiceFactory.get_storage_service(local_settings)
    
    # Should be the same instance
    assert service1 is service2


def test_reset(local_settings, reset_factory):
    """Test that the factory's reset method works correctly."""
    service1 = StorageServiceFactory.get_storage_service(local_settings)
    
    # Reset the factory
    StorageServiceFactory.reset()
    
    service2 = StorageServiceFactory.get_storage_service(local_settings)
    
    # Should be different instances
    assert service1 is not service2