import pytest
from unittest.mock import patch, MagicMock

from backend.utils.oauth_explanation import get_platform_explanation, _get_youtube_explanation
from backend.models.base import PlatformType
from backend.schemas.oauth_explanation import OAuthExplanation


class TestOAuthExplanation:
    """Tests for the OAuth explanation utility functions."""
    
    def test_get_platform_explanation_youtube(self):
        """Test getting explanation for YouTube platform."""
        # Arrange
        platform = PlatformType.YOUTUBE.value
        mock_child_profile = MagicMock()
        mock_child_profile.age = 15
        
        # Act
        result = get_platform_explanation(platform, mock_child_profile)
        
        # Assert
        assert isinstance(result, OAuthExplanation)
        assert result.platform == "youtube"
        assert result.title == "YouTube Account Linking"
        assert len(result.data_accessed) > 0
        assert len(result.process_steps) > 0
        assert len(result.privacy_notes) > 0
        assert result.age_specific_info is not None
        assert result.age_specific_info["consent_required"] == "child_consent"
    
    def test_get_platform_explanation_unsupported(self):
        """Test getting explanation for an unsupported platform."""
        # Arrange
        platform = "unsupported_platform"
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Unsupported platform: {platform}"):
            get_platform_explanation(platform)
    
    def test_get_youtube_explanation_no_child_profile(self):
        """Test getting YouTube explanation without a child profile."""
        # Act
        result = _get_youtube_explanation()
        
        # Assert
        assert isinstance(result, OAuthExplanation)
        assert result.platform == "youtube"
        assert result.age_specific_info is None
    
    def test_get_youtube_explanation_child_under_13(self):
        """Test getting YouTube explanation for a child under 13."""
        # Arrange
        mock_child_profile = MagicMock()
        mock_child_profile.age = 10
        
        # Act
        result = _get_youtube_explanation(mock_child_profile)
        
        # Assert
        assert isinstance(result, OAuthExplanation)
        assert result.age_specific_info is not None
        assert "COPPA" in result.age_specific_info["title"]
        assert result.age_specific_info["consent_required"] == "verifiable_parental_consent"
    
    def test_get_youtube_explanation_child_13_plus(self):
        """Test getting YouTube explanation for a child 13 or older."""
        # Arrange
        mock_child_profile = MagicMock()
        mock_child_profile.age = 15
        
        # Act
        result = _get_youtube_explanation(mock_child_profile)
        
        # Assert
        assert isinstance(result, OAuthExplanation)
        assert result.age_specific_info is not None
        assert "Teen" in result.age_specific_info["title"]
        assert result.age_specific_info["consent_required"] == "child_consent"
    
    def test_get_youtube_explanation_no_age(self):
        """Test getting YouTube explanation for a child with no age specified."""
        # Arrange
        mock_child_profile = MagicMock()
        mock_child_profile.age = None
        
        # Act
        result = _get_youtube_explanation(mock_child_profile)
        
        # Assert
        assert isinstance(result, OAuthExplanation)
        assert result.age_specific_info is None