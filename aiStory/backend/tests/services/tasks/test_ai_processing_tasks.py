"""Tests for the AI processing Celery tasks."""
import unittest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.services.tasks.ai_processing_tasks import (
    _process_photo_async,
    process_photo,
    enqueue_pending_photos
)
from backend.models.photo import AIProcessingStatus
from backend.services.ai_processing import AIProcessingError


class TestAIProcessingTasks(unittest.TestCase):
    """Test the AI Processing Celery tasks."""
    
    @patch("backend.services.tasks.ai_processing_tasks.PhotoRepository")
    @patch("backend.services.tasks.ai_processing_tasks.get_storage_service")
    @patch("backend.services.tasks.ai_processing_tasks.AIService")
    @patch("backend.services.tasks.ai_processing_tasks.get_async_session_factory")
    @patch("asyncio.run")
    def test_process_photo_task(
        self, mock_asyncio_run, mock_session_factory, 
        mock_ai_service, mock_get_storage, mock_photo_repo
    ):
        """Test the process_photo Celery task."""
        # Setup mocks
        mock_asyncio_run.side_effect = lambda x: x  # Just return the coroutine
        
        # Mock task object for retry
        mock_task = MagicMock()
        mock_task.request.retries = 0
        
        # Setup AIService mock
        ai_service_instance = mock_ai_service.return_value
        ai_service_instance.process_photo.return_value = {
            "provider": "local_dummy",
            "objects_detected": []
        }
        
        # Call the task
        process_photo(mock_task, 1, "local/bucket/key.jpg")
        
        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()
    
    @patch("backend.services.tasks.ai_processing_tasks.PhotoRepository")
    @patch("backend.services.tasks.ai_processing_tasks.get_storage_service")
    @patch("backend.services.tasks.ai_processing_tasks.AIService")
    @patch("backend.services.tasks.ai_processing_tasks.get_async_session_factory")
    async def test_process_photo_async_success(
        self, mock_session_factory, mock_ai_service, 
        mock_get_storage, mock_photo_repo
    ):
        """Test successful async photo processing."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        # Setup photo repo mock
        photo_repo_instance = mock_photo_repo.return_value
        photo_repo_instance.update_ai_status = AsyncMock()
        photo_repo_instance.update_ai_results = AsyncMock()
        
        # Setup AIService mock
        ai_service_instance = mock_ai_service.return_value
        ai_service_instance.process_photo.return_value = {
            "provider": "local_dummy",
            "objects_detected": []
        }
        
        # Call the async function
        result = await _process_photo_async(1, "local/bucket/key.jpg")
        
        # Verify results
        self.assertEqual(result["provider"], "local_dummy")
        
        # Verify repository calls
        photo_repo_instance.update_ai_status.assert_called_with(
            mock_session, 1, AIProcessingStatus.PROCESSING
        )
        photo_repo_instance.update_ai_results.assert_called_with(
            mock_session, 1, result, ai_provider_used=result.get('provider')
        )
    
    @patch("backend.services.tasks.ai_processing_tasks.PhotoRepository")
    @patch("backend.services.tasks.ai_processing_tasks.get_storage_service")
    @patch("backend.services.tasks.ai_processing_tasks.AIService")
    @patch("backend.services.tasks.ai_processing_tasks.get_async_session_factory")
    async def test_process_photo_async_error(
        self, mock_session_factory, mock_ai_service, 
        mock_get_storage, mock_photo_repo
    ):
        """Test error handling in async photo processing."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        
        # Setup photo repo mock
        photo_repo_instance = mock_photo_repo.return_value
        photo_repo_instance.update_ai_status = AsyncMock()
        photo_repo_instance.update_ai_error = AsyncMock()
        
        # Setup AIService mock to raise an error
        ai_service_instance = mock_ai_service.return_value
        ai_service_instance.process_photo.side_effect = AIProcessingError(
            "Test error", "local_dummy"
        )
        
        # Call the async function - should raise an exception
        with self.assertRaises(AIProcessingError):
            await _process_photo_async(1, "local/bucket/key.jpg")
        
        # Verify repository calls
        photo_repo_instance.update_ai_status.assert_called_with(
            mock_session, 1, AIProcessingStatus.PROCESSING
        )
        photo_repo_instance.update_ai_error.assert_called_with(
            mock_session, 1, "Test error", ai_provider_used="local_dummy"
        )
    
    @patch("backend.services.tasks.ai_processing_tasks.PhotoRepository")
    @patch("backend.services.tasks.ai_processing_tasks.get_async_session_factory")
    @patch("backend.services.tasks.ai_processing_tasks.process_photo")
    @patch("asyncio.run")
    def test_enqueue_pending_photos(
        self, mock_asyncio_run, mock_process_task, 
        mock_session_factory, mock_photo_repo
    ):
        """Test the enqueue_pending_photos task."""
        # Set up the AsyncMock to return a specific value
        async_mock = AsyncMock(return_value=3)
        mock_asyncio_run.side_effect = lambda x: async_mock()
        
        # Call the task
        result = enqueue_pending_photos(limit=5)
        
        # Verify results
        self.assertEqual(result, 3)
        mock_asyncio_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()