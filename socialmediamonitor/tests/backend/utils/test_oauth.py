import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.utils.oauth import (
    generate_state_token,
    decode_state_token,
    create_youtube_oauth_flow,
    generate_authorization_url,
    exchange_code_for_tokens,
    refresh_access_token
)
from backend.models.base import PlatformType
from backend.config import settings


class TestOAuthUtils:
    """Tests for the OAuth utility functions."""
    
    def test_generate_state_token(self):
        """Test generating a state token."""
        # Arrange
        child_profile_id = 123
        platform = "youtube"
        parent_id = 456
        
        # Act
        token = generate_state_token(child_profile_id, platform, parent_id)
        
        # Assert
        assert isinstance(token, str)
        # Decode the token to verify its contents
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["child_profile_id"] == child_profile_id
        assert payload["platform"] == platform
        assert payload["parent_id"] == parent_id
        assert "timestamp" in payload
        assert "nonce" in payload
    
    def test_decode_state_token(self):
        """Test decoding a state token."""
        # Arrange
        child_profile_id = 123
        platform = "youtube"
        parent_id = 456
        token = generate_state_token(child_profile_id, platform, parent_id)
        
        # Act
        payload = decode_state_token(token)
        
        # Assert
        assert payload["child_profile_id"] == child_profile_id
        assert payload["platform"] == platform
        assert payload["parent_id"] == parent_id
        assert "timestamp" in payload
        assert "nonce" in payload
    
    def test_decode_state_token_expired(self):
        """Test decoding an expired state token."""
        # Arrange
        child_profile_id = 123
        platform = "youtube"
        parent_id = 456
        
        # Create a token with a timestamp that's older than 1 hour
        payload = {
            "child_profile_id": child_profile_id,
            "platform": platform,
            "parent_id": parent_id,
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "nonce": "test_nonce"
        }
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        
        # Act & Assert
        with pytest.raises(ValueError, match="State token has expired"):
            decode_state_token(token)
    
    def test_decode_state_token_invalid(self):
        """Test decoding an invalid state token."""
        # Arrange
        token = "invalid_token"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid state token"):
            decode_state_token(token)
    
    @patch("backend.utils.oauth.Flow")
    def test_create_youtube_oauth_flow(self, mock_flow):
        """Test creating a YouTube OAuth flow."""
        # Arrange
        mock_flow_instance = MagicMock()
        mock_flow.from_client_config.return_value = mock_flow_instance
        
        # Act
        flow = create_youtube_oauth_flow()
        
        # Assert
        assert flow == mock_flow_instance
        mock_flow.from_client_config.assert_called_once()
        # Check that the client config contains the expected values
        client_config = mock_flow.from_client_config.call_args[1]["client_config"]
        assert client_config["web"]["client_id"] == settings.youtube_client_id
        assert client_config["web"]["client_secret"] == settings.youtube_client_secret
        assert settings.youtube_redirect_uri in client_config["web"]["redirect_uris"]
    
    @patch("backend.utils.oauth.create_youtube_oauth_flow")
    @patch("backend.utils.oauth.generate_state_token")
    def test_generate_authorization_url_youtube(self, mock_generate_state_token, mock_create_youtube_oauth_flow):
        """Test generating an authorization URL for YouTube."""
        # Arrange
        child_profile_id = 123
        platform = PlatformType.YOUTUBE.value
        parent_id = 456
        
        mock_state_token = "mock_state_token"
        mock_generate_state_token.return_value = mock_state_token
        
        mock_flow = MagicMock()
        mock_flow.authorization_url.return_value = ("https://example.com/auth", None)
        mock_create_youtube_oauth_flow.return_value = mock_flow
        
        # Act
        result = generate_authorization_url(child_profile_id, platform, parent_id)
        
        # Assert
        assert result["authorization_url"] == "https://example.com/auth"
        assert result["state"] == mock_state_token
        mock_generate_state_token.assert_called_once_with(child_profile_id, platform, parent_id)
        mock_create_youtube_oauth_flow.assert_called_once()
        mock_flow.authorization_url.assert_called_once_with(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=mock_state_token
        )
    
    def test_generate_authorization_url_unsupported_platform(self):
        """Test generating an authorization URL for an unsupported platform."""
        # Arrange
        child_profile_id = 123
        platform = "unsupported_platform"
        parent_id = 456
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Unsupported platform: {platform}"):
            generate_authorization_url(child_profile_id, platform, parent_id)
    
    @patch("backend.utils.oauth.create_youtube_oauth_flow")
    @patch("backend.utils.oauth.build")
    def test_exchange_code_for_tokens_youtube(self, mock_build, mock_create_youtube_oauth_flow):
        """Test exchanging an authorization code for tokens for YouTube."""
        # Arrange
        platform = PlatformType.YOUTUBE.value
        code = "mock_code"
        
        # Mock the OAuth flow
        mock_flow = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.token = "mock_access_token"
        mock_credentials.refresh_token = "mock_refresh_token"
        mock_credentials.expiry = datetime.utcnow() + timedelta(hours=1)
        mock_credentials.scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        mock_credentials.id_token = "mock_id_token"
        mock_flow.credentials = mock_credentials
        mock_create_youtube_oauth_flow.return_value = mock_flow
        
        # Mock the YouTube API client
        mock_youtube = MagicMock()
        mock_channels_list = MagicMock()
        mock_channels_list.execute.return_value = {
            "items": [
                {
                    "id": "mock_channel_id",
                    "snippet": {
                        "title": "Mock Channel Title"
                    }
                }
            ]
        }
        mock_youtube.channels().list.return_value = mock_channels_list
        mock_build.return_value = mock_youtube
        
        # Act
        result = exchange_code_for_tokens(platform, code)
        
        # Assert
        assert result["access_token"] == "mock_access_token"
        assert result["refresh_token"] == "mock_refresh_token"
        assert result["token_expiry"] == mock_credentials.expiry
        assert result["platform_account_id"] == "mock_channel_id"
        assert result["platform_username"] == "Mock Channel Title"
        assert result["metadata"]["scopes"] == ["https://www.googleapis.com/auth/youtube.readonly"]
        assert result["metadata"]["id_token"] == "mock_id_token"
        
        mock_create_youtube_oauth_flow.assert_called_once_with(None)
        mock_flow.fetch_token.assert_called_once_with(code=code)
        mock_build.assert_called_once_with('youtube', 'v3', credentials=mock_credentials)
        mock_youtube.channels().list.assert_called_once_with(part='snippet', mine=True)
    
    def test_exchange_code_for_tokens_unsupported_platform(self):
        """Test exchanging an authorization code for tokens for an unsupported platform."""
        # Arrange
        platform = "unsupported_platform"
        code = "mock_code"
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Unsupported platform: {platform}"):
            exchange_code_for_tokens(platform, code)
    
    @patch("backend.utils.oauth.Credentials")
    @patch("backend.utils.oauth.Request")
    def test_refresh_access_token_youtube(self, mock_request, mock_credentials):
        """Test refreshing an access token for YouTube."""
        # Arrange
        platform = PlatformType.YOUTUBE.value
        refresh_token = "mock_refresh_token"
        
        # Mock the credentials
        mock_credentials_instance = MagicMock()
        mock_credentials_instance.token = "mock_new_access_token"
        mock_credentials_instance.refresh_token = "mock_new_refresh_token"
        mock_credentials_instance.expiry = datetime.utcnow() + timedelta(hours=1)
        mock_credentials.return_value = mock_credentials_instance
        
        # Act
        result = refresh_access_token(platform, refresh_token)
        
        # Assert
        assert result["access_token"] == "mock_new_access_token"
        assert result["refresh_token"] == "mock_new_refresh_token"
        assert result["token_expiry"] == mock_credentials_instance.expiry
        
        mock_credentials.assert_called_once_with(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.youtube_client_id,
            client_secret=settings.youtube_client_secret
        )
        mock_credentials_instance.refresh.assert_called_once()
    
    def test_refresh_access_token_unsupported_platform(self):
        """Test refreshing an access token for an unsupported platform."""
        # Arrange
        platform = "unsupported_platform"
        refresh_token = "mock_refresh_token"
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Unsupported platform: {platform}"):
            refresh_access_token(platform, refresh_token)