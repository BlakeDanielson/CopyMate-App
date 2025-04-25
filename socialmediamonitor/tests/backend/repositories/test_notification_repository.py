import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.repositories.notification import NotificationPreferencesRepository, DeviceTokenRepository
from backend.models.notification import NotificationPreferences, DeviceToken


class TestNotificationPreferencesRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = NotificationPreferencesRepository()
        
        # Create mock notification preferences
        self.mock_preferences = MagicMock(spec=NotificationPreferences)
        self.mock_preferences.id = 1
        self.mock_preferences.parent_id = 101
        self.mock_preferences.email_enabled = True
        self.mock_preferences.push_enabled = True
        self.mock_preferences.scan_complete_notifications = True
        self.mock_preferences.new_flags_notifications = True
        self.mock_preferences.high_risk_notifications = True
        self.mock_preferences.account_change_notifications = True
    
    def test_get_by_parent_id(self):
        """Test getting notification preferences by parent ID"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = self.mock_preferences
        
        # Act
        result = self.repo.get_by_parent_id(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(NotificationPreferences)
        query_mock.filter.assert_called_once()
        self.assertEqual(result, self.mock_preferences)
    
    def test_get_by_parent_id_not_found(self):
        """Test getting notification preferences by parent ID when not found"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = None
        
        # Act
        result = self.repo.get_by_parent_id(self.db, 999)
        
        # Assert
        self.db.query.assert_called_once_with(NotificationPreferences)
        query_mock.filter.assert_called_once()
        self.assertIsNone(result)
    
    @patch.object(NotificationPreferencesRepository, 'get_by_parent_id')
    @patch.object(NotificationPreferencesRepository, 'create')
    def test_create_default_preferences_new(self, mock_create, mock_get_by_parent_id):
        """Test creating default preferences when they don't exist"""
        # Arrange
        mock_get_by_parent_id.return_value = None
        mock_create.return_value = self.mock_preferences
        
        # Act
        result = self.repo.create_default_preferences(self.db, 101)
        
        # Assert
        mock_get_by_parent_id.assert_called_once_with(self.db, 101)
        mock_create.assert_called_once()
        expected_data = {
            "parent_id": 101,
            "email_enabled": True,
            "push_enabled": True,
            "scan_complete_notifications": True,
            "new_flags_notifications": True,
            "high_risk_notifications": True,
            "account_change_notifications": True
        }
        mock_create.assert_called_once_with(self.db, obj_in=expected_data)
        self.assertEqual(result, self.mock_preferences)
    
    @patch.object(NotificationPreferencesRepository, 'get_by_parent_id')
    @patch.object(NotificationPreferencesRepository, 'create')
    def test_create_default_preferences_existing(self, mock_create, mock_get_by_parent_id):
        """Test creating default preferences when they already exist"""
        # Arrange
        mock_get_by_parent_id.return_value = self.mock_preferences
        
        # Act
        result = self.repo.create_default_preferences(self.db, 101)
        
        # Assert
        mock_get_by_parent_id.assert_called_once_with(self.db, 101)
        mock_create.assert_not_called()
        self.assertEqual(result, self.mock_preferences)
    
    @patch.object(NotificationPreferencesRepository, 'get_by_parent_id')
    @patch.object(NotificationPreferencesRepository, 'update')
    def test_update_preferences_existing(self, mock_update, mock_get_by_parent_id):
        """Test updating existing preferences"""
        # Arrange
        mock_get_by_parent_id.return_value = self.mock_preferences
        mock_update.return_value = self.mock_preferences
        preferences_data = {
            "email_enabled": False,
            "high_risk_notifications": False
        }
        
        # Act
        result = self.repo.update_preferences(self.db, 101, preferences_data)
        
        # Assert
        mock_get_by_parent_id.assert_called_once_with(self.db, 101)
        mock_update.assert_called_once_with(
            self.db, db_obj=self.mock_preferences, obj_in=preferences_data
        )
        self.assertEqual(result, self.mock_preferences)
    
    @patch.object(NotificationPreferencesRepository, 'get_by_parent_id')
    @patch.object(NotificationPreferencesRepository, 'create')
    def test_update_preferences_new(self, mock_create, mock_get_by_parent_id):
        """Test updating preferences when they don't exist (should create)"""
        # Arrange
        mock_get_by_parent_id.return_value = None
        mock_create.return_value = self.mock_preferences
        preferences_data = {
            "email_enabled": False,
            "high_risk_notifications": False
        }
        
        # Act
        result = self.repo.update_preferences(self.db, 101, preferences_data)
        
        # Assert
        mock_get_by_parent_id.assert_called_once_with(self.db, 101)
        expected_data = preferences_data.copy()
        expected_data["parent_id"] = 101
        mock_create.assert_called_once_with(self.db, obj_in=expected_data)
        self.assertEqual(result, self.mock_preferences)


class TestDeviceTokenRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = DeviceTokenRepository()
        
        # Create mock device token
        self.mock_token = MagicMock(spec=DeviceToken)
        self.mock_token.id = 1
        self.mock_token.parent_id = 101
        self.mock_token.device_token = "test_token_123"
        self.mock_token.device_type = "ios"
        self.mock_token.device_name = "iPhone 13"
        self.mock_token.last_used_at = datetime.now() - timedelta(days=1)
        
        # Create another mock device token for the same parent
        self.mock_token2 = MagicMock(spec=DeviceToken)
        self.mock_token2.id = 2
        self.mock_token2.parent_id = 101
        self.mock_token2.device_token = "test_token_456"
        self.mock_token2.device_type = "android"
        self.mock_token2.device_name = "Pixel 6"
        self.mock_token2.last_used_at = datetime.now() - timedelta(days=2)
    
    def test_get_by_token(self):
        """Test getting a device token by its value"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = self.mock_token
        
        # Act
        result = self.repo.get_by_token(self.db, "test_token_123")
        
        # Assert
        self.db.query.assert_called_once_with(DeviceToken)
        query_mock.filter.assert_called_once()
        self.assertEqual(result, self.mock_token)
    
    def test_get_by_token_not_found(self):
        """Test getting a device token by its value when not found"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = None
        
        # Act
        result = self.repo.get_by_token(self.db, "nonexistent_token")
        
        # Assert
        self.db.query.assert_called_once_with(DeviceToken)
        query_mock.filter.assert_called_once()
        self.assertIsNone(result)
    
    def test_get_by_parent_id(self):
        """Test getting all device tokens for a parent user"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.all.return_value = [self.mock_token, self.mock_token2]
        
        # Act
        result = self.repo.get_by_parent_id(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(DeviceToken)
        query_mock.filter.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertIn(self.mock_token, result)
        self.assertIn(self.mock_token2, result)
    
    @patch.object(DeviceTokenRepository, 'get_by_token')
    @patch.object(DeviceTokenRepository, 'update')
    @patch.object(DeviceTokenRepository, 'create')
    def test_register_device_new(self, mock_create, mock_update, mock_get_by_token):
        """Test registering a new device token"""
        # Arrange
        mock_get_by_token.return_value = None
        mock_create.return_value = self.mock_token
        current_time = datetime.now()
        
        # Act
        with patch('backend.repositories.notification.datetime') as mock_datetime:
            mock_datetime.now.return_value = current_time
            result = self.repo.register_device(
                self.db, 101, "test_token_123", "ios", "iPhone 13"
            )
        
        # Assert
        mock_get_by_token.assert_called_once_with(self.db, "test_token_123")
        mock_create.assert_called_once()
        expected_data = {
            "parent_id": 101,
            "device_token": "test_token_123",
            "device_type": "ios",
            "device_name": "iPhone 13",
            "last_used_at": current_time
        }
        mock_create.assert_called_once_with(self.db, obj_in=expected_data)
        mock_update.assert_not_called()
        self.assertEqual(result, self.mock_token)
    
    @patch.object(DeviceTokenRepository, 'get_by_token')
    @patch.object(DeviceTokenRepository, 'update')
    @patch.object(DeviceTokenRepository, 'create')
    def test_register_device_existing(self, mock_create, mock_update, mock_get_by_token):
        """Test registering an existing device token (updates last_used_at)"""
        # Arrange
        mock_get_by_token.return_value = self.mock_token
        mock_update.return_value = self.mock_token
        current_time = datetime.now()
        
        # Act
        with patch('backend.repositories.notification.datetime') as mock_datetime:
            mock_datetime.now.return_value = current_time
            result = self.repo.register_device(
                self.db, 101, "test_token_123", "ios", "iPhone 13 Pro"
            )
        
        # Assert
        mock_get_by_token.assert_called_once_with(self.db, "test_token_123")
        expected_update = {
            "last_used_at": current_time,
            "device_name": "iPhone 13 Pro"
        }
        mock_update.assert_called_once_with(self.db, db_obj=self.mock_token, obj_in=expected_update)
        mock_create.assert_not_called()
        self.assertEqual(result, self.mock_token)
    
    @patch.object(DeviceTokenRepository, 'get_by_token')
    @patch.object(DeviceTokenRepository, 'delete')
    def test_unregister_device(self, mock_delete, mock_get_by_token):
        """Test unregistering a device token"""
        # Arrange
        mock_get_by_token.return_value = self.mock_token
        
        # Act
        result = self.repo.unregister_device(self.db, "test_token_123")
        
        # Assert
        mock_get_by_token.assert_called_once_with(self.db, "test_token_123")
        mock_delete.assert_called_once_with(self.db, id=self.mock_token.id)
        self.assertTrue(result)
    
    @patch.object(DeviceTokenRepository, 'get_by_token')
    @patch.object(DeviceTokenRepository, 'delete')
    def test_unregister_device_not_found(self, mock_delete, mock_get_by_token):
        """Test unregistering a device token that doesn't exist"""
        # Arrange
        mock_get_by_token.return_value = None
        
        # Act
        result = self.repo.unregister_device(self.db, "nonexistent_token")
        
        # Assert
        mock_get_by_token.assert_called_once_with(self.db, "nonexistent_token")
        mock_delete.assert_not_called()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()