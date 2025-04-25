"""Tests for the child profile API endpoints."""
import pytest
from datetime import date
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.profile import ProfileCreate
from app.crud.crud_profile import create_profile, get_profiles_by_parent, get_profile


@pytest.fixture
async def test_profile(test_db: AsyncSession, test_user: dict) -> dict:
    """Create a test profile for the test user."""
    profile_data = {
        "name": "Test Child",
        "date_of_birth": date(2018, 1, 15),
        "avatar_url": "https://example.com/avatar.jpg"
    }
    profile_in = ProfileCreate(**profile_data)
    profile = await create_profile(test_db, obj_in=profile_in, parent_id=test_user["id"])
    
    return {
        "id": profile.id,
        "name": profile.name,
        "date_of_birth": profile.date_of_birth,
        "avatar_url": profile.avatar_url,
        "parent_id": profile.parent_id,
    }


@pytest.fixture
async def second_test_user(test_db: AsyncSession) -> dict:
    """Create a second test user for ownership tests."""
    from app.crud.crud_user import create_user
    from app.schemas.user import UserCreate
    
    user_data = {
        "email": "seconduser@example.com",
        "password": "testpassword123",
        "full_name": "Second Test User"
    }
    user_in = UserCreate(**user_data)
    user = await create_user(test_db, obj_in=user_in)
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "password": user_data["password"],
    }


