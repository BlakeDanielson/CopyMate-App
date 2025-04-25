"""Validation utilities for AI processing services."""
import logging
import os
import mimetypes
from typing import List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

# Define constants for validation
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
ALLOWED_IMAGE_MIMETYPES = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp']

# Parameter boundaries
MIN_REKOGNITION_LABELS = 1
MAX_REKOGNITION_LABELS = 100
MIN_REKOGNITION_CONFIDENCE = 0.0
MAX_REKOGNITION_CONFIDENCE = 100.0


def validate_file_path(file_path: Union[str, Path], 
                       base_directory: Optional[str] = None,
                       must_exist: bool = True) -> str:
    """
    Validate a file path to prevent path traversal attacks.
    
    Args:
        file_path: The file path to validate
        base_directory: Optional base directory that the file must be contained within
        must_exist: Whether the file must exist (default: True)
        
    Returns:
        The validated absolute file path as a string
        
    Raises:
        ValueError: If the file path is invalid, outside the base directory, or doesn't exist
    """
    # Convert to Path object for safer path handling
    path = Path(file_path).resolve()
    
    # Check if file exists if required
    if must_exist and not path.exists():
        logger.warning(f"Validated file does not exist: {path}")
        raise ValueError(f"File does not exist: {path}")
    
    # If a base directory is specified, validate the file is within that directory
    if base_directory:
        base_path = Path(base_directory).resolve()
        
        # Check if the file is within the base directory
        if not str(path).startswith(str(base_path)):
            logger.warning(f"Path traversal attempt: {path} is outside of {base_path}")
            raise ValueError(f"File path must be within the specified base directory")
    
    # Convert back to string
    return str(path)


def validate_image_file(file_path: Union[str, Path], 
                        base_directory: Optional[str] = None) -> str:
    """
    Validate that a file is a valid image of an allowed format.
    
    Args:
        file_path: The image file path to validate
        base_directory: Optional base directory that the image must be contained within
        
    Returns:
        The validated absolute file path as a string
        
    Raises:
        ValueError: If the file is not a valid image or has an unsupported format
    """
    # First validate the path
    validated_path = validate_file_path(file_path, base_directory)
    
    # Check file extension
    _, ext = os.path.splitext(validated_path.lower())
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        logger.warning(f"Invalid image extension: {ext} for file {validated_path}")
        raise ValueError(f"Unsupported image format: {ext}. Supported formats: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")
    
    # Check mimetype for additional verification
    mime_type, _ = mimetypes.guess_type(validated_path)
    if not mime_type or mime_type not in ALLOWED_IMAGE_MIMETYPES:
        logger.warning(f"Invalid mime type: {mime_type} for file {validated_path}")
        raise ValueError(f"File does not appear to be a valid image: {validated_path}")
    
    return validated_path


def validate_rekognition_max_labels(max_labels: int) -> int:
    """
    Validate the rekognition_max_labels parameter.
    
    Args:
        max_labels: The maximum number of labels to return
        
    Returns:
        The validated max_labels value
        
    Raises:
        ValueError: If max_labels is outside the allowed range
    """
    if not isinstance(max_labels, int):
        try:
            max_labels = int(max_labels)
        except (ValueError, TypeError):
            logger.warning(f"Invalid max_labels value (not an integer): {max_labels}")
            raise ValueError(f"rekognition_max_labels must be an integer between {MIN_REKOGNITION_LABELS} and {MAX_REKOGNITION_LABELS}")
    
    if max_labels < MIN_REKOGNITION_LABELS or max_labels > MAX_REKOGNITION_LABELS:
        logger.warning(f"Invalid max_labels value (out of range): {max_labels}")
        raise ValueError(f"rekognition_max_labels must be between {MIN_REKOGNITION_LABELS} and {MAX_REKOGNITION_LABELS}")
    
    return max_labels


def validate_rekognition_min_confidence(min_confidence: float) -> float:
    """
    Validate the rekognition_min_confidence parameter.
    
    Args:
        min_confidence: The minimum confidence level (percentage)
        
    Returns:
        The validated min_confidence value
        
    Raises:
        ValueError: If min_confidence is outside the allowed range
    """
    try:
        min_confidence = float(min_confidence)
    except (ValueError, TypeError):
        logger.warning(f"Invalid min_confidence value (not a number): {min_confidence}")
        raise ValueError(f"rekognition_min_confidence must be a number between {MIN_REKOGNITION_CONFIDENCE} and {MAX_REKOGNITION_CONFIDENCE}")
    
    if min_confidence < MIN_REKOGNITION_CONFIDENCE or min_confidence > MAX_REKOGNITION_CONFIDENCE:
        logger.warning(f"Invalid min_confidence value (out of range): {min_confidence}")
        raise ValueError(f"rekognition_min_confidence must be between {MIN_REKOGNITION_CONFIDENCE} and {MAX_REKOGNITION_CONFIDENCE}")
    
    return min_confidence