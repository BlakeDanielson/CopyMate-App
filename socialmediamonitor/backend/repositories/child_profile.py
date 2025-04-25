from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.repositories.base import BaseRepository
from backend.models.user import ChildProfile


class ChildProfileRepository(BaseRepository[ChildProfile, dict, dict]):
    """
    Repository for ChildProfile operations.
    """
    def __init__(self):
        super().__init__(ChildProfile)
        
    def get_profiles_by_parent(
        self, db: Session, parent_id: int, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[ChildProfile]:
        """
        Get child profiles for a specific parent.
        
        Args:
            db: Database session
            parent_id: ID of the parent user
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            active_only: If True, return only active profiles
            
        Returns:
            List of child profiles for the parent
        """
        query = db.query(ChildProfile).filter(ChildProfile.parent_id == parent_id)
        
        if active_only:
            query = query.filter(ChildProfile.is_active == True)
            
        return query.offset(skip).limit(limit).all()
    
    def get_profile_with_linked_accounts(self, db: Session, profile_id: int) -> Optional[ChildProfile]:
        """
        Get a child profile with its linked accounts eager loaded.
        
        Args:
            db: Database session
            profile_id: ID of the child profile
            
        Returns:
            The child profile with linked accounts or None if not found
        """
        from sqlalchemy.orm import joinedload
        
        return db.query(ChildProfile)\
            .options(joinedload(ChildProfile.linked_accounts))\
            .filter(ChildProfile.id == profile_id)\
            .first()
    
    def deactivate_profile(self, db: Session, profile_id: int) -> Optional[ChildProfile]:
        """
        Deactivate a child profile (soft delete).
        
        Args:
            db: Database session
            profile_id: ID of the child profile
            
        Returns:
            The updated child profile or None if not found
        """
        profile = self.get(db, profile_id)
        if profile:
            return self.update(db, db_obj=profile, obj_in={"is_active": False})
        return None
    
    def get_profile_with_alerts(
        self, db: Session, profile_id: int, unread_only: bool = False
    ) -> Optional[ChildProfile]:
        """
        Get a child profile with its alerts eager loaded.
        
        Args:
            db: Database session
            profile_id: ID of the child profile
            unread_only: If True, load only unread alerts
            
        Returns:
            The child profile with alerts or None if not found
        """
        from sqlalchemy.orm import joinedload
        from backend.models.content import Alert
        
        query = db.query(ChildProfile).filter(ChildProfile.id == profile_id)
        
        if unread_only:
            query = query.options(
                joinedload(ChildProfile.alerts.and_(Alert.is_read == False))
            )
        else:
            query = query.options(joinedload(ChildProfile.alerts))
            
        return query.first()