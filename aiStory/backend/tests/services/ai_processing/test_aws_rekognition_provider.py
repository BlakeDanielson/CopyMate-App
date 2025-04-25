"""Tests for the AWS Rekognition AI provider."""
import os
import tempfile
import unittest
import logging
from unittest.mock import patch, MagicMock, mock_open, ANY, call

import boto3
from botocore.exceptions import NoCredentialsError, ClientError, ParamValidationError
from parameterized import parameterized

from backend.services.ai_processing.providers.aws_rekognition_provider import AWSRekognitionProvider
from backend.services.ai_processing.exceptions import (
    AIProviderConfigurationError,
    AIProviderConnectionError,
    ImageProcessingError
)
from backend.services.ai_processing.utils.validation import (
    MIN_REKOGNITION_LABELS,
    MAX_REKOGNITION_LABELS,
    MIN_REKOGNITION_CONFIDENCE,
    MAX_REKOGNITION_CONFIDENCE
)
from backend.config import Settings


class TestAWSRekognitionProvider(unittest.TestCase):
    """Test the AWSRekognitionProvider class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Save original environment variables
        self.original_env = os.environ.copy()
        
        # Set required environment variables for testing
        os.environ["AISTORY_AWS_REGION"] = "us-east-1"
        
        # Create a temporary image file
        self.test_image_handle, self.test_image_path = tempfile.mkstemp(suffix=".jpg")
        with open(self.test_image_path, "wb") as f:
            f.write(b"test image content")
            
        # Mock mimetypes.guess_type to return a valid mimetype for our test image
        patcher = patch('mimetypes.guess_type', return_value=('image/jpeg', None))
        self.addCleanup(patcher.stop)
        patcher.start()
    
    def tearDown(self):
        """Clean up test environment after each test."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Close and remove the test image
        os.close(self.test_image_handle)
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
    
    @patch("boto3.client")
    def test_initialization_with_valid_config(self, mock_boto3_client):
        """Test provider initialization with valid configuration."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Act
        provider = AWSRekognitionProvider()
        
        # Assert
        self.assertEqual(provider.get_provider_name(), "aws_rekognition")
        self.assertEqual(provider.region, "us-east-1")
        self.assertEqual(provider.max_labels, 10)  # Default value
        self.assertEqual(provider.min_confidence, 75.0)  # Default value
        mock_boto3_client.assert_called_once_with("rekognition", region_name="us-east-1")
    
    @patch("boto3.client")
    def test_initialization_with_custom_config(self, mock_boto3_client):
        """Test provider initialization with custom configuration."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Set custom environment variables
        os.environ["AISTORY_REKOGNITION_MAX_LABELS"] = "5"
        os.environ["AISTORY_REKOGNITION_MIN_CONFIDENCE"] = "90.0"
        
        # These should be within the valid ranges
        self.assertTrue(5 >= MIN_REKOGNITION_LABELS)
        self.assertTrue(5 <= MAX_REKOGNITION_LABELS)
        self.assertTrue(90.0 >= MIN_REKOGNITION_CONFIDENCE)
        self.assertTrue(90.0 <= MAX_REKOGNITION_CONFIDENCE)
        
        # Act
        provider = AWSRekognitionProvider()
        
        # Assert
        self.assertEqual(provider.max_labels, 5)
        self.assertEqual(provider.min_confidence, 90.0)
    
    def test_initialization_with_missing_region(self):
        """Test provider initialization with missing AWS region."""
        # Arrange
        # Remove the AWS region from environment variables
        os.environ.pop("AISTORY_AWS_REGION", None)
        
        # Act & Assert
        with self.assertRaises(AIProviderConfigurationError) as context:
            AWSRekognitionProvider()
        
        # Verify error message
        self.assertIn("AWS region is not configured", str(context.exception))
        self.assertIn("aws_rekognition", str(context.exception))
    
    @parameterized.expand([
        ("AISTORY_REKOGNITION_MAX_LABELS", str(MAX_REKOGNITION_LABELS + 1), "must be between"),
        ("AISTORY_REKOGNITION_MAX_LABELS", str(MIN_REKOGNITION_LABELS - 1), "must be between"),
        ("AISTORY_REKOGNITION_MIN_CONFIDENCE", str(MAX_REKOGNITION_CONFIDENCE + 1), "must be between"),
        ("AISTORY_REKOGNITION_MIN_CONFIDENCE", str(MIN_REKOGNITION_CONFIDENCE - 1), "must be between"),
        ("AISTORY_REKOGNITION_MAX_LABELS", "not_a_number", "must be an integer"),
        ("AISTORY_REKOGNITION_MIN_CONFIDENCE", "not_a_number", "must be a number"),
    ])
    @patch("boto3.client")
    def test_boundary_validation(self, env_var, invalid_value, expected_error, mock_boto3_client):
        """Test boundary validation for configuration parameters."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Set invalid environment variables
        os.environ[env_var] = invalid_value
        
        # Act & Assert
        with self.assertRaises(AIProviderConfigurationError) as context:
            AWSRekognitionProvider()
        
        # Verify error message contains expected text but doesn't expose invalid value directly
        self.assertIn("Invalid configuration parameter", str(context.exception))
        self.assertIn("aws_rekognition", str(context.exception))
    
    @patch("boto3.client")
    def test_initialization_with_no_credentials(self, mock_boto3_client):
        """Test provider initialization with missing AWS credentials."""
        # Arrange
        mock_boto3_client.side_effect = NoCredentialsError()
        
        # Act & Assert
        with self.assertRaises(AIProviderConfigurationError) as context:
            AWSRekognitionProvider()
        
        # Verify error message
        self.assertIn("AWS credentials not found", str(context.exception))
        self.assertIn("aws_rekognition", str(context.exception))
    
    @patch("boto3.client")
    def test_initialization_with_client_error(self, mock_boto3_client):
        """Test provider initialization with boto3 client error."""
        # Arrange
        error_response = {"Error": {"Code": "InvalidRegion", "Message": "Invalid region specified"}}
        mock_boto3_client.side_effect = ClientError(error_response, "CreateClient")
        
        # Act & Assert
        with self.assertRaises(AIProviderConfigurationError) as context:
            AWSRekognitionProvider()
        
        # Verify error message
        self.assertIn("Failed to initialize AWS Rekognition client", str(context.exception))
        self.assertIn("aws_rekognition", str(context.exception))
    
    @patch("boto3.client")
    def test_process_image_successful(self, mock_boto3_client):
        """Test successful image processing."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Create sample Rekognition API response
        sample_response = {
            "Labels": [
                {
                    "Name": "Dog",
                    "Confidence": 98.2,
                    "Parents": [
                        {"Name": "Animal"},
                        {"Name": "Pet"}
                    ]
                },
                {
                    "Name": "Grass",
                    "Confidence": 94.5,
                    "Parents": [
                        {"Name": "Plant"}
                    ]
                }
            ]
        }
        mock_client.detect_labels.return_value = sample_response
        
        # Act
        provider = AWSRekognitionProvider()
        result = provider.process_image(self.test_image_path)
        
        # Assert
        self.assertEqual(result["provider"], "aws_rekognition")
        self.assertEqual(result["task"], "detect_labels")
        self.assertIn("labels", result)
        self.assertEqual(len(result["labels"]), 2)
        
        # Check first label
        dog_label = result["labels"][0]
        self.assertEqual(dog_label["name"], "Dog")
        self.assertEqual(dog_label["confidence"], 98.2)
        self.assertEqual(dog_label["parents"], ["Animal", "Pet"])
        
        # Verify API call parameters
        mock_client.detect_labels.assert_called_once()
        call_kwargs = mock_client.detect_labels.call_args.kwargs
        self.assertEqual(call_kwargs["MaxLabels"], 10)
        self.assertEqual(call_kwargs["MinConfidence"], 75.0)
        self.assertIn("Image", call_kwargs)
        self.assertIn("Bytes", call_kwargs["Image"])
    
    @patch("boto3.client")
    @patch("backend.services.ai_processing.utils.validation.validate_image_file")
    @patch("backend.services.ai_processing.providers.aws_rekognition_provider.logger")
    def test_process_image_file_not_found(self, mock_logger, mock_validate, mock_boto3_client):
        """Test processing with non-existent image file."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Mock validation to pass but return a non-existent path
        non_existent_path = "/path/to/non-existent/image.jpg"
        mock_validate.return_value = non_existent_path
        
        # Act & Assert
        provider = AWSRekognitionProvider()
        with self.assertRaises(ImageProcessingError) as context:
            provider.process_image(non_existent_path)
        
        # Verify error message is sanitized (doesn't include full path)
        self.assertIn("Image file not found", str(context.exception))
        self.assertIn("aws_rekognition", str(context.exception))
        self.assertNotIn(non_existent_path, str(context.exception))
        
        # Verify proper logging occurred with the actual path
        mock_logger.error.assert_called_with(f"Image file not found: {non_existent_path}")
    
    @patch("backend.services.ai_processing.utils.validation.validate_image_file")
    @patch("boto3.client")
    @patch("builtins.open", new_callable=mock_open)
    @patch("backend.services.ai_processing.providers.aws_rekognition_provider.logger")
    def test_process_image_io_error(self, mock_logger, mock_file_open, mock_boto3_client, mock_validate):
        """Test processing with IO error when reading image file."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        # Make validation pass
        mock_validate.return_value = self.test_image_path
        
        # But make the file open operation fail
        mock_file_open.side_effect = IOError("Failed to read file: permission denied")
        
        # Act & Assert
        provider = AWSRekognitionProvider()
        with self.assertRaises(ImageProcessingError) as context:
            provider.process_image(self.test_image_path)
        
        # Verify error message is sanitized
        self.assertIn("Failed to read image file", str(context.exception))
        self.assertIn("aws_rekognition", str(context.exception))
        self.assertNotIn("permission denied", str(context.exception))
        
        # Verify proper logging occurred with the detailed error
        mock_logger.error.assert_called_with(ANY)
        self.assertTrue(any("permission denied" in str(call) for call in mock_logger.error.call_args_list))
    
    @patch("backend.services.ai_processing.utils.validation.validate_image_file")
    @patch("boto3.client")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test image data")
    @patch("backend.services.ai_processing.providers.aws_rekognition_provider.logger")
    def test_process_image_invalid_parameters(self, mock_logger, mock_file_open, mock_boto3_client, mock_validate):
        """Test process_image with parameter validation error."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        # Make validation pass
        mock_validate.return_value = self.test_image_path
        
        # Create a detailed error report
        detailed_error = "Invalid parameter format: Parameter validation failed:\nInvalid type for parameter Image, value: None, type: <class 'NoneType'>, valid types: <class 'dict'>"
        mock_client.detect_labels.side_effect = ParamValidationError(report=detailed_error)
        
        # Act & Assert
        provider = AWSRekognitionProvider()
        with self.assertRaises(ImageProcessingError) as context:
            provider.process_image(self.test_image_path)
        
        # Verify error message
        self.assertIn("Invalid parameters provided", str(context.exception))
        self.assertIn("aws_rekognition", str(context.exception))
        
        # Make sure the detailed error is not in the exception message
        self.assertNotIn(detailed_error, str(context.exception))
        
        # Verify the detailed error was properly logged
        mock_logger.error.assert_called_with(ANY)
        self.assertTrue(any(detailed_error in str(call) for call in mock_logger.error.call_args_list))
    
    @parameterized.expand([
        # Authentication/Connection errors
        ("ExpiredTokenException", AIProviderConnectionError, "AWS authentication/connection error"),
        ("InvalidSignatureException", AIProviderConnectionError, "AWS authentication/connection error"),
        ("UnrecognizedClientException", AIProviderConnectionError, "AWS authentication/connection error"),
        ("AuthFailure", AIProviderConnectionError, "AWS authentication/connection error"),
        # Processing errors
        ("InvalidImageFormatException", ImageProcessingError, "Rekognition API error"),
        ("ThrottlingException", ImageProcessingError, "Rekognition API error"),
        ("AccessDeniedException", ImageProcessingError, "Rekognition API error")
    ])
    @patch("boto3.client")
    @patch("backend.services.ai_processing.utils.validation.validate_image_file")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test image data")
    @patch("backend.services.ai_processing.providers.aws_rekognition_provider.logger")
    def test_process_image_client_errors(self, error_code, expected_exception, expected_message,
                                         mock_logger, mock_file_open, mock_boto3_client, mock_validate):
        """Test process_image with different boto ClientError types."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Make validation pass
        mock_validate.return_value = self.test_image_path
        
        # Create a detailed error response with sensitive details
        detailed_message = f"{error_code} error message with sensitive AWS request ID: 4aabb2c-1af3-45g6-90hz and account ID: 123456789012"
        error_response = {"Error": {"Code": error_code, "Message": detailed_message}}
        mock_client.detect_labels.side_effect = ClientError(error_response, "DetectLabels")
        
        # Act & Assert
        provider = AWSRekognitionProvider()
        with self.assertRaises(expected_exception) as context:
            provider.process_image(self.test_image_path)
        
        # Verify error message contains expected text
        self.assertIn(expected_message, str(context.exception))
        self.assertIn(error_code, str(context.exception))
        
        # Verify the sensitive details are not exposed in the exception
        self.assertNotIn("request ID", str(context.exception))
        self.assertNotIn("account ID", str(context.exception))
        
        # Verify the detailed error was properly logged
        mock_logger.error.assert_called_with(ANY)
        self.assertTrue(any(error_code in str(call) for call in mock_logger.error.call_args_list))
    
    @patch("boto3.client")
    def test_parse_rekognition_response_with_labels(self, mock_boto3_client):
        """Test parsing Rekognition response with labels."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        sample_response = {
            "Labels": [
                {
                    "Name": "Person",
                    "Confidence": 99.5,
                    "Parents": []
                },
                {
                    "Name": "Clothing",
                    "Confidence": 96.1,
                    "Parents": [{"Name": "Person"}]
                }
            ]
        }
        
        # Act
        provider = AWSRekognitionProvider()
        result = provider._parse_rekognition_response(sample_response)
        
        # Assert
        self.assertEqual(result["provider"], "aws_rekognition")
        self.assertEqual(result["task"], "detect_labels")
        self.assertEqual(len(result["labels"]), 2)
        
        self.assertEqual(result["labels"][0]["name"], "Person")
        self.assertEqual(result["labels"][0]["confidence"], 99.5)
        self.assertEqual(result["labels"][0]["parents"], [])
        
        self.assertEqual(result["labels"][1]["name"], "Clothing")
        self.assertEqual(result["labels"][1]["confidence"], 96.1)
        self.assertEqual(result["labels"][1]["parents"], ["Person"])
    
    @patch("boto3.client")
    def test_parse_rekognition_response_with_no_labels(self, mock_boto3_client):
        """Test parsing Rekognition response with no labels."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        sample_response = {"Labels": []}
        
        # Act
        provider = AWSRekognitionProvider()
        result = provider._parse_rekognition_response(sample_response)
        
        # Assert
        self.assertEqual(result["provider"], "aws_rekognition")
        self.assertEqual(result["task"], "detect_labels")
        self.assertEqual(len(result["labels"]), 0)
        
    @patch("boto3.client")
    def test_image_format_validation(self, mock_boto3_client):
        """Test validation of image formats."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        provider = AWSRekognitionProvider()
        
        # Test with various invalid file extensions
        invalid_extensions = [
            "/path/to/image.txt",
            "/path/to/image.pdf",
            "/path/to/image.doc",
            "/path/to/image.exe",
            "/path/to/image.js",
            "relative/path/no_extension",
            "../path/traversal/attempt.jpg"  # Path traversal attempt
        ]
        
        for invalid_path in invalid_extensions:
            with self.subTest(invalid_path=invalid_path):
                with self.assertRaises(ImageProcessingError) as context:
                    provider.process_image(invalid_path)
                
                # Verify error message mentions invalid format
                error_msg = str(context.exception)
                self.assertTrue(
                    "Invalid image" in error_msg or
                    "Unsupported image format" in error_msg or
                    "not a valid image" in error_msg
                )
                
                # Ensure the provider name is included
                self.assertIn("aws_rekognition", error_msg)
                
    @patch("boto3.client")
    @patch("backend.services.ai_processing.providers.aws_rekognition_provider.logger")
    def test_proper_logging(self, mock_logger, mock_boto3_client):
        """Test that proper logging is implemented at appropriate levels."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        # Act - initialize provider
        provider = AWSRekognitionProvider()
        
        # Assert - verify initialization logging
        mock_logger.info.assert_any_call(
            f"AWS Rekognition provider initialized successfully with max_labels={provider.max_labels}, min_confidence={provider.min_confidence}"
        )
        
        # Set up mock for successful API response
        sample_response = {"Labels": [{"Name": "Test", "Confidence": 99.0, "Parents": []}]}
        mock_client.detect_labels.return_value = sample_response
        
        # Mock validate_image_file to avoid validation errors
        with patch("backend.services.ai_processing.utils.validation.validate_image_file", return_value=self.test_image_path):
            with patch("builtins.open", mock_open(read_data=b"test image data")):
                # Act - process an image
                result = provider.process_image(self.test_image_path)
                
                # Assert - verify processing logging
                mock_logger.info.assert_any_call(f"Processing image with AWS Rekognition: {os.path.basename(self.test_image_path)}")
                mock_logger.info.assert_any_call(f"Successfully processed image with Rekognition, found {len(result.get('labels', []))} labels")
                
                # Debug level logging should also occur
                self.assertTrue(mock_logger.debug.called)
    
    @patch("boto3.client")
    def test_parse_rekognition_response_missing_labels_key(self, mock_boto3_client):
        """Test parsing Rekognition response with missing Labels key."""
        # Arrange
        mock_client = MagicMock()
        mock_boto3_client.return_value = mock_client
        
        sample_response = {}  # No Labels key
        
        # Act
        provider = AWSRekognitionProvider()
        result = provider._parse_rekognition_response(sample_response)
        
        # Assert
        self.assertEqual(result["provider"], "aws_rekognition")
        self.assertEqual(result["task"], "detect_labels")
        self.assertEqual(len(result["labels"]), 0)


if __name__ == "__main__":
    unittest.main()