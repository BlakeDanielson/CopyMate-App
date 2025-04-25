from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from backend.repositories.base import BaseRepository
from backend.models.content import AnalyzedVideo


class AnalyzedVideoRepository(BaseRepository[AnalyzedVideo, dict, dict]):
    """
    Repository for AnalyzedVideo operations.
    """
    def __init__(self):
        super().__init__(AnalyzedVideo)
        
    def get_by_platform_id(
        self, db: Session, video_platform_id: str
    ) -> Optional[AnalyzedVideo]:
        """
        Get an analyzed video by its platform-specific video ID.
        
        Args:
            db: Database session
            video_platform_id: Platform-specific video identifier
            
        Returns:
            The found analyzed video or None
        """
        return db.query(AnalyzedVideo).filter(
            AnalyzedVideo.video_platform_id == video_platform_id
        ).first()
    
    def get_videos_for_channel(
        self, 
        db: Session, 
        channel_id: int, 
        skip: int = 0, 
        limit: int = 10,
        sort_by: str = "published_at",
        sort_desc: bool = True
    ) -> List[AnalyzedVideo]:
        """
        Get analyzed videos for a specific channel with sorting options.
        
        Args:
            db: Database session
            channel_id: ID of the subscribed channel
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            sort_by: Field to sort by (default: "published_at")
            sort_desc: If True, sort in descending order
            
        Returns:
            List of analyzed videos for the channel
        """
        query = db.query(AnalyzedVideo).filter(
            AnalyzedVideo.channel_id == channel_id
        )
        
        # Apply sorting
        if hasattr(AnalyzedVideo, sort_by):
            order_field = getattr(AnalyzedVideo, sort_by)
            if sort_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(order_field)
        else:
            # Default to published_at descending if invalid sort field
            query = query.order_by(desc(AnalyzedVideo.published_at))
            
        return query.offset(skip).limit(limit).all()
    
    def get_videos_with_analysis(
        self, db: Session, channel_id: int, limit: int = 10
    ) -> List[AnalyzedVideo]:
        """
        Get analyzed videos with their analysis results eager loaded.
        
        Args:
            db: Database session
            channel_id: ID of the subscribed channel
            limit: Maximum number of records to return
            
        Returns:
            List of analyzed videos with analysis results for the channel
        """
        from sqlalchemy.orm import joinedload
        
        return db.query(AnalyzedVideo)\
            .options(joinedload(AnalyzedVideo.analysis_results))\
            .filter(AnalyzedVideo.channel_id == channel_id)\
            .order_by(desc(AnalyzedVideo.published_at))\
            .limit(limit).all()
    
    def update_video_metadata(
        self, db: Session, video_id: int, metadata: Dict[str, Any]
    ) -> Optional[AnalyzedVideo]:
        """
        Update video metadata (view count, like count, etc.).
        
        Args:
            db: Database session
            video_id: ID of the analyzed video
            metadata: Dictionary of metadata fields to update
            
        Returns:
            The updated analyzed video or None if not found
        """
        video = self.get(db, video_id)
        if not video:
            return None
            
        # Update the timestamp
        metadata["updated_at"] = datetime.now()
            
        return self.update(db, db_obj=video, obj_in=metadata)
    
    def bulk_create(
        self, db: Session, videos_data: List[Dict[str, Any]]
    ) -> List[AnalyzedVideo]:
        """
        Create multiple video records in one transaction.
        
        Args:
            db: Database session
            videos_data: List of dictionaries with video data
            
        Returns:
            List of created analyzed videos
        """
        try:
            videos = []
            for data in videos_data:
                db_obj = AnalyzedVideo(**data)
                db.add(db_obj)
                videos.append(db_obj)
                
            db.commit()
            
            # Refresh all objects
            for video in videos:
                db.refresh(video)
                
            return videos
        except Exception as e:
            db.rollback()
            raise e