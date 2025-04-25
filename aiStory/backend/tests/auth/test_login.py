"""Tests for user login endpoints."""
import pytest
from httpx import AsyncClient
from jose import jwt

from backend.config import settings
from backend.main import app
from backend.models.user import User
from backend.tests.test_database import test_db, test_engine, test_settings


class TestUserLogin:
    """Tests for user login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, test_db):
        """Test successful user login."""
        # First create a user with a known password
        password = "SecurePassword123!"
        user = User(
            email="login@example.com",
            username="loginuser",
            hashed_password="temp_hash"  # Will be replaced by the actual implementation
        )
        test_db.add(user)
        await test_db.commit()
        
        # Get the user to retrieve the actual ID before we can update with hashed password
        await test_db.refresh(user)
        
        # Update the user with properly hashed password
        # This assumes we have a password hashing utility function that will be created
        from backend.utils.auth import get_password_hash
        user.hashed_password = get_password_hash(password)
        await test_db.commit()
        
        # Now attempt to login
        async with AsyncClient(app=app, base_url="http://test") as client:
            login_data = {
                "username": "loginuser",  # Test login with username
                "password": password
            }
            
            endpoint = f"{settings.api_prefix}/auth/login"
            response = await client.post(endpoint, json=login_data)
            
            # Assert response
            assert response.status_code == 200
            response_data = response.json()
            
            # Verify token is returned
            assert "access_token" in response_data
            assert "token_type" in response_data
            assert response_data["token_type"] == "bearer"
            
            # Verify user data is returned
            assert "user" in response_data
            assert response_data["user"]["id"] == user.id
            assert response_data["user"]["email"] == user.email
            assert response_data["user"]["username"] == user.username
            assert "hashed_password" not in response_data["user"]
            
            # Verify token content
            from backend.utils.auth import decode_jwt_token
            token_data = decode_jwt_token(response_data["access_token"])
            assert token_data["sub"] == str(user.id)
            assert "exp" in token_data
            assert token_data["token_type"] == "access"
            
            # Verify refresh token is returned
            assert "refresh_token" in response_data
            refresh_token_data = decode_jwt_token(response_data["refresh_token"])
            assert refresh_token_data["sub"] == str(user.id)
            assert "exp" in refresh_token_data
            assert refresh_token_data["token_type"] == "refresh"
    
    @pytest.mark.asyncio
    async def test_login_with_email(self, test_db):
        """Test login with email instead of username."""
        # Create user with known password
        password = "SecurePassword123!"
        user = User(
            email="email_login@example.com",
            username="email_user",
            hashed_password="temp_hash"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        # Update with properly hashed password
        from backend.utils.auth import get_password_hash
        user.hashed_password = get_password_hash(password)
        await test_db.commit()
        
        # Login with email
        async with AsyncClient(app=app, base_url="http://test") as client:
            login_data = {
                "username": "email_login@example.com",  # Use email in username field
                "password": password
            }
            
            endpoint = f"{settings.api_prefix}/auth/login"
            response = await client.post(endpoint, json=login_data)
            
            # Assert response
            assert response.status_code == 200
            response_data = response.json()
            assert "access_token" in response_data
            assert "refresh_token" in response_data
            assert response_data["user"]["email"] == user.email
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, test_db):
        """Test login with invalid password fails."""
        # Create user
        password = "SecurePassword123!"
        user = User(
            email="secure@example.com",
            username="secureuser",
            hashed_password="temp_hash"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        # Update with properly hashed password
        from backend.utils.auth import get_password_hash
        user.hashed_password = get_password_hash(password)
        await test_db.commit()
        
        # Attempt login with wrong password
        async with AsyncClient(app=app, base_url="http://test") as client:
            login_data = {
                "username": "secureuser",
                "password": "WrongPassword123!"
            }
            
            endpoint = f"{settings.api_prefix}/auth/login"
            response = await client.post(endpoint, json=login_data)
            
            # Assert response
            assert response.status_code == 401
            assert response.json()["status"] == "error"
            assert "credentials" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self):
        """Test login with non-existent user fails."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            login_data = {
                "username": "nonexistentuser",
                "password": "Password123!"
            }
            
            endpoint = f"{settings.api_prefix}/auth/login"
            response = await client.post(endpoint, json=login_data)
            
            # Assert response
            assert response.status_code == 401
            assert response.json()["status"] == "error"
            assert "credentials" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, test_db):
        """Test login with inactive user account fails."""
        # Create inactive user
        password = "SecurePassword123!"
        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password="temp_hash",
            is_active=False  # Set user as inactive
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        # Update with properly hashed password
        from backend.utils.auth import get_password_hash
        user.hashed_password = get_password_hash(password)
        await test_db.commit()
        
        # Attempt login with inactive user
        async with AsyncClient(app=app, base_url="http://test") as client:
            login_data = {
                "username": "inactiveuser",
                "password": password
            }
            
            endpoint = f"{settings.api_prefix}/auth/login"
            response = await client.post(endpoint, json=login_data)
            
            # Assert response
            assert response.status_code == 401
            assert response.json()["status"] == "error"
            assert "inactive" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_login_validation_missing_fields(self):
        """Test login validation with missing fields."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test cases with invalid data
            invalid_test_cases = [
                # Missing username
                {
                    "data": {
                        "password": "Password123!"
                    },
                    "expected_status": 422,
                    "error_field": "username"
                },
                # Missing password
                {
                    "data": {
                        "username": "testuser"
                    },
                    "expected_status": 422,
                    "error_field": "password"
                },
                # Empty request
                {
                    "data": {},
                    "expected_status": 422,
                    "error_field": "username"
                }
            ]
            
            endpoint = f"{settings.api_prefix}/auth/login"
            
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
    async def test_token_update_on_login(self, test_db):
        """Test that last_login field is updated on successful login."""
        # Create user
        password = "SecurePassword123!"
        user = User(
            email="timestamp@example.com",
            username="timeuser",
            hashed_password="temp_hash",
            last_login=None  # Start with no login timestamp
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        # Update with properly hashed password
        from backend.utils.auth import get_password_hash
        user.hashed_password = get_password_hash(password)
        await test_db.commit()
        
        # Login
        async with AsyncClient(app=app, base_url="http://test") as client:
            login_data = {
                "username": "timeuser",
                "password": password
            }
            
            endpoint = f"{settings.api_prefix}/auth/login"
            response = await client.post(endpoint, json=login_data)
            
            # Assert response
            assert response.status_code == 200
            
            # Get updated user
            await test_db.refresh(user)
            assert user.last_login is not None  # Timestamp should be set