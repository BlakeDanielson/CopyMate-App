"""Tests for the example Celery tasks."""
import pytest
from app.tasks.example import add


class TestExampleTasks:
    """Test suite for example Celery tasks."""

    def test_add_task_direct_call(self):
        """Test the add task by calling the function directly."""
        # Given two numbers
        x, y = 2, 3
        expected_sum = 5

        # When calling the add function
        result = add(x, y)

        # Then the result should be the sum of the two numbers
        assert result == expected_sum

    def test_add_task_with_different_values(self):
        """Test the add task with different input values."""
        # Test cases with various inputs
        test_cases = [
            (0, 0, 0),    # both zero
            (1, -1, 0),   # positive and negative
            (-5, -7, -12), # both negative
            (100, 200, 300) # larger numbers
        ]

        # Verify all test cases
        for x, y, expected in test_cases:
            result = add(x, y)
            assert result == expected, f"add({x}, {y}) should return {expected}, got {result}"


@pytest.fixture
def configure_celery_for_testing(monkeypatch):
    """Configure Celery for testing by setting task_always_eager to True."""
    # This fixture can be used when we want to actually execute the task through Celery
    # but have it run synchronously for testing
    monkeypatch.setenv("CELERY_TASK_ALWAYS_EAGER", "True")
    monkeypatch.setenv("CELERY_TASK_EAGER_PROPAGATES", "True")
    
    # We could also patch the celery app directly if environment variables don't work
    # from app.celery_app import celery_app
    # celery_app.conf.task_always_eager = True
    # celery_app.conf.task_eager_propagates = True


def test_add_task_through_celery(configure_celery_for_testing):
    """Test the add task by executing it through Celery (with task_always_eager=True)."""
    # This test shows how to use the fixture above to test through Celery
    # Note: This test isn't strictly necessary since we're testing the function directly,
    # but it demonstrates how to set up Celery for testing if needed in the future
    from app.tasks.example import add

    # Given a task to add two numbers
    task_result = add.delay(3, 4)
    
    # When getting the result
    result = task_result.get()
    
    # Then it should return their sum
    assert result == 7