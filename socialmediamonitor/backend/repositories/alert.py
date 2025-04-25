from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from backend.repositories.base import BaseRepository
from backend.models.content import Alert
from backend.models.base import AlertType
from backend.repositories.parent_user import ParentUserRepository
from backend.repositories.child_profile import ChildProfileRepository
from backend.services.notification_service import NotificationService


class AlertRepository(BaseRepository[Alert, dict, dict]):
    """
    Repository for Alert operations.
    """
    def __init__(self):
        super().__init__(Alert)
        self.parent_user_repo = ParentUserRepository()
        self.child_profile_repo = ChildProfileRepository()
        
    def get_alerts_for_child(
        self, 
        db: Session, 
        child_profile_id: int, 
        unread_only: bool = False,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Alert]:
        """
        Get alerts for a specific child profile with optional filtering for unread.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            unread_only: If True, return only unread alerts
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of alerts for the child profile
        """
        query = db.query(Alert).filter(Alert.child_profile_id == child_profile_id)
        
        if unread_only:
            query = query.filter(Alert.is_read == False)
            
        return query.order_by(
            Alert.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_alerts_by_type(
        self, 
        db: Session, 
        child_profile_id: int, 
        alert_type: AlertType,
        unread_only: bool = False,
        limit: int = 10
    ) -> List[Alert]:
        """
        Get alerts of a specific type for a child profile.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            alert_type: Type of alert to filter by
            unread_only: If True, return only unread alerts
            limit: Maximum number of records to return
            
        Returns:
            List of alerts of the specified type for the child profile
        """
        query = db.query(Alert).filter(
            Alert.child_profile_id == child_profile_id,
            Alert.alert_type == alert_type
        )
        
        if unread_only:
            query = query.filter(Alert.is_read == False)
            
        return query.order_by(
            Alert.created_at.desc()
        ).limit(limit).all()
    
    def mark_as_read(self, db: Session, alert_id: int) -> Optional[Alert]:
        """
        Mark an alert as read.
        
        Args:
            db: Database session
            alert_id: ID of the alert
            
        Returns:
            The updated alert or None if not found
        """
        alert = self.get(db, alert_id)
        if not alert:
            return None
            
        return self.update(db, db_obj=alert, obj_in={
            "is_read": True, 
            "read_at": datetime.now()
        })
    
    def mark_all_read(self, db: Session, child_profile_id: int) -> int:
        """
        Mark all alerts for a child profile as read.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            
        Returns:
            Number of alerts marked as read
        """
        try:
            now = datetime.now()
            result = db.query(Alert).filter(
                Alert.child_profile_id == child_profile_id,
                Alert.is_read == False
            ).update({
                "is_read": True,
                "read_at": now
            })
            
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise e
    
    # Alias for backward compatibility
    mark_all_as_read = mark_all_read
    
    def create_scan_complete_alert(
        self,
        db: Session,
        child_profile_id: int,
        channels_count: int,
        flagged_count: int,
        send_notification: bool = True
    ) -> Alert:
        """
        Create a scan complete alert.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            channels_count: Total number of channels scanned
            flagged_count: Number of channels flagged
            send_notification: Whether to send a notification for this alert
            
        Returns:
            The created alert
        """
        alert_data = {
            "child_profile_id": child_profile_id,
            "alert_type": AlertType.SCAN_COMPLETE,
            "title": "YouTube Channel Scan Complete",
            "message": f"We've scanned {channels_count} channels and found {flagged_count} with potential concerns.",
            "summary_data": {
                "channels_scanned": channels_count,
                "channels_flagged": flagged_count,
                "scan_date": datetime.now().isoformat()
            }
        }
        
        # Create the alert
        alert = self.create(db, obj_in=alert_data)
        
        # Send notification if requested
        if send_notification:
            self._send_notification_for_alert(db, alert)
            
        return alert
    
    def create_new_flags_alert(
        self,
        db: Session,
        child_profile_id: int,
        new_flags_count: int,
        categories: List[str],
        send_notification: bool = True
    ) -> Alert:
        """
        Create an alert for newly flagged content.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            new_flags_count: Number of new flags found
            categories: List of risk categories found
            send_notification: Whether to send a notification for this alert
            
        Returns:
            The created alert
        """
        category_text = ", ".join(categories) if categories else "various categories"
        
        alert_data = {
            "child_profile_id": child_profile_id,
            "alert_type": AlertType.NEW_FLAGS,
            "title": "New Content Flags Detected",
            "message": f"We've found {new_flags_count} new flags in {category_text}.",
            "summary_data": {
                "new_flags_count": new_flags_count,
                "categories": categories,
                "alert_date": datetime.now().isoformat()
            }
        }
        
        # Create the alert
        alert = self.create(db, obj_in=alert_data)
        
        # Send notification if requested
        if send_notification:
            self._send_notification_for_alert(db, alert)
            
        return alert
        
    def _send_notification_for_alert(self, db: Session, alert: Alert) -> Dict[str, bool]:
        """
        Send a notification for an alert.
        
        Args:
            db: Database session
            alert: Alert to send notification for
            
        Returns:
            Dictionary with notification status for each channel
        """
        try:
            # Get the child profile
            child_profile = self.child_profile_repo.get(db, alert.child_profile_id)
            if not child_profile:
                return {"error": "Child profile not found"}
                
            # Get the parent user
            parent = self.parent_user_repo.get(db, child_profile.parent_id)
            if not parent:
                return {"error": "Parent user not found"}
                
            # Send notification
            notification_results = NotificationService.send_alert_notification(
                parent=parent,
                alert=alert,
                child_profile=child_profile
            )
            
            return notification_results
            
        except Exception as e:
            # Log the error but don't fail the alert creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send notification for alert {alert.id}: {str(e)}")
            
            return {"error": str(e)}