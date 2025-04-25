from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, case
from datetime import datetime

from backend.repositories.base import BaseRepository
from backend.models.content import AnalysisResult
from backend.models.base import RiskCategory


class AnalysisResultRepository(BaseRepository[AnalysisResult, dict, dict]):
    """
    Repository for AnalysisResult operations.
    """
    def __init__(self):
        super().__init__(AnalysisResult)
        
    def get_results_by_channel(
        self, db: Session, channel_id: int, marked_not_harmful: bool = False
    ) -> List[AnalysisResult]:
        """
        Get analysis results for a specific channel.
        
        Args:
            db: Database session
            channel_id: ID of the subscribed channel
            marked_not_harmful: If True, include results marked as not harmful
            
        Returns:
            List of analysis results for the channel
        """
        query = db.query(AnalysisResult).filter(AnalysisResult.channel_id == channel_id)
        
        if not marked_not_harmful:
            query = query.filter(AnalysisResult.marked_not_harmful == False)
            
        return query.order_by(
            AnalysisResult.severity,
            AnalysisResult.created_at.desc()
        ).all()
    
    def get_results_by_video(
        self, db: Session, video_id: int, marked_not_harmful: bool = False
    ) -> List[AnalysisResult]:
        """
        Get analysis results for a specific video.
        
        Args:
            db: Database session
            video_id: ID of the analyzed video
            marked_not_harmful: If True, include results marked as not harmful
            
        Returns:
            List of analysis results for the video
        """
        query = db.query(AnalysisResult).filter(AnalysisResult.video_id == video_id)
        
        if not marked_not_harmful:
            query = query.filter(AnalysisResult.marked_not_harmful == False)
            
        return query.order_by(
            AnalysisResult.severity,
            AnalysisResult.created_at.desc()
        ).all()
    
    def get_results_by_category(
        self, 
        db: Session, 
        risk_category: RiskCategory,
        skip: int = 0,
        limit: int = 100,
        marked_not_harmful: bool = False
    ) -> List[AnalysisResult]:
        """
        Get analysis results for a specific risk category.
        
        Args:
            db: Database session
            risk_category: Risk category to filter by
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            marked_not_harmful: If True, include results marked as not harmful
            
        Returns:
            List of analysis results for the category
        """
        query = db.query(AnalysisResult).filter(AnalysisResult.risk_category == risk_category)
        
        if not marked_not_harmful:
            query = query.filter(AnalysisResult.marked_not_harmful == False)
            
        return query.order_by(
            AnalysisResult.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def mark_as_not_harmful(
        self, db: Session, result_id: int, parent_user_id: int
    ) -> Optional[AnalysisResult]:
        """
        Mark an analysis result as not harmful by a parent user.
        
        Args:
            db: Database session
            result_id: ID of the analysis result
            parent_user_id: ID of the parent user making the determination
            
        Returns:
            The updated analysis result or None if not found
        """
        result = self.get(db, result_id)
        if not result:
            return None
            
        update_data = {
            "marked_not_harmful": True,
            "marked_not_harmful_at": datetime.now(),
            "marked_not_harmful_by": parent_user_id
        }
            
        return self.update(db, db_obj=result, obj_in=update_data)
    
    def get_new_results_count(
        self, db: Session, child_profile_id: int, since_datetime: datetime
    ) -> int:
        """
        Get count of new analysis results for a child profile's channels since a specific time.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            since_datetime: Datetime to check results since
            
        Returns:
            Count of new analysis results
        """
        from backend.models.user import LinkedAccount
        from backend.models.content import SubscribedChannel
        
        return db.query(AnalysisResult).join(
            SubscribedChannel, AnalysisResult.channel_id == SubscribedChannel.id
        ).join(
            LinkedAccount, SubscribedChannel.linked_account_id == LinkedAccount.id
        ).filter(
            LinkedAccount.child_profile_id == child_profile_id,
            AnalysisResult.created_at >= since_datetime,
            AnalysisResult.marked_not_harmful == False
        ).count()
    
    def bulk_create(
        self, db: Session, results_data: List[Dict[str, Any]]
    ) -> List[AnalysisResult]:
        """
        Create multiple analysis result records in one transaction.
        
        Args:
            db: Database session
            results_data: List of dictionaries with analysis result data
            
        Returns:
            List of created analysis results
        """
        try:
            results = []
            for data in results_data:
                db_obj = AnalysisResult(**data)
                db.add(db_obj)
                results.append(db_obj)
                
            db.commit()
            
            # Refresh all objects
            for result in results:
                db.refresh(result)
                
            return results
        except Exception as e:
            db.rollback()
            raise e