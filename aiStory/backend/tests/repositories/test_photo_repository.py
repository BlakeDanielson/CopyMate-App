"""Tests for PhotoRepository."""
import uuid
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.photo import Photo, PhotoStatus
from backend.models.user import User
from backend.repositories.photo_repository import PhotoRepository
from backend.repositories.base import ItemNotFoundError, DatabaseError


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db: AsyncSession):
    """Create a test user for photos."""
    # Create a test user
    user = User(
        email="phototest@example.com",
        username="phototester",
        hashed_password="fakehash",  # Not testing auth here
        is_active=True
    )
    test_db.add(user)
    await test_db.flush()
    
    yield user
    
    # Clean up - delete the user and related photos (cascade)
    await test_db.delete(user)
    await test_db.commit()


@pytest_asyncio.fixture(scope="function")
async def photo_repository():
    """Create a PhotoRepository instance for testing."""
    return PhotoRepository()


@pytest_asyncio.fixture(scope="function")
async def test_photos(test_db: AsyncSession, test_user: User):
    """Create test photos for testing."""
    photos = []
    
    # Create test photos with different statuses
    for i, status in enumerate([
        PhotoStatus.PENDING,
        PhotoStatus.UPLOADED,
        PhotoStatus.PROCESSING,
        PhotoStatus.COMPLETED,
        PhotoStatus.FAILED
    ]):
        photo = Photo(
            user_id=test_user.id,
            storage_provider="test-provider",
            bucket_name="test-bucket",
            storage_key=f"test-key-{i}",
            original_filename=f"test-file-{i}.jpg",
            content_type="image/jpeg",
            status=status.value
        )
        test_db.add(photo)
    
    await test_db.flush()
    
    # Get all created photos
    query = select(Photo).where(Photo.user_id == test_user.id)
    result = await test_db.execute(query)
    photos = list(result.scalars().all())
    
    yield photos
    
    # Cleanup happens automatically through User cascade delete


