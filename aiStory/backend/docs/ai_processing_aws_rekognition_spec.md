# Specification: AWS Rekognition AI Provider

This document outlines the specification and pseudocode for implementing the AWS Rekognition provider for image labeling within the AI Story Creator backend.

**Target File:** `backend/services/ai_processing/providers/aws_rekognition_provider.py`

## 1. Objective

Implement the `AIProviderBase` interface (`backend/services/ai_processing/base.py`) to perform image labeling (tagging) using the AWS Rekognition `detect_labels` API via the `boto3` SDK.

## 2. Configuration

The provider requires AWS configuration. Following the project's pattern (`backend/config.py`), these settings should be managed via environment variables (prefixed with `AISTORY_`) or the root `.env` file. **Credentials must NOT be hardcoded.**

**Required Settings:**

*   `AISTORY_AWS_REGION`: (String) The AWS region where the Rekognition service will be called (e.g., `us-east-1`).
*   **Credentials:** The provider will rely on the standard `boto3` credential resolution chain:
    1.  Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`).
    2.  Shared credential file (`~/.aws/credentials`).
    3.  AWS config file (`~/.aws/config`).
    4.  IAM role attached to the compute environment (e.g., EC2 instance profile, ECS task role).
    *   *Note:* While the existing `config.py` has S3-specific credential settings (`AISTORY_STORAGE_S3_ACCESS_KEY_ID`, etc.), we will rely on the standard `boto3` chain for Rekognition unless a specific need arises to override it. This promotes standard AWS practices.

**Optional Settings:**

*   `AISTORY_REKOGNITION_MAX_LABELS`: (Integer, default: 10) Maximum number of labels to return.
*   `AISTORY_REKOGNITION_MIN_CONFIDENCE`: (Float, default: 75.0) Minimum confidence level for labels to be included.

These settings should be added to the `Settings` class in `backend/config.py`.

## 3. Input/Output

*   **Input:** The `process_image(self, image_path: str)` method receives the path to the image file on the local filesystem where the backend worker is running. The provider implementation must read the image file content as bytes.
*   **Output:** The `process_image` method must return a dictionary (`Dict[str, Any]`) conforming to the structure expected by the `ai_results` field in the `Photo` schema (`backend/schemas/photo.py`).

**Output Dictionary Schema (`ai_results`):**

```json
{
  "provider": "aws_rekognition",
  "task": "detect_labels",
  "labels": [
    {
      "name": "LabelName", // e.g., "Dog", "Outdoors"
      "confidence": 99.5, // Float percentage
      "parents": ["Parent1", "Parent2"] // List of parent categories, if any
    },
    // ... more labels
  ]
}
```

## 4. Error Handling

The provider must catch relevant exceptions and raise corresponding custom exceptions defined in `backend/services/ai_processing/exceptions.py`.

*   **Configuration Issues:**
    *   Missing region: Raise `AIProviderConfigurationError`.
    *   `boto3` client initialization errors: Raise `AIProviderConfigurationError`.
*   **Connection/Authentication Issues:**
    *   `botocore.exceptions.NoCredentialsError`: Raise `AIProviderConfigurationError` (as it's a setup issue).
    *   `botocore.exceptions.ClientError` (related to connection/auth): Raise `AIProviderConnectionError`.
*   **Image Processing Issues:**
    *   `FileNotFoundError` when reading `image_path`: Raise `ImageProcessingError`.
    *   `IOError` when reading `image_path`: Raise `ImageProcessingError`.
    *   `botocore.exceptions.ClientError` (from `detect_labels` API call, e.g., throttling, invalid image format, permissions): Raise `ImageProcessingError`. Include details from the AWS error response.
    *   `botocore.exceptions.ParamValidationError`: Raise `ImageProcessingError`.

All raised custom exceptions should include the provider name ("aws_rekognition").

## 5. Pseudocode

```python
# File: backend/services/ai_processing/providers/aws_rekognition_provider.py

IMPORT ABC, abstractmethod from abc
IMPORT Dict, Any, List from typing
IMPORT boto3
IMPORT ClientError from botocore.exceptions
IMPORT NoCredentialsError from botocore.exceptions
IMPORT ParamValidationError from botocore.exceptions

IMPORT AIProviderBase from ..base
IMPORT AIProcessingError, AIProviderConfigurationError, AIProviderConnectionError, ImageProcessingError from ..exceptions
IMPORT get_settings # Assuming settings are accessible, e.g., via dependency injection or global import

# Define constants for provider name and default config values
PROVIDER_NAME = "aws_rekognition"
DEFAULT_MAX_LABELS = 10
DEFAULT_MIN_CONFIDENCE = 75.0

