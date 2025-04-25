import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.models.user import ParentUser
from backend.models.base import AuditActionType, PlatformType
from backend.schemas.oauth_explanation import OAuthExplanation


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


class TestOAuthExplanationRouter:
    """Tests for the OAuth explanation router endpoints."""
    
    @patch("backend.routers.oauth_explanation.get_platform_explanation")
    @patch("backend.routers.oauth_explanation.child_profile_repo")
    @patch("backend.routers.oauth_explanation.audit_log_repo")
    @patch("backend.auth.get_current_active_user")
    def test_get_oauth_explanation_success(
        self, 
        mock_get_current_user,
        mock_audit_log_repo, 
        mock_child_profile_repo, 
        mock_get_platform_explanation,
        mock_current_user,
        client
    ):
        """Test the get OAuth explanation endpoint with a successful flow."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        platform = PlatformType.YOUTUBE.value
        child_profile_id = 123
        
        # Mock the child profile
        mock_child_profile = MagicMock()
        mock_child_profile.id = child_profile_id
        mock_child_profile.parent_id = mock_current_user.id
        mock_child_profile.age = 15
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Mock the explanation
        mock_explanation = OAuthExplanation(
            platform=platform,
            title="Test Title",
            description="Test Description",
            data_accessed=[],
            process_steps=[],
            privacy_notes=[]
        )
        mock_get_platform_explanation.return_value = mock_explanation
        
        # Act
        response = client.get(f"/api/v1/oauth-explanation/{platform}/{child_profile_id}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["explanation"]["platform"] == platform
        assert response.json()["explanation"]["title"] == "Test Title"
        
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
        mock_get_platform_explanation.assert_called_once_with(platform, mock_child_profile)
        mock_audit_log_repo.log_action.assert_called_once_with(
            pytest.ANY,
            action=AuditActionType.DATA_ACCESS,
            parent_id=mock_current_user.id,
            resource_type="oauth_explanation",
            resource_id=None,
            details={
                "platform": platform,
                "child_profile_id": child_profile_id
            }
        )
    
    @patch("backend.routers.oauth_explanation.child_profile_repo")
    @patch("backend.auth.get_current_active_user")
    def test_get_oauth_explanation_child_not_found(
        self, 
        mock_get_current_user,
        mock_child_profile_repo,
        mock_current_user,
        client
    ):
        """Test the get OAuth explanation endpoint with a non-existent child profile."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        platform = PlatformType.YOUTUBE.value
        child_profile_id = 999  # Non-existent ID
        
        # Mock the child profile not found
        mock_child_profile_repo.get.return_value = None
        
        # Act
        response = client.get(f"/api/v1/oauth-explanation/{platform}/{child_profile_id}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Child profile not found"
        
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
    
    @patch("backend.routers.oauth_explanation.child_profile_repo")
    @patch("backend.auth.get_current_active_user")
    def test_get_oauth_explanation_unauthorized(
        self, 
        mock_get_current_user,
        mock_child_profile_repo,
        mock_current_user,
        client
    ):
        """Test the get OAuth explanation endpoint with an unauthorized child profile."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        platform = PlatformType.YOUTUBE.value
        child_profile_id = 123
        
        # Mock the child profile belonging to a different parent
        mock_child_profile = MagicMock()
        mock_child_profile.id = child_profile_id
        mock_child_profile.parent_id = 999  # Different parent ID
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Act
        response = client.get(f"/api/v1/oauth-explanation/{platform}/{child_profile_id}")
        
        # Assert
        assert response.status_code == 403
        assert response.json()["detail"] == "You can only access information for your own children's profiles"
        
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)
    
    @patch("backend.routers.oauth_explanation.get_platform_explanation")
    @patch("backend.routers.oauth_explanation.child_profile_repo")
    @patch("backend.auth.get_current_active_user")
    def test_get_oauth_explanation_unsupported_platform(
        self, 
        mock_get_current_user,
        mock_child_profile_repo,
        mock_get_platform_explanation,
        mock_current_user,
        client
    ):
        """Test the get OAuth explanation endpoint with an unsupported platform."""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        platform = "unsupported_platform"
        child_profile_id = 123
        
        # Mock the child profile
        mock_child_profile = MagicMock()
        mock_child_profile.id = child_profile_id
        mock_child_profile.parent_id = mock_current_user.id
        mock_child_profile_repo.get.return_value = mock_child_profile
        
        # Mock the platform explanation to raise an error
        error_message = f"Unsupported platform: {platform}"
        mock_get_platform_explanation.side_effect = ValueError(error_message)
        
        # Act
        response = client.get(f"/api/v1/oauth-explanation/{platform}/{child_profile_id}")
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == error_message
        
        mock_child_profile_repo.get.assert_called_once_with(pytest.ANY, id=child_profile_id)