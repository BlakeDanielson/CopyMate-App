from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from backend.repositories.base import BaseRepository
from backend.models.notification import NotificationPreferences, DeviceToken
from backend.models.user import ParentUser

class NotificationPreferencesRepository(BaseRepository[NotificationPreferences, dict, dict]):
    """
    Repository for NotificationPreferences operations.
    """
    def __init__(self):
        super().__init__(NotificationPreferences)
    
    def get_by_parent_id(self, db: Session, parent_id: int) -> Optional[NotificationPreferences]:
        """
        Get notification preferences for a parent user.
        
        Args:
            db: Database session
            parent_id: ID of the parent user
            
        Returns:
            NotificationPreferences object or None if not found
        """
        return db.query(NotificationPreferences).filter(
            NotificationPreferences.parent_id == parent_id
        ).first()
    
    def create_default_preferences(self, db: Session, parent_id: int) -> NotificationPreferences:
        """
        Create default notification preferences for a parent user.
        
        Args:
            db: Database session
            parent_id: ID of the parent user
            
        Returns:
            Created NotificationPreferences object
        """
        # Check if preferences already exist
        existing = self.get_by_parent_id(db, parent_id)
        if existing:
            return existing
            
        # Create default preferences
        preferences_data = {
            "parent_id": parent_id,
            "email_enabled": True,
            "push_enabled": True,
            "scan_complete_notifications": True,
            "new_flags_notifications": True,
            "high_risk_notifications": True,
            "account_change_notifications": True
        }
        
        return self.create(db, obj_in=preferences_data)
    
    def update_preferences(
        self, 
        db: Session, 
        parent_id: int, 
        preferences_data: dict
    ) -> Optional[NotificationPreferences]:
        """
        Update notification preferences for a parent user.
        
        Args:
            db: Database session
            parent_id: ID of the parent user
            preferences_data: Dictionary with preference fields to update
            
        Returns:
            Updated NotificationPreferences object or None if not found
        """
        preferences = self.get_by_parent_id(db, parent_id)
        if not preferences:
            # Create preferences if they don't exist
            preferences_data["parent_id"] = parent_id
            return self.create(db, obj_in=preferences_data)
            
        # Update existing preferences
        return self.update(db, db_obj=preferences, obj_in=preferences_data)


class DeviceTokenRepository(BaseRepository[DeviceToken, dict, dict]):
    """
    Repository for DeviceToken operations.
    """
    def __init__(self):
        super().__init__(DeviceToken)
    
    def get_by_token(self, db: Session, device_token: str) -> Optional[DeviceToken]:
        """
        Get a device token by its value.
        
        Args:
            db: Database session
            device_token: Device token value
            
        Returns:
            DeviceToken object or None if not found
        """
        return db.query(DeviceToken).filter(
            DeviceToken.device_token == device_token
        ).first()
    
    def get_by_parent_id(self, db: Session, parent_id: int) -> List[DeviceToken]:
        """
        Get all device tokens for a parent user.
        
        Args:
            db: Database session
            parent_id: ID of the parent user
            
        Returns:
            List of DeviceToken objects
        """
        return db.query(DeviceToken).filter(
            DeviceToken.parent_id == parent_id
        ).all()
    
    def register_device(
        self, 
        db: Session, 
        parent_id: int, 
        device_token: str,
        device_type: str,
        device_name: Optional[str] = None
    ) -> DeviceToken:
        """
        Register a device token for a parent user.
        If the token already exists, update its last_used_at timestamp.
        
        Args:
            db: Database session
            parent_id: ID of the parent user
            device_token: Device token value
            device_type: Type of device (ios, android, web)
            device_name: Name of the device (optional)
            
        Returns:
            Created or updated DeviceToken object
        """
        # Check if token already exists
        existing = self.get_by_token(db, device_token)
        if existing:
            # Update last_used_at timestamp
            return self.update(db, db_obj=existing, obj_in={
                "last_used_at": datetime.now(),
                "device_name": device_name or existing.device_name
            })
            
        # Create new token
        token_data = {
            "parent_id": parent_id,
            "device_token": device_token,
            "device_type": device_type,
            "device_name": device_name,
            "last_used_at": datetime.now()
        }
        
        return self.create(db, obj_in=token_data)
    
    def unregister_device(self, db: Session, device_token: str) -> bool:
        """
        Unregister a device token.
        
        Args:
            db: Database session
            device_token: Device token value
            
        Returns:
            True if the token was deleted, False otherwise
        """
        existing = self.get_by_token(db, device_token)
        if not existing:
            return False
            
        self.delete(db, id=existing.id)
        return True