"""Global pytest configuration and fixtures."""
import asyncio
import pytest
from typing import AsyncGenerator, Dict, Generator
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.main import app as app_instance
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.models.user import ParentUser
from app.schemas.user import UserCreate
from app.crud.crud_user import create_user


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session.
    
    This is needed for pytest-asyncio to work properly with FastAPI.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# Create a test database engine and session
@pytest.fixture(scope="session")
def test_engine():
    """Create a test SQLite engine with in-memory database."""
    # Use SQLite in-memory database for testing
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Set up a fresh test database for each test."""
    # Create all tables in test database
    from app.db.base import Base
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session for test
    test_session_maker = async_sessionmaker(
        bind=test_engine, expire_on_commit=False, autoflush=False, autocommit=False
    )
    async with test_session_maker() as session:
        yield session
    
    # Clean up after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def app() -> FastAPI:
    """Return FastAPI application fixture."""
    from app.api.deps import get_db

    # Override get_db dependency to use test database
    async def override_get_db():
        """Return test database session."""
        async with AsyncSession(bind=test_engine) as session:
            yield session

    app_instance.dependency_overrides[get_db] = override_get_db
    return app_instance


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user(test_db) -> Dict[str, str]:
    """Create a test user and return user data."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    user_in = UserCreate(**user_data)
    user = await create_user(test_db, obj_in=user_in)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "password": user_data["password"],  # Store original password for tests
    }


@pytest.fixture
def token_headers(test_user) -> Dict[str, str]:
    """Create token headers for authenticated requests."""
    access_token = create_access_token(subject=test_user["email"])
    return {"Authorization": f"Bearer {access_token}"}


# Create an endpoint fixture for the protected endpoint test
@pytest.fixture
def protected_endpoint(app) -> None:
    """Add a test-only protected endpoint to the app."""
    from fastapi import Depends, APIRouter

    test_router = APIRouter()

    @test_router.get("/test-auth", tags=["test"])
    async def test_auth_endpoint(current_user: ParentUser = Depends(get_current_user)):
        """Test protected endpoint that requires authentication."""
        return {"email": current_user.email, "id": current_user.id}

    app.include_router(test_router, prefix=f"{settings.API_V1_STR}/test")