class TestPhotoRepository:
    """Tests for PhotoRepository."""
    
    @pytest.mark.asyncio
    async def test_create(self, test_db, photo_repository, test_user):
        """Test creating a photo."""
        # Prepare data
        photo_data = {
            "user_id": test_user.id,
            "storage_provider": "test-provider",
            "bucket_name": "test-bucket",
            "storage_key": "test-create-key",
            "original_filename": "test-create.jpg",
            "content_type": "image/jpeg"
        }
        
        # Create photo
        photo = await photo_repository.create(test_db, photo_data)
        
        # Verify
        assert photo is not None
        assert photo.id is not None
        assert photo.uuid is not None
        assert photo.user_id == test_user.id
        assert photo.storage_provider == "test-provider"
        assert photo.bucket_name == "test-bucket"
        assert photo.storage_key == "test-create-key"
        assert photo.original_filename == "test-create.jpg"
        assert photo.content_type == "image/jpeg"
        assert photo.status == PhotoStatus.PENDING.value
    
    @pytest.mark.asyncio
    async def test_get(self, test_db, photo_repository, test_photos):
        """Test getting a photo by ID."""
        # Get a photo
        photo = await photo_repository.get(test_db, test_photos[0].id)
        
        # Verify
        assert photo is not None
        assert photo.id == test_photos[0].id
        assert photo.uuid == test_photos[0].uuid
    
    @pytest.mark.asyncio
    async def test_get_nonexistent(self, test_db, photo_repository):
        """Test getting a non-existent photo."""
        # Get a non-existent photo
        photo = await photo_repository.get(test_db, 9999)
        
        # Verify
        assert photo is None
    
    @pytest.mark.asyncio
    async def test_get_by_field(self, test_db, photo_repository, test_photos):
        """Test getting a photo by field."""
        # Get a photo by storage_key
        photo = await photo_repository.get_by_field(
            test_db, "storage_key", test_photos[0].storage_key
        )
        
        # Verify
        assert photo is not None
        assert photo.id == test_photos[0].id
        assert photo.storage_key == test_photos[0].storage_key
    
    @pytest.mark.asyncio
    async def test_get_by_uuid(self, test_db, photo_repository, test_photos):
        """Test getting a photo by UUID."""
        # Get a photo by UUID
        photo = await photo_repository.get_by_uuid(test_db, test_photos[0].uuid)
        
        # Verify
        assert photo is not None
        assert photo.id == test_photos[0].id
        assert photo.uuid == test_photos[0].uuid
    
    @pytest.mark.asyncio
    async def test_list(self, test_db, photo_repository, test_photos):
        """Test listing photos."""
        # List photos
        photos = await photo_repository.list(test_db)
        
        # Verify
        assert len(photos) == len(test_photos)
    
    @pytest.mark.asyncio
    async def test_list_with_pagination(self, test_db, photo_repository, test_photos):
        """Test listing photos with pagination."""
        # List photos with pagination
        photos = await photo_repository.list(test_db, skip=1, limit=2)
        
        # Verify
        assert len(photos) == 2
    
    @pytest.mark.asyncio
    async def test_list_by_user_id(self, test_db, photo_repository, test_photos, test_user):
        """Test listing photos by user ID."""
        # List photos by user ID
        photos = await photo_repository.list_by_user_id(test_db, test_user.id)
        
        # Verify
        assert len(photos) == len(test_photos)
        assert all(photo.user_id == test_user.id for photo in photos)
    
    @pytest.mark.asyncio
    async def test_list_by_status(self, test_db, photo_repository, test_photos):
        """Test listing photos by status."""
        # List photos by status
        photos = await photo_repository.list_by_status(test_db, PhotoStatus.PENDING)
        
        # Verify
        assert len(photos) == 1
        assert all(photo.status == PhotoStatus.PENDING.value for photo in photos)
    
    @pytest.mark.asyncio
    async def test_update(self, test_db, photo_repository, test_photos):
        """Test updating a photo."""
        # Update data
        update_data = {
            "storage_key": "updated-key",
            "original_filename": "updated.jpg"
        }
        
        # Update photo
        photo = await photo_repository.update(test_db, test_photos[0].id, update_data)
        
        # Verify
        assert photo is not None
        assert photo.id == test_photos[0].id
        assert photo.storage_key == "updated-key"
        assert photo.original_filename == "updated.jpg"
    
    @pytest.mark.asyncio
    async def test_update_nonexistent(self, test_db, photo_repository):
        """Test updating a non-existent photo."""
        # Update data
        update_data = {
            "storage_key": "updated-key",
            "original_filename": "updated.jpg"
        }
        
        # Update non-existent photo
        with pytest.raises(ItemNotFoundError):
            await photo_repository.update(test_db, 9999, update_data)
    
    @pytest.mark.asyncio
    async def test_update_status(self, test_db, photo_repository, test_photos):
        """Test updating a photo status."""
        # Update status
        photo = await photo_repository.update_status(
            test_db, test_photos[0].id, PhotoStatus.COMPLETED
        )
        
        # Verify
        assert photo is not None
        assert photo.id == test_photos[0].id
        assert photo.status == PhotoStatus.COMPLETED.value
    
    @pytest.mark.asyncio
    async def test_update_status_by_uuid(self, test_db, photo_repository, test_photos):
        """Test updating a photo status by UUID."""
        # Update status by UUID
        photo = await photo_repository.update_status_by_uuid(
            test_db, test_photos[0].uuid, PhotoStatus.COMPLETED
        )
        
        # Verify
        assert photo is not None
        assert photo.id == test_photos[0].id
        assert photo.uuid == test_photos[0].uuid
        assert photo.status == PhotoStatus.COMPLETED.value
    
    @pytest.mark.asyncio
    async def test_delete(self, test_db, photo_repository, test_photos):
        """Test deleting a photo."""
        # Delete photo
        await photo_repository.delete(test_db, test_photos[0].id)
        
        # Verify
        photo = await photo_repository.get(test_db, test_photos[0].id)
        assert photo is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, test_db, photo_repository):
        """Test deleting a non-existent photo."""
        # Delete non-existent photo
        with pytest.raises(ItemNotFoundError):
            await photo_repository.delete(test_db, 9999)
    
    @pytest.mark.asyncio
    async def test_count(self, test_db, photo_repository, test_photos):
        """Test counting photos."""
        # Count photos
        count = await photo_repository.count(test_db)
        
        # Verify
        assert count == len(test_photos)
    
    @pytest.mark.asyncio
    async def test_count_by_user_id(self, test_db, photo_repository, test_photos, test_user):
        """Test counting photos by user ID."""
        # Count photos by user ID
        count = await photo_repository.count_by_user_id(test_db, test_user.id)
        
        # Verify
        assert count == len(test_photos)
    
    @pytest.mark.asyncio
    async def test_count_by_status(self, test_db, photo_repository, test_photos):
        """Test counting photos by status."""
        # Count photos by status
        count = await photo_repository.count_by_status(test_db, PhotoStatus.PENDING)
        
        # Verify
        assert count == 1