from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.repositories.base import BaseRepository
from backend.models.user import ParentUser


class ParentUserRepository(BaseRepository[ParentUser, dict, dict]):
    """
    Repository for ParentUser operations.
    """
    def __init__(self):
        super().__init__(ParentUser)
        
    def get_by_email(self, db: Session, email: str) -> Optional[ParentUser]:
        """
        Get a parent user by email.
        
        Args:
            db: Database session
            email: Email to search for
            
        Returns:
            The found parent user or None
        """
        return db.query(ParentUser).filter(ParentUser.email == email).first()
    
    def search_by_name_or_email(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[ParentUser]:
        """
        Search parent users by name or email.
        
        Args:
            db: Database session
            search_term: Term to search for in names or email
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of matching parent users
        """
        search = f"%{search_term}%"
        return db.query(ParentUser).filter(
            or_(
                ParentUser.email.ilike(search),
                ParentUser.first_name.ilike(search),
                ParentUser.last_name.ilike(search)
            )
        ).offset(skip).limit(limit).all()
    
    def update_last_login(self, db: Session, user_id: int) -> Optional[ParentUser]:
        """
        Update the last_login timestamp of a parent user.
        
        Args:
            db: Database session
            user_id: ID of the parent user
            
        Returns:
            The updated parent user or None if not found
        """
        from datetime import datetime
        user = self.get(db, user_id)
        if user:
            return self.update(db, db_obj=user, obj_in={"last_login": datetime.now()})
        return None