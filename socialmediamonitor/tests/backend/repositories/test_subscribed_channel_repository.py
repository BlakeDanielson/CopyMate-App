import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.repositories.subscribed_channel import SubscribedChannelRepository
from backend.models.content import SubscribedChannel


class TestSubscribedChannelRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = SubscribedChannelRepository()
        
        # Create mock subscribed channel
        self.mock_channel = MagicMock(spec=SubscribedChannel)
        self.mock_channel.id = 1
        self.mock_channel.linked_account_id = 101
        self.mock_channel.channel_id = "channel123"
        self.mock_channel.title = "Test Channel"
        self.mock_channel.description = "This is a test channel"
        self.mock_channel.thumbnail_url = "https://example.com/thumb.jpg"
        self.mock_channel.subscriber_count = 10000
        self.mock_channel.video_count = 100
        self.mock_channel.topic_details = {"topics": ["Education", "Technology"]}
        self.mock_channel.last_fetched_at = datetime.now() - timedelta(hours=12)
        self.mock_channel.created_at = datetime.now() - timedelta(days=30)
        self.mock_channel.updated_at = datetime.now() - timedelta(days=1)
        
        # Create another mock channel for the same account
        self.mock_channel2 = MagicMock(spec=SubscribedChannel)
        self.mock_channel2.id = 2
        self.mock_channel2.linked_account_id = 101
        self.mock_channel2.channel_id = "channel456"
        self.mock_channel2.title = "Another Channel"
        self.mock_channel2.subscriber_count = 5000
        self.mock_channel2.video_count = 50
        self.mock_channel2.last_fetched_at = datetime.now() - timedelta(hours=36)
    
    def test_get_by_channel_id(self):
        """Test getting a channel by its platform-specific ID"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = self.mock_channel
        
        # Act
        result = self.repo.get_by_channel_id(self.db, 101, "channel123")
        
        # Assert
        self.db.query.assert_called_once_with(SubscribedChannel)
        query_mock.filter.assert_called_once()
        filter_mock.first.assert_called_once()
        self.assertEqual(result, self.mock_channel)
    
    def test_get_by_channel_id_not_found(self):
        """Test getting a channel by its platform-specific ID when not found"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = None
        
        # Act
        result = self.repo.get_by_channel_id(self.db, 101, "nonexistent")
        
        # Assert
        self.db.query.assert_called_once_with(SubscribedChannel)
        query_mock.filter.assert_called_once()
        filter_mock.first.assert_called_once()
        self.assertIsNone(result)
    
    def test_get_channels_for_account_with_default_sort(self):
        """Test getting channels for an account with default sorting"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_channel, self.mock_channel2]
        
        # Act
        result = self.repo.get_channels_for_account(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(SubscribedChannel)
        query_mock.filter.assert_called_once()
        filter_mock.order_by.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertIn(self.mock_channel, result)
        self.assertIn(self.mock_channel2, result)
    
    def test_get_channels_for_account_with_custom_sort(self):
        """Test getting channels for an account with custom sorting"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_channel]
        
        # Act
        result = self.repo.get_channels_for_account(
            self.db, 101, sort_by="subscriber_count", sort_desc=True
        )
        
        # Assert
        self.db.query.assert_called_once_with(SubscribedChannel)
        query_mock.filter.assert_called_once()
        filter_mock.order_by.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_channel)
    
    def test_get_channels_for_account_with_invalid_sort(self):
        """Test getting channels for an account with invalid sort field"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_channel]
        
        # Act
        result = self.repo.get_channels_for_account(
            self.db, 101, sort_by="invalid_field"
        )
        
        # Assert
        self.db.query.assert_called_once_with(SubscribedChannel)
        query_mock.filter.assert_called_once()
        filter_mock.order_by.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_channel)
    
    def test_get_channels_needing_update(self):
        """Test getting channels that need to be updated"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.limit.return_value
        limit_mock.all.return_value = [self.mock_channel2]  # older than 24 hours
        
        # Act
        with patch('backend.repositories.subscribed_channel.datetime') as mock_datetime:
            mock_now = datetime.now()
            mock_datetime.now.return_value = mock_now
            result = self.repo.get_channels_needing_update(self.db)
        
        # Assert
        self.db.query.assert_called_once_with(SubscribedChannel)
        query_mock.filter.assert_called_once()
        filter_mock.order_by.assert_called_once()
        order_mock.limit.assert_called_once_with(100)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_channel2)
    
    def test_get_channels_needing_update_custom_threshold(self):
        """Test getting channels with custom update threshold"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.limit.return_value
        limit_mock.all.return_value = [self.mock_channel, self.mock_channel2]  # Both older than 6 hours
        
        # Act
        with patch('backend.repositories.subscribed_channel.datetime') as mock_datetime:
            mock_now = datetime.now()
            mock_datetime.now.return_value = mock_now
            result = self.repo.get_channels_needing_update(self.db, hours_threshold=6, limit=50)
        
        # Assert
        self.db.query.assert_called_once_with(SubscribedChannel)
        query_mock.filter.assert_called_once()
        filter_mock.order_by.assert_called_once()
        order_mock.limit.assert_called_once_with(50)
        self.assertEqual(len(result), 2)
        self.assertIn(self.mock_channel, result)
        self.assertIn(self.mock_channel2, result)
    
    @patch.object(SubscribedChannelRepository, 'get')
    @patch.object(SubscribedChannelRepository, 'update')
    def test_update_channel_metadata_existing(self, mock_update, mock_get):
        """Test updating metadata for an existing channel"""
        # Arrange
        mock_get.return_value = self.mock_channel
        mock_update.return_value = self.mock_channel
        
        metadata = {
            "subscriber_count": 15000,
            "video_count": 120
        }
        
        # Act
        with patch('backend.repositories.subscribed_channel.datetime') as mock_datetime:
            mock_now = datetime.now()
            mock_datetime.now.return_value = mock_now
            result = self.repo.update_channel_metadata(self.db, 1, metadata)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 1)
        
        # Verify last_fetched_at was added to metadata
        updated_metadata = metadata.copy()
        updated_metadata["last_fetched_at"] = mock_now
        
        mock_update.assert_called_once_with(
            self.db, db_obj=self.mock_channel, obj_in=updated_metadata
        )
        self.assertEqual(result, self.mock_channel)
    
    @patch.object(SubscribedChannelRepository, 'get')
    @patch.object(SubscribedChannelRepository, 'update')
    def test_update_channel_metadata_nonexistent(self, mock_update, mock_get):
        """Test updating metadata for a nonexistent channel"""
        # Arrange
        mock_get.return_value = None
        
        metadata = {
            "subscriber_count": 15000,
            "video_count": 120
        }
        
        # Act
        result = self.repo.update_channel_metadata(self.db, 999, metadata)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 999)
        mock_update.assert_not_called()
        self.assertIsNone(result)
    
    def test_get_channels_with_videos(self):
        """Test getting channels with videos eager loaded"""
        # Arrange
        query_mock = self.db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_channel]
        
        # Act
        with patch('backend.repositories.subscribed_channel.joinedload') as mock_joinedload:
            result = self.repo.get_channels_with_videos(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(SubscribedChannel)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.order_by.assert_called_once()
        order_mock.offset.assert_called_once_with(0)
        limit_mock.all.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_channel)


if __name__ == '__main__':
    unittest.main()