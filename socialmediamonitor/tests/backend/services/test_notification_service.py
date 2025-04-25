import unittest
from unittest.mock import patch, MagicMock, call
import smtplib
import json
from datetime import datetime

from backend.services.notification_service import NotificationService
from backend.models.user import ParentUser, ChildProfile
from backend.models.content import Alert
from backend.models.base import AlertType


class TestNotificationService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        # Create a mock parent user
        self.mock_parent = MagicMock(spec=ParentUser)
        self.mock_parent.id = 101
        self.mock_parent.email = "test@example.com"
        self.mock_parent.device_token = "test-device-token-123"
        
        # Create a mock child profile
        self.mock_child = MagicMock(spec=ChildProfile)
        self.mock_child.id = 201
        self.mock_child.parent_id = 101
        self.mock_child.display_name = "Test Child"
        
        # Create a mock alert
        self.mock_alert = MagicMock(spec=Alert)
        self.mock_alert.id = 1
        self.mock_alert.child_profile_id = 201
        self.mock_alert.alert_type = AlertType.SCAN_COMPLETE
        self.mock_alert.title = "Test Alert"
        self.mock_alert.message = "This is a test alert message"
        self.mock_alert.created_at = datetime(2025, 4, 22, 13, 15, 0)
    
    @patch('backend.services.notification_service.settings')
    @patch('backend.services.notification_service.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, mock_settings):
        """Test sending an email - successful case"""
        # Arrange
        mock_settings.email_enabled = True
        mock_settings.smtp_username = "user"
        mock_settings.smtp_password = "pass"
        mock_settings.smtp_server = "smtp.example.com"
        mock_settings.smtp_port = 587
        mock_settings.email_sender = "sender@example.com"
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Act
        result = NotificationService.send_email(
            recipient_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test Content</p>"
        )
        
        # Assert
        self.assertTrue(result)
        mock_smtp.assert_called_once_with(mock_settings.smtp_server, mock_settings.smtp_port)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(mock_settings.smtp_username, mock_settings.smtp_password)
        mock_server.sendmail.assert_called_once()
        self.assertEqual(mock_server.sendmail.call_args[0][0], mock_settings.email_sender)
        self.assertEqual(mock_server.sendmail.call_args[0][1], "recipient@example.com")
    
    @patch('backend.services.notification_service.settings')
    def test_send_email_disabled(self, mock_settings):
        """Test sending an email when email notifications are disabled"""
        # Arrange
        mock_settings.email_enabled = False
        
        # Act
        result = NotificationService.send_email(
            recipient_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test Content</p>"
        )
        
        # Assert
        self.assertFalse(result)
    
    @patch('backend.services.notification_service.settings')
    def test_send_email_no_credentials(self, mock_settings):
        """Test sending an email when SMTP credentials are not configured"""
        # Arrange
        mock_settings.email_enabled = True
        mock_settings.smtp_username = None
        mock_settings.smtp_password = None
        
        # Act
        result = NotificationService.send_email(
            recipient_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test Content</p>"
        )
        
        # Assert
        self.assertFalse(result)
    
    @patch('backend.services.notification_service.settings')
    @patch('backend.services.notification_service.smtplib.SMTP')
    def test_send_email_exception(self, mock_smtp, mock_settings):
        """Test sending an email with an exception"""
        # Arrange
        mock_settings.email_enabled = True
        mock_settings.smtp_username = "user"
        mock_settings.smtp_password = "pass"
        mock_settings.smtp_server = "smtp.example.com"
        mock_settings.smtp_port = 587
        
        mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException("SMTP Error")
        
        # Act
        result = NotificationService.send_email(
            recipient_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test Content</p>"
        )
        
        # Assert
        self.assertFalse(result)
    
    @patch('backend.services.notification_service.settings')
    @patch('backend.services.notification_service.requests.post')
    def test_send_push_notification_success(self, mock_post, mock_settings):
        """Test sending a push notification - successful case"""
        # Arrange
        mock_settings.push_enabled = True
        mock_settings.fcm_api_key = "test-fcm-api-key"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Act
        result = NotificationService.send_push_notification(
            device_token="test-device-token",
            title="Test Title",
            body="Test Body",
            data={"key": "value"}
        )
        
        # Assert
        self.assertTrue(result)
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        
        # Check headers
        self.assertEqual(call_args["headers"]["Authorization"], "key=test-fcm-api-key")
        
        # Check JSON payload
        data = json.loads(call_args["data"])
        self.assertEqual(data["to"], "test-device-token")
        self.assertEqual(data["notification"]["title"], "Test Title")
        self.assertEqual(data["notification"]["body"], "Test Body")
        self.assertEqual(data["data"]["key"], "value")
    
    @patch('backend.services.notification_service.settings')
    def test_send_push_notification_disabled(self, mock_settings):
        """Test sending a push notification when push notifications are disabled"""
        # Arrange
        mock_settings.push_enabled = False
        
        # Act
        result = NotificationService.send_push_notification(
            device_token="test-device-token",
            title="Test Title",
            body="Test Body"
        )
        
        # Assert
        self.assertFalse(result)
    
    @patch('backend.services.notification_service.settings')
    def test_send_push_notification_no_api_key(self, mock_settings):
        """Test sending a push notification when FCM API key is not configured"""
        # Arrange
        mock_settings.push_enabled = True
        mock_settings.fcm_api_key = None
        
        # Act
        result = NotificationService.send_push_notification(
            device_token="test-device-token",
            title="Test Title",
            body="Test Body"
        )
        
        # Assert
        self.assertFalse(result)
    
    @patch('backend.services.notification_service.settings')
    @patch('backend.services.notification_service.requests.post')
    def test_send_push_notification_server_error(self, mock_post, mock_settings):
        """Test sending a push notification with a server error response"""
        # Arrange
        mock_settings.push_enabled = True
        mock_settings.fcm_api_key = "test-fcm-api-key"
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        mock_post.return_value = mock_response
        
        # Act
        result = NotificationService.send_push_notification(
            device_token="test-device-token",
            title="Test Title",
            body="Test Body"
        )
        
        # Assert
        self.assertFalse(result)
    
    @patch('backend.services.notification_service.settings')
    @patch('backend.services.notification_service.requests.post')
    def test_send_push_notification_exception(self, mock_post, mock_settings):
        """Test sending a push notification with an exception"""
        # Arrange
        mock_settings.push_enabled = True
        mock_settings.fcm_api_key = "test-fcm-api-key"
        
        mock_post.side_effect = Exception("Connection Error")
        
        # Act
        result = NotificationService.send_push_notification(
            device_token="test-device-token",
            title="Test Title",
            body="Test Body"
        )
        
        # Assert
        self.assertFalse(result)
    
    @patch('backend.services.notification_service.settings')
    @patch.object(NotificationService, 'send_email')
    @patch.object(NotificationService, 'send_push_notification')
    def test_send_alert_notification_scan_complete(self, mock_send_push, mock_send_email, mock_settings):
        """Test sending an alert notification for a scan complete alert"""
        # Arrange
        mock_settings.frontend_url = "https://example.com"
        mock_send_email.return_value = True
        mock_send_push.return_value = True
        
        # Act
        result = NotificationService.send_alert_notification(
            parent=self.mock_parent,
            alert=self.mock_alert,
            child_profile=self.mock_child
        )
        
        # Assert
        self.assertEqual(result, {"email": True, "push": True})
        
        # Verify email call
        mock_send_email.assert_called_once()
        email_args = mock_send_email.call_args[1]
        self.assertEqual(email_args["recipient_email"], "test@example.com")
        self.assertIn("Scan Complete for Test Child", email_args["subject"])
        self.assertIn(self.mock_alert.title, email_args["html_content"])
        self.assertIn(self.mock_alert.message, email_args["html_content"])
        
        # Verify push notification call
        mock_send_push.assert_called_once()
        push_args = mock_send_push.call_args[1]
        self.assertEqual(push_args["device_token"], "test-device-token-123")
        self.assertEqual(push_args["title"], "YouTube Channel Scan Complete")
        self.assertEqual(push_args["body"], self.mock_alert.message)
        self.assertEqual(push_args["data"]["alert_id"], self.mock_alert.id)
        self.assertEqual(push_args["data"]["child_profile_id"], self.mock_child.id)
    
    @patch('backend.services.notification_service.settings')
    @patch.object(NotificationService, 'send_email')
    @patch.object(NotificationService, 'send_push_notification')
    def test_send_alert_notification_new_flags(self, mock_send_push, mock_send_email, mock_settings):
        """Test sending an alert notification for a new flags alert"""
        # Arrange
        mock_settings.frontend_url = "https://example.com"
        mock_send_email.return_value = True
        mock_send_push.return_value = True
        
        # Create a new flags alert
        new_flags_alert = MagicMock(spec=Alert)
        new_flags_alert.id = 2
        new_flags_alert.child_profile_id = 201
        new_flags_alert.alert_type = AlertType.NEW_FLAGS
        new_flags_alert.title = "New Flags Alert"
        new_flags_alert.message = "We found new content flags"
        new_flags_alert.created_at = datetime(2025, 4, 22, 14, 0, 0)
        
        # Act
        result = NotificationService.send_alert_notification(
            parent=self.mock_parent,
            alert=new_flags_alert,
            child_profile=self.mock_child
        )
        
        # Assert
        self.assertEqual(result, {"email": True, "push": True})
        
        # Verify email call
        mock_send_email.assert_called_once()
        email_args = mock_send_email.call_args[1]
        self.assertIn("Content Flags Detected for Test Child", email_args["subject"])
        
        # Verify push notification call
        mock_send_push.assert_called_once()
        push_args = mock_send_push.call_args[1]
        self.assertEqual(push_args["title"], "⚠️ New Content Flags Detected")
    
    @patch('backend.services.notification_service.settings')
    @patch.object(NotificationService, 'send_email')
    @patch.object(NotificationService, 'send_push_notification')
    def test_send_alert_notification_other_alert_type(self, mock_send_push, mock_send_email, mock_settings):
        """Test sending an alert notification for other alert types"""
        # Arrange
        mock_settings.frontend_url = "https://example.com"
        mock_send_email.return_value = True
        mock_send_push.return_value = True
        
        # Create a different type of alert
        other_alert = MagicMock(spec=Alert)
        other_alert.id = 3
        other_alert.child_profile_id = 201
        other_alert.alert_type = AlertType.HIGH_RISK
        other_alert.title = "High Risk Alert"
        other_alert.message = "We found high risk content"
        other_alert.created_at = datetime(2025, 4, 22, 15, 0, 0)
        
        # Act
        result = NotificationService.send_alert_notification(
            parent=self.mock_parent,
            alert=other_alert,
            child_profile=self.mock_child
        )
        
        # Assert
        self.assertEqual(result, {"email": True, "push": True})
        
        # Verify email call
        mock_send_email.assert_called_once()
        email_args = mock_send_email.call_args[1]
        self.assertIn("New Alert for Test Child", email_args["subject"])
        
        # Verify push notification call
        mock_send_push.assert_called_once()
        push_args = mock_send_push.call_args[1]
        self.assertEqual(push_args["title"], "New Alert")
    
    @patch('backend.services.notification_service.settings')
    @patch.object(NotificationService, 'send_email')
    @patch.object(NotificationService, 'send_push_notification')
    def test_send_alert_notification_no_email(self, mock_send_push, mock_send_email, mock_settings):
        """Test sending an alert notification when parent has no email"""
        # Arrange
        mock_settings.frontend_url = "https://example.com"
        mock_send_push.return_value = True
        
        # Parent with no email
        parent_no_email = MagicMock(spec=ParentUser)
        parent_no_email.id = 102
        parent_no_email.email = None
        parent_no_email.device_token = "test-device-token-123"
        
        # Act
        result = NotificationService.send_alert_notification(
            parent=parent_no_email,
            alert=self.mock_alert,
            child_profile=self.mock_child
        )
        
        # Assert
        self.assertEqual(result, {"email": False, "push": True})
        mock_send_email.assert_not_called()
        mock_send_push.assert_called_once()
    
    @patch('backend.services.notification_service.settings')
    @patch.object(NotificationService, 'send_email')
    @patch.object(NotificationService, 'send_push_notification')
    def test_send_alert_notification_no_device_token(self, mock_send_push, mock_send_email, mock_settings):
        """Test sending an alert notification when parent has no device token"""
        # Arrange
        mock_settings.frontend_url = "https://example.com"
        mock_send_email.return_value = True
        
        # Parent with no device token
        parent_no_token = MagicMock(spec=ParentUser)
        parent_no_token.id = 103
        parent_no_token.email = "test@example.com"
        parent_no_token.device_token = None
        
        # Act
        result = NotificationService.send_alert_notification(
            parent=parent_no_token,
            alert=self.mock_alert,
            child_profile=self.mock_child
        )
        
        # Assert
        self.assertEqual(result, {"email": True, "push": False})
        mock_send_email.assert_called_once()
        mock_send_push.assert_not_called()


if __name__ == '__main__':
    unittest.main()