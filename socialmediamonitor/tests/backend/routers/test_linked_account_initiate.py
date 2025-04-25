import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.models.user import ParentUser
from backend.models.base import AuditActionType
from backend.schemas.linked_account import LinkedAccountInitiate, PlatformEnum


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


class TestLinkedAccountInitiate:
    """Tests for the linked account initiation endpoint."""
    
    @patch("backend.routers.linked_account.generate_authorization_url")
    @patch("backend.routers.linked_account.child_profile_repo")
    @patch("backend.routers.linked_account.audit_log_repo")
    @patch("backend.auth.get_current_active_user")
    def test_initiate_account_linking_success(
        self, 
        mock_get_current_user,
        mock_audit_log_repo, 
        mock_child_profile_repo, 
        mock_generate_authorization_url,
        mock_current_user,
        client
    ):
        """Test the initiate account linking endpoint with a successful flow."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        child_profile_id = 123
        platform = PlatformEnum.YOUTUBE
        
        # Mock the child profile
        mock_child_profile = MagicMock()
        mock_child_profile.id = child_profile_id
        mock_child_profile.parent_id = mock_current_user.id
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Mock the authorization URL generation
        mock_auth_data = {
            "authorization_url": "https://example.com/auth",
            "state": "mock_state_token"
        }
        mock_generate_authorization_url.return_value = mock_auth_data
        
        # Act
        response = client.post(
            "/api/v1/linked_accounts/initiate-linking",
            json={
                "child_profile_id": child_profile_id,
                "platform": platform.value
            }
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == mock_auth_data
        
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
        mock_generate_authorization_url.assert_called_once_with(
            child_profile_id=child_profile_id,
            platform=platform.value,
            parent_id=mock_current_user.id
        )
        mock_audit_log_repo.log_action.assert_called_once_with(
            pytest.ANY,
            action=AuditActionType.ACCOUNT_LINK,
            parent_id=mock_current_user.id,
            resource_type="child_profile",
            resource_id=child_profile_id,
            details={
                "platform": platform.value,
                "action": "initiate_linking"
            }
        )
    
    @patch("backend.routers.linked_account.child_profile_repo")
    @patch("backend.auth.get_current_active_user")
    def test_initiate_account_linking_child_not_found(
        self, 
        mock_get_current_user,
        mock_child_profile_repo,
        mock_current_user,
        client
    ):
        """Test the initiate account linking endpoint with a non-existent child profile."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        child_profile_id = 999  # Non-existent ID
        platform = PlatformEnum.YOUTUBE
        
        # Mock the child profile not found
        mock_child_profile_repo.get.return_value = None
        
        # Act
        response = client.post(
            "/api/v1/linked_accounts/initiate-linking",
            json={
                "child_profile_id": child_profile_id,
                "platform": platform.value
            }
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Child profile not found"
        
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
    
    @patch("backend.routers.linked_account.child_profile_repo")
    @patch("backend.auth.get_current_active_user")
    def test_initiate_account_linking_unauthorized(
        self, 
        mock_get_current_user,
        mock_child_profile_repo,
        mock_current_user,
        client
    ):
        """Test the initiate account linking endpoint with an unauthorized child profile."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        child_profile_id = 123
        platform = PlatformEnum.YOUTUBE
        
        # Mock the child profile belonging to a different parent
        mock_child_profile = MagicMock()
        mock_child_profile.id = child_profile_id
        mock_child_profile.parent_id = 999  # Different parent ID
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Act
        response = client.post(
            "/api/v1/linked_accounts/initiate-linking",
            json={
                "child_profile_id": child_profile_id,
                "platform": platform.value
            }
        )
        
        # Assert
        assert response.status_code == 403
        assert response.json()["detail"] == "You can only link accounts to your own children's profiles"
        
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
    
    @patch("backend.routers.linked_account.generate_authorization_url")
    @patch("backend.routers.linked_account.child_profile_repo")
    @patch("backend.auth.get_current_active_user")
    def test_initiate_account_linking_platform_error(
        self, 
        mock_get_current_user,
        mock_child_profile_repo, 
        mock_generate_authorization_url,
        mock_current_user,
        client
    ):
        """Test the initiate account linking endpoint with an error from the platform."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        child_profile_id = 123
        platform = PlatformEnum.YOUTUBE
        
        # Mock the child profile
        mock_child_profile = MagicMock()
        mock_child_profile.id = child_profile_id
        mock_child_profile.parent_id = mock_current_user.id
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Mock the authorization URL generation to raise an error
        error_message = "Failed to generate authorization URL"
        mock_generate_authorization_url.side_effect = ValueError(error_message)
        
        # Act
        response = client.post(
            "/api/v1/linked_accounts/initiate-linking",
            json={
                "child_profile_id": child_profile_id,
                "platform": platform.value
            }
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == error_message
        
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
        mock_generate_authorization_url.assert_called_once_with(
            child_profile_id=child_profile_id,
            platform=platform.value,
            parent_id=mock_current_user.id
        )