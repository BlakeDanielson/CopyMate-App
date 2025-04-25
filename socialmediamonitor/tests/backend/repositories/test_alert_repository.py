import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from sqlalchemy.orm import Session

from backend.repositories.alert import AlertRepository
from backend.models.content import Alert
from backend.models.base import AlertType
from backend.services.notification_service import NotificationService


class TestAlertRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = AlertRepository()
        
        # Create mock alert
        self.mock_alert = MagicMock(spec=Alert)
        self.mock_alert.id = 1
        self.mock_alert.child_profile_id = 101
        self.mock_alert.alert_type = AlertType.SCAN_COMPLETE
        self.mock_alert.title = "Test Alert"
        self.mock_alert.message = "This is a test alert"
        self.mock_alert.summary_data = {"test": "data"}
        self.mock_alert.is_read = False
        self.mock_alert.read_at = None
        self.mock_alert.created_at = datetime.now()
    
    def test_get_alerts_for_child(self):
        """Test getting alerts for a child profile"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_alert]
        
        # Act
        result = self.repo.get_alerts_for_child(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(Alert)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_alert)
    
    def test_get_alerts_for_child_unread_only(self):
        """Test getting only unread alerts for a child profile"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_unread_mock = filter_mock.filter.return_value
        order_mock = filter_unread_mock.order_by.return_value
        limit_mock = order_mock.offset.return_value.limit.return_value
        limit_mock.all.return_value = [self.mock_alert]
        
        # Act
        result = self.repo.get_alerts_for_child(self.db, 101, unread_only=True)
        
        # Assert
        self.db.query.assert_called_once_with(Alert)
        query_mock.filter.assert_called_once()
        filter_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_alert)
    
    def test_get_alerts_by_type(self):
        """Test getting alerts by type for a child profile"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        limit_mock = order_mock.limit.return_value
        limit_mock.all.return_value = [self.mock_alert]
        
        # Act
        result = self.repo.get_alerts_by_type(
            self.db, 101, AlertType.SCAN_COMPLETE
        )
        
        # Assert
        self.db.query.assert_called_once_with(Alert)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_alert)
    
    def test_get_alerts_by_type_unread_only(self):
        """Test getting only unread alerts by type for a child profile"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_unread_mock = filter_mock.filter.return_value
        order_mock = filter_unread_mock.order_by.return_value
        limit_mock = order_mock.limit.return_value
        limit_mock.all.return_value = [self.mock_alert]
        
        # Act
        result = self.repo.get_alerts_by_type(
            self.db, 101, AlertType.SCAN_COMPLETE, unread_only=True
        )
        
        # Assert
        self.db.query.assert_called_once_with(Alert)
        query_mock.filter.assert_called_once()
        filter_mock.filter.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_alert)
    
    @patch.object(AlertRepository, 'get')
    @patch.object(AlertRepository, 'update')
    def test_mark_as_read_existing(self, mock_update, mock_get):
        """Test marking an existing alert as read"""
        # Arrange
        mock_get.return_value = self.mock_alert
        mock_update.return_value = self.mock_alert
        
        # Act
        result = self.repo.mark_as_read(self.db, 1)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 1)
        mock_update.assert_called_once()
        self.assertEqual(result, self.mock_alert)
    
    @patch.object(AlertRepository, 'get')
    @patch.object(AlertRepository, 'update')
    def test_mark_as_read_nonexistent(self, mock_update, mock_get):
        """Test marking a nonexistent alert as read"""
        # Arrange
        mock_get.return_value = None
        
        # Act
        result = self.repo.mark_as_read(self.db, 999)
        
        # Assert
        mock_get.assert_called_once_with(self.db, 999)
        mock_update.assert_not_called()
        self.assertIsNone(result)
    
    def test_mark_all_read(self):
        """Test marking all alerts for a child profile as read"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.update.return_value = 3  # 3 alerts updated
        
        # Act
        result = self.repo.mark_all_read(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(Alert)
        query_mock.filter.assert_called_once()
        self.db.commit.assert_called_once()
        self.assertEqual(result, 3)
    
    def test_mark_all_read_exception(self):
        """Test marking all alerts as read with an exception"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.update.side_effect = Exception("Database error")
        
        # Act/Assert
        with self.assertRaises(Exception):
            self.repo.mark_all_read(self.db, 101)
        
        self.db.rollback.assert_called_once()
    
    def test_mark_all_as_read_alias(self):
        """Test the mark_all_as_read alias method"""
        # Arrange
        with patch.object(AlertRepository, 'mark_all_read') as mock_mark_all_read:
            mock_mark_all_read.return_value = 3
            
            # Act
            result = self.repo.mark_all_as_read(self.db, 101)
            
            # Assert
            mock_mark_all_read.assert_called_once_with(self.db, 101)
            self.assertEqual(result, 3)
    
    @patch.object(AlertRepository, 'create')
    @patch.object(AlertRepository, '_send_notification_for_alert')
    def test_create_scan_complete_alert_with_notification(self, mock_send_notification, mock_create):
        """Test creating a scan complete alert with notification"""
        # Arrange
        mock_create.return_value = self.mock_alert
        mock_send_notification.return_value = {"email": True, "push": True}
        
        # Act
        result = self.repo.create_scan_complete_alert(
            self.db, 101, 5, 2, send_notification=True
        )
        
        # Assert
        mock_create.assert_called_once()
        self.assertEqual(mock_create.call_args[1]['obj_in']['child_profile_id'], 101)
        self.assertEqual(mock_create.call_args[1]['obj_in']['alert_type'], AlertType.SCAN_COMPLETE)
        self.assertIn("5 channels", mock_create.call_args[1]['obj_in']['message'])
        self.assertIn("2 with potential concerns", mock_create.call_args[1]['obj_in']['message'])
        mock_send_notification.assert_called_once_with(self.db, self.mock_alert)
        self.assertEqual(result, self.mock_alert)
    
    @patch.object(AlertRepository, 'create')
    @patch.object(AlertRepository, '_send_notification_for_alert')
    def test_create_scan_complete_alert_without_notification(self, mock_send_notification, mock_create):
        """Test creating a scan complete alert without notification"""
        # Arrange
        mock_create.return_value = self.mock_alert
        
        # Act
        result = self.repo.create_scan_complete_alert(
            self.db, 101, 5, 2, send_notification=False
        )
        
        # Assert
        mock_create.assert_called_once()
        mock_send_notification.assert_not_called()
        self.assertEqual(result, self.mock_alert)
    
    @patch.object(AlertRepository, 'create')
    @patch.object(AlertRepository, '_send_notification_for_alert')
    def test_create_new_flags_alert_with_notification(self, mock_send_notification, mock_create):
        """Test creating a new flags alert with notification"""
        # Arrange
        mock_create.return_value = self.mock_alert
        mock_send_notification.return_value = {"email": True, "push": True}
        categories = ["hate_speech", "explicit_content"]
        
        # Act
        result = self.repo.create_new_flags_alert(
            self.db, 101, 3, categories, send_notification=True
        )
        
        # Assert
        mock_create.assert_called_once()
        self.assertEqual(mock_create.call_args[1]['obj_in']['child_profile_id'], 101)
        self.assertEqual(mock_create.call_args[1]['obj_in']['alert_type'], AlertType.NEW_FLAGS)
        self.assertIn("3 new flags", mock_create.call_args[1]['obj_in']['message'])
        self.assertIn("hate_speech, explicit_content", mock_create.call_args[1]['obj_in']['message'])
        mock_send_notification.assert_called_once_with(self.db, self.mock_alert)
        self.assertEqual(result, self.mock_alert)
    
    @patch.object(AlertRepository, 'create')
    @patch.object(AlertRepository, '_send_notification_for_alert')
    def test_create_new_flags_alert_without_notification(self, mock_send_notification, mock_create):
        """Test creating a new flags alert without notification"""
        # Arrange
        mock_create.return_value = self.mock_alert
        categories = ["hate_speech", "explicit_content"]
        
        # Act
        result = self.repo.create_new_flags_alert(
            self.db, 101, 3, categories, send_notification=False
        )
        
        # Assert
        mock_create.assert_called_once()
        mock_send_notification.assert_not_called()
        self.assertEqual(result, self.mock_alert)
    
    @patch.object(AlertRepository, 'create')
    @patch.object(AlertRepository, '_send_notification_for_alert')
    def test_create_new_flags_alert_empty_categories(self, mock_send_notification, mock_create):
        """Test creating a new flags alert with empty categories list"""
        # Arrange
        mock_create.return_value = self.mock_alert
        
        # Act
        result = self.repo.create_new_flags_alert(
            self.db, 101, 3, [], send_notification=True
        )
        
        # Assert
        mock_create.assert_called_once()
        self.assertIn("various categories", mock_create.call_args[1]['obj_in']['message'])
        mock_send_notification.assert_called_once_with(self.db, self.mock_alert)
        self.assertEqual(result, self.mock_alert)
    
    @patch('backend.repositories.child_profile.ChildProfileRepository.get')
    @patch('backend.repositories.parent_user.ParentUserRepository.get')
    @patch('backend.services.notification_service.NotificationService.send_alert_notification')
    def test_send_notification_for_alert_success(self, mock_send_notification, mock_get_parent, mock_get_child):
        """Test sending a notification for an alert - successful case"""
        # Arrange
        mock_get_child.return_value = MagicMock()
        mock_get_parent.return_value = MagicMock()
        mock_send_notification.return_value = {"email": True, "push": True}
        
        # Act
        result = self.repo._send_notification_for_alert(self.db, self.mock_alert)
        
        # Assert
        mock_get_child.assert_called_once_with(self.db, self.mock_alert.child_profile_id)
        mock_get_parent.assert_called_once()
        mock_send_notification.assert_called_once()
        self.assertEqual(result, {"email": True, "push": True})
    
    @patch('backend.repositories.child_profile.ChildProfileRepository.get')
    def test_send_notification_for_alert_child_not_found(self, mock_get_child):
        """Test sending a notification when child profile is not found"""
        # Arrange
        mock_get_child.return_value = None
        
        # Act
        result = self.repo._send_notification_for_alert(self.db, self.mock_alert)
        
        # Assert
        mock_get_child.assert_called_once_with(self.db, self.mock_alert.child_profile_id)
        self.assertEqual(result, {"error": "Child profile not found"})
    
    @patch('backend.repositories.child_profile.ChildProfileRepository.get')
    @patch('backend.repositories.parent_user.ParentUserRepository.get')
    def test_send_notification_for_alert_parent_not_found(self, mock_get_parent, mock_get_child):
        """Test sending a notification when parent user is not found"""
        # Arrange
        mock_child = MagicMock()
        mock_child.parent_id = 201
        mock_get_child.return_value = mock_child
        mock_get_parent.return_value = None
        
        # Act
        result = self.repo._send_notification_for_alert(self.db, self.mock_alert)
        
        # Assert
        mock_get_child.assert_called_once_with(self.db, self.mock_alert.child_profile_id)
        mock_get_parent.assert_called_once_with(self.db, mock_child.parent_id)
        self.assertEqual(result, {"error": "Parent user not found"})
    
    @patch('backend.repositories.child_profile.ChildProfileRepository.get')
    @patch('backend.repositories.parent_user.ParentUserRepository.get')
    @patch('backend.services.notification_service.NotificationService.send_alert_notification')
    def test_send_notification_for_alert_exception(self, mock_send_notification, mock_get_parent, mock_get_child):
        """Test handling exceptions when sending a notification"""
        # Arrange
        mock_get_child.return_value = MagicMock()
        mock_get_parent.return_value = MagicMock()
        mock_send_notification.side_effect = Exception("Notification error")
        
        # Act
        with patch('logging.getLogger') as mock_logger:
            mock_logger.return_value = MagicMock()
            result = self.repo._send_notification_for_alert(self.db, self.mock_alert)
        
        # Assert
        mock_logger.return_value.error.assert_called_once()
        self.assertEqual(result, {"error": "Notification error"})


if __name__ == '__main__':
    unittest.main()