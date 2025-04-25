"""Photo storage services package.

This package provides storage services for handling file uploads, retrievals, and deletions
for the application, supporting different storage backends such as local filesystem and S3.
"""

from backend.services.storage.base import StorageService, StorageError
from backend.services.storage.local_storage import LocalStorageService
from backend.services.storage.s3_storage import S3StorageService
from backend.services.storage.factory import StorageServiceFactory

__all__ = [
    "StorageService",
    "StorageError",
    "LocalStorageService",
    "S3StorageService",
    "StorageServiceFactory",
]