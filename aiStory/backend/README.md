# AI Story Creator Backend

This is the backend service for the AI Story Creator application, built with FastAPI.

## Dependency Management

### Decision: Poetry

For this project, we've chosen to use `Poetry` for dependency management over alternatives like requirements.txt or PDM. This decision was made for the following reasons:

- **Robust Dependency Resolution**: Poetry resolves dependencies more reliably and handles complex dependency graphs
- **Integrated Virtual Environment Management**: Poetry creates and manages virtual environments automatically
- **Lockfile System**: Poetry.lock ensures consistent installs across all environments
- **Project Packaging**: Built-in packaging capabilities for publishing if needed
- **Development Groups**: Separation of development and production dependencies

Poetry offers these advanced features while maintaining a straightforward workflow through its intuitive CLI commands.

### Usage Guidelines

When adding new dependencies:

1. Add a package: `poetry add package_name`
2. Add a development dependency: `poetry add --group dev package_name`
3. Update dependencies: `poetry update`
4. Install all dependencies: `poetry install`
5. Commit both pyproject.toml and poetry.lock to version control

## Environment Setup

### Local Development

1. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Navigate to the backend directory and generate the lock file:
   ```bash
   cd backend
   poetry lock
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Activate the Poetry shell (virtual environment):
   ```bash
   poetry shell
   ```

5. Verify your environment setup:
   ```bash
   python verify_env.py
   ```
   This will check that all required dependencies are properly installed and importable.

4. Environment variables:
   This project uses a shared `.env` file at the project root (parent directory of `backend/`) to support both backend and frontend configuration.
   
   ```
   # Project root directory
   .env                # Active environment variables (development)
   .env.example        # Template showing required variables
   ```
   
   Key backend environment variables (prefixed with `aistory_`):
   ```
   aistory_debug=True
   aistory_database_url=postgresql+asyncpg://user:password@localhost:5432/story_creator_db
   # See .env.example for the complete list
   ```

5. Run the application:
   ```bash
   poetry run uvicorn main:app --reload
   ```
### Docker Development

The project includes Docker support using `docker-compose`. To use it:

1. Ensure Docker is installed and running on your system.
2. From the root directory of the project, run:
   ```bash
   docker-compose up --build
   ```

   This command builds the Docker images and starts the containers defined in `docker-compose.yml`.

   The backend container exposes port 8000, which you can access in your browser at `http://localhost:8000`.

## Project Structure

```
backend/
├── __init__.py
├── main.py              # Application entry point
├── config.py            # Configuration management
├── pyproject.toml       # Poetry dependency management and project metadata
├── poetry.lock          # Locked dependencies (commit this!)
├── alembic/             # Database migration scripts
│   ├── env.py           # Alembic environment configuration
│   ├── script.py.mako   # Migration template
│   └── versions/        # Migration version scripts
├── models/              # SQLAlchemy models
│   ├── base.py          # Base model class
│   └── user.py          # User model definition
├── schemas/             # Pydantic schemas for data validation
├── routers/             # API route definitions
├── services/            # Business logic
├── repositories/        # Database access
├── middlewares/         # Custom middleware
├── utils/               # Helper functions
│   └── database.py      # Database utilities
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_main.py     # Tests for main.py
│   └── test_database.py # Tests for database functionality
└── docs/                # Documentation
    ├── api_design_principles.md
    └── database_guide.md    # Database usage patterns and procedures
```

## Database Setup

The application uses SQLAlchemy for ORM and Alembic for database migrations. For detailed information on database usage patterns and migration procedures, see the [Database Guide](docs/database_guide.md).

### Setting Up the Database

1. Configure the database connection in your `.env` file:
   ```
   AISTORY_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aistory
   ```

2. Apply database migrations:
   ```bash
   # Inside the backend directory
   poetry run alembic upgrade head
   ```

   Alternatively, in development mode (when `AISTORY_DEBUG=true`), the application will automatically create tables on startup.

### Environment-specific Database Configuration

The application supports different database configurations for various environments:

```
# Main database URL (used if no environment-specific URL is provided)
AISTORY_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aistory

# Environment-specific database URLs
AISTORY_DATABASE_URL_DEV=postgresql+asyncpg://user:password@localhost:5432/aistory_dev
AISTORY_DATABASE_URL_TEST=postgresql+asyncpg://user:password@localhost:5432/aistory_test
AISTORY_DATABASE_URL_PROD=postgresql+asyncpg://user:password@localhost:5432/aistory_prod

# Set the environment
AISTORY_ENVIRONMENT=development  # Options: development, testing, production
```

### Creating and Running Migrations

To create a new migration after model changes:

```bash
# Inside the backend directory
poetry run alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
# Apply all pending migrations
poetry run alembic upgrade head

# Apply a specific number of migrations
poetry run alembic upgrade +1

# Revert migrations
poetry run alembic downgrade -1
```

## Configuration Management

The application uses `pydantic-settings` to handle configuration. Settings are loaded from environment variables, with `.env` file support for local development. The configuration system looks for the `.env` file in the project root directory, not in the backend directory.

Key environment variables:
- `AISTORY_DEBUG`: Set to "True" for development mode
- `AISTORY_ENVIRONMENT`: Set to "development", "testing", or "production"
- `AISTORY_DATABASE_URL`: PostgreSQL connection string
- `AISTORY_SECRET_KEY`: Secret key for JWT and security features

Environment variables for the backend are prefixed with `AISTORY_` to distinguish them from frontend variables in the shared `.env` file. See `.env.example` for a complete list of available configuration options.

## Testing

Run tests with:

```bash
poetry run pytest
```

This will automatically discover and run all tests in the `tests` directory.

You can also use coverage:

```bash
poetry run pytest --cov=backend
```

## Environment Variable Verification

You can verify that your environment variables are correctly configured by running:

```bash
poetry run python verify_env.py
```

This script checks that:
- All required dependencies are installed
- Environment variables are being loaded properly
- Database connection (if configured) works