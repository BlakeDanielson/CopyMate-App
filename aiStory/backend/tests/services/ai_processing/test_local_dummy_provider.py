"""Tests for the local dummy AI provider."""
import os
import tempfile
import unittest
from unittest.mock import patch

from backend.services.ai_processing.providers.local_dummy_provider import LocalDummyProvider
from backend.services.ai_processing.exceptions import ImageProcessingError


class TestLocalDummyProvider(unittest.TestCase):
    """Test the LocalDummyProvider class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a test image file
        self.test_image_handle, self.test_image_path = tempfile.mkstemp(suffix=".jpg")
        with open(self.test_image_path, "wb") as f:
            # Write some dummy image content (not a real image, just for testing)
            f.write(b"test image content")
        
        # Create the provider with minimal delay for faster tests
        self.provider = LocalDummyProvider(min_delay=0.01, max_delay=0.05)
    
    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove the test image
        os.close(self.test_image_handle)
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
    
    def test_provider_name(self):
        """Test the get_provider_name method."""
        self.assertEqual(self.provider.get_provider_name(), "local_dummy")
    
    def test_process_image_returns_valid_result(self):
        """Test that process_image returns a valid result dictionary."""
        result = self.provider.process_image(self.test_image_path)
        
        # Check that the result has the expected structure
        self.assertIsInstance(result, dict)
        self.assertIn("provider", result)
        self.assertIn("processing_time_seconds", result)
        self.assertIn("image_path", result)
        self.assertIn("objects_detected", result)
        self.assertIn("tags", result)
        self.assertIn("sentiment", result)
        self.assertIn("moderation", result)
        
        # Check specific fields
        self.assertEqual(result["provider"], "local_dummy")
        self.assertEqual(result["image_path"], self.test_image_path)
        
        # Check object detection data
        self.assertIsInstance(result["objects_detected"], list)
        if result["objects_detected"]:  # If any objects were detected
            obj = result["objects_detected"][0]
            self.assertIn("class", obj)
            self.assertIn("confidence", obj)
            self.assertIn("bounding_box", obj)
            
        # Check tags
        self.assertIsInstance(result["tags"], list)
        if result["tags"]:  # If any tags were generated
            tag = result["tags"][0]
            self.assertIn("name", tag)
            self.assertIn("confidence", tag)
            
        # Check moderation
        self.assertIn("safe", result["moderation"])
        self.assertIn("categories", result["moderation"])
    
    def test_failure_simulation(self):
        """Test that the provider correctly simulates failures based on failure rate."""
        # Create a provider with 100% failure rate
        failing_provider = LocalDummyProvider(
            min_delay=0.01, 
            max_delay=0.05, 
            failure_rate=1.0
        )
        
        # Process should raise an ImageProcessingError
        with self.assertRaises(ImageProcessingError):
            failing_provider.process_image(self.test_image_path)
    
    @patch("time.sleep")  # Patch time.sleep to avoid actual delays in tests
    def test_processing_delay(self, mock_sleep):
        """Test that the provider simulates processing delay."""
        self.provider.process_image(self.test_image_path)
        
        # Verify that sleep was called at least once
        mock_sleep.assert_called()
    
    def test_random_text_detection(self):
        """Test that text detection results are properly structured."""
        # Force text detection to be included
        with patch("random.random", return_value=0.0):
            result = self.provider.process_image(self.test_image_path)
            
            # Check if text_detected field exists and is properly structured
            self.assertIn("text_detected", result)
            self.assertIsInstance(result["text_detected"], list)
            
            if result["text_detected"]:
                text = result["text_detected"][0]
                self.assertIn("text", text)
                self.assertIn("confidence", text)
                self.assertIn("position", text)


if __name__ == "__main__":
    unittest.main()