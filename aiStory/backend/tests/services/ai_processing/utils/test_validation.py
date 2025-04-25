"""Tests for the AI Processing validation utilities."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

from backend.services.ai_processing.utils.validation import (
    validate_file_path,
    validate_image_file,
    validate_rekognition_max_labels,
    validate_rekognition_min_confidence,
    MIN_REKOGNITION_LABELS,
    MAX_REKOGNITION_LABELS,
    MIN_REKOGNITION_CONFIDENCE,
    MAX_REKOGNITION_CONFIDENCE,
    ALLOWED_IMAGE_EXTENSIONS
)


class TestValidationUtilities(unittest.TestCase):
    """Test the validation utilities for AI processing."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()
        self.base_dir = os.path.join(self.test_dir, "base")
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Create a temporary image file
        self.test_image_path = os.path.join(self.base_dir, "test_image.jpg")
        with open(self.test_image_path, "wb") as f:
            f.write(b"test image content")
            
        # Create a file outside the base directory for path traversal tests
        self.outside_dir = os.path.join(self.test_dir, "outside")
        os.makedirs(self.outside_dir, exist_ok=True)
        self.outside_file = os.path.join(self.outside_dir, "outside.txt")
        with open(self.outside_file, "w") as f:
            f.write("outside content")
    
    def tearDown(self):
        """Clean up test environment after each test."""
        # Clean up temporary files
        for path in [self.test_image_path, self.outside_file]:
            if os.path.exists(path):
                os.remove(path)
                
        # Clean up temporary directories
        for directory in [self.base_dir, self.outside_dir, self.test_dir]:
            if os.path.exists(directory):
                try:
                    os.rmdir(directory)
                except OSError:
                    # Directory not empty, which is fine for our tests
                    pass
    
    def test_validate_file_path_valid(self):
        """Test validating a valid file path."""
        # Arrange & Act
        validated_path = validate_file_path(self.test_image_path)
        
        # Assert
        self.assertEqual(validated_path, str(Path(self.test_image_path).resolve()))
    
    def test_validate_file_path_nonexistent(self):
        """Test validating a non-existent file path."""
        # Arrange
        non_existent_path = os.path.join(self.base_dir, "nonexistent.txt")
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            validate_file_path(non_existent_path)
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_validate_file_path_nonexistent_no_check(self):
        """Test validating a non-existent file path without existence check."""
        # Arrange
        non_existent_path = os.path.join(self.base_dir, "nonexistent.txt")
        
        # Act
        validated_path = validate_file_path(non_existent_path, must_exist=False)
        
        # Assert
        self.assertEqual(validated_path, str(Path(non_existent_path).resolve()))
    
    def test_validate_file_path_base_directory_valid(self):
        """Test validating a file path within a base directory."""
        # Arrange & Act
        validated_path = validate_file_path(self.test_image_path, base_directory=self.base_dir)
        
        # Assert
        self.assertEqual(validated_path, str(Path(self.test_image_path).resolve()))
    
    def test_validate_file_path_base_directory_traversal(self):
        """Test validating a file path with path traversal attempt."""
        # Arrange 
        # Attempt to access outside file through a path traversal
        traversal_path = os.path.join(self.base_dir, "../outside/outside.txt")
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            validate_file_path(traversal_path, base_directory=self.base_dir)
        
        self.assertIn("must be within the specified base directory", str(context.exception))
    
    def test_validate_image_file_valid(self):
        """Test validating a valid image file."""
        # Mock mimetypes.guess_type to return a valid mimetype
        with patch('mimetypes.guess_type', return_value=('image/jpeg', None)):
            # Act
            validated_path = validate_image_file(self.test_image_path)
            
            # Assert
            self.assertEqual(validated_path, str(Path(self.test_image_path).resolve()))
    
    def test_validate_image_file_invalid_extension(self):
        """Test validating a file with invalid image extension."""
        # Arrange
        non_image_path = os.path.join(self.base_dir, "test.txt")
        with open(non_image_path, "w") as f:
            f.write("not an image")
        
        try:
            # Act & Assert
            with self.assertRaises(ValueError) as context:
                validate_image_file(non_image_path)
            
            self.assertIn("Unsupported image format", str(context.exception))
            self.assertTrue(any(ext in str(context.exception) for ext in ALLOWED_IMAGE_EXTENSIONS))
        
        finally:
            # Clean up
            if os.path.exists(non_image_path):
                os.remove(non_image_path)
    
    def test_validate_image_file_invalid_mimetype(self):
        """Test validating a file with valid extension but invalid mimetype."""
        # Arrange - create a fake image with a .jpg extension
        fake_image_path = os.path.join(self.base_dir, "fake.jpg")
        with open(fake_image_path, "w") as f:
            f.write("not a real image")
        
        try:
            # Mock mimetypes.guess_type to return an invalid mimetype
            with patch('mimetypes.guess_type', return_value=('text/plain', None)):
                # Act & Assert
                with self.assertRaises(ValueError) as context:
                    validate_image_file(fake_image_path)
                
                self.assertIn("does not appear to be a valid image", str(context.exception))
        
        finally:
            # Clean up
            if os.path.exists(fake_image_path):
                os.remove(fake_image_path)
    
    def test_validate_rekognition_max_labels_valid(self):
        """Test validating valid rekognition_max_labels values."""
        # Test min boundary
        self.assertEqual(validate_rekognition_max_labels(MIN_REKOGNITION_LABELS), MIN_REKOGNITION_LABELS)
        
        # Test max boundary
        self.assertEqual(validate_rekognition_max_labels(MAX_REKOGNITION_LABELS), MAX_REKOGNITION_LABELS)
        
        # Test middle value
        middle_value = (MIN_REKOGNITION_LABELS + MAX_REKOGNITION_LABELS) // 2
        self.assertEqual(validate_rekognition_max_labels(middle_value), middle_value)
        
        # Test string conversion
        self.assertEqual(validate_rekognition_max_labels("50"), 50)
    
    def test_validate_rekognition_max_labels_invalid(self):
        """Test validating invalid rekognition_max_labels values."""
        # Test below min boundary
        with self.assertRaises(ValueError) as context:
            validate_rekognition_max_labels(MIN_REKOGNITION_LABELS - 1)
        self.assertIn("must be between", str(context.exception))
        
        # Test above max boundary
        with self.assertRaises(ValueError) as context:
            validate_rekognition_max_labels(MAX_REKOGNITION_LABELS + 1)
        self.assertIn("must be between", str(context.exception))
        
        # Test non-numeric string
        with self.assertRaises(ValueError) as context:
            validate_rekognition_max_labels("not_a_number")
        self.assertIn("must be an integer", str(context.exception))
        
        # Test other types
        for invalid_value in [None, {}, [], True, 1.5]:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(ValueError):
                    validate_rekognition_max_labels(invalid_value)
    
    def test_validate_rekognition_min_confidence_valid(self):
        """Test validating valid rekognition_min_confidence values."""
        # Test min boundary
        self.assertEqual(validate_rekognition_min_confidence(MIN_REKOGNITION_CONFIDENCE), MIN_REKOGNITION_CONFIDENCE)
        
        # Test max boundary
        self.assertEqual(validate_rekognition_min_confidence(MAX_REKOGNITION_CONFIDENCE), MAX_REKOGNITION_CONFIDENCE)
        
        # Test middle value
        middle_value = (MIN_REKOGNITION_CONFIDENCE + MAX_REKOGNITION_CONFIDENCE) / 2
        self.assertEqual(validate_rekognition_min_confidence(middle_value), middle_value)
        
        # Test string conversion
        self.assertEqual(validate_rekognition_min_confidence("75.5"), 75.5)
        
        # Test integer value
        self.assertEqual(validate_rekognition_min_confidence(50), 50.0)
    
    def test_validate_rekognition_min_confidence_invalid(self):
        """Test validating invalid rekognition_min_confidence values."""
        # Test below min boundary
        with self.assertRaises(ValueError) as context:
            validate_rekognition_min_confidence(MIN_REKOGNITION_CONFIDENCE - 0.1)
        self.assertIn("must be between", str(context.exception))
        
        # Test above max boundary
        with self.assertRaises(ValueError) as context:
            validate_rekognition_min_confidence(MAX_REKOGNITION_CONFIDENCE + 0.1)
        self.assertIn("must be between", str(context.exception))
        
        # Test non-numeric string
        with self.assertRaises(ValueError) as context:
            validate_rekognition_min_confidence("not_a_number")
        self.assertIn("must be a number", str(context.exception))
        
        # Test other types
        for invalid_value in [None, {}, [], True]:
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(ValueError):
                    validate_rekognition_min_confidence(invalid_value)


if __name__ == "__main__":
    unittest.main()