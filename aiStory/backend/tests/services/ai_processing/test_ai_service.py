"""Tests for the AI Service."""
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from backend.services.ai_processing.ai_service import AIService
from backend.services.ai_processing.exceptions import AIProcessingError, ImageProcessingError
from backend.services.ai_processing.base import AIProviderBase
from backend.config import Settings


class MockAIProvider(AIProviderBase):
    """Mock AI provider for testing."""
    
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.process_called = False
    
    def process_image(self, image_path):
        """Mock implementation of process_image."""
        self.process_called = True
        
        if self.should_fail:
            raise ImageProcessingError("Simulated processing error", "mock_provider")
            
        return {
            "provider": "mock_provider",
            "objects_detected": [{"class": "test_object", "confidence": 0.95}],
            "tags": [{"name": "test_tag", "confidence": 0.95}]
        }
    
    def get_provider_name(self):
        """Mock implementation of get_provider_name."""
        return "mock_provider"


class TestAIService(unittest.TestCase):
    """Test the AIService class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create test settings
        self.test_settings = Settings(
            storage_backend="local",
            storage_local_path="./uploads",
            ai_provider_type="local",
            secret_key="secret-key-long-enough-for-validation-test"
        )
        
        # Create mock storage service
        self.mock_storage = MagicMock()
        
        # Create a test image file
        self.test_image_handle, self.test_image_path = tempfile.mkstemp(suffix=".jpg")
        with open(self.test_image_path, "wb") as f:
            f.write(b"test image content")
        
        # Create mock provider
        self.mock_provider = MockAIProvider()
        
        # Create AIService with mock provider and storage
        self.service = AIService(
            storage_service=self.mock_storage,
            ai_provider=self.mock_provider,
            settings=self.test_settings
        )
    
    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove the test image
        os.close(self.test_image_handle)
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
    
    def test_process_photo_success(self):
        """Test successful photo processing."""
        # Setup mock storage service
        self.mock_storage.download_file.return_value = self.test_image_path
        
        # Process a photo
        result = self.service.process_photo(1, "local/bucket/key.jpg")
        
        # Verify provider was called
        self.assertTrue(self.mock_provider.process_called)
        
        # Check result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["provider"], "mock_provider")
        self.assertEqual(result["photo_id"], 1)
        self.assertIn("objects_detected", result)
        self.assertIn("tags", result)
    
    def test_process_photo_provider_error(self):
        """Test handling of provider errors."""
        # Setup mock storage service
        self.mock_storage.download_file.return_value = self.test_image_path
        
        # Create service with failing provider
        failing_provider = MockAIProvider(should_fail=True)
        service = AIService(
            storage_service=self.mock_storage,
            ai_provider=failing_provider,
            settings=self.test_settings
        )
        
        # Process should raise an AIProcessingError
        with self.assertRaises(ImageProcessingError):
            service.process_photo(1, "local/bucket/key.jpg")
        
        # Verify provider was called
        self.assertTrue(failing_provider.process_called)
    
    def test_process_photo_storage_error(self):
        """Test handling of storage service errors."""
        # Setup mock storage service to fail
        self.mock_storage.download_file.side_effect = Exception("Storage error")
        
        # Process should raise an AIProcessingError
        with self.assertRaises(AIProcessingError):
            self.service.process_photo(1, "local/bucket/key.jpg")
    
    @patch("os.path.isfile")
    def test_local_storage_direct_path(self, mock_isfile):
        """Test handling of local storage paths."""
        # Setup mocks
        mock_isfile.return_value = True
        
        # Process a photo
        self.service.process_photo(1, "local/bucket/key.jpg")
        
        # Verify provider was called with correct path
        self.assertTrue(self.mock_provider.process_called)
    
    def test_cleanup_local_image(self):
        """Test cleanup of temporary files."""
        # Create a test temp file
        temp_handle, temp_path = tempfile.mkstemp(
            suffix=".jpg", 
            prefix="process_", 
            dir=os.path.join(os.getcwd(), "temp_ai_processing")
        )
        os.close(temp_handle)
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.join(os.getcwd(), "temp_ai_processing"), exist_ok=True)
        
        # Ensure the file exists
        self.assertTrue(os.path.exists(temp_path))
        
        # Cleanup the file
        self.service._cleanup_local_image(temp_path)
        
        # Verify file was removed
        self.assertFalse(os.path.exists(temp_path))
        
        # Test with a non-existent file (should not raise error)
        self.service._cleanup_local_image("non_existent_file.jpg")
        
        # Test with a file that's not in the temp directory (should not delete)
        with tempfile.NamedTemporaryFile(delete=False) as regular_temp:
            regular_path = regular_temp.name
            
        try:
            self.service._cleanup_local_image(regular_path)
            # Should still exist because it's not in temp_ai_processing
            self.assertTrue(os.path.exists(regular_path))
        finally:
            # Clean up
            if os.path.exists(regular_path):
                os.unlink(regular_path)


if __name__ == "__main__":
    unittest.main()