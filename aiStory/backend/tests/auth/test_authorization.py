"""Tests for role-based authorization functionality."""
import pytest
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from httpx import AsyncClient
from typing import List, Optional
from unittest.mock import patch

from backend.config import settings
from backend.main import app
from backend.models.user import User
from backend.tests.test_database import test_db, test_engine, test_settings
from backend.utils.auth import create_access_token, get_current_user, get_current_active_user


class TestRoleBasedAuthorization:
    """Tests for role-based authorization features."""
    
    @pytest.mark.asyncio
    async def test_user_roles_in_model(self, test_db):
        """Test that the User model has a role field."""
        # Create a regular user
        regular_user = User(
            email="user@example.com",
            username="regularuser",
            hashed_password="hashed_password",
            role="user"  # This will fail until we update the model
        )
        test_db.add(regular_user)
        await test_db.commit()
        await test_db.refresh(regular_user)
        
        # Create an admin user
        admin_user = User(
            email="admin@example.com",
            username="adminuser",
            hashed_password="hashed_password",
            role="admin"  # This will fail until we update the model
        )
        test_db.add(admin_user)
        await test_db.commit()
        await test_db.refresh(admin_user)
        
        # Assert roles are set correctly
        assert regular_user.role == "user"
        assert admin_user.role == "admin"
    
    @pytest.mark.asyncio
    async def test_has_role_utility(self, test_db):
        """Test the has_role utility function."""
        # Create a user with admin role
        admin_user = User(
            email="admin_check@example.com",
            username="admincheck",
            hashed_password="hashed_password",
            role="admin"  # This will fail until we update the model
        )
        test_db.add(admin_user)
        await test_db.commit()
        await test_db.refresh(admin_user)
        
        # Import the has_role function (which doesn't exist yet)
        from backend.utils.auth import has_role
        
        # Check if the user has admin role
        assert has_role(admin_user, "admin") is True
        
        # Check if the user has user role
        assert has_role(admin_user, "user") is False
    
    @pytest.mark.asyncio
    async def test_has_any_role_utility(self, test_db):
        """Test the has_any_role utility function."""
        # Create a user with admin role
        admin_user = User(
            email="admin_multi@example.com",
            username="adminmulti",
            hashed_password="hashed_password",
            role="admin"  # This will fail until we update the model
        )
        test_db.add(admin_user)
        await test_db.commit()
        await test_db.refresh(admin_user)
        
        # Import the has_any_role function (which doesn't exist yet)
        from backend.utils.auth import has_any_role
        
        # Check if the user has any of the roles
        assert has_any_role(admin_user, ["admin", "superuser"]) is True
        assert has_any_role(admin_user, ["user", "moderator"]) is False
    
    @pytest.mark.asyncio
    async def test_require_role_decorator(self, test_db):
        """Test the require_role decorator."""
        # Create a test user with 'user' role
        regular_user = User(
            email="role_test@example.com",
            username="roletest",
            hashed_password="hashed_password",
            role="user"  # This will fail until we update the model
        )
        test_db.add(regular_user)
        await test_db.commit()
        await test_db.refresh(regular_user)
        
        # Create a test access token for this user
        access_token = create_access_token(
            data={"sub": str(regular_user.id)},
            expires_delta=timedelta(minutes=15)
        )
        
        # Create a test endpoint using the require_role decorator
        test_app = FastAPI()
        
        # Import the require_role decorator (which doesn't exist yet)
        from backend.utils.auth import require_role
        
        @test_app.get("/test-admin-only")
        async def admin_only_endpoint(current_user: User = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}
        
        @test_app.get("/test-user-role")
        async def user_role_endpoint(current_user: User = Depends(require_role("user"))):
            return {"message": "User access granted"}
        
        # Mock the get_current_user function to return our test user
        with patch("backend.utils.auth.get_current_user", return_value=regular_user):
            async with AsyncClient(app=test_app, base_url="http://test") as client:
                # Test accessing admin endpoint with user role (should be forbidden)
                response = await client.get(
                    "/test-admin-only", 
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
                
                # Test accessing user endpoint with user role (should be allowed)
                response = await client.get(
                    "/test-user-role", 
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_require_any_role_decorator(self, test_db):
        """Test the require_any_role decorator."""
        # Create a test user with 'moderator' role
        moderator_user = User(
            email="mod_test@example.com",
            username="modtest",
            hashed_password="hashed_password",
            role="moderator"  # This will fail until we update the model
        )
        test_db.add(moderator_user)
        await test_db.commit()
        await test_db.refresh(moderator_user)
        
        # Create a test access token for this user
        access_token = create_access_token(
            data={"sub": str(moderator_user.id)},
            expires_delta=timedelta(minutes=15)
        )
        
        # Create a test endpoint using the require_any_role decorator
        test_app = FastAPI()
        
        # Import the require_any_role decorator (which doesn't exist yet)
        from backend.utils.auth import require_any_role
        
        @test_app.get("/test-admin-or-mod")
        async def admin_or_mod_endpoint(
            current_user: User = Depends(require_any_role(["admin", "moderator"]))
        ):
            return {"message": "Admin or moderator access granted"}
        
        @test_app.get("/test-admin-or-super")
        async def admin_or_super_endpoint(
            current_user: User = Depends(require_any_role(["admin", "superuser"]))
        ):
            return {"message": "Admin or superuser access granted"}
        
        # Mock the get_current_user function to return our test user
        with patch("backend.utils.auth.get_current_user", return_value=moderator_user):
            async with AsyncClient(app=test_app, base_url="http://test") as client:
                # Test accessing admin/mod endpoint with moderator role (should be allowed)
                response = await client.get(
                    "/test-admin-or-mod", 
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                assert response.status_code == status.HTTP_200_OK
                
                # Test accessing admin/super endpoint with moderator role (should be forbidden)
                response = await client.get(
                    "/test-admin-or-super", 
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_role_in_token_payload(self, test_db):
        """Test that the user's role is included in the JWT token payload."""
        # Create an admin user
        admin_user = User(
            email="admin_token@example.com",
            username="admintoken",
            hashed_password="hashed_password",
            role="admin"  # This will fail until we update the model
        )
        test_db.add(admin_user)
        await test_db.commit()
        await test_db.refresh(admin_user)
        
        # Generate a token for this user
        access_token = create_access_token(
            data={"sub": str(admin_user.id), "role": admin_user.role}
        )
        
        # Decode the token and verify role is included
        from backend.utils.auth import decode_jwt_token
        payload = decode_jwt_token(access_token)
        assert payload["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_with_authentication(self, test_db):
        """Test that a protected endpoint requires authentication."""
        # Create a test app with a protected endpoint
        test_app = FastAPI()
        
        # Import the get_current_user dependency to protect the endpoint
        from backend.utils.auth import get_current_user
        
        @test_app.get("/protected")
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            return {"message": "Access granted"}
        
        # Test accessing the endpoint without a token
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            response = await client.get("/protected")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED