import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.user import ParentUser

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
    session.close()

def test_create_parent_user(db_session):
    """
    Test creating a new ParentUser instance and saving it to the database.
    """
    new_user = ParentUser(
        email="test@example.com",
        hashed_password="fakehashedpassword",
        first_name="Test",
        last_name="User"
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    assert new_user.id is not None
    assert new_user.email == "test@example.com"
    assert new_user.hashed_password == "fakehashedpassword"
    assert new_user.first_name == "Test"
    assert new_user.last_name == "User"
    assert new_user.is_active is True
    assert new_user.created_at is not None
    # updated_at should be None initially
    assert new_user.updated_at is None

    # Verify the user can be retrieved from the database
    retrieved_user = db_session.query(ParentUser).filter(ParentUser.email == "test@example.com").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"