"""Tests for the YouTube OAuth endpoints."""
import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from fastapi import status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.schemas.linked_account import LinkedAccountCreate


@pytest.fixture
async def test_profile_for_youtube(test_db: AsyncSession, test_user: dict) -> dict:
    """Create a test profile specifically for YouTube tests."""
    from app.schemas.profile import ProfileCreate
    from app.crud.crud_profile import create_profile
    
    profile_data = {
        "name": "YouTube Test Child",
    }
    profile_in = ProfileCreate(**profile_data)
    profile = await create_profile(test_db, obj_in=profile_in, parent_id=test_user["id"])
    
    return {
        "id": profile.id,
        "name": profile.name,
        "parent_id": profile.parent_id,
    }


# ----- TEST AUTH URL GENERATION -----

@pytest.mark.asyncio
async def test_get_auth_url_success(
    client: AsyncClient, 
    token_headers: dict, 
    test_profile_for_youtube: dict, 
    monkeypatch
):
    """Test successful generation of YouTube auth URL for an owned profile."""
    # Arrange
    profile_id = test_profile_for_youtube["id"]
    mock_auth_url = "https://accounts.google.com/o/oauth2/auth?mock=parameters"
    
    # Use patch to mock the Flow class and its methods
    with patch("app.api.v1.endpoints.youtube.Flow") as mock_flow_class:
        # Set up the mock flow instance
        mock_flow_instance = MagicMock()
        mock_flow_class.from_client_config.return_value = mock_flow_instance
        
        # Mock the authorization_url method to return our test URL and state
        mock_flow_instance.authorization_url.return_value = (mock_auth_url, "mock_state")
        
        # Act
        response = await client.get(
            f"/api/v1/youtube/auth/url?profile_id={profile_id}",
            headers=token_headers
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "authorization_url" in data
        assert data["authorization_url"] == mock_auth_url
        
        # Verify Flow was created with correct parameters
        mock_flow_class.from_client_config.assert_called_once()
        
        # Verify authorization_url was called with expected parameters
        mock_flow_instance.authorization_url.assert_called_once()
        call_kwargs = mock_flow_instance.authorization_url.call_args.kwargs
        assert call_kwargs.get("access_type") == "offline"
        assert call_kwargs.get("prompt") == "consent"
        
        # Verify the state parameter is a valid JWT containing the profile_id
        state = call_kwargs.get("state")
        decoded_state = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "profile_id" in decoded_state
        assert decoded_state["profile_id"] == profile_id


@pytest.mark.asyncio
async def test_get_auth_url_profile_not_owned(
    client: AsyncClient, 
    second_token_headers: dict, 
    test_profile_for_youtube: dict
):
    """Test failure when requesting auth URL for a profile not owned by the authenticated user."""
    # Arrange
    profile_id = test_profile_for_youtube["id"]
    
    # Act
    response = await client.get(
        f"/api/v1/youtube/auth/url?profile_id={profile_id}",
        headers=second_token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_auth_url_unauthenticated(
    client: AsyncClient, 
    test_profile_for_youtube: dict
):
    """Test failure when requesting auth URL without authentication."""
    # Arrange
    profile_id = test_profile_for_youtube["id"]
    
    # Act
    response = await client.get(
        f"/api/v1/youtube/auth/url?profile_id={profile_id}"
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ----- TEST AUTH CALLBACK HANDLING -----

@pytest.mark.asyncio
async def test_auth_callback_success(
    client: AsyncClient, 
    test_db: AsyncSession,
    test_profile_for_youtube: dict, 
    monkeypatch
):
    """Test successful handling of OAuth callback."""
    # Arrange
    profile_id = test_profile_for_youtube["id"]
    
    # Generate a valid state JWT
    state_data = {"profile_id": profile_id, "csrf": "test_csrf_token"}
    state = jwt.encode(state_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Mock code from Google
    mock_code = "4/test_auth_code"
    
    # Create mock credentials
    mock_credentials = MagicMock()
    mock_credentials.token = "mock_access_token"
    mock_credentials.refresh_token = "mock_refresh_token"
    mock_credentials.expiry = None  # Could be a datetime if needed
    mock_credentials.scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    mock_credentials.valid = True
    
    # URL with parameters that would be received from Google
    callback_url = f"/api/v1/youtube/auth/callback?code={mock_code}&state={state}"
    
    # Mock create_or_update_linked_account function
    with patch("app.api.v1.endpoints.youtube.Flow") as mock_flow_class, \
         patch("app.crud.crud_linked_account.create_or_update_linked_account") as mock_create_account:
        
        # Set up mock flow
        mock_flow_instance = MagicMock()
        mock_flow_class.from_client_config.return_value = mock_flow_instance
        mock_flow_instance.credentials = mock_credentials
        
        # Act
        response = await client.get(callback_url)
        
        # Assert
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        
        # Verify redirect location
        assert "profile_id" in response.headers["location"]
        
        # Verify Flow.fetch_token was called
        mock_flow_instance.fetch_token.assert_called_once()
        
        # Verify create_or_update_linked_account was called with correct data
        mock_create_account.assert_called_once()
        call_kwargs = mock_create_account.call_args.kwargs
        obj_in = call_kwargs["obj_in"]
        assert isinstance(obj_in, LinkedAccountCreate)
        assert obj_in.provider == "youtube"
        assert obj_in.profile_id == profile_id
        assert obj_in.access_token == mock_credentials.token
        assert obj_in.refresh_token == mock_credentials.refresh_token


@pytest.mark.asyncio
async def test_auth_callback_missing_state(client: AsyncClient):
    """Test callback failure when state parameter is missing."""
    # Arrange
    callback_url = "/api/v1/youtube/auth/callback?code=4/test_code"
    
    # Act
    response = await client.get(callback_url)
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Missing state parameter" in data["detail"]


@pytest.mark.asyncio
async def test_auth_callback_invalid_state(client: AsyncClient):
    """Test callback failure when state parameter is invalid."""
    # Arrange
    invalid_state = "invalid-state-token"
    callback_url = f"/api/v1/youtube/auth/callback?code=4/test_code&state={invalid_state}"
    
    # Act
    response = await client.get(callback_url)
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "Invalid state parameter" in data["detail"]


@pytest.mark.asyncio
async def test_auth_callback_missing_profile_id(client: AsyncClient):
    """Test callback failure when state is missing profile_id."""
    # Arrange
    # Generate a state JWT without profile_id
    state_data = {"csrf": "test_csrf_token"}  # Missing profile_id
    state = jwt.encode(state_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    callback_url = f"/api/v1/youtube/auth/callback?code=4/test_code&state={state}"
    
    # Act
    response = await client.get(callback_url)
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "detail" in data
    assert "missing profile_id" in data["detail"]


@pytest.mark.asyncio
async def test_auth_callback_fetch_token_exception(client: AsyncClient, test_profile_for_youtube: dict):
    """Test callback failure when fetch_token raises an exception."""
    # Arrange
    profile_id = test_profile_for_youtube["id"]
    
    # Generate a valid state JWT
    state_data = {"profile_id": profile_id, "csrf": "test_csrf_token"}
    state = jwt.encode(state_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # URL with parameters
    callback_url = f"/api/v1/youtube/auth/callback?code=invalid_code&state={state}"
    
    # Mock Flow to raise an exception when fetch_token is called
    with patch("app.api.v1.endpoints.youtube.Flow") as mock_flow_class:
        mock_flow_instance = MagicMock()
        mock_flow_class.from_client_config.return_value = mock_flow_instance
        mock_flow_instance.fetch_token.side_effect = Exception("Invalid code")
        
        # Act
        response = await client.get(callback_url)
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert "error occurred during OAuth callback" in data["detail"].lower()