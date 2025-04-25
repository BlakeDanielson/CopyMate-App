import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from sqlalchemy.orm import Session

from backend.repositories.analyzed_video import AnalyzedVideoRepository
from backend.models.content import AnalyzedVideo


class TestAnalyzedVideoRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = AnalyzedVideoRepository()
        
        # Create mock analyzed video
        self.mock_video = MagicMock(spec=AnalyzedVideo)
        self.mock_video.id = 1
        self.mock_video.channel_id = 101
        self.mock_video.video_platform_id = "video123"
        self.mock_video.title = "Test Video"
        self.mock_video.description = "Test video description"
        self.mock_video.thumbnail_url = "https://example.com/thumb.jpg"
        self.mock_video.published_at = datetime.now()
        self.mock_video.duration = "PT10M30S"
        self.mock_video.view_count = 1000
        self.mock_video.like_count = 100
        self.mock_video.fetched_at = datetime.now()
        self.mock_video.updated_at = datetime.now()
        
        # Create another mock video for the same channel
        self.mock_video2 = MagicMock(spec=AnalyzedVideo)
        self.mock_video2.id = 2
        self.mock_video2.channel_id = 101
        self.mock_video2.video_platform_id = "video456"
        self.mock_video2.title = "Test Video 2"
    
    def test_get_by_platform_id(self):
        """Test getting a video by its platform-specific ID"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = self.mock_video
        
        # Act
        result = self.repo.get_by_platform_id(self.db, "video123")
        
        # Assert
        self.db.query.assert_called_once_with(AnalyzedVideo)
        query_mock.filter.assert_called_once()
        self.assertEqual(result, self.mock_video)
    
    def test_get_by_platform_id_not_found(self):
        """Test getting a video by its platform-specific ID when not found"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = None
        
        # Act
        result = self.repo.get_by_platform_id(self.db, "nonexistent")
        
        # Assert
        self.db.query.assert_called_once_with(AnalyzedVideo)
        query_mock.filter.assert_called_once()
        self.assertIsNone(result)
    
    def test_get_videos_for_channel_with_default_sort(self):
        """Test getting videos for a channel with default sorting"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_video, self.mock_video2]
        
        # Act
        result = self.repo.get_videos_for_channel(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(AnalyzedVideo)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertIn(self.mock_video, result)
        self.assertIn(self.mock_video2, result)
    
    def test_get_videos_for_channel_with_custom_sort(self):
        """Test getting videos for a channel with custom sorting"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_video]
        
        # Act
        result = self.repo.get_videos_for_channel(
            self.db, 101, sort_by="view_count", sort_desc=False
        )
        
        # Assert
        self.db.query.assert_called_once_with(AnalyzedVideo)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_video)
    
    def test_get_videos_for_channel_with_invalid_sort(self):
        """Test getting videos for a channel with invalid sort field"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_video]
        
        # Act
        result = self.repo.get_videos_for_channel(
            self.db, 101, sort_by="invalid_field"
        )
        
        # Assert
        self.db.query.assert_called_once_with(AnalyzedVideo)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_video)
    
    def test_get_videos_with_analysis(self):
        """Test getting videos with analysis results eager loaded"""
        # Arrange
        query_mock = self.db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.limit.return_value
        limit_mock.all.return_value = [self.mock_video]
        
        # Act
        with patch('backend.repositories.analyzed_video.joinedload') as mock_joinedload:
            result = self.repo.get_videos_with_analysis(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(AnalyzedVideo)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.order_by.assert_called_once()
        order_mock.limit.assert_called_once_with(10)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_video)
    
    @patch.object(AnalyzedVideoRepository, 'get')
    @patch.object(AnalyzedVideoRepository, 'update')
    def test_update_video_metadata_existing(self, mock_update, mock_get):
        """Test updating metadata for an existing video"""
        # Arrange
        mock_get.return_value = self.mock_video
        mock_update.return_value = self.mock_video
        metadata = {
            "view_count": 2000,
            "like_count": 200
        }
        
        # Act
        with patch('backend.repositories.analyzed_video.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 4, 22)
            result = self.repo.update_video_metadata(self.db, 1, metadata)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 1)
        # Check that updated_at was added to metadata
        self.assertIn("updated_at", mock_update.call_args[1]['obj_in'])
        self.assertEqual(result, self.mock_video)
    
    @patch.object(AnalyzedVideoRepository, 'get')
    @patch.object(AnalyzedVideoRepository, 'update')
    def test_update_video_metadata_nonexistent(self, mock_update, mock_get):
        """Test updating metadata for a nonexistent video"""
        # Arrange
        mock_get.return_value = None
        metadata = {
            "view_count": 2000,
            "like_count": 200
        }
        
        # Act
        result = self.repo.update_video_metadata(self.db, 999, metadata)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 999)
        mock_update.assert_not_called()
        self.assertIsNone(result)
    
    def test_bulk_create_success(self):
        """Test bulk creation of videos - successful case"""
        # Arrange
        videos_data = [
            {
                "channel_id": 101,
                "video_platform_id": "video123",
                "title": "Test Video 1"
            },
            {
                "channel_id": 101,
                "video_platform_id": "video456",
                "title": "Test Video 2"
            }
        ]
        
        # Act
        results = self.repo.bulk_create(self.db, videos_data)
        
        # Assert
        self.assertEqual(len(results), 2)
        self.db.add.call_count = 2
        self.db.commit.assert_called_once()
        self.db.refresh.call_count = 2
    
    def test_bulk_create_exception(self):
        """Test bulk creation of videos with an exception"""
        # Arrange
        videos_data = [
            {
                "channel_id": 101,
                "video_platform_id": "video123",
                "title": "Test Video 1"
            }
        ]
        self.db.add.side_effect = Exception("Database error")
        
        # Act/Assert
        with self.assertRaises(Exception):
            self.repo.bulk_create(self.db, videos_data)
        
        self.db.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()