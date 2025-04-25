"""Factory for creating storage service instances."""

import logging
from typing import Optional

from backend.config import Settings
from backend.services.storage.base import StorageService, StorageError
from backend.services.storage.local_storage import LocalStorageService
from backend.services.storage.s3_storage import S3StorageService

logger = logging.getLogger(__name__)


class StorageServiceFactory:
    """Factory class for creating storage service instances.
    
    This factory creates instances of the appropriate StorageService implementation
    based on the application settings.
    """
    
    _instance: Optional[StorageService] = None
    
    @staticmethod
    def get_storage_service(settings: Settings) -> StorageService:
        """Get a storage service instance based on configuration.
        
        This method implements the Singleton pattern, returning the same
        instance for subsequent calls.
        
        Args:
            settings: Application settings
            
        Returns:
            An instance of a StorageService implementation
            
        Raises:
            StorageError: If the configured storage backend is not supported
        """
        if StorageServiceFactory._instance is not None:
            return StorageServiceFactory._instance
        
        backend = settings.storage_backend.lower()
        
        if backend == "local":
            logger.info("Using LocalStorageService for file storage")
            StorageServiceFactory._instance = LocalStorageService(settings)
            
        elif backend == "s3":
            logger.info("Using S3StorageService for file storage")
            StorageServiceFactory._instance = S3StorageService(settings)
            
        else:
            error_msg = f"Unsupported storage backend: {backend}"
            logger.error(error_msg)
            raise StorageError(error_msg)
        
        return StorageServiceFactory._instance
        
    @staticmethod
    def reset() -> None:
        """Reset the factory's singleton instance.
        
        This is primarily useful for testing purposes.
        """
        StorageServiceFactory._instance = None