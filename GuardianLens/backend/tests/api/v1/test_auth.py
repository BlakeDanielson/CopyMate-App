"""Tests for the authentication endpoints."""
import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.crud.crud_user import get_user_by_email
from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, test_db: AsyncSession):
    """Test successful user registration."""
    # Arrange
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New Test User"
    }
    
    # Act
    response = await client.post(
        "/api/v1/auth/register",
        json=user_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "password" not in data
    assert "hashed_password" not in data
    
    # Verify user exists in DB
    db_user = await get_user_by_email(test_db, email=user_data["email"])
    assert db_user is not None
    assert db_user.email == user_data["email"]
    
    # Verify password is properly hashed
    assert verify_password(user_data["password"], db_user.hashed_password)


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient, test_user: dict):
    """Test registration fails with duplicate email."""
    # Arrange
    duplicate_user_data = {
        "email": test_user["email"],  # Same email as existing test user
        "password": "uniquepassword123",
        "full_name": "Another Name"
    }
    
    # Act
    response = await client.post(
        "/api/v1/auth/register",
        json=duplicate_user_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_data,expected_status",
    [
        (
            {"email": "notanemail", "password": "password123", "full_name": "Invalid Email User"},
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ),
        (
            {"email": "short@example.com", "password": "short", "full_name": "Short Password User"},
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ),
        (
            {"email": "missing@example.com", "password": "password123"},  # Missing full_name
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ),
    ],
)
async def test_register_user_invalid_input(client: AsyncClient, invalid_data, expected_status):
    """Test registration fails with invalid input data."""
    # Act
    response = await client.post(
        "/api/v1/auth/register",
        json=invalid_data
    )
    
    # Assert
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: dict):
    """Test successful login with valid credentials."""
    # Arrange
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    
    # Act
    response = await client.post(
        "/api/v1/auth/token",
        data=login_data  # Use form data for OAuth2 password flow
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # Verify token is non-empty
    assert data["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: dict):
    """Test login fails with wrong password."""
    # Arrange
    login_data = {
        "username": test_user["email"],
        "password": "wrongpassword"
    }
    
    # Act
    response = await client.post(
        "/api/v1/auth/token",
        data=login_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert "Incorrect email or password" in data["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient):
    """Test login fails with non-existent email."""
    # Arrange
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password123"
    }
    
    # Act
    response = await client.post(
        "/api/v1/auth/token",
        data=login_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
    assert "Incorrect email or password" in data["detail"]


@pytest.mark.asyncio
async def test_access_protected_endpoint_with_token(
    client: AsyncClient, token_headers: dict, protected_endpoint
):
    """Test accessing protected endpoint with valid token."""
    # Act
    response = await client.get(
        "/api/v1/test/test-auth",
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_access_protected_endpoint_without_token(client: AsyncClient, protected_endpoint):
    """Test accessing protected endpoint without token fails."""
    # Act
    response = await client.get("/api/v1/test/test-auth")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_access_protected_endpoint_invalid_token(client: AsyncClient, protected_endpoint):
    """Test accessing protected endpoint with invalid token fails."""
    # Arrange
    invalid_headers = {"Authorization": "Bearer invalidtokenvalue"}
    
    # Act
    response = await client.get(
        "/api/v1/test/test-auth",
        headers=invalid_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    data = response.json()
    assert "detail" in data
    assert "Could not validate credentials" in data["detail"]