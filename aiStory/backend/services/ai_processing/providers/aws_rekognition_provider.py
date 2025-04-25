"""AWS Rekognition AI Provider implementation for the AI Story Creator."""
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ParamValidationError

from ..base import AIProviderBase
from ..exceptions import (
    AIProcessingError,
    AIProviderConfigurationError,
    AIProviderConnectionError,
    ImageProcessingError
)
from ..utils.validation import (
    validate_image_file,
    validate_rekognition_max_labels,
    validate_rekognition_min_confidence
)
from backend.config import get_settings

# Set up logger
logger = logging.getLogger(__name__)

# Define constants for provider name and default config values
PROVIDER_NAME = "aws_rekognition"
DEFAULT_MAX_LABELS = 10
DEFAULT_MIN_CONFIDENCE = 75.0


class AWSRekognitionProvider(AIProviderBase):
    """AI Provider implementation using AWS Rekognition for image labeling."""

    def __init__(self):
        """Initialize the Rekognition provider."""
        self.settings = get_settings()
        self.region = getattr(self.settings, "aws_region", None)
        self.rekognition_client = None
        
        # Validate and set max_labels with boundary check
        try:
            max_labels_setting = getattr(self.settings, "rekognition_max_labels", DEFAULT_MAX_LABELS)
            self.max_labels = validate_rekognition_max_labels(max_labels_setting)
            
            # Validate and set min_confidence with boundary check
            min_confidence_setting = getattr(self.settings, "rekognition_min_confidence", DEFAULT_MIN_CONFIDENCE)
            self.min_confidence = validate_rekognition_min_confidence(min_confidence_setting)
        except ValueError as e:
            logger.error(f"Configuration validation error: {str(e)}")
            raise AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message=f"Invalid configuration parameter: {str(e)}"
            )

        if not self.region:
            logger.error("AWS region not configured")
            raise AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message="AWS region is not configured (AISTORY_AWS_REGION)."
            )

        try:
            logger.info(f"Initializing AWS Rekognition client in region {self.region}")
            self.rekognition_client = boto3.client('rekognition', region_name=self.region)
        except NoCredentialsError:
            logger.error("AWS credentials not found or configured correctly")
            raise AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message="AWS credentials not found or configured correctly."
            )
        except ClientError as e:
            # Log the full error for internal diagnostics but don't expose in the exception
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Failed to initialize AWS Rekognition client: {error_code}, Details: {str(e)}")
            
            # Return a sanitized error message
            raise AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message=f"Failed to initialize AWS Rekognition client: {error_code}"
            )
        except Exception as e:  # Catch any other unexpected init errors
            logger.error(f"Unexpected error during Rekognition client initialization: {str(e)}", exc_info=True)
            
            # Return a sanitized error message
            raise AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message="An unexpected error occurred during Rekognition client initialization."
            )
        
        logger.info(f"AWS Rekognition provider initialized successfully with max_labels={self.max_labels}, min_confidence={self.min_confidence}")

    def get_provider_name(self) -> str:
        """Get the name of this AI provider."""
        return PROVIDER_NAME

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image using Rekognition detect_labels.
        
        Args:
            image_path: The path to the image file to process
            
        Returns:
            Dict containing the processed image labels and metadata
            
        Raises:
            ImageProcessingError: If the image cannot be processed
            AIProviderConnectionError: If there's an authentication or connection issue
        """
        logger.info(f"Processing image with AWS Rekognition: {os.path.basename(image_path)}")
        
        try:
            # Validate image path and format - prevents path traversal and ensures proper format
            validated_path = validate_image_file(image_path)
            logger.debug(f"Image validated successfully: {validated_path}")
            
            try:
                with open(validated_path, 'rb') as image_file:
                    image_bytes = image_file.read()
                    logger.debug(f"Successfully read image file: {os.path.basename(validated_path)} ({len(image_bytes)} bytes)")
            except FileNotFoundError:
                logger.error(f"Image file not found: {validated_path}")
                raise ImageProcessingError(
                    provider_name=PROVIDER_NAME,
                    message=f"Image file not found",
                    image_path=image_path
                )
            except IOError as e:
                logger.error(f"Failed to read image file {validated_path}: {str(e)}")
                raise ImageProcessingError(
                    provider_name=PROVIDER_NAME,
                    message=f"Failed to read image file",
                    image_path=image_path
                )

            try:
                logger.debug(f"Calling Rekognition detect_labels with MaxLabels={self.max_labels}, MinConfidence={self.min_confidence}")
                response = self.rekognition_client.detect_labels(
                    Image={'Bytes': image_bytes},
                    MaxLabels=self.max_labels,
                    MinConfidence=self.min_confidence
                )

                parsed_results = self._parse_rekognition_response(response)
                logger.info(f"Successfully processed image with Rekognition, found {len(parsed_results.get('labels', []))} labels")
                return parsed_results

            except ParamValidationError as e:
                # Log the detailed error but return a sanitized message
                logger.error(f"Invalid parameters provided to Rekognition API: {str(e)}")
                raise ImageProcessingError(
                    provider_name=PROVIDER_NAME,
                    message="Invalid parameters provided to Rekognition API",
                    image_path=image_path
                )
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                error_message = e.response.get('Error', {}).get('Message', str(e))
                
                # Log the full error details for debugging
                logger.error(f"AWS Rekognition API error: {error_code}: {error_message}")

                # Distinguish between connection/auth errors and processing errors
                auth_error_codes = ['ExpiredTokenException', 'InvalidSignatureException',
                                'UnrecognizedClientException', 'AuthFailure']
                if error_code in auth_error_codes:
                    # Authentication errors - sanitize message
                    raise AIProviderConnectionError(
                        provider_name=PROVIDER_NAME,
                        message=f"AWS authentication/connection error ({error_code})"
                    )
                else:  # Treat other ClientErrors as image processing issues
                    # Processing errors - sanitize message
                    raise ImageProcessingError(
                        provider_name=PROVIDER_NAME,
                        message=f"Rekognition API error ({error_code})",
                        image_path=image_path
                    )
            except Exception as e:  # Catch any other unexpected processing errors
                # Log the full exception details
                logger.error(f"Unexpected error during Rekognition processing: {str(e)}", exc_info=True)
                
                # Return a sanitized error message
                raise ImageProcessingError(
                    provider_name=PROVIDER_NAME,
                    message="An unexpected error occurred during image processing",
                    image_path=image_path
                )
                
        except ValueError as e:
            # This catches validation errors from our validation utilities
            logger.error(f"Image validation error: {str(e)}")
            raise ImageProcessingError(
                provider_name=PROVIDER_NAME,
                message=f"Invalid image: {str(e)}",
                image_path=image_path
            )

    def _parse_rekognition_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the raw Rekognition detect_labels response.
        
        Args:
            response: The raw response from AWS Rekognition
            
        Returns:
            Dict containing parsed and structured response data
        """
        logger.debug("Parsing Rekognition response")
        labels_data = []
        if 'Labels' in response:
            for label in response['Labels']:
                label_info = {
                    "name": label.get('Name'),
                    "confidence": label.get('Confidence'),
                    "parents": [parent['Name'] for parent in label.get('Parents', [])]
                }
                labels_data.append(label_info)
                logger.debug(f"Found label: {label.get('Name')} with confidence {label.get('Confidence')}")

        return {
            "provider": PROVIDER_NAME,
            "task": "detect_labels",
            "labels": labels_data
        }