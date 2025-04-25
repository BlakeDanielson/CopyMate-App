"""
Data service module that encapsulates common operations across repositories.
This service layer helps decouple the API routes from direct repository access.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from backend.models import (
    ParentUser, ChildProfile, LinkedAccount,
    SubscribedChannel, AnalyzedVideo, AnalysisResult, Alert, AuditLog,
    PlatformType, RiskCategory, AlertType, AuditActionType
)
from backend.repositories import (
    ParentUserRepository, ChildProfileRepository, LinkedAccountRepository,
    SubscribedChannelRepository, AnalyzedVideoRepository, AnalysisResultRepository,
    AlertRepository, AuditLogRepository
)


class DataService:
    """Data service for common operations across repositories."""
    
    def __init__(self):
        """Initialize repositories."""
        self.parent_user_repo = ParentUserRepository()
        self.child_profile_repo = ChildProfileRepository()
        self.linked_account_repo = LinkedAccountRepository()
        self.subscribed_channel_repo = SubscribedChannelRepository()
        self.analyzed_video_repo = AnalyzedVideoRepository()
        self.analysis_result_repo = AnalysisResultRepository()
        self.alert_repo = AlertRepository()
        self.audit_log_repo = AuditLogRepository()
    
    # ParentUser operations
    
    def get_parent_by_email(self, db: Session, email: str) -> Optional[ParentUser]:
        """Get a parent user by email."""
        return self.parent_user_repo.get_by_email(db, email)
    
    # ChildProfile operations
    
    def get_child_profiles_for_parent(
        self, db: Session, parent_id: int, active_only: bool = True
    ) -> List[ChildProfile]:
        """Get all child profiles for a parent."""
        return self.child_profile_repo.get_profiles_by_parent(
            db, parent_id, active_only=active_only
        )
    
    def create_child_profile(
        self, db: Session, parent_id: int, display_name: str, age: Optional[int] = None
    ) -> ChildProfile:
        """Create a new child profile."""
        child_data = {
            "parent_id": parent_id,
            "display_name": display_name,
            "age": age
        }
        profile = self.child_profile_repo.create(db, obj_in=child_data)
        
        # Log the action
        self.audit_log_repo.log_action(
            db,
            action=AuditActionType.PROFILE_CREATE,
            parent_id=parent_id,
            resource_type="child_profile",
            resource_id=profile.id,
            details={"display_name": display_name}
        )
        
        return profile
    
    # LinkedAccount operations
    
    def link_youtube_account(
        self, 
        db: Session, 
        child_profile_id: int, 
        platform_account_id: str,
        platform_username: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LinkedAccount:
        """Link a YouTube account to a child profile."""
        account_data = {
            "child_profile_id": child_profile_id,
            "platform": PlatformType.YOUTUBE.value,
            "platform_account_id": platform_account_id,
            "platform_username": platform_username,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiry": token_expiry,
            "metadata": metadata or {},
            "is_active": True
        }
        
        linked_account = self.linked_account_repo.create(db, obj_in=account_data)
        
        # Get child profile to find parent ID
        child_profile = self.child_profile_repo.get(db, child_profile_id)
        
        # Log the action
        self.audit_log_repo.log_action(
            db,
            action=AuditActionType.ACCOUNT_LINK,
            parent_id=child_profile.parent_id if child_profile else None,
            resource_type="linked_account",
            resource_id=linked_account.id,
            details={
                "platform": PlatformType.YOUTUBE.value,
                "username": platform_username
            }
        )
        
        return linked_account
    
    def unlink_account(
        self, db: Session, account_id: int, parent_id: Optional[int] = None
    ) -> Optional[LinkedAccount]:
        """Unlink a social media account."""
        account = self.linked_account_repo.deactivate_account(db, account_id)
        
        if account:
            # Log the action
            self.audit_log_repo.log_action(
                db,
                action=AuditActionType.ACCOUNT_UNLINK,
                parent_id=parent_id,
                resource_type="linked_account",
                resource_id=account.id,
                details={
                    "platform": account.platform,
                    "username": account.platform_username
                }
            )
        
        return account
    
    def get_linked_accounts_for_child(
        self, db: Session, child_profile_id: int, active_only: bool = True
    ) -> List[LinkedAccount]:
        """Get all linked accounts for a child profile."""
        return self.linked_account_repo.get_linked_accounts_for_child(
            db, child_profile_id, active_only=active_only
        )
    
    # SubscribedChannel operations
    
    def get_channels_for_linked_account(
        self, 
        db: Session, 
        linked_account_id: int, 
        sort_by: str = "title", 
        sort_desc: bool = False
    ) -> List[SubscribedChannel]:
        """Get all subscribed channels for a linked account."""
        return self.subscribed_channel_repo.get_channels_for_account(
            db, linked_account_id, sort_by=sort_by, sort_desc=sort_desc
        )
    
    # Alert operations
    
    def get_unread_alerts_for_child(
        self, db: Session, child_profile_id: int, limit: int = 10
    ) -> List[Alert]:
        """Get unread alerts for a child profile."""
        return self.alert_repo.get_alerts_for_child(
            db, child_profile_id, unread_only=True, limit=limit
        )
    
    def mark_alert_as_read(
        self, db: Session, alert_id: int, parent_id: Optional[int] = None
    ) -> Optional[Alert]:
        """Mark an alert as read."""
        alert = self.alert_repo.mark_as_read(db, alert_id)
        
        if alert and parent_id:
            # Log the action
            self.audit_log_repo.log_action(
                db,
                action=AuditActionType.DATA_ACCESS,
                parent_id=parent_id,
                resource_type="alert",
                resource_id=alert_id,
                details={"action": "mark_as_read"}
            )
        
        return alert
    
    # AnalysisResult operations
    
    def mark_result_as_not_harmful(
        self, db: Session, result_id: int, parent_id: int
    ) -> Optional[AnalysisResult]:
        """Mark an analysis result as not harmful."""
        result = self.analysis_result_repo.mark_as_not_harmful(db, result_id, parent_id)
        
        if result:
            # Log the action
            self.audit_log_repo.log_action(
                db,
                action=AuditActionType.MARK_NOT_HARMFUL,
                parent_id=parent_id,
                resource_type="analysis_result",
                resource_id=result_id,
                details={
                    "risk_category": str(result.risk_category.value) if result.risk_category else None
                }
            )
        
        return result
    
    def get_flagged_channels_for_child(
        self, db: Session, child_profile_id: int, include_marked_not_harmful: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get flagged channels for a child profile.
        
        Returns:
            List of dictionaries containing channel and analysis data
        """
        # This is a more complex query that joins multiple tables
        # Implementation would depend on the specific requirements
        # For now, this is a placeholder that would need to be implemented
        # based on specific dashboard requirements
        
        # Example implementation:
        from sqlalchemy.orm import aliased
        from sqlalchemy import func, distinct
        
        Channel = aliased(SubscribedChannel)
        Result = aliased(AnalysisResult)
        LinkedAcc = aliased(LinkedAccount)
        
        # Using a raw SQL approach for demonstration
        # In a real implementation, this would be more sophisticated
        query = db.query(
            Channel.id,
            Channel.title,
            Channel.thumbnail_url,
            Channel.subscriber_count,
            func.count(distinct(Result.id)).label('flag_count')
        ).join(
            LinkedAcc, Channel.linked_account_id == LinkedAcc.id
        ).join(
            Result, Channel.id == Result.channel_id
        ).filter(
            LinkedAcc.child_profile_id == child_profile_id,
            LinkedAcc.is_active == True
        )
        
        if not include_marked_not_harmful:
            query = query.filter(Result.marked_not_harmful == False)
            
        query = query.group_by(
            Channel.id,
            Channel.title,
            Channel.thumbnail_url,
            Channel.subscriber_count
        ).having(
            func.count(distinct(Result.id)) > 0
        ).order_by(
            func.count(distinct(Result.id)).desc()
        )
        
        results = query.all()
        
        # Convert to list of dictionaries
        return [
            {
                "channel_id": r[0],
                "title": r[1],
                "thumbnail_url": r[2],
                "subscriber_count": r[3],
                "flag_count": r[4]
            }
            for r in results
        ]


# Create a singleton instance
data_service = DataService()