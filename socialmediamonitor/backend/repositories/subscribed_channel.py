from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta

from backend.repositories.base import BaseRepository
from backend.models.content import SubscribedChannel


class SubscribedChannelRepository(BaseRepository[SubscribedChannel, dict, dict]):
    """
    Repository for SubscribedChannel operations.
    """
    def __init__(self):
        super().__init__(SubscribedChannel)
        
    def get_by_channel_id(
        self, db: Session, linked_account_id: int, channel_id: str
    ) -> Optional[SubscribedChannel]:
        """
        Get a subscribed channel by its platform-specific channel ID for a linked account.
        
        Args:
            db: Database session
            linked_account_id: ID of the linked account
            channel_id: Platform-specific channel identifier
            
        Returns:
            The found subscribed channel or None
        """
        return db.query(SubscribedChannel).filter(
            SubscribedChannel.linked_account_id == linked_account_id,
            SubscribedChannel.channel_id == channel_id
        ).first()

    def get_channels_for_account(
        self, 
        db: Session, 
        linked_account_id: int, 
        skip: int = 0, 
        limit: int = 100,
        sort_by: str = "title",
        sort_desc: bool = False
    ) -> List[SubscribedChannel]:
        """
        Get subscribed channels for a specific linked account with sorting options.
        
        Args:
            db: Database session
            linked_account_id: ID of the linked account
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            sort_by: Field to sort by (default: "title")
            sort_desc: If True, sort in descending order
            
        Returns:
            List of subscribed channels for the linked account
        """
        query = db.query(SubscribedChannel).filter(
            SubscribedChannel.linked_account_id == linked_account_id
        )
        
        # Apply sorting
        if hasattr(SubscribedChannel, sort_by):
            order_field = getattr(SubscribedChannel, sort_by)
            if sort_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(order_field)
        else:
            # Default to title ascending if invalid sort field
            query = query.order_by(SubscribedChannel.title)
            
        return query.offset(skip).limit(limit).all()
    
    def get_channels_needing_update(
        self, db: Session, hours_threshold: int = 24, limit: int = 100
    ) -> List[SubscribedChannel]:
        """
        Get subscribed channels that need to be updated based on last_fetched_at.
        
        Args:
            db: Database session
            hours_threshold: Number of hours since last update to consider a channel needs updating
            limit: Maximum number of records to return
            
        Returns:
            List of subscribed channels that need updating
        """
        threshold_time = datetime.now() - timedelta(hours=hours_threshold)
        
        return db.query(SubscribedChannel).filter(
            (SubscribedChannel.last_fetched_at == None) | 
            (SubscribedChannel.last_fetched_at < threshold_time)
        ).order_by(
            SubscribedChannel.last_fetched_at.asc().nullsfirst()
        ).limit(limit).all()
    
    def update_channel_metadata(
        self, db: Session, channel_id: int, metadata: Dict[str, Any]
    ) -> Optional[SubscribedChannel]:
        """
        Update channel metadata (subscriber count, video count, etc.).
        
        Args:
            db: Database session
            channel_id: ID of the subscribed channel
            metadata: Dictionary of metadata fields to update
            
        Returns:
            The updated subscribed channel or None if not found
        """
        channel = self.get(db, channel_id)
        if not channel:
            return None
            
        # Add last_fetched_at to the update
        metadata["last_fetched_at"] = datetime.now()
            
        return self.update(db, db_obj=channel, obj_in=metadata)
    
    def get_channels_with_videos(
        self, db: Session, linked_account_id: int, skip: int = 0, limit: int = 100
    ) -> List[SubscribedChannel]:
        """
        Get subscribed channels with their analyzed videos eager loaded.
        
        Args:
            db: Database session
            linked_account_id: ID of the linked account
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of subscribed channels with videos for the linked account
        """
        from sqlalchemy.orm import joinedload
        
        return db.query(SubscribedChannel)\
            .options(joinedload(SubscribedChannel.analyzed_videos))\
            .filter(SubscribedChannel.linked_account_id == linked_account_id)\
            .order_by(SubscribedChannel.title)\
            .offset(skip).limit(limit).all()