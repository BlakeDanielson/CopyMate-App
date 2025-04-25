import pytest
from unittest.mock import patch, MagicMock

from backend.utils.oauth_revocation import revoke_oauth_token, _revoke_google_token
from backend.models.base import PlatformType


class TestOAuthRevocation:
    """Tests for the OAuth revocation utility functions."""
    
    @patch("backend.utils.oauth_revocation._revoke_google_token")
    def test_revoke_oauth_token_youtube(self, mock_revoke_google_token):
        """Test revoking a token for YouTube platform."""
        # Arrange
        platform = PlatformType.YOUTUBE.value
        token = "mock_token"
        token_type = "access_token"
        
        mock_result = {"status": "success", "message": "Token successfully revoked"}
        mock_revoke_google_token.return_value = mock_result
        
        # Act
        result = revoke_oauth_token(platform, token, token_type)
        
        # Assert
        assert result == mock_result
        mock_revoke_google_token.assert_called_once_with(token, token_type)
    
    def test_revoke_oauth_token_unsupported(self):
        """Test revoking a token for an unsupported platform."""
        # Arrange
        platform = "unsupported_platform"
        token = "mock_token"
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Unsupported platform: {platform}"):
            revoke_oauth_token(platform, token)
    
    @patch("backend.utils.oauth_revocation.requests.post")
    def test_revoke_google_token_success(self, mock_post):
        """Test successful Google token revocation."""
        # Arrange
        token = "mock_token"
        token_type = "access_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Act
        result = _revoke_google_token(token, token_type)
        
        # Assert
        assert result["status"] == "success"
        assert result["message"] == "Token successfully revoked"
        mock_post.assert_called_once()
        
        # Check that the correct data was sent
        call_args = mock_post.call_args
        assert "token=mock_token" in call_args[1]["data"]
        assert "token_type_hint=access_token" in call_args[1]["data"]
    
    @patch("backend.utils.oauth_revocation.requests.post")
    def test_revoke_google_token_error(self, mock_post):
        """Test Google token revocation with error."""
        # Arrange
        token = "mock_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_token", "error_description": "Token expired or revoked"}
        mock_post.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(ValueError, match="Token expired or revoked"):
            _revoke_google_token(token)
        
        mock_post.assert_called_once()
    
    @patch("backend.utils.oauth_revocation.requests.post")
    def test_revoke_google_token_error_no_json(self, mock_post):
        """Test Google token revocation with error and no JSON response."""
        # Arrange
        token = "mock_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(ValueError, match="Failed to revoke token: HTTP 500"):
            _revoke_google_token(token)
        
        mock_post.assert_called_once()