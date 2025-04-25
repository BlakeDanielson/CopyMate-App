from abc import ABC, abstractmethod
from typing import Dict, Any


class AIProviderBase(ABC):
    """
    Base abstract class for AI image processing providers.
    
    All concrete AI provider implementations must inherit from this class
    and implement the required methods.
    """
    
    @abstractmethod
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image and return the results.
        
        Args:
            image_path: Path to the image file to process
            
        Returns:
            A dictionary containing the processing results. The structure may vary
            between providers but should follow a consistent schema for each provider.
            
        Raises:
            AIProcessingError: If there's an error processing the image
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this AI provider.
        
        Returns:
            The provider's name as a string
        """
        pass