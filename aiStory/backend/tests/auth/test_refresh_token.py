"""Tests for refresh token functionality."""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from jose import jwt

from backend.config import settings
from backend.main import app
from backend.models.user import User
from backend.models.refresh_token import RefreshToken
from backend.schemas.user import RefreshToken as RefreshTokenSchema
from backend.tests.test_database import test_db, test_engine, test_settings
from backend.utils.auth import create_access_token, create_refresh_token


class TestRefreshToken:
    """Tests for refresh token operations."""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, test_db):
        """Test successful token refresh."""
        # Create a user with known credentials
        password = "SecurePassword123!"
        user = User(
            email="refresh@example.com",
            username="refreshuser",
            hashed_password="temp_hash"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        # Update with properly hashed password
        from backend.utils.auth import get_password_hash
        user.hashed_password = get_password_hash(password)
        await test_db.commit()
        
        # Create valid refresh token and store in database
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        token_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        db_refresh_token = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=token_expires,
            revoked=False
        )
        test_db.add(db_refresh_token)
        await test_db.commit()
        
        # Use refresh token to get new access token
        async with AsyncClient(app=app, base_url="http://test") as client:
            refresh_data = {
                "refresh_token": refresh_token
            }
            
            endpoint = f"{settings.api_prefix}/auth/refresh"
            response = await client.post(endpoint, json=refresh_data)
            
            # Assert response
            assert response.status_code == 200
            response_data = response.json()
            
            # Verify tokens are returned
            assert "access_token" in response_data
            assert "refresh_token" in response_data
            assert response_data["token_type"] == "bearer"
            
            # Verify token content
            from backend.utils.auth import decode_jwt_token
            access_token_data = decode_jwt_token(response_data["access_token"])
            assert access_token_data["sub"] == str(user.id)
            assert access_token_data["token_type"] == "access"
            
            new_refresh_token_data = decode_jwt_token(response_data["refresh_token"])
            assert new_refresh_token_data["sub"] == str(user.id)
            assert new_refresh_token_data["token_type"] == "refresh"
            
            # Verify new refresh token is different from old one
            assert response_data["refresh_token"] != refresh_token
            
            # Verify old token is revoked in database
            await test_db.refresh(db_refresh_token)
            assert db_refresh_token.revoked == True
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, test_db):
        """Test refresh with invalid token."""
        # Create an invalid refresh token
        invalid_token = "invalid.token.here"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            refresh_data = {
                "refresh_token": invalid_token
            }
            
            endpoint = f"{settings.api_prefix}/auth/refresh"
            response = await client.post(endpoint, json=refresh_data)
            
            # Assert response
            assert response.status_code == 401
            assert response.json()["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_refresh_token_expired(self, test_db):
        """Test refresh with expired token."""
        # Create a user
        user = User(
            email="expired@example.com",
            username="expireduser",
            hashed_password="temp_hash"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        # Create expired refresh token
        expired_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )
        
        # Store expired token in database
        expired_time = datetime.utcnow() - timedelta(seconds=1)
        db_refresh_token = RefreshToken(
            token=expired_token,
            user_id=user.id,
            expires_at=expired_time,
            revoked=False
        )
        test_db.add(db_refresh_token)
        await test_db.commit()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            refresh_data = {
                "refresh_token": expired_token
            }
            
            endpoint = f"{settings.api_prefix}/auth/refresh"
            response = await client.post(endpoint, json=refresh_data)
            
            # Assert response
            assert response.status_code == 401
            assert response.json()["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_refresh_token_revoked(self, test_db):
        """Test refresh with revoked token."""
        # Create a user
        user = User(
            email="revoked@example.com",
            username="revokeduser",
            hashed_password="temp_hash"
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        
        # Create valid refresh token
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        token_expires = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        # Store revoked token in database
        db_refresh_token = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=token_expires,
            revoked=True  # Token is already revoked
        )
        test_db.add(db_refresh_token)
        await test_db.commit()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            refresh_data = {
                "refresh_token": refresh_token
            }
            
            endpoint = f"{settings.api_prefix}/auth/refresh"
            response = await client.post(endpoint, json=refresh_data)
            
            # Assert response
            assert response.status_code == 401
            assert response.json()["status"] == "error"