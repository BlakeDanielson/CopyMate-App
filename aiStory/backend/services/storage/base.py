"""Abstract interface for file storage services."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, BinaryIO

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """Abstract interface for file storage operations.
    
    This interface defines the operations that any storage service implementation
    must provide, allowing for different storage backends (local filesystem, S3, etc.)
    to be used interchangeably.
    """
    
    @abstractmethod
    async def upload_file(
        self, 
        file: BinaryIO, 
        key: str, 
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file to storage.
        
        Args:
            file: File-like object to upload
            key: Storage key/path where the file will be stored
            metadata: Optional metadata to associate with the file
            content_type: Optional content type of the file
            
        Returns:
            String URL to access the uploaded file
            
        Raises:
            StorageError: If an error occurs during upload
        """
        pass
    
    @abstractmethod
    async def get_file_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing a file.
        
        Args:
            key: Storage key identifying the file
            expires_in: Optional expiration time in seconds for the URL
            
        Returns:
            URL to access the file
            
        Raises:
            StorageError: If an error occurs generating the URL
            FileNotFoundError: If the file does not exist
        """
        pass
    
    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Delete a file from storage.
        
        Args:
            key: Storage key identifying the file to delete
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            StorageError: If an error occurs during deletion
        """
        pass
    
    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """Check if a file exists in storage.
        
        Args:
            key: Storage key identifying the file
            
        Returns:
            True if the file exists, False otherwise
            
        Raises:
            StorageError: If an error occurs checking the file
        """
        pass
    
    @abstractmethod
    def generate_key(self, user_id: int, filename: str) -> str:
        """Generate a storage key for a file.
        
        Args:
            user_id: User ID associated with the file
            filename: Original filename
            
        Returns:
            Storage key to use for the file
        """
        pass
    
    @abstractmethod
    async def generate_presigned_upload_url(
        self,
        bucket: str,
        object_key: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None,
        expires_in: int = 3600
    ) -> Dict[str, Any]:
        """Generate a pre-signed URL for direct file uploads.
        
        Args:
            bucket: Storage bucket name
            object_key: Key/path where the file will be stored
            content_type: Content type of the file to be uploaded
            metadata: Optional metadata to associate with the file
            expires_in: Expiration time for the URL in seconds (default: 1 hour)
            
        Returns:
            Dict containing the presigned URL and any additional fields needed for upload
            
        Raises:
            StorageError: If an error occurs generating the URL
        """
        pass


class StorageError(Exception):
    """Exception raised for errors in the storage service."""
    pass