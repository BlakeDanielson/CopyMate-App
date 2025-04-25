import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.models.user import ParentUser
from backend.models.base import AuditActionType
from backend.utils.oauth import generate_state_token


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestOAuthRouter:
    """Tests for the OAuth router endpoints."""
    
    @patch("backend.routers.oauth.decode_state_token")
    @patch("backend.routers.oauth.exchange_code_for_tokens")
    @patch("backend.routers.oauth.child_profile_repo")
    @patch("backend.routers.oauth.linked_account_repo")
    @patch("backend.routers.oauth.audit_log_repo")
    def test_oauth_callback_success(
        self, 
        mock_audit_log_repo, 
        mock_linked_account_repo, 
        mock_child_profile_repo, 
        mock_exchange_code_for_tokens, 
        mock_decode_state_token,
        client
    ):
        """Test the OAuth callback endpoint with a successful flow."""
        # Arrange
        code = "mock_code"
        state = "mock_state"
        child_profile_id = 123
        platform = "youtube"
        parent_id = 456
        
        # Mock the state token decoding
        mock_decode_state_token.return_value = {
            "child_profile_id": child_profile_id,
            "platform": platform,
            "parent_id": parent_id,
            "timestamp": "2025-04-22T08:00:00"
        }
        
        # Mock the child profile
        mock_child_profile = MagicMock()
        mock_child_profile.id = child_profile_id
        mock_child_profile.parent_id = parent_id
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Mock the token exchange
        mock_exchange_code_for_tokens.return_value = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "token_expiry": None,
            "platform_account_id": "mock_channel_id",
            "platform_username": "Mock Channel",
            "metadata": {"key": "value"}
        }
        
        # Mock the linked account creation
        mock_db_account = MagicMock()
        mock_db_account.id = 789
        mock_linked_account_repo.create.return_value = mock_db_account
        mock_linked_account_repo.list.return_value = []  # No existing accounts
        
        # Act
        response = client.get(f"/api/v1/oauth/callback?code={code}&state={state}")
        
        # Assert
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["status"] == "success"
        assert response_json["message"] == "Account successfully linked"
        assert response_json["redirect_to"] == f"/dashboard/child/{child_profile_id}"
        
        # Check the linked account details
        assert "linked_account" in response_json
        linked_account = response_json["linked_account"]
        assert linked_account["id"] == mock_db_account.id
        assert linked_account["platform"] == platform
        assert linked_account["platform_username"] == "Mock Channel"
        assert linked_account["platform_account_id"] == "mock_channel_id"
        assert linked_account["child_profile_id"] == child_profile_id
        assert linked_account["is_new"] is True
        assert "timestamp" in linked_account
        
        mock_decode_state_token.assert_called_once_with(state)
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
        mock_exchange_code_for_tokens.assert_called_once_with(platform, code)
        mock_linked_account_repo.create.assert_called_once()
        mock_audit_log_repo.log_action.assert_called_once_with(
            pytest.ANY,
            action=AuditActionType.ACCOUNT_LINK,
            parent_id=parent_id,
            resource_type="linked_account",
            resource_id=mock_db_account.id,
            details={
                "platform": platform,
                "platform_username": "Mock Channel",
                "action": "created"
            }
        )
    
    @patch("backend.routers.oauth.decode_state_token")
    @patch("backend.routers.oauth.exchange_code_for_tokens")
    @patch("backend.routers.oauth.child_profile_repo")
    @patch("backend.routers.oauth.linked_account_repo")
    @patch("backend.routers.oauth.audit_log_repo")
    def test_oauth_callback_update_existing_account(
        self, 
        mock_audit_log_repo, 
        mock_linked_account_repo, 
        mock_child_profile_repo, 
        mock_exchange_code_for_tokens, 
        mock_decode_state_token,
        client
    ):
        """Test the OAuth callback endpoint with an existing account."""
        # Arrange
        code = "mock_code"
        state = "mock_state"
        child_profile_id = 123
        platform = "youtube"
        parent_id = 456
        
        # Mock the state token decoding
        mock_decode_state_token.return_value = {
            "child_profile_id": child_profile_id,
            "platform": platform,
            "parent_id": parent_id,
            "timestamp": "2025-04-22T08:00:00"
        }
        
        # Mock the child profile
        mock_child_profile = MagicMock()
        mock_child_profile.id = child_profile_id
        mock_child_profile.parent_id = parent_id
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Mock the token exchange
        mock_exchange_code_for_tokens.return_value = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "token_expiry": None,
            "platform_account_id": "mock_channel_id",
            "platform_username": "Mock Channel",
            "metadata": {"key": "value"}
        }
        
        # Mock an existing linked account
        mock_existing_account = MagicMock()
        mock_existing_account.id = 789
        mock_existing_account.platform_account_id = "mock_channel_id"
        mock_linked_account_repo.list.return_value = [mock_existing_account]
        
        # Mock the linked account update
        mock_updated_account = MagicMock()
        mock_updated_account.id = 789
        mock_linked_account_repo.update.return_value = mock_updated_account
        
        # Act
        response = client.get(f"/api/v1/oauth/callback?code={code}&state={state}")
        
        # Assert
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["status"] == "success"
        assert response_json["message"] == "Account successfully linked"
        assert response_json["redirect_to"] == f"/dashboard/child/{child_profile_id}"
        
        # Check the linked account details
        assert "linked_account" in response_json
        linked_account = response_json["linked_account"]
        assert linked_account["id"] == mock_updated_account.id
        assert linked_account["platform"] == platform
        assert linked_account["platform_username"] == "Mock Channel"
        assert linked_account["platform_account_id"] == "mock_channel_id"
        assert linked_account["child_profile_id"] == child_profile_id
        assert linked_account["is_new"] is False
        assert "timestamp" in linked_account
        
        mock_decode_state_token.assert_called_once_with(state)
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
        mock_exchange_code_for_tokens.assert_called_once_with(platform, code)
        mock_linked_account_repo.update.assert_called_once()
        mock_audit_log_repo.log_action.assert_called_once_with(
            pytest.ANY,
            action=AuditActionType.ACCOUNT_LINK,
            parent_id=parent_id,
            resource_type="linked_account",
            resource_id=mock_updated_account.id,
            details={
                "platform": platform,
                "platform_username": "Mock Channel",
                "action": "updated"
            }
        )
    
    @patch("backend.routers.oauth.audit_log_repo")
    def test_oauth_callback_error(self, mock_audit_log_repo, client):
        """Test the OAuth callback endpoint with an error from the OAuth provider."""
        # Arrange
        error = "access_denied"
        state = "mock_state"
        
        # Act
        response = client.get(f"/api/v1/oauth/callback?error={error}&state={state}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "error"
        assert "Authorization denied or error occurred" in response.json()["message"]
        assert response.json()["redirect_to"] == "/account-linking-error"
        
        mock_audit_log_repo.log_action.assert_called_once_with(
            pytest.ANY,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=None,
            resource_type="oauth",
            resource_id=None,
            details={
                "error": error,
                "state": state
            }
        )
    
    @patch("backend.routers.oauth.decode_state_token")
    @patch("backend.routers.oauth.audit_log_repo")
    def test_oauth_callback_invalid_state(self, mock_audit_log_repo, mock_decode_state_token, client):
        """Test the OAuth callback endpoint with an invalid state token."""
        # Arrange
        code = "mock_code"
        state = "invalid_state"
        
        # Mock the state token decoding to raise an error
        mock_decode_state_token.side_effect = ValueError("Invalid state token")
        
        # Act
        response = client.get(f"/api/v1/oauth/callback?code={code}&state={state}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "error"
        assert response.json()["message"] == "Invalid or expired state token"
        assert response.json()["redirect_to"] == "/account-linking-error"
        
        mock_decode_state_token.assert_called_once_with(state)
        mock_audit_log_repo.log_action.assert_called_once_with(
            pytest.ANY,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=None,
            resource_type="oauth",
            resource_id=None,
            details={
                "error": "Invalid state token",
                "state": state
            }
        )