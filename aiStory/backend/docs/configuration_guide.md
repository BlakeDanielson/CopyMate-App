# Configuration Guide

## Environment Variables

The following environment variables are used to configure the application:

*   `STORAGE_PROVIDER`: Specifies the storage provider to use (`local` or `s3`).
*   `LOCAL_STORAGE_PATH`: Specifies the path to the local storage directory (if `STORAGE_PROVIDER` is `local`).
*   `S3_BUCKET_NAME`: Specifies the name of the S3 bucket (if `STORAGE_PROVIDER` is `s3`).
*   `AI_PROVIDER`: Specifies the AI provider to use (`dummy`, `aws_rekognition`, or `external`).
*   `AWS_REGION`: Specifies the AWS region for Rekognition (required if `AI_PROVIDER` is `aws_rekognition`).
*   `REKOGNITION_MAX_LABELS`: Sets the maximum number of labels Rekognition should return (optional, defaults to 10).
*   `REKOGNITION_MIN_CONFIDENCE`: Sets the minimum confidence level for labels returned by Rekognition (optional, defaults to 90.0).
*   `REDIS_HOST`: Specifies the Redis host.
*   `REDIS_PORT`: Specifies the Redis port.
*   `CELERY_BROKER_URL`: Specifies the Celery broker URL.
*   `CELERY_RESULT_BACKEND`: Specifies the Celery result backend.

## Storage Provider Configuration

### Local Storage

To configure the application to use local storage:

1.  Set `STORAGE_PROVIDER` to `local`.
2.  Set `LOCAL_STORAGE_PATH` to the desired local storage directory.

### S3 Storage

To configure the application to use S3 storage:

1.  Set `STORAGE_PROVIDER` to `s3`.
2.  Set `S3_BUCKET_NAME` to the name of the S3 bucket.
3.  Configure AWS credentials (e.g., via environment variables or IAM roles).

## AI Provider Configuration

### Dummy AI Provider

To configure the application to use the dummy AI provider:
### AWS Rekognition Provider

To configure the application to use the AWS Rekognition provider for image labeling:

1.  Set `AI_PROVIDER` to `aws_rekognition`.
2.  Set `AWS_REGION` to the desired AWS region (e.g., `us-east-1`).
3.  Optionally, set `REKOGNITION_MAX_LABELS` and `REKOGNITION_MIN_CONFIDENCE` if you need to override the defaults.
4.  Ensure your environment is configured with AWS credentials. The application uses `boto3`, which follows the standard AWS credential chain (environment variables, shared credential file, AWS config file, IAM role, etc.). Refer to the [Boto3 Credentials Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html) for details on secure credential configuration.



1.  Set `AI_PROVIDER` to `dummy`.

### External AI Provider

To configure the application to use an external AI provider:

1.  Set `AI_PROVIDER` to `external`.
2.  Configure the external AI provider's API endpoint and credentials.

## Redis and Celery Setup

1.  Install Redis and Celery.
2.  Configure the Celery broker URL and result backend to point to the Redis instance.
3.  Start the Celery worker.