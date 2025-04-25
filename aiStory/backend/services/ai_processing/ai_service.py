"""AI service for processing images."""
import logging
import os
from typing import Dict, Any, Optional

from backend.config import Settings, get_settings
from backend.services.ai_processing.base import AIProviderBase
from backend.services.ai_processing.exceptions import (
    AIProcessingError, 
    ImageProcessingError, 
    AIProviderConnectionError
)
from backend.services.ai_processing.factory import AIProviderFactory
from backend.services.storage.base import StorageService

# Configure logger
logger = logging.getLogger(__name__)


class AIService:
    """
    Service for AI image processing.
    
    This service provides a high-level interface for the application to interact with
    AI providers. It handles:
    1. Getting the appropriate AI provider from the factory
    2. Downloading images from storage when needed
    3. Coordinating the processing workflow
    4. Error handling and retries
    """
    
    def __init__(
        self, 
        storage_service: StorageService,
        ai_provider: Optional[AIProviderBase] = None,
        settings: Optional[Settings] = None
    ):
        """
        Initialize the AI service.
        
        Args:
            storage_service: Service for file storage operations
            ai_provider: AI provider instance (optional, if None will be created from factory)
            settings: Application settings (optional, if None will use default)
        """
        self.storage_service = storage_service
        self.settings = settings or get_settings()
        
        # If AI provider is not provided, get it from the factory
        if ai_provider is None:
            self.ai_provider = AIProviderFactory.get_provider(self.settings)
        else:
            self.ai_provider = ai_provider
            
        logger.info(f"AIService initialized with provider: {self.ai_provider.get_provider_name()}")
    
    def process_photo(self, photo_id: int, storage_path: str) -> Dict[str, Any]:
        """
        Process a photo with AI.
        
        Args:
            photo_id: ID of the photo in the database
            storage_path: Path to the photo in storage
            
        Returns:
            Dictionary containing the AI processing results
            
        Raises:
            AIProcessingError: If there's an error processing the photo
        """
        logger.info(f"Processing photo {photo_id} from {storage_path}")
        
        try:
            # Prepare a local copy of the image for processing
            local_image_path = self._prepare_image_for_processing(storage_path)
            
            try:
                # Process the image with the AI provider
                logger.info(f"Calling AI provider {self.ai_provider.get_provider_name()} for photo {photo_id}")
                results = self.ai_provider.process_image(local_image_path)
                
                # Add metadata to the results
                results["photo_id"] = photo_id
                results["provider"] = self.ai_provider.get_provider_name()
                
                logger.info(f"Successfully processed photo {photo_id}")
                return results
                
            finally:
                # Clean up temporary file if it exists
                self._cleanup_local_image(local_image_path)
                
        except Exception as e:
            logger.error(f"Error processing photo {photo_id}: {str(e)}")
            
            # Wrap the exception in an appropriate AIProcessingError
            if isinstance(e, AIProcessingError):
                # Already an AIProcessingError, re-raise
                raise
            else:
                # Wrap other exceptions
                raise AIProcessingError(
                    f"Unexpected error processing photo: {str(e)}",
                    provider_name=self.ai_provider.get_provider_name()
                )
    
    def _prepare_image_for_processing(self, storage_path: str) -> str:
        """
        Prepare an image for AI processing.
        
        This includes:
        1. Download from remote storage if needed
        2. Create a local copy that the provider can access
        
        Args:
            storage_path: Path to the image in storage
            
        Returns:
            Local path to the image ready for processing
            
        Raises:
            AIProcessingError: If there's an error preparing the image
        """
        try:
            # Create temporary directory if it doesn't exist
            temp_dir = os.path.join(os.getcwd(), "temp_ai_processing")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate a unique filename for the local copy
            base_filename = os.path.basename(storage_path)
            local_path = os.path.join(temp_dir, f"process_{base_filename}")
            
            # For local storage, we might be able to use the file directly
            # For remote storage, we need to download it first
            if self.settings.storage_backend == "local":
                # For local storage - just use the actual path
                # Assuming storage_path is something like "local/bucket/key"
                parts = storage_path.split("/", 2)
                if len(parts) == 3:
                    _, _, actual_path = parts
                    absolute_path = os.path.join(self.settings.storage_local_path, actual_path)
                    
                    # Check if the file exists
                    if os.path.isfile(absolute_path):
                        logger.info(f"Using local file directly: {absolute_path}")
                        return absolute_path
            
            # If we get here, we need to download the file
            logger.info(f"Downloading file from {storage_path} to {local_path}")
            self.storage_service.download_file(storage_path, local_path)
            
            return local_path
            
        except Exception as e:
            logger.error(f"Error preparing image for processing: {str(e)}")
            raise AIProcessingError(
                f"Failed to prepare image for processing: {str(e)}",
                provider_name=self.ai_provider.get_provider_name()
            )
    
    def _cleanup_local_image(self, local_path: str) -> None:
        """
        Clean up temporary local image file.
        
        Args:
            local_path: Path to the local image to clean up
        """
        try:
            # Check if this is a file we should delete (in our temp directory)
            if (os.path.exists(local_path) and 
                "temp_ai_processing" in local_path and
                os.path.isfile(local_path)):
                logger.debug(f"Cleaning up temporary file: {local_path}")
                os.unlink(local_path)
        except Exception as e:
            # Just log cleanup errors, don't raise
            logger.warning(f"Error cleaning up temporary file {local_path}: {str(e)}")