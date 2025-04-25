"""Tests for the AI Provider Factory."""
import os
import unittest
from unittest.mock import patch, MagicMock

from backend.services.ai_processing.factory import AIProviderFactory
from backend.services.ai_processing.base import AIProviderBase
from backend.services.ai_processing.exceptions import (
    AIProviderNotFoundError,
    AIProviderConfigurationError
)
from backend.services.ai_processing.providers.local_dummy_provider import LocalDummyProvider
from backend.services.ai_processing.providers.aws_rekognition_provider import AWSRekognitionProvider
from backend.config import Settings



class TestAIProviderFactory(unittest.TestCase):
    """Test the AIProviderFactory class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create test settings with local provider
        self.test_settings = Settings(
            ai_provider_type="local",
            secret_key="secret-key-long-enough-for-validation-test"
        )
        
        # Save original environment variables
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up test environment after each test."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_get_local_provider(self):
        """Test getting a local provider."""
        provider = AIProviderFactory.get_provider(self.test_settings)
        
        # Check provider type
        self.assertIsInstance(provider, LocalDummyProvider)
        self.assertEqual(provider.get_provider_name(), "local_dummy")
    
    def test_invalid_provider_type(self):
        """Test error handling for invalid provider type."""
        # Create settings with invalid provider type
        invalid_settings = Settings(
            ai_provider_type="invalid_provider",
            secret_key="secret-key-long-enough-for-validation-test"
        )
        
        # Getting provider should raise AIProviderNotFoundError
        with self.assertRaises(AIProviderNotFoundError):
            AIProviderFactory.get_provider(invalid_settings)
    
    def test_local_provider_configuration(self):
        """Test local provider configuration from environment variables."""
        # Set test environment variables
        os.environ["AISTORY_AI_LOCAL_MIN_DELAY"] = "0.5"
        os.environ["AISTORY_AI_LOCAL_MAX_DELAY"] = "1.5"
        os.environ["AISTORY_AI_LOCAL_FAILURE_RATE"] = "0.1"
        
        with patch("backend.services.ai_processing.providers.local_dummy_provider.LocalDummyProvider") as mock_provider:
            AIProviderFactory.get_provider(self.test_settings)
            
            # Verify provider was created with correct parameters
            mock_provider.assert_called_once_with(
                min_delay=0.5,
                max_delay=1.5,
                failure_rate=0.1
            )
    
    def test_register_custom_provider(self):
        """Test registering a custom provider."""
        # Create a mock provider class
        class CustomProvider(AIProviderBase):
            def process_image(self, image_path):
                return {"result": "custom"}
                
            def get_provider_name(self):
                return "custom_provider"
        
        # Register the custom provider
        AIProviderFactory.register_provider("custom", CustomProvider)
        
        # Update settings to use custom provider
        custom_settings = Settings(
            ai_provider_type="custom",
            secret_key="secret-key-long-enough-for-validation-test"
        )
        
        # Get provider and verify it's the custom one
        provider = AIProviderFactory.get_provider(custom_settings)
        self.assertIsInstance(provider, CustomProvider)
        self.assertEqual(provider.get_provider_name(), "custom_provider")
    
    @patch("boto3.client")
    def test_get_aws_rekognition_provider(self, mock_boto3_client):
        """Test getting an AWS Rekognition provider."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Set required environment variables
        os.environ["AISTORY_AWS_REGION"] = "us-west-2"
        
        # Create settings with AWS provider type
        aws_settings = Settings(
            ai_provider_type="aws_rekognition",
            aws_region="us-west-2",
            secret_key="secret-key-long-enough-for-validation-test"
        )
        
        # Act
        provider = AIProviderFactory.get_provider(aws_settings)
        
        # Assert
        self.assertIsInstance(provider, AWSRekognitionProvider)
        self.assertEqual(provider.get_provider_name(), "aws_rekognition")
        self.assertEqual(provider.region, "us-west-2")
        mock_boto3_client.assert_called_once_with("rekognition", region_name="us-west-2")


if __name__ == "__main__":
    unittest.main()