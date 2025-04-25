# Database Guide

This document provides comprehensive information about the database setup, usage patterns, and migration procedures for the AI Story Creator backend.

## Database Architecture

The AI Story Creator uses SQLAlchemy as its ORM (Object-Relational Mapping) tool with asynchronous support through SQLAlchemy 2.0's async capabilities. The database layer is designed with the following components:

- **Models**: SQLAlchemy ORM models that represent database tables
- **Schemas**: Pydantic models for request/response data validation
- **Migrations**: Alembic-managed database migrations

## Environment Configuration

The application supports different database configurations for various environments:

- **Development**: Used during local development
- **Testing**: Used for automated tests
- **Production**: Used in production environment

Database connection URLs for each environment can be configured through environment variables:

```
AISTORY_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aistory
AISTORY_DATABASE_URL_DEV=postgresql+asyncpg://user:password@localhost:5432/aistory_dev
AISTORY_DATABASE_URL_TEST=postgresql+asyncpg://user:password@localhost:5432/aistory_test
AISTORY_DATABASE_URL_PROD=postgresql+asyncpg://user:password@localhost:5432/aistory_prod
```

The appropriate database URL is selected based on the `AISTORY_ENVIRONMENT` setting.

## Database Initialization

The database is initialized during application startup:

1. Database engine is created based on environment-specific configuration
2. Database connection is verified
3. In development mode, tables are created if they don't exist (for quick iteration)
4. In production, migrations must be applied explicitly

## Using Dependency Injection for Database Sessions

The application follows FastAPI's dependency injection pattern for database sessions:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.utils.database import get_db

@router.get("/items")
async def read_items(db: AsyncSession = Depends(get_db)):
    # Use the database session
    result = await db.execute("SELECT 1")
    return {"result": result.scalar()}
```

The `get_db` dependency automatically manages session lifecycle, including:
- Creating a session from the session factory
- Committing transactions on successful execution
- Rolling back transactions on errors
- Closing the session after use

## Database Migrations

Migrations are managed using Alembic. The following commands are available for working with migrations:

### Creating a New Migration

```bash
# Generate a new migration with automatic detection of model changes
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
# Apply all pending migrations
cd backend
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +1

# Revert specific number of migrations
alembic downgrade -1

# Migrate to a specific revision
alembic upgrade revision_id
```

### Migration Workflow Best Practices

1. Always create migrations for schema changes instead of modifying existing migrations
2. Test migrations by applying them to a development database before committing
3. Include both upgrade and downgrade paths in migrations
4. Run migrations as a separate step in the deployment process
5. Back up the database before applying migrations in production

## Database Models

All models inherit from the `Base` class defined in `backend/models/base.py`. This base class provides:

- Automatic table naming based on the class name
- `created_at` and `updated_at` timestamp columns
- A `to_dict()` method for converting models to dictionaries

Example model:

```python
from sqlalchemy import Column, Integer, String
from backend.models.base import Base

class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
```
### Photo Table

The `photos` table stores information about uploaded photos.

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.models.base import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    object_key = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="photos")
```

- `id`: Unique identifier for the photo.
- `user_id`: Foreign key referencing the user who uploaded the photo.
- `object_key`: The key of the photo in the storage bucket.
- `status`: The status of the photo (e.g., pending, uploaded, processing, completed, failed).
- `created_at`: Timestamp indicating when the photo was uploaded.
- `updated_at`: Timestamp indicating when the photo was last updated.


## Database Utility Functions

The `backend/utils/database.py` module provides utility functions for working with the database:

- `init_db()`: Initialize the database connection
- `verify_database_connection()`: Verify that the database connection is working
- `close_db_connection()`: Close database connections
- `get_db()`: Dependency for obtaining a database session
- `create_database_tables()`: Create database tables (for development only)

## Testing Database Code

The application includes tests for database operations in `tests/test_database.py`. These tests:

- Use an in-memory SQLite database for fast testing
- Test connection verification
- Test session commit and rollback
- Test the dependency injection pattern
- Test database operations across different environments

## Performance Considerations

- The database connection pool size can be configured with `AISTORY_DB_POOL_SIZE`
- The maximum overflow connections can be configured with `AISTORY_DB_MAX_OVERFLOW`
- Connection health checks are enabled by default with pool pre-ping
- Connections are recycled after 5 minutes of inactivity

## Troubleshooting

Common database issues and their solutions:

### Connection Issues

If the application fails to connect to the database:

1. Verify that the database server is running
2. Check that the database URL is correct
3. Ensure the database user has appropriate permissions
4. Check network connectivity between the application and database

### Migration Errors

If migrations fail to apply:

1. Check that the database is accessible
2. Verify that the user has sufficient privileges
3. Examine the Alembic error message for specific issues
4. Check for conflicting migrations

### Performance Issues

If database operations are slow:

1. Enable query logging with `AISTORY_DB_ECHO=True`
2. Review slow queries and optimize them
3. Adjust connection pool settings
4. Consider adding appropriate indexes to tables