import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from backend.main import app
from backend.models.user import ParentUser
from backend.models.base import AuditActionType


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_current_user():
    """Create a mock authenticated user."""
    user = ParentUser()
    user.id = 1
    user.email = "test@example.com"
    user.is_active = True
    return user


class TestLinkedAccountUnlink:
    """Tests for the linked account unlinking endpoint."""
    
    @patch("backend.routers.linked_account.revoke_oauth_token")
    @patch("backend.routers.linked_account.linked_account_repo")
    @patch("backend.routers.linked_account.child_profile_repo")
    @patch("backend.routers.linked_account.audit_log_repo")
    @patch("backend.auth.get_current_active_user")
    def test_unlink_account_success(
        self, 
        mock_get_current_user,
        mock_audit_log_repo, 
        mock_child_profile_repo, 
        mock_linked_account_repo,
        mock_revoke_oauth_token,
        mock_current_user,
        client
    ):
        """Test the unlink account endpoint with a successful flow."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        account_id = 123
        platform = "youtube"
        
        # Mock the linked account
        mock_account = MagicMock()
        mock_account.id = account_id
        mock_account.platform = platform
        mock_account.platform_username = "Mock Channel"
        mock_account.child_profile_id = 456
        mock_account.access_token = "mock_access_token"
        mock_account.refresh_token = "mock_refresh_token"
        mock_linked_account_repo.get.return_value = mock_account
        
        # Mock the child profile
        mock_child_profile = MagicMock()
        mock_child_profile.id = mock_account.child_profile_id
        mock_child_profile.parent_id = mock_current_user.id
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Mock the account update
        mock_updated_account = MagicMock()
        mock_updated_account.id = account_id
        mock_updated_account.platform = platform
        mock_updated_account.platform_username = "Mock Channel"
        mock_updated_account.is_active = False
        mock_linked_account_repo.update.return_value = mock_updated_account
        
        # Act
        response = client.post(f"/api/v1/linked_accounts/{account_id}/unlink")
        
        # Assert
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["status"] == "success"
        assert response_json["message"] == "Account successfully unlinked"
        assert response_json["account_id"] == account_id
        assert response_json["platform"] == platform
        assert "unlinked_at" in response_json
        
        mock_linked_account_repo.get.assert_called_once_with(pytest.ANY, id=account_id)
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=mock_account.child_profile_id)
        
        # Check that both tokens were revoked
        assert mock_revoke_oauth_token.call_count == 2
        mock_revoke_oauth_token.assert_any_call(platform, "mock_access_token", "access_token")
        mock_revoke_oauth_token.assert_any_call(platform, "mock_refresh_token", "refresh_token")
        
        # Check that the account was deactivated
        mock_linked_account_repo.update.assert_called_once()
        update_data = mock_linked_account_repo.update.call_args[1]["obj_in"]
        assert update_data["is_active"] is False
        assert "updated_at" in update_data
        
        # Check that the action was logged
        mock_audit_log_repo.log_action.assert_called_once_with(
            pytest.ANY,
            action=AuditActionType.ACCOUNT_UNLINK,
            parent_id=mock_current_user.id,
            resource_type="linked_account",
            resource_id=account_id,
            details={
                "platform": platform,
                "platform_username": "Mock Channel"
            }
        )
    
    @patch("backend.routers.linked_account.revoke_oauth_token")
    @patch("backend.routers.linked_account.linked_account_repo")
    @patch("backend.routers.linked_account.child_profile_repo")
    @patch("backend.routers.linked_account.audit_log_repo")
    @patch("backend.auth.get_current_active_user")
    def test_unlink_account_token_revocation_error(
        self, 
        mock_get_current_user,
        mock_audit_log_repo, 
        mock_child_profile_repo, 
        mock_linked_account_repo,
        mock_revoke_oauth_token,
        mock_current_user,
        client
    ):
        """Test the unlink account endpoint with a token revocation error."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        account_id = 123
        platform = "youtube"
        
        # Mock the linked account
        mock_account = MagicMock()
        mock_account.id = account_id
        mock_account.platform = platform
        mock_account.platform_username = "Mock Channel"
        mock_account.child_profile_id = 456
        mock_account.access_token = "mock_access_token"
        mock_account.refresh_token = "mock_refresh_token"
        mock_linked_account_repo.get.return_value = mock_account
        
        # Mock the child profile
        mock_child_profile = MagicMock()
        mock_child_profile.id = mock_account.child_profile_id
        mock_child_profile.parent_id = mock_current_user.id
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Mock the token revocation to fail
        error_message = "Token revocation failed"
        mock_revoke_oauth_token.side_effect = ValueError(error_message)
        
        # Mock the account update
        mock_updated_account = MagicMock()
        mock_updated_account.id = account_id
        mock_updated_account.platform = platform
        mock_updated_account.platform_username = "Mock Channel"
        mock_updated_account.is_active = False
        mock_linked_account_repo.update.return_value = mock_updated_account
        
        # Act
        response = client.post(f"/api/v1/linked_accounts/{account_id}/unlink")
        
        # Assert
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["status"] == "success"
        assert response_json["message"] == "Account successfully unlinked"
        
        # Check that the error was logged
        mock_audit_log_repo.log_action.assert_any_call(
            pytest.ANY,
            action=AuditActionType.SYSTEM_ERROR,
            parent_id=mock_current_user.id,
            resource_type="oauth",
            resource_id=account_id,
            details={
                "error": error_message,
                "action": "token_revocation"
            }
        )
        
        # Check that the account was still deactivated despite the error
        mock_linked_account_repo.update.assert_called_once()
        update_data = mock_linked_account_repo.update.call_args[1]["obj_in"]
        assert update_data["is_active"] is False
    
    @patch("backend.routers.linked_account.linked_account_repo")
    @patch("backend.auth.get_current_active_user")
    def test_unlink_account_not_found(
        self, 
        mock_get_current_user,
        mock_linked_account_repo,
        mock_current_user,
        client
    ):
        """Test the unlink account endpoint with a non-existent account."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        account_id = 999  # Non-existent ID
        
        # Mock the account not found
        mock_linked_account_repo.get.return_value = None
        
        # Act
        response = client.post(f"/api/v1/linked_accounts/{account_id}/unlink")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Linked account not found"
        
        mock_linked_account_repo.get.assert_called_once_with(pytest.ANY, id=account_id)
    
    @patch("backend.routers.linked_account.linked_account_repo")
    @patch("backend.routers.linked_account.child_profile_repo")
    @patch("backend.auth.get_current_active_user")
    def test_unlink_account_unauthorized(
        self, 
        mock_get_current_user,
        mock_child_profile_repo,
        mock_linked_account_repo,
        mock_current_user,
        client
    ):
        """Test the unlink account endpoint with an unauthorized account."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        account_id = 123
        
        # Mock the linked account
        mock_account = MagicMock()
        mock_account.id = account_id
        mock_account.child_profile_id = 456
        mock_linked_account_repo.get.return_value = mock_account
        
        # Mock the child profile belonging to a different parent
        mock_child_profile = MagicMock()
        mock_child_profile.id = mock_account.child_profile_id
        mock_child_profile.parent_id = 999  # Different parent ID
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Act
        response = client.post(f"/api/v1/linked_accounts/{account_id}/unlink")
        
        # Assert
        assert response.status_code == 403
        assert response.json()["detail"] == "You can only unlink accounts linked to your own children's profiles"
        
        mock_linked_account_repo.get.assert_called_once_with(pytest.ANY, id=account_id)
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=mock_account.child_profile_id)