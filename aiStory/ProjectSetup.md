# Project Setup and Backend Initialization

This document outlines the initial project setup steps, backend initialization, and implementation of the `/health` endpoint for the AI Story Creator project.

## 1. Project Structure and Initial Setup

### 1.1. Git Repository Setup

The project utilizes a monorepo structure, with separate directories for the frontend and backend:

```
ai-story-creator/
├── frontend/
├── backend/
├── README.md
└── .gitignore
```

To initialize the Git repository:

```bash
git init ai-story-creator
cd ai-story-creator
mkdir frontend backend
touch README.md .gitignore
# Add standard Node.js/Flutter and Python .gitignore rules
git add .
git commit -m "Initial project structure setup"
# Push to your remote (GitHub/GitLab/etc.)
```

A branching strategy, such as Gitflow Lite (main, develop, feature/*), should be defined and documented in the `README.md` or Notion. A pull request template should also be set up in `.github/pull_request_template.md` to ensure consistent and informative pull requests.

### 1.2. Notion Project Setup

A Notion database or board is used for task management. The following columns/statuses are defined:

*   To Do
*   In Progress
*   Blocked
*   Code Review
*   QA Ready
*   Done

Task template fields include:

*   Assignee
*   Sprint (e.g., Sprint 0)
*   Status
*   Priority
*   Story Points (optional)
*   Link to Spec Task #
*   Link to PR

## 2. Backend Dependency Management

The project uses `pip` with `requirements.txt` for backend dependency management due to its simplicity for the MVP. To ensure consistent dependency versions, it is crucial to run `pip freeze > requirements.txt` after adding or updating packages.

## 3. IDE and Linter Setup

### 3.1. Backend

1.  Create a virtual environment:

    ```bash
    python -m venv .venv
    ```
2.  Activate the virtual environment:

    ```bash
    source .venv/bin/activate  # Linux/macOS
    .\.venv\Scripts\activate   # Windows
    ```
3.  Install development dependencies:

    ```bash
    pip install black isort flake8 pytest pytest-asyncio
    ```
4.  Configure your IDE (e.g., VS Code) to use the virtual environment's Python interpreter.
5.  Configure format-on-save using `black` and `isort`. Add `setup.cfg` or `pyproject.toml` for `flake8` configuration (e.g., ignore specific errors, set line length).

### 3.2. Frontend

1.  Install recommended Flutter/Dart extensions for your IDE.
2.  Configure format-on-save (`dart format`).
3.  Review/customize `frontend/analysis_options.yaml` for stricter linting rules if desired.

## 4. Local Docker Environment Setup

A `docker-compose.yml` file is used to define the local development environment, including services for PostgreSQL and the backend API.

```yaml
version: '3.8'
services:
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: story_creator_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password # Use secrets in real setup
    ports:
      - "5432:5432" # Map only if needed locally outside Docker

  backend:
    build: ./backend # Points to the directory with Dockerfile
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload # Example command
    volumes:
      - ./backend:/app # Mount local code for hot-reloading
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/story_creator_db
      STORAGE_TYPE: local # or s3
      S3_BUCKET_NAME: your-s3-bucket-name
      S3_REGION: your-s3-region
      S3_ACCESS_KEY_ID: your-s3-access-key-id
      S3_SECRET_ACCESS_KEY: your-s3-secret-access-key
      PHOTO_PROCESSING_QUEUE_URL: your-photo-processing-queue-url

      # Add other necessary ENV VARS (JWT_SECRET, etc.)
    depends_on:
      - db

volumes:
  postgres_data:
```

A `Dockerfile` is created in the `backend` directory to define the steps to copy code, install dependencies, and expose the FastAPI port.

To start the local Docker environment:

```bash
docker-compose up --build
```

## 5. FastAPI Project Initialization

1.  Create `backend/main.py`:

    ```python
    from fastapi import FastAPI

    app = FastAPI()
    ```
2.  Create `backend/requirements.txt` with the following dependencies:

    ```
    fastapi
    uvicorn[standard]
    pydantic-settings
    ```
3.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## 6. /health Endpoint Implementation (TDD)

### 6.1. Test First (Red)

1.  Create `backend/tests/test_main.py`:

    ```python
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    def test_health_check():
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    ```
2.  Run tests:

    ```bash
    pytest backend/tests
    ```

    Verify that the test fails (e.g., 404 Not Found).

### 6.2. Implement (Green)

1.  In `backend/main.py`, add the `/health` endpoint:

    ```python
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    ```

### 6.3. Test Again

1.  Run tests:

    ```bash
    pytest backend/tests
    ```

    Verify that the test passes.

### 6.4. Refactor
## 7. Developer Onboarding Guide for Photo Uploads

### 7.1. Setting up the Development Environment

To set up the development environment for photo uploads, follow these steps:

1.  Ensure that you have the required environment variables configured as described in section 4.
2.  Install the necessary dependencies for the backend and frontend.
3.  Configure your IDE to use the correct Python interpreter and Dart SDK.
4.  Start the local Docker environment using `docker-compose up --build`.

### 7.2. Testing Guidelines

To test the photo upload feature, follow these guidelines:

1.  Write unit tests for the backend services and repositories.
2.  Write widget tests for the frontend UI components.
3.  Write integration tests to verify the complete flow from the frontend to the backend.
4.  Use a testing library such as `pytest` for backend tests and `flutter_test` for frontend tests.
5.  Ensure that all tests pass before submitting your code.

### 7.3. Integration Points with Other Features

The photo upload feature integrates with the following other features:

1.  User authentication: Only authenticated users can upload photos.
2.  Story creation: Uploaded photos can be used as protagonist photos in stories.
3.  Order management: Uploaded photos can be used in printed books.

When integrating with other features, ensure that you follow these guidelines:

1.  Use the correct API endpoints and data formats.
2.  Handle errors gracefully.
3.  Provide informative error messages to the user.
4.  Write integration tests to verify that the integration is working correctly.


Review the code for clarity and simplicity.

### 6.5. Commit

```bash
git add backend/main.py backend/tests/test_main.py backend/requirements.txt
git commit -m "feat(backend): initialize FastAPI and add /health endpoint via TDD"