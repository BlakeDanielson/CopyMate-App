import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from backend.database import Base
from backend.models.user import ParentUser, ChildProfile, LinkedAccount
from backend.models.content import (
    SubscribedChannel, AnalyzedVideo, AnalysisResult, Alert, AuditLog
)
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
def parent_user(db_session):
    """Create a parent user for testing."""
    user = ParentUser(
        email="parent@example.com",
        hashed_password="hashed_password",
        first_name="Parent",
        last_name="User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def child_profile(db_session, parent_user):
    """Create a child profile for testing."""
    profile = ChildProfile(
        parent_id=parent_user.id,
        display_name="Child Profile",
        age=12,
        notes="Test notes"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile

@pytest.fixture
def linked_account(db_session, child_profile):
    """Create a linked account for testing."""
    account = LinkedAccount(
        child_profile_id=child_profile.id,
        platform=PlatformType.YOUTUBE.value,
        platform_account_id="youtube_account_id",
        platform_username="youtube_username",
        access_token="access_token",
        refresh_token="refresh_token",
        token_expiry=datetime.now(),
        platform_metadata={"key": "value"},
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account

@pytest.fixture
def subscribed_channel(db_session, linked_account):
    """Create a subscribed channel for testing."""
    channel = SubscribedChannel(
        linked_account_id=linked_account.id,
        channel_id="channel_id",
        title="Channel Title",
        description="Channel Description",
        thumbnail_url="thumbnail_url",
        subscriber_count=1000,
        video_count=100,
        topic_details={"topics": ["topic1", "topic2"]},
        last_fetched_at=datetime.now()
    )
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel

@pytest.fixture
def analyzed_video(db_session, subscribed_channel):
    """Create an analyzed video for testing."""
    video = AnalyzedVideo(
        channel_id=subscribed_channel.id,
        video_platform_id="video_id",
        title="Video Title",
        description="Video Description",
        thumbnail_url="thumbnail_url",
        published_at=datetime.now(),
        duration="PT5M30S",
        view_count=1000,
        like_count=100
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video

@pytest.fixture
def analysis_result(db_session, analyzed_video, subscribed_channel):
    """Create an analysis result for testing."""
    result = AnalysisResult(
        video_id=analyzed_video.id,
        channel_id=subscribed_channel.id,
        risk_category=RiskCategory.VIOLENCE,
        severity="medium",
        flagged_text="This video contains violent content",
        keywords_matched=["violence", "weapon"],
        confidence_score=0.8,
        marked_not_harmful=False
    )
    db_session.add(result)
    db_session.commit()
    db_session.refresh(result)
    return result

@pytest.fixture
def alert(db_session, child_profile):
    """Create an alert for testing."""
    alert = Alert(
        child_profile_id=child_profile.id,
        alert_type=AlertType.NEW_FLAGS.value,
        title="New flags detected",
        message="We found potentially concerning content",
        details={"categories": ["VIOLENCE"], "count": 1},
        is_read=False
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert

@pytest.fixture
def audit_log(db_session, parent_user):
    """Create an audit log for testing."""
    log = AuditLog(
        parent_id=parent_user.id,
        action=AuditActionType.USER_LOGIN,
        resource_type="parent_user",
        resource_id=parent_user.id,
        details={"method": "password"},
        ip_address="127.0.0.1",
        user_agent="Test User Agent"
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log

def test_parent_user_model(db_session, parent_user):
    """Test creating and retrieving a ParentUser."""
    # Verify the user was created correctly
    assert parent_user.id is not None
    assert parent_user.email == "parent@example.com"
    assert parent_user.hashed_password == "hashed_password"
    assert parent_user.first_name == "Parent"
    assert parent_user.last_name == "User"
    assert parent_user.is_active is True
    assert parent_user.created_at is not None
    assert parent_user.updated_at is None
    
    # Verify the user can be retrieved from the database
    retrieved_user = db_session.query(ParentUser).filter(ParentUser.id == parent_user.id).first()
    assert retrieved_user is not None
    assert retrieved_user.email == "parent@example.com"

def test_parent_user_unique_email(db_session, parent_user):
    """Test that ParentUser email must be unique."""
    # Try to create another user with the same email
    duplicate_user = ParentUser(
        email="parent@example.com",  # Same email as the fixture
        hashed_password="different_password",
        first_name="Another",
        last_name="User"
    )
    db_session.add(duplicate_user)
    
    # This should raise an IntegrityError due to the unique constraint on email
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_child_profile_model(db_session, child_profile, parent_user):
    """Test creating and retrieving a ChildProfile."""
    # Verify the profile was created correctly
    assert child_profile.id is not None
    assert child_profile.parent_id == parent_user.id
    assert child_profile.display_name == "Child Profile"
    assert child_profile.age == 12
    assert child_profile.notes == "Test notes"
    assert child_profile.is_active is True
    assert child_profile.created_at is not None
    
    # Verify the profile can be retrieved from the database
    retrieved_profile = db_session.query(ChildProfile).filter(ChildProfile.id == child_profile.id).first()
    assert retrieved_profile is not None
    assert retrieved_profile.display_name == "Child Profile"
    
    # Verify the relationship with ParentUser
    assert retrieved_profile.parent_id == parent_user.id
    assert retrieved_profile.parent.email == "parent@example.com"

def test_linked_account_model(db_session, linked_account, child_profile):
    """Test creating and retrieving a LinkedAccount."""
    # Verify the account was created correctly
    assert linked_account.id is not None
    assert linked_account.child_profile_id == child_profile.id
    assert linked_account.platform == PlatformType.YOUTUBE.value
    assert linked_account.platform_account_id == "youtube_account_id"
    assert linked_account.platform_username == "youtube_username"
    assert linked_account.access_token == "access_token"
    assert linked_account.refresh_token == "refresh_token"
    assert linked_account.token_expiry is not None
    assert linked_account.platform_metadata == {"key": "value"}
    assert linked_account.is_active is True
    assert linked_account.created_at is not None
    
    # Verify the account can be retrieved from the database
    retrieved_account = db_session.query(LinkedAccount).filter(LinkedAccount.id == linked_account.id).first()
    assert retrieved_account is not None
    assert retrieved_account.platform_username == "youtube_username"
    
    # Verify the relationship with ChildProfile
    assert retrieved_account.child_profile_id == child_profile.id
    assert retrieved_account.child_profile.display_name == "Child Profile"

def test_subscribed_channel_model(db_session, subscribed_channel, linked_account):
    """Test creating and retrieving a SubscribedChannel."""
    # Verify the channel was created correctly
    assert subscribed_channel.id is not None
    assert subscribed_channel.linked_account_id == linked_account.id
    assert subscribed_channel.channel_id == "channel_id"
    assert subscribed_channel.title == "Channel Title"
    assert subscribed_channel.description == "Channel Description"
    assert subscribed_channel.thumbnail_url == "thumbnail_url"
    assert subscribed_channel.subscriber_count == 1000
    assert subscribed_channel.video_count == 100
    assert subscribed_channel.topic_details == {"topics": ["topic1", "topic2"]}
    assert subscribed_channel.last_fetched_at is not None
    assert subscribed_channel.created_at is not None
    
    # Verify the channel can be retrieved from the database
    retrieved_channel = db_session.query(SubscribedChannel).filter(SubscribedChannel.id == subscribed_channel.id).first()
    assert retrieved_channel is not None
    assert retrieved_channel.title == "Channel Title"
    
    # Verify the relationship with LinkedAccount
    assert retrieved_channel.linked_account_id == linked_account.id
    assert retrieved_channel.linked_account.platform_username == "youtube_username"

def test_analyzed_video_model(db_session, analyzed_video, subscribed_channel):
    """Test creating and retrieving an AnalyzedVideo."""
    # Verify the video was created correctly
    assert analyzed_video.id is not None
    assert analyzed_video.channel_id == subscribed_channel.id
    assert analyzed_video.video_platform_id == "video_id"
    assert analyzed_video.title == "Video Title"
    assert analyzed_video.description == "Video Description"
    assert analyzed_video.thumbnail_url == "thumbnail_url"
    assert analyzed_video.published_at is not None
    assert analyzed_video.duration == "PT5M30S"
    assert analyzed_video.view_count == 1000
    assert analyzed_video.like_count == 100
    assert analyzed_video.created_at is not None
    
    # Verify the video can be retrieved from the database
    retrieved_video = db_session.query(AnalyzedVideo).filter(AnalyzedVideo.id == analyzed_video.id).first()
    assert retrieved_video is not None
    assert retrieved_video.title == "Video Title"
    
    # Verify the relationship with SubscribedChannel
    assert retrieved_video.channel_id == subscribed_channel.id
    assert retrieved_video.channel.title == "Channel Title"

def test_analysis_result_model(db_session, analysis_result, analyzed_video, subscribed_channel):
    """Test creating and retrieving an AnalysisResult."""
    # Verify the result was created correctly
    assert analysis_result.id is not None
    assert analysis_result.video_id == analyzed_video.id
    assert analysis_result.channel_id == subscribed_channel.id
    assert analysis_result.risk_category == RiskCategory.VIOLENCE
    assert analysis_result.severity == "medium"
    assert analysis_result.flagged_text == "This video contains violent content"
    assert analysis_result.keywords_matched == ["violence", "weapon"]
    assert analysis_result.confidence_score == 0.8
    assert analysis_result.marked_not_harmful is False
    assert analysis_result.created_at is not None
    
    # Verify the result can be retrieved from the database
    retrieved_result = db_session.query(AnalysisResult).filter(AnalysisResult.id == analysis_result.id).first()
    assert retrieved_result is not None
    assert retrieved_result.risk_category == RiskCategory.VIOLENCE
    
    # Verify the relationships
    assert retrieved_result.video_id == analyzed_video.id
    assert retrieved_result.video.title == "Video Title"
    assert retrieved_result.channel_id == subscribed_channel.id
    assert retrieved_result.channel.title == "Channel Title"

def test_alert_model(db_session, alert, child_profile):
    """Test creating and retrieving an Alert."""
    # Verify the alert was created correctly
    assert alert.id is not None
    assert alert.child_profile_id == child_profile.id
    assert alert.alert_type == AlertType.NEW_FLAGS.value
    assert alert.title == "New flags detected"
    assert alert.message == "We found potentially concerning content"
    assert alert.details == {"categories": ["VIOLENCE"], "count": 1}
    assert alert.is_read is False
    assert alert.created_at is not None
    
    # Verify the alert can be retrieved from the database
    retrieved_alert = db_session.query(Alert).filter(Alert.id == alert.id).first()
    assert retrieved_alert is not None
    assert retrieved_alert.title == "New flags detected"
    
    # Verify the relationship with ChildProfile
    assert retrieved_alert.child_profile_id == child_profile.id
    assert retrieved_alert.child_profile.display_name == "Child Profile"

def test_audit_log_model(db_session, audit_log, parent_user):
    """Test creating and retrieving an AuditLog."""
    # Verify the log was created correctly
    assert audit_log.id is not None
    assert audit_log.parent_id == parent_user.id
    assert audit_log.action == AuditActionType.USER_LOGIN
    assert audit_log.resource_type == "parent_user"
    assert audit_log.resource_id == parent_user.id
    assert audit_log.details == {"method": "password"}
    assert audit_log.ip_address == "127.0.0.1"
    assert audit_log.user_agent == "Test User Agent"
    assert audit_log.created_at is not None
    
    # Verify the log can be retrieved from the database
    retrieved_log = db_session.query(AuditLog).filter(AuditLog.id == audit_log.id).first()
    assert retrieved_log is not None
    assert retrieved_log.action == AuditActionType.USER_LOGIN
    
    # Verify the relationship with ParentUser
    assert retrieved_log.parent_id == parent_user.id
    assert retrieved_log.parent.email == "parent@example.com"

def test_cascade_delete_parent_user(db_session, parent_user, child_profile, audit_log):
    """Test that deleting a ParentUser cascades to related entities."""
    # Verify the related entities exist
    assert db_session.query(ChildProfile).filter(ChildProfile.parent_id == parent_user.id).count() > 0
    assert db_session.query(AuditLog).filter(AuditLog.parent_id == parent_user.id).count() > 0
    
    # Delete the parent user
    db_session.delete(parent_user)
    db_session.commit()
    
    # Verify the related entities were deleted
    assert db_session.query(ChildProfile).filter(ChildProfile.parent_id == parent_user.id).count() == 0
    assert db_session.query(AuditLog).filter(AuditLog.parent_id == parent_user.id).count() == 0

def test_cascade_delete_child_profile(db_session, child_profile, linked_account, alert):
    """Test that deleting a ChildProfile cascades to related entities."""
    # Verify the related entities exist
    assert db_session.query(LinkedAccount).filter(LinkedAccount.child_profile_id == child_profile.id).count() > 0
    assert db_session.query(Alert).filter(Alert.child_profile_id == child_profile.id).count() > 0
    
    # Delete the child profile
    db_session.delete(child_profile)
    db_session.commit()
    
    # Verify the related entities were deleted
    assert db_session.query(LinkedAccount).filter(LinkedAccount.child_profile_id == child_profile.id).count() == 0
    assert db_session.query(Alert).filter(Alert.child_profile_id == child_profile.id).count() == 0

def test_cascade_delete_linked_account(db_session, linked_account, subscribed_channel):
    """Test that deleting a LinkedAccount cascades to related entities."""
    # Verify the related entities exist
    assert db_session.query(SubscribedChannel).filter(SubscribedChannel.linked_account_id == linked_account.id).count() > 0
    
    # Delete the linked account
    db_session.delete(linked_account)
    db_session.commit()
    
    # Verify the related entities were deleted
    assert db_session.query(SubscribedChannel).filter(SubscribedChannel.linked_account_id == linked_account.id).count() == 0