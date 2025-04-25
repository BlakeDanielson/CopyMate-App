"""Tests for user registration endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from backend.config import settings
from backend.main import app
from backend.models.user import User
from backend.tests.test_database import test_db, test_engine, test_settings


class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, test_db):
        """Test successful user registration."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create test data
            register_data = {
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "StrongPassword123!",
                "full_name": "New User"
            }
            
            # Send registration request
            endpoint = f"{settings.api_prefix}/auth/register"
            response = await client.post(endpoint, json=register_data)
            
            # Assert response
            assert response.status_code == 201
            response_data = response.json()
            assert "id" in response_data
            assert "email" in response_data
            assert response_data["email"] == register_data["email"]
            assert response_data["username"] == register_data["username"]
            assert response_data["full_name"] == register_data["full_name"]
            assert "hashed_password" not in response_data
            assert "token" in response_data
            
            # Verify user was created in database
            result = await test_db.execute(
                select(User).where(User.email == register_data["email"])
            )
            user = result.scalar_one_or_none()
            assert user is not None
            assert user.email == register_data["email"]
            assert user.username == register_data["username"]
            assert user.hashed_password != register_data["password"]  # Password should be hashed
    
    @pytest.mark.asyncio
    async def test_register_user_invalid_data(self):
        """Test registration with invalid data fails with appropriate error messages."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test cases with invalid data
            invalid_test_cases = [
                # Missing email
                {
                    "data": {
                        "username": "testuser",
                        "password": "StrongPassword123!",
                    },
                    "expected_status": 422,
                    "error_field": "email"
                },
                # Invalid email format
                {
                    "data": {
                        "email": "invalid-email",
                        "username": "testuser",
                        "password": "StrongPassword123!",
                    },
                    "expected_status": 422,
                    "error_field": "email"
                },
                # Missing username
                {
                    "data": {
                        "email": "test@example.com",
                        "password": "StrongPassword123!",
                    },
                    "expected_status": 422,
                    "error_field": "username"
                },
                # Missing password
                {
                    "data": {
                        "email": "test@example.com",
                        "username": "testuser",
                    },
                    "expected_status": 422,
                    "error_field": "password"
                },
                # Password too short
                {
                    "data": {
                        "email": "test@example.com",
                        "username": "testuser",
                        "password": "short",
                    },
                    "expected_status": 422,
                    "error_field": "password"
                },
            ]
            
            endpoint = f"{settings.api_prefix}/auth/register"
            
            # Test each invalid case
            for test_case in invalid_test_cases:
                response = await client.post(endpoint, json=test_case["data"])
                
                assert response.status_code == test_case["expected_status"]
                assert response.json()["status"] == "error"
                
                # Check that the error details mention the expected field
                error_details = response.json()["details"]
                field_found = any(
                    test_case["error_field"] in str(error.get("loc", []))
                    for error in error_details
                )
                assert field_found, f"Expected error for field {test_case['error_field']} not found"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, test_db):
        """Test registration with an existing email fails."""
        # First create a user
        existing_user = User(
            email="existing@example.com",
            username="existinguser",
            hashed_password="hashedpassword"  # In real code, this would be properly hashed
        )
        test_db.add(existing_user)
        await test_db.commit()
        
        # Try to register with the same email
        async with AsyncClient(app=app, base_url="http://test") as client:
            register_data = {
                "email": "existing@example.com",  # Same email
                "username": "differentuser",      # Different username
                "password": "StrongPassword123!"
            }
            
            endpoint = f"{settings.api_prefix}/auth/register"
            response = await client.post(endpoint, json=register_data)
            
            # Assert response
            assert response.status_code == 400
            assert response.json()["status"] == "error"
            assert "email" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, test_db):
        """Test registration with an existing username fails."""
        # First create a user
        existing_user = User(
            email="user@example.com",
            username="existinguser",
            hashed_password="hashedpassword"  # In real code, this would be properly hashed
        )
        test_db.add(existing_user)
        await test_db.commit()
        
        # Try to register with the same username
        async with AsyncClient(app=app, base_url="http://test") as client:
            register_data = {
                "email": "different@example.com",  # Different email
                "username": "existinguser",        # Same username
                "password": "StrongPassword123!"
            }
            
            endpoint = f"{settings.api_prefix}/auth/register"
            response = await client.post(endpoint, json=register_data)
            
            # Assert response
            assert response.status_code == 400
            assert response.json()["status"] == "error"
            assert "username" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_password_hashing(self, test_db):
        """Test that passwords are properly hashed during registration."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            password = "SecurePassword123!"
            register_data = {
                "email": "security@example.com",
                "username": "securityuser",
                "password": password
            }
            
            endpoint = f"{settings.api_prefix}/auth/register"
            response = await client.post(endpoint, json=register_data)
            
            # Assert successful registration
            assert response.status_code == 201
            
            # Verify password is hashed in database
            result = await test_db.execute(
                select(User).where(User.email == register_data["email"])
            )
            user = result.scalar_one_or_none()
            assert user is not None
            assert user.hashed_password != password
            assert len(user.hashed_password) > 20  # Hashed passwords are typically long