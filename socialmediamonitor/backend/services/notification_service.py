import smtplib
import logging
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.config import settings
from backend.models.content import Alert
from backend.models.user import ParentUser, ChildProfile
from backend.models.base import AlertType

# Configure logging
logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for sending notifications to users through various channels.
    Currently supports email and Firebase Cloud Messaging (FCM) for push notifications.
    """
    
    @staticmethod
    def send_email(
        recipient_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email notification.
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content of the email (optional)
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        if not settings.email_enabled:
            logger.info("Email notifications are disabled. Would have sent email to %s", recipient_email)
            return False
            
        if not settings.smtp_username or not settings.smtp_password:
            logger.error("SMTP credentials not configured")
            return False
            
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.email_sender
            message["To"] = recipient_email
            
            # Add plain text version if provided, otherwise create from HTML
            if text_content is None:
                # Simple conversion from HTML to text (not perfect but works for basic emails)
                text_content = html_content.replace("<p>", "").replace("</p>", "\n\n")
                text_content = text_content.replace("<br>", "\n").replace("<br/>", "\n")
                text_content = text_content.replace("&nbsp;", " ")
                
            # Attach parts
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Connect to SMTP server
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(settings.smtp_username, settings.smtp_password)
                server.sendmail(settings.email_sender, recipient_email, message.as_string())
                
            logger.info("Email sent successfully to %s", recipient_email)
            return True
            
        except Exception as e:
            logger.error("Failed to send email to %s: %s", recipient_email, str(e))
            return False
    
    @staticmethod
    def send_push_notification(
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a push notification using Firebase Cloud Messaging.
        
        Args:
            device_token: FCM device token of the recipient
            title: Notification title
            body: Notification body
            data: Additional data to send with the notification (optional)
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise
        """
        if not settings.push_enabled:
            logger.info("Push notifications are disabled. Would have sent push to device %s", device_token)
            return False
            
        if not settings.fcm_api_key:
            logger.error("FCM API key not configured")
            return False
            
        try:
            # Prepare FCM message
            fcm_message = {
                "to": device_token,
                "notification": {
                    "title": title,
                    "body": body,
                    "sound": "default"
                }
            }
            
            # Add data payload if provided
            if data:
                fcm_message["data"] = data
                
            # Send to FCM
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"key={settings.fcm_api_key}"
            }
            
            response = requests.post(
                "https://fcm.googleapis.com/fcm/send",
                headers=headers,
                data=json.dumps(fcm_message)
            )
            
            if response.status_code == 200:
                logger.info("Push notification sent successfully to device %s", device_token)
                return True
            else:
                logger.error(
                    "Failed to send push notification to device %s: %s", 
                    device_token, 
                    response.text
                )
                return False
                
        except Exception as e:
            logger.error("Failed to send push notification to device %s: %s", device_token, str(e))
            return False
    
    @classmethod
    def send_alert_notification(cls, parent: ParentUser, alert: Alert, child_profile: ChildProfile) -> Dict[str, bool]:
        """
        Send a notification for an alert to a parent user.
        
        Args:
            parent: Parent user to notify
            alert: Alert to send notification for
            child_profile: Child profile associated with the alert
            
        Returns:
            Dict with status of each notification channel
        """
        results = {
            "email": False,
            "push": False
        }
        
        # Prepare notification content based on alert type
        if alert.alert_type == AlertType.SCAN_COMPLETE:
            subject = f"GuardianLens: Scan Complete for {child_profile.display_name}"
            title = "YouTube Channel Scan Complete"
        elif alert.alert_type == AlertType.NEW_FLAGS:
            subject = f"GuardianLens: Content Flags Detected for {child_profile.display_name}"
            title = "⚠️ New Content Flags Detected"
        else:
            subject = f"GuardianLens: New Alert for {child_profile.display_name}"
            title = "New Alert"
            
        # Send email notification
        html_content = f"""
        <html>
        <body>
            <h2>{alert.title}</h2>
            <p>{alert.message}</p>
            <p>Child Profile: {child_profile.display_name}</p>
            <p>Date: {alert.created_at.strftime('%Y-%m-%d %H:%M')}</p>
            <p>
                <a href="{settings.frontend_url}/alerts/{alert.id}">
                    View Alert Details
                </a>
            </p>
        </body>
        </html>
        """
        
        if parent.email:
            results["email"] = cls.send_email(
                recipient_email=parent.email,
                subject=subject,
                html_content=html_content
            )
            
        # Send push notification if device token is available
        # In a real implementation, we would store device tokens in the database
        # For now, we'll just log that we would send a push notification
        if hasattr(parent, 'device_token') and parent.device_token:
            results["push"] = cls.send_push_notification(
                device_token=parent.device_token,
                title=title,
                body=alert.message,
                data={
                    "alert_id": alert.id,
                    "alert_type": alert.alert_type.value,
                    "child_profile_id": child_profile.id
                }
            )
            
        return results