"""Fixtures for testing the core utility functions."""
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_db():
    """Returns a mock database session for testing."""
    return AsyncMock()