"""AWS S3 implementation of the StorageService interface."""

import os
import uuid
import logging
from typing import BinaryIO, Dict, Optional
from urllib.parse import urljoin

# Import boto3 conditionally to avoid errors if it's not installed
try:
    import boto3
    import botocore
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from backend.config import Settings
from backend.services.storage.base import StorageService, StorageError

logger = logging.getLogger(__name__)


class S3StorageService(StorageService):
    """Implementation of StorageService that stores files in AWS S3.
    
    This implementation is intended for production use and requires boto3 to be installed.
    It stores files in a configurable S3 bucket and generates pre-signed URLs for access.
    """
    
    def __init__(self, settings: Settings):
        """Initialize the S3 storage service.
        
        Args:
            settings: Application settings
            
        Raises:
            ImportError: If boto3 is not installed
            StorageError: If S3 configuration is invalid
        """
        self.settings = settings
        self.provider = "s3"
        
        # Check if boto3 is available
        if not BOTO3_AVAILABLE:
            error_msg = "boto3 is required for S3StorageService but is not installed. Install with 'pip install boto3'"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        # Validate settings
        if not settings.storage_s3_bucket:
            error_msg = "S3 bucket name is required for S3StorageService"
            logger.error(error_msg)
            raise StorageError(error_msg)
            
        if not settings.storage_s3_region:
            error_msg = "S3 region is required for S3StorageService"
            logger.error(error_msg)
            raise StorageError(error_msg)
            
        self.bucket_name = settings.storage_s3_bucket
        self.region = settings.storage_s3_region
        
        # Initialize S3 client
        try:
            # Start with basic S3 client configuration
            client_kwargs = {
                'region_name': self.region
            }
            
            # Add custom endpoint URL if provided
            if settings.storage_s3_endpoint_url:
                client_kwargs['endpoint_url'] = settings.storage_s3_endpoint_url
                
            # Add credentials if provided
            if settings.storage_s3_access_key_id and settings.storage_s3_secret_access_key:
                client_kwargs['aws_access_key_id'] = settings.storage_s3_access_key_id
                client_kwargs['aws_secret_access_key'] = settings.storage_s3_secret_access_key
            
            self.s3_client = boto3.client('s3', **client_kwargs)
            
            logger.info(
                f"S3StorageService initialized with bucket: {self.bucket_name}, "
                f"region: {self.region}, "
                f"endpoint: {settings.storage_s3_endpoint_url or 'default AWS'}"
            )
        except Exception as e:
            error_msg = f"Failed to initialize S3 client: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    async def upload_file(
        self, 
        file: BinaryIO, 
        key: str, 
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file to S3.
        
        Args:
            file: File-like object to upload
            key: Storage key/path where the file will be stored
            metadata: Optional metadata to associate with the file
            content_type: Optional content type of the file
            
        Returns:
            URL to access the uploaded file
            
        Raises:
            StorageError: If an error occurs during upload
        """
        try:
            extra_args = {}
            
            if metadata:
                extra_args['Metadata'] = metadata
                
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Upload file to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"File uploaded to S3: {self.bucket_name}/{key}")
            return await self.get_file_url(key)
            
        except Exception as e:
            error_msg = f"Failed to upload file to S3: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    async def get_file_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing a file in S3.
        
        Args:
            key: Storage key identifying the file
            expires_in: Optional expiration time in seconds for the URL (default: 3600)
            
        Returns:
            Pre-signed URL to access the file
            
        Raises:
            StorageError: If an error occurs generating the URL
            FileNotFoundError: If the file does not exist
        """
        try:
            # Check if file exists
            if not await self.file_exists(key):
                error_msg = f"File not found in S3: {self.bucket_name}/{key}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Generate pre-signed URL
            expiration = expires_in or 3600  # Default to 1 hour
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            
            return url
            
        except FileNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to generate pre-signed URL for S3 file: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    async def delete_file(self, key: str) -> bool:
        """Delete a file from S3.
        
        Args:
            key: Storage key identifying the file to delete
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            StorageError: If an error occurs during deletion
        """
        try:
            # Check if file exists
            if not await self.file_exists(key):
                logger.warning(f"Attempted to delete non-existent file: {self.bucket_name}/{key}")
                return False
            
            # Delete file from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(f"File deleted from S3: {self.bucket_name}/{key}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete file from S3: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    async def file_exists(self, key: str) -> bool:
        """Check if a file exists in S3.
        
        Args:
            key: Storage key identifying the file
            
        Returns:
            True if the file exists, False otherwise
            
        Raises:
            StorageError: If an error occurs checking the file
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            error_msg = f"Error checking if file exists in S3: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Failed to check if file exists in S3: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e
    
    def generate_key(self, user_id: int, filename: str) -> str:
        """Generate a storage key for a file in S3.
        
        Args:
            user_id: User ID associated with the file
            filename: Original filename
            
        Returns:
            Storage key to use for the file
        """
        # Extract file extension
        _, ext = os.path.splitext(filename)
        
        # Generate a UUID for the file
        file_uuid = str(uuid.uuid4())
        
        # Create a path with user_id/yyyy-mm-dd/uuid.ext format
        import datetime
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return f"{user_id}/{date_str}/{file_uuid}{ext.lower()}"
        
    async def generate_presigned_upload_url(
        self,
        bucket: str,
        object_key: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None,
        expires_in: int = 3600
    ) -> Dict[str, Any]:
        """Generate a pre-signed URL for direct file uploads to S3.
        
        Args:
            bucket: Storage bucket name (will use the default if not specified)
            object_key: Key/path where the file will be stored
            content_type: Content type of the file to be uploaded
            metadata: Optional metadata to associate with the file
            expires_in: Expiration time for the URL in seconds (default: 1 hour)
            
        Returns:
            Dict containing the presigned URL and fields needed for upload
            
        Raises:
            StorageError: If an error occurs generating the URL
        """
        try:
            # Use the instance bucket if none specified
            bucket_name = bucket or self.bucket_name
            
            # Prepare conditions and fields
            fields = {}
            conditions = []
            
            # Set content type
            if content_type:
                fields['Content-Type'] = content_type
                conditions.append({'Content-Type': content_type})
            
            # Add metadata if provided
            if metadata:
                for key, value in metadata.items():
                    metadata_key = f'x-amz-meta-{key}'
                    fields[metadata_key] = value
                    conditions.append({metadata_key: value})
            
            # Generate the presigned POST data
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=bucket_name,
                Key=object_key,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expires_in
            )
            
            # Return in the format expected by the API
            return {
                "url": presigned_post['url'],
                "fields": presigned_post['fields']
            }
            
        except Exception as e:
            error_msg = f"Failed to generate pre-signed upload URL: {str(e)}"
            logger.error(error_msg)
            raise StorageError(error_msg) from e