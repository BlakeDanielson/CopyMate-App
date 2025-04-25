# Development Guide

## Setting Up Local Development Environment

1.  Install Python and Poetry.
2.  Create a virtual environment using Poetry:
    ```bash
    poetry env use python3.9
    poetry shell
    ```
3.  Install the project dependencies using Poetry:
    ```bash
    poetry install
    ```
4.  Configure the environment variables (see Configuration Guide).
5.  Start the backend application:
    ```bash
    python backend/main.py
    ```

### Configuring AWS Credentials for Local Testing

If you intend to test with `AI_PROVIDER` set to `aws_rekognition` locally, ensure your development environment has valid AWS credentials configured. The application uses `boto3`, which automatically searches for credentials in standard locations (environment variables, shared credential file, etc.). Refer to the [Configuration Guide](./configuration_guide.md#aws-rekognition-provider) for more details on how credentials are handled.

## Running Tests

1.  Run the unit tests using pytest:
    ```bash
    pytest backend/tests/unit
    ```
2.  Run the integration tests using pytest:
    ```bash
    pytest backend/tests/integration
    ```

## Using the Dummy AI Provider for Testing

1.  Set the `AI_PROVIDER` environment variable to `dummy`.
2.  Start the backend application.
3.  Upload a photo and verify that the AI processing results are the predefined dummy results.