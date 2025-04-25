import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.models.user import ParentUser
from backend.auth import get_password_hash, create_access_token
from backend.routers.auth import router as auth_router
from backend.config import settings

# Setup for in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a test app
app = FastAPI()
app.include_router(auth_router)

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_database):
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    hashed_password = get_password_hash("Password123")
    user = ParentUser(
        email="test@example.com",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def user_token(sample_user):
    """Create a token for the sample user."""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return create_access_token(
        data={"sub": str(sample_user.id)}, expires_delta=access_token_expires
    )

@patch("backend.routers.auth.parent_user_repo")
@patch("backend.routers.auth.audit_log_repo")
def test_login_for_access_token_success(mock_audit_log_repo, mock_parent_user_repo, db_session, sample_user):
    """Test successful login."""
    # Mock the authenticate_user function
    with patch("backend.routers.auth.authenticate_user", return_value=sample_user):
        # Mock the update_last_login method
        mock_parent_user_repo.update_last_login.return_value = sample_user
        
        # Make the request
        response = client.post(
            "/auth/token",
            data={"username": "test@example.com", "password": "Password123"}
        )
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify the mocks were called correctly
        mock_parent_user_repo.update_last_login.assert_called_once_with(db_session, sample_user.id)
        mock_audit_log_repo.log_action.assert_called_once()

@patch("backend.routers.auth.authenticate_user")
def test_login_for_access_token_invalid_credentials(mock_authenticate_user, db_session):
    """Test login with invalid credentials."""
    # Mock the authenticate_user function to return None (authentication failure)
    mock_authenticate_user.return_value = None
    
    # Make the request
    response = client.post(
        "/auth/token",
        data={"username": "wrong@example.com", "password": "WrongPassword"}
    )
    
    # Check the response
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Incorrect email or password"

@patch("backend.routers.auth.parent_user_repo")
@patch("backend.routers.auth.audit_log_repo")
def test_register_user_success(mock_audit_log_repo, mock_parent_user_repo, db_session):
    """Test successful user registration."""
    # Mock the get_by_email method to return None (no existing user)
    mock_parent_user_repo.get_by_email.return_value = None
    
    # Mock the create method to return a new user
    new_user = ParentUser(
        id=1,
        email="new@example.com",
        hashed_password="hashed_password",
        first_name="New",
        last_name="User",
        is_active=True,
        created_at=datetime.now()
    )
    mock_parent_user_repo.create.return_value = new_user
    
    # Make the request
    response = client.post(
        "/auth/register",
        json={
            "email": "new@example.com",
            "password": "Password123",
            "first_name": "New",
            "last_name": "User"
        }
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert "id" in data
    
    # Verify the mocks were called correctly
    mock_parent_user_repo.get_by_email.assert_called_once_with(db_session, email="new@example.com")
    mock_parent_user_repo.create.assert_called_once()
    mock_audit_log_repo.log_action.assert_called_once()

@patch("backend.routers.auth.parent_user_repo")
def test_register_user_email_already_exists(mock_parent_user_repo, db_session, sample_user):
    """Test registration with an email that already exists."""
    # Mock the get_by_email method to return an existing user
    mock_parent_user_repo.get_by_email.return_value = sample_user
    
    # Make the request
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    # Check the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Email already registered"
    
    # Verify the mock was called correctly
    mock_parent_user_repo.get_by_email.assert_called_once_with(db_session, email="test@example.com")

def test_register_user_invalid_password(db_session):
    """Test registration with an invalid password."""
    # Make the request with a password that doesn't meet requirements
    response = client.post(
        "/auth/register",
        json={
            "email": "new@example.com",
            "password": "password",  # Missing uppercase and digit
            "first_name": "New",
            "last_name": "User"
        }
    )
    
    # Check the response
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # The error should mention the password requirements
    assert any("Password must contain" in error["msg"] for error in data["detail"])

@patch("backend.auth.get_current_active_user")
def test_read_users_me(mock_get_current_active_user, sample_user):
    """Test getting the current user's information."""
    # Mock the get_current_active_user dependency
    mock_get_current_active_user.return_value = sample_user
    
    # Make the request
    response = client.get("/auth/me")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user.email
    assert data["first_name"] == sample_user.first_name
    assert data["last_name"] == sample_user.last_name
    assert data["id"] == sample_user.id