"""Local filesystem implementation of the StorageService interface."""

import os
import uuid
import shutil
import logging
import mimetypes
from pathlib import Path
from typing import BinaryIO, Dict, Optional, Any
from urllib.parse import urljoin

from backend.config import Settings
from backend.services.storage.base import StorageService, StorageError

logger = logging.getLogger(__name__)


class LocalStorageService(StorageService):
    """Implementation of StorageService that stores files on the local filesystem.
    
    This implementation is primarily intended for development and testing purposes.
    It stores files in a configurable directory on the local filesystem.
    """
    
    def __init__(self, settings: Settings):
        """Initialize the local storage service.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.storage_path = Path(settings.storage_local_path).resolve()
        self.provider = "local"
        self.bucket_name = "local"
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        logger.info(f"LocalStorageService initialized with storage path: {self.storage_path}")
    
    async def upload_file(
        self, 
        file: BinaryIO, 
        key: str, 
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file to local storage.
        
        Args:
            file: File-like object to upload
            key: Storage key/path where the file will be stored
            metadata: Optional metadata to associate with the file (ignored in local storage)
            content_type: Optional content type of the file (ignored in local storage)
            
        Returns:
            URL to access the uploaded file
            
        Raises:
            StorageError: If an error occurs during upload
        """
        try:
            # Ensure directory exists
            file_path = self.storage_path / key
            os.makedirs(file_path.parent, exist_ok=True)
            
            # Copy file content to destination
            with open(file_path, 'wb') as dest_file:
                shutil.copyfileobj(file, dest_file)
                
            logger.info(f"File uploaded to local storage: {file_path}")
            return await self.get_file_url(key)
        
        except Exception as e:
            error_msg = f"Failed to upload file to local storage: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    async def get_file_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing a file in local storage.
        
        For local storage, this is a file:// URL or a relative URL depending on the context.
        The expires_in parameter is ignored for local storage.
        
        Args:
            key: Storage key identifying the file
            expires_in: Optional expiration time in seconds (ignored for local storage)
            
        Returns:
            URL to access the file
            
        Raises:
            StorageError: If an error occurs generating the URL
            FileNotFoundError: If the file does not exist
        """
        file_path = self.storage_path / key
        
        if not file_path.exists():
            error_msg = f"File not found in local storage: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # For local development, we'll return a relative URL to the uploads directory
        # This assumes the uploads directory is accessible via the web server
        relative_url = f"/uploads/{key}"
        return relative_url
    
    async def delete_file(self, key: str) -> bool:
        """Delete a file from local storage.
        
        Args:
            key: Storage key identifying the file to delete
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            StorageError: If an error occurs during deletion
        """
        try:
            file_path = self.storage_path / key
            
            if not file_path.exists():
                logger.warning(f"Attempted to delete non-existent file: {file_path}")
                return False
            
            os.remove(file_path)
            logger.info(f"File deleted from local storage: {file_path}")
            
            # Try to remove empty parent directories
            self._cleanup_empty_dirs(file_path.parent)
            
            return True
        
        except Exception as e:
            error_msg = f"Failed to delete file from local storage: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    async def file_exists(self, key: str) -> bool:
        """Check if a file exists in local storage.
        
        Args:
            key: Storage key identifying the file
            
        Returns:
            True if the file exists, False otherwise
            
        Raises:
            StorageError: If an error occurs checking the file
        """
        try:
            file_path = self.storage_path / key
            return file_path.exists()
        
        except Exception as e:
            error_msg = f"Failed to check if file exists in local storage: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    def generate_key(self, user_id: int, filename: str) -> str:
        """Generate a storage key for a file in local storage.
        
        Args:
            user_id: User ID associated with the file
            filename: Original filename
            
        Returns:
            Storage key to use for the file
        """
        # Extract file extension
        _, ext = os.path.splitext(filename)
        
        # Generate a UUID for the file
        file_uuid = str(uuid.uuid4())
        
        # Create a path with user_id/yyyy-mm-dd/uuid.ext format
        import datetime
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return f"{user_id}/{date_str}/{file_uuid}{ext.lower()}"
    
    def _cleanup_empty_dirs(self, path: Path) -> None:
        """Recursively remove empty directories.
        
        Args:
            path: Directory path to check and potentially remove
        """
        try:
            # Don't remove the base storage directory
            if path == self.storage_path or not path.is_relative_to(self.storage_path):
                return
            
            # If directory is empty, remove it and check parent
            if path.exists() and path.is_dir() and not any(path.iterdir()):
                path.rmdir()
                logger.debug(f"Removed empty directory: {path}")
                self._cleanup_empty_dirs(path.parent)
        
        except Exception as e:
            logger.warning(f"Failed to cleanup empty directory {path}: {str(e)}")
            # Don't raise - this is just a cleanup operation
            
    async def generate_presigned_upload_url(
        self,
        bucket: str,
        object_key: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None,
        expires_in: int = 3600
    ) -> Dict[str, Any]:
        """Generate a pre-signed URL for direct file uploads to local storage.
        
        For local storage, this is a simplified implementation that returns
        a local endpoint URL and mock fields for compatibility with the API.
        
        Args:
            bucket: Storage bucket name (ignored for local storage)
            object_key: Key/path where the file will be stored
            content_type: Content type of the file to be uploaded
            metadata: Optional metadata to associate with the file
            expires_in: Expiration time for the URL in seconds (ignored for local storage)
            
        Returns:
            Dict containing mock URL and fields for compatibility
            
        Raises:
            StorageError: If an error occurs generating the URL
        """
        try:
            # Ensure directory exists
            file_path = self.storage_path / object_key
            os.makedirs(file_path.parent, exist_ok=True)
            
            # The actual URL would be handled by the frontend in development mode
            # Just return a mock URL pointing to a local endpoint
            upload_url = f"/api/v1/storage/upload/{object_key}"
            
            # Create mock fields similar to what S3 would provide
            fields = {
                "Content-Type": content_type
            }
            
            # Add metadata if provided
            if metadata:
                for key, value in metadata.items():
                    fields[f'x-meta-{key}'] = value
            
            return {
                "url": upload_url,
                "fields": fields
            }
            
        except Exception as e:
            error_msg = f"Failed to generate mock pre-signed upload URL: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e