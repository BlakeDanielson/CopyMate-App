import pytest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.celery_worker import perform_account_scan
from backend.models.user import LinkedAccount, ChildProfile
from backend.models.content import SubscribedChannel, AnalyzedVideo, AnalysisResult, Alert
from backend.models.base import PlatformType, RiskCategory, AlertType, AuditActionType

# Setup for in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_database):
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def mock_celery_task():
    """Create a mock Celery task."""
    mock_task = MagicMock()
    mock_task.request.id = "mock-task-id"
    return mock_task

@pytest.fixture
def sample_linked_account(db_session):
    """Create a sample linked account for testing."""
    # Create a parent user
    from backend.models.user import ParentUser
    parent = ParentUser(
        email="parent@example.com",
        hashed_password="hashed_password",
        first_name="Parent",
        last_name="User"
    )
    db_session.add(parent)
    db_session.commit()
    
    # Create a child profile
    child = ChildProfile(
        parent_id=parent.id,
        display_name="Child Profile",
        age=12
    )
    db_session.add(child)
    db_session.commit()
    
    # Create a linked account
    account = LinkedAccount(
        child_profile_id=child.id,
        platform=PlatformType.YOUTUBE.value,
        platform_account_id="youtube_account_id",
        platform_username="youtube_username",
        access_token="access_token",
        refresh_token="refresh_token",
        token_expiry=datetime.now(),
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    
    return account

@patch("backend.celery_worker.SessionLocal")
@patch("backend.celery_worker.Cache")
@patch("backend.celery_worker.linked_account_repo")
@patch("backend.celery_worker.child_profile_repo")
def test_perform_account_scan_account_not_found(
    mock_child_profile_repo, mock_linked_account_repo, mock_cache, mock_session_local, 
    mock_celery_task, db_session
):
    """Test perform_account_scan when the linked account is not found."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session_local.return_value = mock_session_instance
    
    # Mock the linked_account_repo.get method to return None
    mock_linked_account_repo.get.return_value = None
    
    # Call the task
    result = perform_account_scan(mock_celery_task, 999)
    
    # Verify the result
    assert result["linked_account_id"] == 999
    assert result["status"] == "failed"
    assert result["message"] == "Linked account not found"
    
    # Verify the mocks were called correctly
    mock_linked_account_repo.get.assert_called_once_with(mock_session_instance, 999)
    mock_session_instance.close.assert_called_once()

@patch("backend.celery_worker.SessionLocal")
@patch("backend.celery_worker.Cache")
@patch("backend.celery_worker.linked_account_repo")
@patch("backend.celery_worker.child_profile_repo")
def test_perform_account_scan_child_profile_not_found(
    mock_child_profile_repo, mock_linked_account_repo, mock_cache, mock_session_local, 
    mock_celery_task, db_session
):
    """Test perform_account_scan when the child profile is not found."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session_local.return_value = mock_session_instance
    
    # Create a mock linked account
    mock_account = MagicMock()
    mock_account.id = 1
    mock_account.child_profile_id = 999
    
    # Mock the linked_account_repo.get method to return the mock account
    mock_linked_account_repo.get.return_value = mock_account
    
    # Mock the child_profile_repo.get method to return None
    mock_child_profile_repo.get.return_value = None
    
    # Call the task
    result = perform_account_scan(mock_celery_task, 1)
    
    # Verify the result
    assert result["linked_account_id"] == 1
    assert result["status"] == "failed"
    assert result["message"] == "Child profile not found"
    
    # Verify the mocks were called correctly
    mock_linked_account_repo.get.assert_called_once_with(mock_session_instance, 1)
    mock_child_profile_repo.get.assert_called_once_with(mock_session_instance, 999)
    mock_session_instance.close.assert_called_once()

@patch("backend.celery_worker.SessionLocal")
@patch("backend.celery_worker.Cache")
@patch("backend.celery_worker.linked_account_repo")
@patch("backend.celery_worker.child_profile_repo")
@patch("backend.celery_worker.fetch_channel_details")
@patch("backend.celery_worker.audit_log_repo")
def test_perform_account_scan_channel_details_not_found(
    mock_audit_log_repo, mock_fetch_channel_details, mock_child_profile_repo, 
    mock_linked_account_repo, mock_cache, mock_session_local, mock_celery_task, db_session
):
    """Test perform_account_scan when channel details cannot be fetched."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session_local.return_value = mock_session_instance
    
    # Create mock objects
    mock_account = MagicMock()
    mock_account.id = 1
    mock_account.child_profile_id = 2
    
    mock_child = MagicMock()
    mock_child.id = 2
    mock_child.parent_id = 3
    
    # Mock the repository methods
    mock_linked_account_repo.get.return_value = mock_account
    mock_child_profile_repo.get.return_value = mock_child
    
    # Mock the cache
    mock_cache_instance = MagicMock()
    mock_cache_instance.get.return_value = None
    mock_cache.return_value = mock_cache_instance
    
    # Mock fetch_channel_details to return None
    mock_fetch_channel_details.return_value = None
    
    # Call the task
    result = perform_account_scan(mock_celery_task, 1)
    
    # Verify the result
    assert result["linked_account_id"] == 1
    assert result["status"] == "failed"
    assert result["message"] == "Failed to fetch channel details"
    
    # Verify the mocks were called correctly
    mock_linked_account_repo.get.assert_called_once_with(mock_session_instance, 1)
    mock_child_profile_repo.get.assert_called_once_with(mock_session_instance, 2)
    mock_cache_instance.get.assert_called_once()
    mock_fetch_channel_details.assert_called_once()
    mock_audit_log_repo.log_action.assert_called_once()
    mock_session_instance.close.assert_called_once()

@patch("backend.celery_worker.SessionLocal")
@patch("backend.celery_worker.Cache")
@patch("backend.celery_worker.linked_account_repo")
@patch("backend.celery_worker.child_profile_repo")
@patch("backend.celery_worker.fetch_channel_details")
@patch("backend.celery_worker.subscribed_channel_repo")
@patch("backend.celery_worker.fetch_recent_videos")
@patch("backend.celery_worker.audit_log_repo")
@patch("backend.celery_worker.alert_repo")
def test_perform_account_scan_no_recent_videos(
    mock_alert_repo, mock_audit_log_repo, mock_fetch_recent_videos, 
    mock_subscribed_channel_repo, mock_fetch_channel_details, mock_child_profile_repo, 
    mock_linked_account_repo, mock_cache, mock_session_local, mock_celery_task, db_session
):
    """Test perform_account_scan when no recent videos are found."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session_local.return_value = mock_session_instance
    
    # Create mock objects
    mock_account = MagicMock()
    mock_account.id = 1
    mock_account.child_profile_id = 2
    
    mock_child = MagicMock()
    mock_child.id = 2
    mock_child.parent_id = 3
    
    mock_channel = MagicMock()
    mock_channel.id = 4
    mock_channel.title = "Test Channel"
    
    # Mock the repository methods
    mock_linked_account_repo.get.return_value = mock_account
    mock_child_profile_repo.get.return_value = mock_child
    mock_subscribed_channel_repo.get_by_channel_id.return_value = None
    mock_subscribed_channel_repo.create.return_value = mock_channel
    
    # Mock the cache
    mock_cache_instance = MagicMock()
    mock_cache_instance.get.return_value = None
    mock_cache.return_value = mock_cache_instance
    
    # Mock fetch_channel_details to return channel details
    mock_fetch_channel_details.return_value = {
        "snippet": {
            "title": "Test Channel",
            "description": "Test Description",
            "thumbnails": {"default": {"url": "thumbnail_url"}}
        },
        "statistics": {
            "subscriberCount": "1000",
            "videoCount": "100"
        }
    }
    
    # Mock fetch_recent_videos to return None (no videos)
    mock_fetch_recent_videos.return_value = None
    
    # Call the task
    result = perform_account_scan(mock_celery_task, 1)
    
    # Verify the result
    assert result["linked_account_id"] == 1
    assert result["status"] == "completed"
    assert result["message"] == "No recent videos found"
    
    # Verify the mocks were called correctly
    mock_linked_account_repo.get.assert_called_once_with(mock_session_instance, 1)
    mock_child_profile_repo.get.assert_called_once_with(mock_session_instance, 2)
    mock_cache_instance.get.assert_called()
    mock_fetch_channel_details.assert_called_once()
    mock_subscribed_channel_repo.get_by_channel_id.assert_called_once()
    mock_subscribed_channel_repo.create.assert_called_once()
    mock_fetch_recent_videos.assert_called_once()
    mock_linked_account_repo.update_last_scan.assert_called_once()
    mock_audit_log_repo.log_action.assert_called_once()
    mock_alert_repo.create_scan_complete_alert.assert_called_once()
    mock_session_instance.close.assert_called_once()

@patch("backend.celery_worker.SessionLocal")
@patch("backend.celery_worker.Cache")
@patch("backend.celery_worker.linked_account_repo")
@patch("backend.celery_worker.child_profile_repo")
@patch("backend.celery_worker.fetch_channel_details")
@patch("backend.celery_worker.subscribed_channel_repo")
@patch("backend.celery_worker.fetch_recent_videos")
@patch("backend.celery_worker.Analyzer")
@patch("backend.celery_worker.analyzed_video_repo")
@patch("backend.celery_worker.analysis_result_repo")
@patch("backend.celery_worker.audit_log_repo")
@patch("backend.celery_worker.alert_repo")
def test_perform_account_scan_successful_with_videos(
    mock_alert_repo, mock_audit_log_repo, mock_analysis_result_repo, 
    mock_analyzed_video_repo, mock_analyzer, mock_fetch_recent_videos, 
    mock_subscribed_channel_repo, mock_fetch_channel_details, mock_child_profile_repo, 
    mock_linked_account_repo, mock_cache, mock_session_local, mock_celery_task, db_session
):
    """Test perform_account_scan with successful video analysis."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session_local.return_value = mock_session_instance
    
    # Create mock objects
    mock_account = MagicMock()
    mock_account.id = 1
    mock_account.child_profile_id = 2
    
    mock_child = MagicMock()
    mock_child.id = 2
    mock_child.parent_id = 3
    
    mock_channel = MagicMock()
    mock_channel.id = 4
    mock_channel.title = "Test Channel"
    
    mock_video = MagicMock()
    mock_video.id = 5
    mock_video.title = "Test Video"
    
    mock_result = MagicMock()
    mock_result.id = 6
    mock_result.risk_category = RiskCategory.VIOLENCE
    
    # Mock the repository methods
    mock_linked_account_repo.get.return_value = mock_account
    mock_child_profile_repo.get.return_value = mock_child
    mock_subscribed_channel_repo.get_by_channel_id.return_value = None
    mock_subscribed_channel_repo.create.return_value = mock_channel
    mock_analyzed_video_repo.get_by_platform_id.return_value = None
    mock_analyzed_video_repo.create.return_value = mock_video
    mock_analysis_result_repo.create.return_value = mock_result
    
    # Mock the cache
    mock_cache_instance = MagicMock()
    mock_cache_instance.get.return_value = None
    mock_cache.return_value = mock_cache_instance
    
    # Mock fetch_channel_details to return channel details
    mock_fetch_channel_details.return_value = {
        "snippet": {
            "title": "Test Channel",
            "description": "Test Description",
            "thumbnails": {"default": {"url": "thumbnail_url"}}
        },
        "statistics": {
            "subscriberCount": "1000",
            "videoCount": "100"
        }
    }
    
    # Mock fetch_recent_videos to return videos
    mock_fetch_recent_videos.return_value = [
        {
            "id": "video_id_1",
            "snippet": {
                "title": "Test Video",
                "description": "Test Description",
                "thumbnails": {"default": {"url": "thumbnail_url"}},
                "publishedAt": "2023-01-01T00:00:00Z"
            }
        }
    ]
    
    # Mock the analyzer
    mock_analyzer_instance = MagicMock()
    mock_analyzer_instance.analyze_text.return_value = ["violence", "weapon"]
    mock_analyzer_instance.assign_flags.return_value = {"VIOLENCE": ["violence", "weapon"]}
    mock_analyzer.return_value = mock_analyzer_instance
    
    # Call the task
    result = perform_account_scan(mock_celery_task, 1)
    
    # Verify the result
    assert result["linked_account_id"] == 1
    assert result["status"] == "completed"
    assert result["videos_analyzed"] == 1
    assert result["flags_found"] == 1
    
    # Verify the mocks were called correctly
    mock_linked_account_repo.get.assert_called_once_with(mock_session_instance, 1)
    mock_child_profile_repo.get.assert_called_once_with(mock_session_instance, 2)
    mock_cache_instance.get.assert_called()
    mock_fetch_channel_details.assert_called_once()
    mock_subscribed_channel_repo.get_by_channel_id.assert_called_once()
    mock_subscribed_channel_repo.create.assert_called_once()
    mock_fetch_recent_videos.assert_called_once()
    mock_analyzed_video_repo.get_by_platform_id.assert_called_once()
    mock_analyzed_video_repo.create.assert_called_once()
    mock_analyzer_instance.analyze_text.assert_called_once()
    mock_analyzer_instance.assign_flags.assert_called_once()
    mock_analysis_result_repo.create.assert_called_once()
    mock_alert_repo.create_scan_complete_alert.assert_called_once()
    mock_alert_repo.create_new_flags_alert.assert_called_once()
    mock_audit_log_repo.log_action.assert_called_once()
    mock_linked_account_repo.update_last_scan.assert_called_once()
    mock_session_instance.close.assert_called_once()

@patch("backend.celery_worker.SessionLocal")
def test_perform_account_scan_exception_handling(
    mock_session_local, mock_celery_task, db_session
):
    """Test perform_account_scan exception handling."""
    # Mock the session
    mock_session_instance = MagicMock()
    mock_session_local.return_value = mock_session_instance
    
    # Make the session raise an exception when accessed
    mock_session_instance.__enter__.side_effect = Exception("Test exception")
    
    # Call the task
    result = perform_account_scan(mock_celery_task, 1)
    
    # Verify the result
    assert result["linked_account_id"] == 1
    assert result["status"] == "failed"
    assert "error" in result
    
    # Verify the session was closed
    mock_session_instance.close.assert_called_once()