import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.user import ParentUser
from backend.repositories.parent_user import ParentUserRepository

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
def parent_user_repo():
    return ParentUserRepository()

@pytest.fixture
def sample_users(db_session):
    """Create sample users for testing."""
    users = [
        ParentUser(
            email="user1@example.com",
            hashed_password="hashed_password1",
            first_name="John",
            last_name="Doe"
        ),
        ParentUser(
            email="user2@example.com",
            hashed_password="hashed_password2",
            first_name="Jane",
            last_name="Smith"
        ),
        ParentUser(
            email="admin@example.com",
            hashed_password="hashed_password3",
            first_name="Admin",
            last_name="User"
        )
    ]
    
    for user in users:
        db_session.add(user)
    
    db_session.commit()
    
    # Refresh users to get their IDs
    for user in users:
        db_session.refresh(user)
    
    return users

def test_get_by_email(db_session, parent_user_repo, sample_users):
    """Test retrieving a parent user by email."""
    # Test with existing email
    user = parent_user_repo.get_by_email(db_session, "user1@example.com")
    assert user is not None
    assert user.email == "user1@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    
    # Test with non-existent email
    user = parent_user_repo.get_by_email(db_session, "nonexistent@example.com")
    assert user is None

def test_search_by_name_or_email(db_session, parent_user_repo, sample_users):
    """Test searching parent users by name or email."""
    # Test search by email (partial match)
    users = parent_user_repo.search_by_name_or_email(db_session, "user")
    assert len(users) == 3  # Should match all users with "user" in email
    
    # Test search by first name
    users = parent_user_repo.search_by_name_or_email(db_session, "John")
    assert len(users) == 1
    assert users[0].first_name == "John"
    
    # Test search by last name
    users = parent_user_repo.search_by_name_or_email(db_session, "Smith")
    assert len(users) == 1
    assert users[0].last_name == "Smith"
    
    # Test with no matches
    users = parent_user_repo.search_by_name_or_email(db_session, "NonExistent")
    assert len(users) == 0
    
    # Test pagination
    all_users = parent_user_repo.search_by_name_or_email(db_session, "user")
    paginated_users = parent_user_repo.search_by_name_or_email(db_session, "user", skip=1, limit=1)
    assert len(paginated_users) == 1
    assert paginated_users[0].id != all_users[0].id

def test_update_last_login(db_session, parent_user_repo, sample_users):
    """Test updating the last_login timestamp of a parent user."""
    user = sample_users[0]
    
    # Initial state - last_login should be None
    assert user.last_login is None
    
    # Update last_login
    before_update = datetime.now()
    updated_user = parent_user_repo.update_last_login(db_session, user.id)
    after_update = datetime.now()
    
    # Verify last_login was updated
    assert updated_user is not None
    assert updated_user.id == user.id
    assert updated_user.last_login is not None
    
    # Verify the timestamp is within the expected range
    assert before_update <= updated_user.last_login <= after_update
    
    # Test with non-existent user ID
    non_existent_update = parent_user_repo.update_last_login(db_session, 9999)
    assert non_existent_update is None

def test_create_parent_user(db_session, parent_user_repo):
    """Test creating a new parent user."""
    user_data = {
        "email": "newuser@example.com",
        "hashed_password": "newhashed_password",
        "first_name": "New",
        "last_name": "User"
    }
    
    new_user = parent_user_repo.create(db_session, obj_in=user_data)
    
    assert new_user.id is not None
    assert new_user.email == "newuser@example.com"
    assert new_user.hashed_password == "newhashed_password"
    assert new_user.first_name == "New"
    assert new_user.last_name == "User"
    assert new_user.is_active is True
    assert new_user.created_at is not None
    
    # Verify the user can be retrieved
    retrieved_user = parent_user_repo.get_by_email(db_session, "newuser@example.com")
    assert retrieved_user is not None
    assert retrieved_user.id == new_user.id

def test_update_parent_user(db_session, parent_user_repo, sample_users):
    """Test updating a parent user."""
    user = sample_users[0]
    
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    
    updated_user = parent_user_repo.update(db_session, db_obj=user, obj_in=update_data)
    
    assert updated_user.id == user.id
    assert updated_user.first_name == "Updated"
    assert updated_user.last_name == "Name"
    assert updated_user.email == user.email  # Should remain unchanged
    assert updated_user.updated_at is not None
    
    # Verify the update is persisted
    retrieved_user = parent_user_repo.get(db_session, user.id)
    assert retrieved_user.first_name == "Updated"
    assert retrieved_user.last_name == "Name"

def test_deactivate_parent_user(db_session, parent_user_repo, sample_users):
    """Test deactivating a parent user."""
    user = sample_users[0]
    
    # Initially, user should be active
    assert user.is_active is True
    
    # Deactivate the user
    deactivated_user = parent_user_repo.update(db_session, db_obj=user, obj_in={"is_active": False})
    
    assert deactivated_user.id == user.id
    assert deactivated_user.is_active is False
    
    # Verify the deactivation is persisted
    retrieved_user = parent_user_repo.get(db_session, user.id)
    assert retrieved_user.is_active is False