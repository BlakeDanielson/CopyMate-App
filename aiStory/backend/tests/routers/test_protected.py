"""Tests for protected endpoints with role-based authorization."""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import select

from backend.config import settings
from backend.main import app
from backend.models.user import User
from backend.tests.test_database import test_db, test_engine, test_settings
from backend.utils.auth import create_access_token, get_password_hash


class TestProtectedEndpoints:
    """Tests for protected routes with role-based authorization."""
    
    async def create_test_user(self, test_db, role="user"):
        """Helper to create a test user with the specified role."""
        user = User(
            email=f"{role}@example.com",
            username=f"{role}user",
            hashed_password=get_password_hash("Password123!"),
            role=role
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user
    
    def create_token_for_user(self, user, expires_delta=None):
        """Helper to create an access token for a user."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=15)
        
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=expires_delta
        )
        return access_token
    
    @pytest.mark.asyncio
    async def test_auth_only_endpoint(self, test_db):
        """Test endpoint that requires authentication but no specific role."""
        # Create a regular user
        user = await self.create_test_user(test_db, role="user")
        access_token = self.create_token_for_user(user)
        
        # Test accessing auth-only endpoint
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/protected/auth-only",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify success response
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["user"]["username"] == user.username
            assert data["user"]["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_admin_only_endpoint_with_admin(self, test_db):
        """Test admin-only endpoint with admin user."""
        # Create an admin user
        admin = await self.create_test_user(test_db, role="admin")
        access_token = self.create_token_for_user(admin)
        
        # Test accessing admin-only endpoint with admin role
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/protected/admin-only",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify success response
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["user"]["role"] == "admin"
            assert "admin_data" in data
    
    @pytest.mark.asyncio
    async def test_admin_only_endpoint_with_user(self, test_db):
        """Test admin-only endpoint with regular user (should be forbidden)."""
        # Create a regular user
        user = await self.create_test_user(test_db, role="user")
        access_token = self.create_token_for_user(user)
        
        # Test accessing admin-only endpoint with user role
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/protected/admin-only",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Verify forbidden response
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_moderator_or_admin_endpoint(self, test_db):
        """Test endpoint that allows either moderator or admin role."""
        # Create a moderator user
        moderator = await self.create_test_user(test_db, role="moderator")
        mod_token = self.create_token_for_user(moderator)
        
        # Create an admin user
        admin = await self.create_test_user(test_db, role="admin")
        admin_token = self.create_token_for_user(admin)
        
        # Create a regular user
        user = await self.create_test_user(test_db, role="user")
        user_token = self.create_token_for_user(user)
        
        # Test with moderator role (should succeed)
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/protected/moderator-or-admin",
                headers={"Authorization": f"Bearer {mod_token}"}
            )
            assert response.status_code == 200
            assert response.json()["user"]["role"] == "moderator"
        
        # Test with admin role (should succeed)
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/protected/moderator-or-admin",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            assert response.json()["user"]["role"] == "admin"
        
        # Test with regular user role (should be forbidden)
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/protected/moderator-or-admin",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_unauthenticated_request(self, test_db):
        """Test accessing protected endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"{settings.api_prefix}/protected/auth-only")
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_user_only_endpoint(self, test_db):
        """Test endpoint that requires user role."""
        # Create a regular user
        user = await self.create_test_user(test_db, role="user")
        user_token = self.create_token_for_user(user)
        
        # Create an admin user
        admin = await self.create_test_user(test_db, role="admin")
        admin_token = self.create_token_for_user(admin)
        
        # Test with user role (should succeed)
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/protected/user-only",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 200
            assert response.json()["user"]["role"] == "user"
        
        # Test with admin role (should be forbidden despite being higher privilege)
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"{settings.api_prefix}/protected/user-only",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 403