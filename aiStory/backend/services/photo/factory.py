"""Factory for creating photo service instances."""
import logging
from typing import Optional

from backend.config import Settings, get_settings
from backend.repositories.photo_repository import PhotoRepository
from backend.services.photo.base import PhotoService
from backend.services.photo.photo_service import PhotoServiceImpl
from backend.services.storage.factory import StorageServiceFactory


logger = logging.getLogger(__name__)


class PhotoServiceFactory:
    """Factory class for creating photo service instances.
    
    This factory creates and manages instances of the PhotoService implementation
    following the Singleton pattern to ensure consistent service access.
    """
    
    _instance: Optional[PhotoService] = None
    
    @staticmethod
    def get_photo_service(
        settings: Optional[Settings] = None,
        photo_repository: Optional[PhotoRepository] = None
    ) -> PhotoService:
        """Get a photo service instance.
        
        This method implements the Singleton pattern, returning the same
        instance for subsequent calls.
        
        Args:
            settings: Optional application settings (if None, will be loaded)
            photo_repository: Optional photo repository (if None, will be created)
            
        Returns:
            An instance of the PhotoService implementation
        """
        if PhotoServiceFactory._instance is not None:
            return PhotoServiceFactory._instance
        
        # Get settings if not provided
        if settings is None:
            settings = get_settings()
        
        # Create photo repository if not provided
        if photo_repository is None:
            photo_repository = PhotoRepository()
        
        # Get storage service
        storage_service = StorageServiceFactory.get_storage_service(settings)
        
        # Create and return the photo service
        logger.info("Creating new PhotoServiceImpl instance")
        PhotoServiceFactory._instance = PhotoServiceImpl(
            photo_repository=photo_repository,
            storage_service=storage_service,
            settings=settings
        )
        
        return PhotoServiceFactory._instance
    
    @staticmethod
    def reset() -> None:
        """Reset the factory's singleton instance.
        
        This is primarily useful for testing purposes.
        """
        PhotoServiceFactory._instance = None