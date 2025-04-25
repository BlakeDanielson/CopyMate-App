"""Factory for creating AI provider instances."""
import logging
import os
from typing import Optional, Dict, Any, Type

from backend.services.ai_processing.base import AIProviderBase
from backend.services.ai_processing.exceptions import AIProviderNotFoundError, AIProviderConfigurationError
from backend.services.ai_processing.providers.local_dummy_provider import LocalDummyProvider
from backend.services.ai_processing.providers.aws_rekognition_provider import AWSRekognitionProvider
from backend.config import Settings, get_settings

# Configure logger
logger = logging.getLogger(__name__)


class AIProviderFactory:
    """
    Factory class for creating AI provider instances.
    
    This factory encapsulates the logic for selecting and instantiating
    the appropriate AI provider based on configuration.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[AIProviderBase]] = {
        "local": LocalDummyProvider,
        "aws_rekognition": AWSRekognitionProvider,
        # Add more providers as they are implemented:
        # "google_vision": GoogleVisionProvider,
    }
    
    @classmethod
    def get_provider(cls, settings: Optional[Settings] = None) -> AIProviderBase:
        """
        Get an instance of the configured AI provider.
        
        Args:
            settings: Application settings, if None will use default settings
            
        Returns:
            An instance of the configured AIProviderBase implementation
            
        Raises:
            AIProviderNotFoundError: If the configured provider is not found
            AIProviderConfigurationError: If there's an error configuring the provider
        """
        # Use provided settings or get default
        if settings is None:
            settings = get_settings()
            
        # Get provider type from settings
        provider_type = settings.ai_provider_type.lower()
        
        logger.info(f"Creating AI provider of type: {provider_type}")
        
        # Check if provider type is registered
        if provider_type not in cls._providers:
            error_msg = f"AI provider '{provider_type}' not found. Available providers: {list(cls._providers.keys())}"
            logger.error(error_msg)
            raise AIProviderNotFoundError(provider_type)
            
        try:
            # Get the provider class
            provider_class = cls._providers[provider_type]
            
            # Initialize based on provider type
            if provider_type == "local":
                # Get configuration for local dummy provider
                min_delay = float(os.environ.get("AISTORY_AI_LOCAL_MIN_DELAY", "1.0"))
                max_delay = float(os.environ.get("AISTORY_AI_LOCAL_MAX_DELAY", "3.0"))
                failure_rate = float(os.environ.get("AISTORY_AI_LOCAL_FAILURE_RATE", "0.0"))
                
                return provider_class(
                    min_delay=min_delay,
                    max_delay=max_delay,
                    failure_rate=failure_rate
                )
                
            # Handle initialization for other provider types as they are implemented
            elif provider_type == "aws_rekognition":
                # AWS Rekognition provider uses boto3's credential chain
                # and doesn't need credentials passed directly
                return provider_class()
            
            # If we get here, we have a registered provider type but no initialization logic
            logger.warning(f"No specific initialization for {provider_type}, using default constructor")
            return provider_class()
            
        except Exception as e:
            error_msg = f"Failed to initialize AI provider '{provider_type}': {str(e)}"
            logger.exception(error_msg)
            raise AIProviderConfigurationError(provider_type, str(e))
    
    @classmethod
    def register_provider(cls, provider_type: str, provider_class: Type[AIProviderBase]) -> None:
        """
        Register a new provider type.
        
        This method can be used to extend the factory with additional providers
        without modifying the factory code directly.
        
        Args:
            provider_type: The name/type of the provider
            provider_class: The provider class (must inherit from AIProviderBase)
        """
        cls._providers[provider_type.lower()] = provider_class
        logger.info(f"Registered new AI provider type: {provider_type}")