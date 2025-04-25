# GuardianLens Backend

This directory contains the FastAPI and Celery components for the GuardianLens application.

## Technology Stack

- **Framework**: FastAPI
- **Language**: Python
- **Background Processing**: Celery
- **ORM**: SQLAlchemy (with asyncpg)
- **Migrations**: Alembic
- **Database**: PostgreSQL
- **Cache/Broker**: Redis
- **Authentication**: JWT (python-jose)
- **Password Hashing**: passlib
- **API Documentation**: Swagger UI (built into FastAPI)

## Project Structure

Once initialized, the project will follow this structure:

```
backend/
├── app/
│   ├── api/                  # API endpoints
│   │   ├── v1/               # API version 1
│   │   │   ├── auth/         # Authentication endpoints
│   │   │   ├── profiles/     # Child profile endpoints
│   │   │   ├── youtube/      # YouTube integration endpoints
│   │   │   └── dashboard/    # Dashboard data endpoints
│   ├── core/                 # Core modules (config, security)
│   ├── db/                   # Database setup and models
│   │   ├── migrations/       # Alembic migrations
│   │   └── models/           # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas for request/response validation
│   ├── services/             # Business logic and external service clients
│   ├── tasks/                # Celery tasks
│   └── main.py               # Application entry point
├── tests/                    # Test directory
│   ├── api/                  # API tests
│   ├── tasks/                # Celery task tests
│   └── conftest.py           # pytest fixtures
├── celery_worker.py          # Celery worker entry point
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Dependencies
├── Dockerfile                # Backend service Dockerfile
├── Dockerfile.celery         # Celery worker Dockerfile
└── .env.example              # Example environment variables
```

## Setup and Development

### Requirements

- Python 3.9+
- PostgreSQL
- Redis
- Docker and Docker Compose (for local development)

### Local Development Environment

Instructions for setting up the local development environment using Docker Compose will be provided once the project is initialized.

### Virtual Environment

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Database Migrations

```bash
# Generate a migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### Running the API

```bash
# Development mode
uvicorn app.main:app --reload

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

### Running Celery Worker

```bash
# Start Celery worker
celery -A celery_worker.celery worker --loglevel=info

# Start Celery Beat (if needed for scheduled tasks)
celery -A celery_worker.celery beat --loglevel=info
```

## Testing

This project follows a Test-Driven Development (TDD) approach:

1. Write tests first (using pytest)
2. Implement features to make tests pass
3. Refactor code while ensuring tests remain green

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Environment Variables

The backend requires several environment variables for configuration. A `.env.example` file will be provided to document required variables.