CLASS AWSRekognitionProvider(AIProviderBase):
    """AI Provider implementation using AWS Rekognition for image labeling."""

    DEFINE __init__(self):
        """Initialize the Rekognition provider."""
        # TDD Anchor: Test initialization with valid/invalid config
        self.settings = get_settings() # Or receive settings via constructor/DI
        self.region = self.settings.aws_region # Get from config.py settings
        self.max_labels = self.settings.rekognition_max_labels OR DEFAULT_MAX_LABELS
        self.min_confidence = self.settings.rekognition_min_confidence OR DEFAULT_MIN_CONFIDENCE
        self.rekognition_client = None

        IF NOT self.region:
            RAISE AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message="AWS region is not configured (AISTORY_AWS_REGION)."
            )

        TRY:
            # TDD Anchor: Mock boto3.client call
            # Rely on standard boto3 credential chain (env vars, ~/.aws/credentials, IAM role etc.)
            self.rekognition_client = boto3.client('rekognition', region_name=self.region)
            # Perform a simple test call to verify credentials/connection early (optional but recommended)
            # Example: self.rekognition_client.list_collections(MaxResults=1)
        EXCEPT NoCredentialsError as e:
            RAISE AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message=f"AWS credentials not found or configured correctly: {e}"
            )
        EXCEPT ClientError as e:
            # Catch potential client init errors (e.g., invalid region)
             RAISE AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message=f"Failed to initialize AWS Rekognition client: {e}"
            )
        EXCEPT Exception as e: # Catch any other unexpected init errors
             RAISE AIProviderConfigurationError(
                provider_name=PROVIDER_NAME,
                message=f"An unexpected error occurred during Rekognition client initialization: {e}"
            )

    DEFINE get_provider_name(self) -> str:
        """Get the name of this AI provider."""
        RETURN PROVIDER_NAME

    DEFINE process_image(self, image_path: str) -> Dict[str, Any]:
        """Process an image using Rekognition detect_labels."""
        # TDD Anchor: Test with valid/invalid image paths

        TRY:
            WITH open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
        EXCEPT FileNotFoundError:
            RAISE ImageProcessingError(
                provider_name=PROVIDER_NAME,
                message=f"Image file not found at path: {image_path}",
                image_path=image_path
            )
        EXCEPT IOError as e:
            RAISE ImageProcessingError(
                provider_name=PROVIDER_NAME,
                message=f"Failed to read image file {image_path}: {e}",
                image_path=image_path
            )

        TRY:
            # TDD Anchor: Mock rekognition_client.detect_labels call and its response/exceptions
            response = self.rekognition_client.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=self.max_labels,
                MinConfidence=self.min_confidence
            )

            # TDD Anchor: Test parsing of various valid Rekognition responses
            parsed_results = self._parse_rekognition_response(response)
            RETURN parsed_results

        EXCEPT ParamValidationError as e:
             RAISE ImageProcessingError(
                provider_name=PROVIDER_NAME,
                message=f"Invalid parameters provided to Rekognition API: {e}",
                image_path=image_path
            )
        EXCEPT ClientError as e:
            # TDD Anchor: Test mapping of specific ClientErrors (e.g., throttling, access denied)
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))

            # Distinguish between connection/auth errors and processing errors if possible
            IF error_code in ['ExpiredTokenException', 'InvalidSignatureException', 'UnrecognizedClientException', 'AuthFailure']:
                 RAISE AIProviderConnectionError(
                    provider_name=PROVIDER_NAME,
                    message=f"AWS authentication/connection error ({error_code}): {error_message}"
                )
            ELSE: # Treat other ClientErrors as image processing issues
                 RAISE ImageProcessingError(
                    provider_name=PROVIDER_NAME,
                    message=f"Rekognition API error ({error_code}): {error_message}",
                    image_path=image_path
                )
        EXCEPT Exception as e: # Catch any other unexpected processing errors
             RAISE ImageProcessingError(
                provider_name=PROVIDER_NAME,
                message=f"An unexpected error occurred during Rekognition processing: {e}",
                image_path=image_path
            )

    DEFINE _parse_rekognition_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the raw Rekognition detect_labels response."""
        # TDD Anchor: Test this parsing logic thoroughly
        labels_data = []
        IF 'Labels' in response:
            FOR label in response['Labels']:
                label_info = {
                    "name": label.get('Name'),
                    "confidence": label.get('Confidence'),
                    "parents": [parent['Name'] for parent in label.get('Parents', [])]
                }
                labels_data.append(label_info)

        RETURN {
            "provider": PROVIDER_NAME,
            "task": "detect_labels",
            "labels": labels_data
        }

# END CLASS AWSRekognitionProvider

```

## 6. Testing Considerations (TDD Anchors)

*   **Initialization:**
    *   Test successful initialization with valid configuration (mock `boto3.client`).
    *   Test initialization failure with missing region (`AIProviderConfigurationError`).
    *   Test initialization failure due to `boto3` client errors (e.g., `NoCredentialsError`, `ClientError`) raising `AIProviderConfigurationError` or `AIProviderConnectionError`.
*   **`process_image` Method:**
    *   Mock file reading (`open`) to simulate `FileNotFoundError` and `IOError`, ensuring `ImageProcessingError` is raised.
    *   Mock `rekognition_client.detect_labels` call:
        *   Simulate successful API calls with various realistic responses (e.g., multiple labels, no labels, labels with/without parents). Verify the output dictionary structure and content using `_parse_rekognition_response`.
        *   Simulate API errors (`ClientError` with different error codes like `ThrottlingException`, `InvalidImageFormatException`, `AccessDeniedException`, `ExpiredTokenException`). Verify that the correct custom exceptions (`ImageProcessingError`, `AIProviderConnectionError`) are raised with appropriate messages.
        *   Simulate `ParamValidationError` and verify `ImageProcessingError` is raised.
*   **`_parse_rekognition_response` Method:**
    *   Test directly with sample Rekognition `detect_labels` response dictionaries (including edge cases like empty `Labels` list, missing `Parents`) to ensure correct parsing into the target output schema.