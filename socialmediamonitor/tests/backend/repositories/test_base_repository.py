import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

from backend.database import Base
from backend.repositories.base import BaseRepository

# Define a simple model for testing
class TestModel(Base):
    __tablename__ = "test_model"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Define Pydantic schemas for the test model
class TestModelCreate(BaseModel):
    name: str
    description: str

class TestModelUpdate(BaseModel):
    name: str = None
    description: str = None

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

@pytest.fixture
def test_repo():
    return BaseRepository(TestModel)

def test_create(db_session, test_repo):
    """Test creating a new record."""
    obj_in = TestModelCreate(name="Test Item", description="Test Description")
    db_obj = test_repo.create(db_session, obj_in=obj_in)
    
    assert db_obj.id is not None
    assert db_obj.name == "Test Item"
    assert db_obj.description == "Test Description"

def test_get(db_session, test_repo):
    """Test retrieving a record by ID."""
    # Create a test record
    obj_in = TestModelCreate(name="Get Test", description="Get Description")
    created_obj = test_repo.create(db_session, obj_in=obj_in)
    
    # Retrieve the record
    db_obj = test_repo.get(db_session, created_obj.id)
    
    assert db_obj is not None
    assert db_obj.id == created_obj.id
    assert db_obj.name == "Get Test"
    assert db_obj.description == "Get Description"

def test_get_by(db_session, test_repo):
    """Test retrieving a record by arbitrary filters."""
    # Create a test record
    obj_in = TestModelCreate(name="Filter Test", description="Filter Description")
    test_repo.create(db_session, obj_in=obj_in)
    
    # Retrieve by name
    db_obj = test_repo.get_by(db_session, name="Filter Test")
    
    assert db_obj is not None
    assert db_obj.name == "Filter Test"
    assert db_obj.description == "Filter Description"
    
    # Test with non-existent filter
    db_obj = test_repo.get_by(db_session, name="Non-existent")
    assert db_obj is None

def test_list(db_session, test_repo):
    """Test listing records with pagination and filtering."""
    # Create multiple test records
    for i in range(5):
        obj_in = TestModelCreate(name=f"List Test {i}", description=f"List Description {i}")
        test_repo.create(db_session, obj_in=obj_in)
    
    # List all records
    all_records = test_repo.list(db_session)
    assert len(all_records) >= 5
    
    # Test pagination
    paginated_records = test_repo.list(db_session, skip=1, limit=2)
    assert len(paginated_records) == 2
    
    # Test filtering
    filtered_records = test_repo.list(db_session, name="List Test 1")
    assert len(filtered_records) == 1
    assert filtered_records[0].name == "List Test 1"

def test_update(db_session, test_repo):
    """Test updating a record."""
    # Create a test record
    obj_in = TestModelCreate(name="Update Test", description="Update Description")
    db_obj = test_repo.create(db_session, obj_in=obj_in)
    
    # Update the record
    update_data = TestModelUpdate(name="Updated Name", description="Updated Description")
    updated_obj = test_repo.update(db_session, db_obj=db_obj, obj_in=update_data)
    
    assert updated_obj.id == db_obj.id
    assert updated_obj.name == "Updated Name"
    assert updated_obj.description == "Updated Description"
    
    # Test partial update
    partial_update = TestModelUpdate(name="Partially Updated")
    partially_updated_obj = test_repo.update(db_session, db_obj=updated_obj, obj_in=partial_update)
    
    assert partially_updated_obj.name == "Partially Updated"
    assert partially_updated_obj.description == "Updated Description"  # Should remain unchanged

def test_delete(db_session, test_repo):
    """Test deleting a record."""
    # Create a test record
    obj_in = TestModelCreate(name="Delete Test", description="Delete Description")
    db_obj = test_repo.create(db_session, obj_in=obj_in)
    
    # Delete the record
    deleted_obj = test_repo.delete(db_session, id=db_obj.id)
    
    assert deleted_obj is not None
    assert deleted_obj.id == db_obj.id
    
    # Verify it's deleted
    retrieved_obj = test_repo.get(db_session, db_obj.id)
    assert retrieved_obj is None
    
    # Test deleting non-existent record
    non_existent_delete = test_repo.delete(db_session, id=9999)
    assert non_existent_delete is None

def test_count(db_session, test_repo):
    """Test counting records."""
    # Create multiple test records
    for i in range(3):
        obj_in = TestModelCreate(name=f"Count Test", description=f"Count Description {i}")
        test_repo.create(db_session, obj_in=obj_in)
    
    # Count all records
    count = test_repo.count(db_session)
    assert count >= 3
    
    # Count with filter
    filtered_count = test_repo.count(db_session, name="Count Test")
    assert filtered_count >= 3
    
    # Count with non-matching filter
    zero_count = test_repo.count(db_session, name="Non-existent")
    assert zero_count == 0