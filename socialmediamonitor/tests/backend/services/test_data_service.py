import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.user import ParentUser, ChildProfile, LinkedAccount
from backend.models.content import Alert, AuditLog
from backend.models.base import PlatformType, AuditActionType
from backend.services.data_service import DataService

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
def data_service():
    return DataService()

@pytest.fixture
def sample_parent_user(db_session):
    """Create a sample parent user for testing."""
    parent = ParentUser(
        email="parent@example.com",
        hashed_password="hashed_password",
        first_name="Parent",
        last_name="User"
    )
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)
    return parent

@pytest.fixture
def sample_child_profile(db_session, sample_parent_user):
    """Create a sample child profile for testing."""
    child = ChildProfile(
        parent_id=sample_parent_user.id,
        display_name="Child Profile",
        age=12
    )
    db_session.add(child)
    db_session.commit()
    db_session.refresh(child)
    return child

@pytest.fixture
def sample_linked_account(db_session, sample_child_profile):
    """Create a sample linked account for testing."""
    account = LinkedAccount(
        child_profile_id=sample_child_profile.id,
        platform=PlatformType.YOUTUBE.value,
        platform_account_id="youtube_account_id",
        platform_username="youtube_username",
        access_token="access_token",
        refresh_token="refresh_token",
        token_expiry=datetime.now() + timedelta(days=1),
        platform_metadata={"key": "value"},
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account

def test_get_parent_by_email(db_session, data_service, sample_parent_user):
    """Test retrieving a parent user by email."""
    # Mock the repository method
    data_service.parent_user_repo.get_by_email = MagicMock(return_value=sample_parent_user)
    
    # Call the service method
    parent = data_service.get_parent_by_email(db_session, "parent@example.com")
    
    # Verify the repository method was called correctly
    data_service.parent_user_repo.get_by_email.assert_called_once_with(db_session, "parent@example.com")
    
    # Verify the result
    assert parent is not None
    assert parent.id == sample_parent_user.id
    assert parent.email == "parent@example.com"

def test_get_child_profiles_for_parent(db_session, data_service, sample_parent_user, sample_child_profile):
    """Test retrieving child profiles for a parent."""
    # Mock the repository method
    data_service.child_profile_repo.get_profiles_by_parent = MagicMock(return_value=[sample_child_profile])
    
    # Call the service method
    profiles = data_service.get_child_profiles_for_parent(db_session, sample_parent_user.id)
    
    # Verify the repository method was called correctly
    data_service.child_profile_repo.get_profiles_by_parent.assert_called_once_with(
        db_session, sample_parent_user.id, active_only=True
    )
    
    # Verify the result
    assert len(profiles) == 1
    assert profiles[0].id == sample_child_profile.id
    assert profiles[0].parent_id == sample_parent_user.id

def test_create_child_profile(db_session, data_service, sample_parent_user):
    """Test creating a new child profile."""
    # Mock the repository methods
    mock_profile = ChildProfile(
        id=1,
        parent_id=sample_parent_user.id,
        display_name="New Child",
        age=10
    )
    data_service.child_profile_repo.create = MagicMock(return_value=mock_profile)
    data_service.audit_log_repo.log_action = MagicMock()
    
    # Call the service method
    profile = data_service.create_child_profile(
        db_session, sample_parent_user.id, "New Child", age=10
    )
    
    # Verify the repository methods were called correctly
    data_service.child_profile_repo.create.assert_called_once()
    data_service.audit_log_repo.log_action.assert_called_once()
    
    # Verify the result
    assert profile is not None
    assert profile.parent_id == sample_parent_user.id
    assert profile.display_name == "New Child"
    assert profile.age == 10

def test_link_youtube_account(db_session, data_service, sample_child_profile):
    """Test linking a YouTube account to a child profile."""
    # Mock the repository methods
    mock_account = LinkedAccount(
        id=1,
        child_profile_id=sample_child_profile.id,
        platform=PlatformType.YOUTUBE.value,
        platform_account_id="youtube_id",
        platform_username="youtube_user",
        access_token="token"
    )
    data_service.linked_account_repo.create = MagicMock(return_value=mock_account)
    data_service.child_profile_repo.get = MagicMock(return_value=sample_child_profile)
    data_service.audit_log_repo.log_action = MagicMock()
    
    # Call the service method
    account = data_service.link_youtube_account(
        db_session,
        sample_child_profile.id,
        "youtube_id",
        "youtube_user",
        "token"
    )
    
    # Verify the repository methods were called correctly
    data_service.linked_account_repo.create.assert_called_once()
    data_service.child_profile_repo.get.assert_called_once_with(db_session, sample_child_profile.id)
    data_service.audit_log_repo.log_action.assert_called_once()
    
    # Verify the result
    assert account is not None
    assert account.child_profile_id == sample_child_profile.id
    assert account.platform == PlatformType.YOUTUBE.value
    assert account.platform_account_id == "youtube_id"
    assert account.platform_username == "youtube_user"
    assert account.access_token == "token"

def test_unlink_account(db_session, data_service, sample_linked_account):
    """Test unlinking a social media account."""
    # Mock the repository methods
    data_service.linked_account_repo.deactivate_account = MagicMock(return_value=sample_linked_account)
    data_service.audit_log_repo.log_action = MagicMock()
    
    # Call the service method
    account = data_service.unlink_account(
        db_session, sample_linked_account.id, parent_id=1
    )
    
    # Verify the repository methods were called correctly
    data_service.linked_account_repo.deactivate_account.assert_called_once_with(
        db_session, sample_linked_account.id
    )
    data_service.audit_log_repo.log_action.assert_called_once()
    
    # Verify the result
    assert account is not None
    assert account.id == sample_linked_account.id

def test_get_linked_accounts_for_child(db_session, data_service, sample_child_profile, sample_linked_account):
    """Test retrieving linked accounts for a child profile."""
    # Mock the repository method
    data_service.linked_account_repo.get_linked_accounts_for_child = MagicMock(
        return_value=[sample_linked_account]
    )
    
    # Call the service method
    accounts = data_service.get_linked_accounts_for_child(
        db_session, sample_child_profile.id
    )
    
    # Verify the repository method was called correctly
    data_service.linked_account_repo.get_linked_accounts_for_child.assert_called_once_with(
        db_session, sample_child_profile.id, active_only=True
    )
    
    # Verify the result
    assert len(accounts) == 1
    assert accounts[0].id == sample_linked_account.id
    assert accounts[0].child_profile_id == sample_child_profile.id

def test_get_unread_alerts_for_child(db_session, data_service, sample_child_profile):
    """Test retrieving unread alerts for a child profile."""
    # Create a mock alert
    mock_alert = Alert(
        id=1,
        child_profile_id=sample_child_profile.id,
        alert_type="NEW_FLAGS",
        is_read=False
    )
    
    # Mock the repository method
    data_service.alert_repo.get_alerts_for_child = MagicMock(
        return_value=[mock_alert]
    )
    
    # Call the service method
    alerts = data_service.get_unread_alerts_for_child(
        db_session, sample_child_profile.id
    )
    
    # Verify the repository method was called correctly
    data_service.alert_repo.get_alerts_for_child.assert_called_once_with(
        db_session, sample_child_profile.id, unread_only=True, limit=10
    )
    
    # Verify the result
    assert len(alerts) == 1
    assert alerts[0].id == mock_alert.id
    assert alerts[0].child_profile_id == sample_child_profile.id
    assert alerts[0].is_read is False

def test_mark_alert_as_read(db_session, data_service):
    """Test marking an alert as read."""
    # Create a mock alert
    mock_alert = Alert(
        id=1,
        child_profile_id=1,
        alert_type="NEW_FLAGS",
        is_read=True
    )
    
    # Mock the repository methods
    data_service.alert_repo.mark_as_read = MagicMock(return_value=mock_alert)
    data_service.audit_log_repo.log_action = MagicMock()
    
    # Call the service method
    alert = data_service.mark_alert_as_read(
        db_session, 1, parent_id=1
    )
    
    # Verify the repository methods were called correctly
    data_service.alert_repo.mark_as_read.assert_called_once_with(db_session, 1)
    data_service.audit_log_repo.log_action.assert_called_once()
    
    # Verify the result
    assert alert is not None
    assert alert.id == 1
    assert alert.is_read is True

def test_mark_result_as_not_harmful(db_session, data_service):
    """Test marking an analysis result as not harmful."""
    # Create a mock analysis result
    from backend.models.content import AnalysisResult
    from backend.models.base import RiskCategory
    
    mock_result = AnalysisResult(
        id=1,
        video_id=1,
        channel_id=1,
        risk_category=RiskCategory.VIOLENCE,
        marked_not_harmful=True,
        marked_by_parent_id=1
    )
    
    # Mock the repository methods
    data_service.analysis_result_repo.mark_as_not_harmful = MagicMock(return_value=mock_result)
    data_service.audit_log_repo.log_action = MagicMock()
    
    # Call the service method
    result = data_service.mark_result_as_not_harmful(
        db_session, 1, parent_id=1
    )
    
    # Verify the repository methods were called correctly
    data_service.analysis_result_repo.mark_as_not_harmful.assert_called_once_with(
        db_session, 1, 1
    )
    data_service.audit_log_repo.log_action.assert_called_once()
    
    # Verify the result
    assert result is not None
    assert result.id == 1
    assert result.marked_not_harmful is True
    assert result.marked_by_parent_id == 1

def test_get_flagged_channels_for_child(db_session, data_service, sample_child_profile):
    """Test retrieving flagged channels for a child profile."""
    # Mock the complex query result
    mock_result = [
        (1, "Channel Title", "thumbnail_url", 1000, 5)
    ]
    
    # Create a mock for the query execution
    mock_query = MagicMock()
    mock_query.all.return_value = mock_result
    
    # Mock the session query method to return our mock query
    db_session.query = MagicMock(return_value=mock_query)
    
    # Set up the chain of mock calls
    mock_query.join.return_value = mock_query
    mock_query.join.return_value.join.return_value = mock_query
    mock_query.join.return_value.join.return_value.filter.return_value = mock_query
    mock_query.join.return_value.join.return_value.filter.return_value.filter.return_value = mock_query
    mock_query.join.return_value.join.return_value.filter.return_value.group_by.return_value = mock_query
    mock_query.join.return_value.join.return_value.filter.return_value.group_by.return_value.having.return_value = mock_query
    mock_query.join.return_value.join.return_value.filter.return_value.group_by.return_value.having.return_value.order_by.return_value = mock_query
    
    # Call the service method
    channels = data_service.get_flagged_channels_for_child(
        db_session, sample_child_profile.id
    )
    
    # Verify the result
    assert len(channels) == 1
    assert channels[0]["channel_id"] == 1
    assert channels[0]["title"] == "Channel Title"
    assert channels[0]["thumbnail_url"] == "thumbnail_url"
    assert channels[0]["subscriber_count"] == 1000
    assert channels[0]["flag_count"] == 5