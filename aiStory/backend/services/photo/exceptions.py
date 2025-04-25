"""Exceptions for the photo service."""


class PhotoServiceError(Exception):
    """Base exception for all photo service errors."""
    pass


class PhotoUploadError(PhotoServiceError):
    """Exception raised when a photo upload fails."""
    pass


class PhotoNotFoundError(PhotoServiceError):
    """Exception raised when a photo is not found."""
    pass


class PhotoProcessingError(PhotoServiceError):
    """Exception raised when photo processing fails."""
    pass


class InvalidPhotoError(PhotoServiceError):
    """Exception raised when a photo is invalid (e.g., wrong format)."""
    pass


class StorageError(PhotoServiceError):
    """Exception raised when a storage operation fails."""
    pass


class PhotoQuotaExceededError(PhotoServiceError):
    """Exception raised when a user's photo quota is exceeded."""
    pass