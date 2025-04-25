"""Tests for database utilities and functionality."""
import asyncio
import os
import uuid
from typing import AsyncGenerator, List, Optional

import pytest
import pytest_asyncio
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import Settings, settings
from models.base import Base
from utils.database import get_db, init_db, verify_database_connection, close_db_connection


# Test model for database operations
class TestUser(Base):
    """Test user model for database testing."""
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String, default=lambda: str(uuid.uuid4()), unique=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)


# Create a test-specific settings with SQLite in-memory database
@pytest.fixture(scope="session")
def test_settings():
    """Return test-specific settings using SQLite in-memory database."""
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        db_echo=True,
        debug=True
    )


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_settings):
    """Create a test database engine."""
    engine = create_async_engine(
        str(test_settings.database_url),
        echo=test_settings.db_echo,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield engine
    finally:
        # Close engine
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create session with specific engine
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Add some test data
            test_user = TestUser(
                username="testuser",
                email="test@example.com"
            )
            session.add(test_user)
            await session.commit()
            
            yield session
        finally:
            # Roll back any uncommitted changes
            await session.rollback()
            
            # Clean up test data
            await session.execute(select(TestUser).where(TestUser.username == "testuser"))
            await session.commit()


class TestDatabaseConnection:
    """Tests for database connection and session management."""
    
    @pytest.mark.asyncio
    async def test_verify_database_connection(self, test_settings, monkeypatch):
        """Test database connection verification."""
        # Patch settings for test
        monkeypatch.setattr("backend.utils.database.settings", test_settings)
        
        # Verify connection works
        await verify_database_connection()
        
        # Test with invalid settings
        invalid_settings = Settings(
            database_url="postgresql://nonexistent:wrongpass@localhost:5432/nonexistent",
            db_echo=True
        )
        monkeypatch.setattr("backend.utils.database.settings", invalid_settings)
        
        # Should raise exception with invalid connection
        with pytest.raises(Exception):
            await verify_database_connection()

    @pytest.mark.asyncio
    async def test_init_and_close_db(self, test_settings, monkeypatch):
        """Test database initialization and closing."""
        # Patch settings for test
        monkeypatch.setattr("backend.utils.database.settings", test_settings)
        
        # Initialize database
        await init_db()
        
        # Close database connection
        await close_db_connection()


class TestDatabaseOperations:
    """Tests for database CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_session_commit_and_rollback(self, test_db):
        """Test session commit and rollback operations."""
        # Create a new user
        new_user = TestUser(
            username="newuser",
            email="new@example.com"
        )
        test_db.add(new_user)
        await test_db.commit()
        
        # Verify user was created
        result = await test_db.execute(select(TestUser).where(TestUser.username == "newuser"))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.username == "newuser"
        
        # Test rollback
        update_user = TestUser(
            username="updateuser",
            email="update@example.com"
        )
        test_db.add(update_user)
        
        # Don't commit, explicitly rollback
        await test_db.rollback()
        
        # Verify user was not created
        result = await test_db.execute(select(TestUser).where(TestUser.username == "updateuser"))
        user = result.scalar_one_or_none()
        assert user is None

    @pytest.mark.asyncio
    async def test_get_db_dependency(self, test_settings, monkeypatch):
        """Test the get_db dependency function."""
        # Patch settings for test
        monkeypatch.setattr("backend.utils.database.settings", test_settings)
        
        # Initialize DB first
        await init_db()
        
        # Test the get_db dependency
        async for session in get_db():
            # Verify we get a working session
            assert isinstance(session, AsyncSession)
            
            # Test simple query to ensure session works
            result = await session.execute(select(1))
            value = result.scalar_one()
            assert value == 1

    @pytest.mark.asyncio
    async def test_multiple_environment_db_urls(self):
        """Test handling of different environment database URLs."""
        # Test development environment
        dev_settings = Settings(
            database_url="sqlite+aiosqlite:///dev.db",
            db_echo=True
        )
        assert str(dev_settings.database_url).startswith("sqlite+aiosqlite")
        
        # Test production environment with PostgreSQL
        prod_url = "postgresql://user:pass@db:5432/proddb"
        prod_settings = Settings(database_url=prod_url)
        assert str(prod_settings.database_url).startswith("postgresql://")

        # Test legacy postgres:// URL gets converted
        legacy_url = "postgres://user:pass@db:5432/legacydb"
        legacy_settings = Settings(database_url=legacy_url)
        assert "postgresql://" in str(legacy_settings.database_url)
        assert "postgres://" not in str(legacy_settings.database_url)