@pytest.fixture
def second_token_headers(second_test_user) -> dict:
    """Create token headers for the second test user."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(subject=second_test_user["email"])
    return {"Authorization": f"Bearer {access_token}"}


# ----- TEST PROFILE CREATION -----

@pytest.mark.asyncio
async def test_create_profile_success(client: AsyncClient, token_headers: dict, test_db: AsyncSession, test_user: dict):
    """Test successful profile creation with valid data."""
    # Arrange
    profile_data = {
        "name": "New Child",
        "date_of_birth": "2020-03-10",
        "avatar_url": "https://example.com/new-avatar.jpg"
    }
    
    # Act
    response = await client.post(
        "/api/v1/profiles/",
        json=profile_data,
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == profile_data["name"]
    assert data["date_of_birth"] == profile_data["date_of_birth"]
    assert data["avatar_url"] == profile_data["avatar_url"]
    assert data["parent_id"] == test_user["id"]
    
    # Verify profile exists in DB
    profiles = await get_profiles_by_parent(test_db, parent_id=test_user["id"])
    assert any(profile.name == profile_data["name"] for profile in profiles)


@pytest.mark.asyncio
async def test_create_profile_invalid_data(client: AsyncClient, token_headers: dict):
    """Test profile creation failure with invalid data (missing required field)."""
    # Arrange
    invalid_profile_data = {
        # Missing required "name" field
        "date_of_birth": "2020-03-10",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    # Act
    response = await client.post(
        "/api/v1/profiles/",
        json=invalid_profile_data,
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_profile_unauthenticated(client: AsyncClient):
    """Test profile creation failure by an unauthenticated user."""
    # Arrange
    profile_data = {
        "name": "Unauthorized Child",
        "date_of_birth": "2020-03-10",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    # Act
    response = await client.post(
        "/api/v1/profiles/",
        json=profile_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ----- TEST PROFILE READING -----

@pytest.mark.asyncio
async def test_read_profiles_success(client: AsyncClient, token_headers: dict, test_profile: dict):
    """Test retrieving profiles for an authenticated parent who has profiles."""
    # Act
    response = await client.get(
        "/api/v1/profiles/",
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Verify our test profile is in the returned data
    profile_ids = [profile["id"] for profile in data]
    assert test_profile["id"] in profile_ids


@pytest.mark.asyncio
async def test_read_profiles_empty(client: AsyncClient, second_token_headers: dict):
    """Test retrieving profiles for an authenticated parent with no profiles."""
    # Act
    response = await client.get(
        "/api/v1/profiles/",
        headers=second_token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_read_profiles_unauthenticated(client: AsyncClient):
    """Test retrieving profiles by an unauthenticated user."""
    # Act
    response = await client.get("/api/v1/profiles/")
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_read_profiles_pagination(client: AsyncClient, token_headers: dict, test_db: AsyncSession, test_user: dict):
    """Test pagination for retrieving profiles."""
    # Arrange - Create multiple profiles
    for i in range(3):
        profile_in = ProfileCreate(name=f"Paged Child {i}")
        await create_profile(test_db, obj_in=profile_in, parent_id=test_user["id"])
    
    # Act - Get first page with limit 2
    response = await client.get(
        "/api/v1/profiles/?skip=0&limit=2",
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Act - Get second page with limit 2
    response = await client.get(
        "/api/v1/profiles/?skip=2&limit=2",
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Should have at least one more profile


# ----- TEST PROFILE UPDATE -----

@pytest.mark.asyncio
async def test_update_profile_success(client: AsyncClient, token_headers: dict, test_profile: dict):
    """Test successful update of an owned profile."""
    # Arrange
    update_data = {
        "name": "Updated Child Name",
        "avatar_url": "https://example.com/updated-avatar.jpg"
    }
    
    # Act
    response = await client.put(
        f"/api/v1/profiles/{test_profile['id']}",
        json=update_data,
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["avatar_url"] == update_data["avatar_url"]
    # Fields not in update_data should remain unchanged
    assert data["date_of_birth"] == test_profile["date_of_birth"].isoformat()
    assert data["parent_id"] == test_profile["parent_id"]


@pytest.mark.asyncio
async def test_update_profile_not_owned(
    client: AsyncClient, second_token_headers: dict, test_profile: dict
):
    """Test update failure when trying to update a profile not owned by the parent."""
    # Arrange
    update_data = {
        "name": "Not My Child",
    }
    
    # Act
    response = await client.put(
        f"/api/v1/profiles/{test_profile['id']}",
        json=update_data,
        headers=second_token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_profile_invalid_id(client: AsyncClient, token_headers: dict):
    """Test update failure with an invalid profile_id."""
    # Arrange
    update_data = {
        "name": "Invalid Profile",
    }
    invalid_id = 9999  # ID that doesn't exist
    
    # Act
    response = await client.put(
        f"/api/v1/profiles/{invalid_id}",
        json=update_data,
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_profile_unauthenticated(client: AsyncClient, test_profile: dict):
    """Test update failure by an unauthenticated user."""
    # Arrange
    update_data = {
        "name": "Unauthorized Update",
    }
    
    # Act
    response = await client.put(
        f"/api/v1/profiles/{test_profile['id']}",
        json=update_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ----- TEST PROFILE DELETION -----

@pytest.mark.asyncio
async def test_delete_profile_success(client: AsyncClient, token_headers: dict, test_db: AsyncSession, test_user: dict):
    """Test successful deletion of an owned profile."""
    # Arrange - Create a profile to delete
    profile_in = ProfileCreate(name="Profile To Delete")
    profile = await create_profile(test_db, obj_in=profile_in, parent_id=test_user["id"])
    
    # Act
    response = await client.delete(
        f"/api/v1/profiles/{profile.id}",
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    
    # Verify profile is removed from DB
    deleted_profile = await get_profile(test_db, profile_id=profile.id, parent_id=test_user["id"])
    assert deleted_profile is None


@pytest.mark.asyncio
async def test_delete_profile_not_owned(
    client: AsyncClient, second_token_headers: dict, test_profile: dict
):
    """Test deletion failure when trying to delete a profile not owned by the parent."""
    # Act
    response = await client.delete(
        f"/api/v1/profiles/{test_profile['id']}",
        headers=second_token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_profile_invalid_id(client: AsyncClient, token_headers: dict):
    """Test deletion failure with an invalid profile_id."""
    # Arrange
    invalid_id = 9999  # ID that doesn't exist
    
    # Act
    response = await client.delete(
        f"/api/v1/profiles/{invalid_id}",
        headers=token_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_profile_unauthenticated(client: AsyncClient, test_profile: dict):
    """Test deletion failure by an unauthenticated user."""
    # Act
    response = await client.delete(
        f"/api/v1/profiles/{test_profile['id']}"
    )
    
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED