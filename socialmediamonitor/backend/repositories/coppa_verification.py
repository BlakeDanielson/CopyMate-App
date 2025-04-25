from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from backend.repositories.base import BaseRepository
from backend.models.coppa_verification import CoppaVerification
from backend.schemas.coppa_verification import VerificationStatusEnum


class CoppaVerificationRepository(BaseRepository[CoppaVerification, dict, dict]):
    """
    Repository for CoppaVerification operations.
    """
    def __init__(self):
        super().__init__(CoppaVerification)
    
    def create_verification(
        self, 
        db: Session, 
        *, 
        obj_in: Union[dict, BaseModel]
    ) -> CoppaVerification:
        """
        Create a new COPPA verification with expiry date.
        
        Args:
            db: Database session
            obj_in: Data to create the verification with (dict or Pydantic model)
            
        Returns:
            The created COPPA verification
        """
        if isinstance(obj_in, BaseModel):
            obj_data = obj_in.model_dump(exclude_unset=True)
        else:
            obj_data = obj_in
        
        # Create the verification with expiry
        db_obj = CoppaVerification.create_with_expiry(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_active_verification(
        self, 
        db: Session, 
        child_profile_id: int, 
        platform: str
    ) -> Optional[CoppaVerification]:
        """
        Get the active (valid) COPPA verification for a child profile and platform.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            platform: Platform name (e.g., 'youtube')
            
        Returns:
            The active verification or None if not found
        """
        verification = db.query(CoppaVerification).filter(
            CoppaVerification.child_profile_id == child_profile_id,
            CoppaVerification.platform == platform,
            CoppaVerification.verification_status == VerificationStatusEnum.VERIFIED,
            (CoppaVerification.expires_at > datetime.utcnow()) | (CoppaVerification.expires_at.is_(None))
        ).order_by(CoppaVerification.verified_at.desc()).first()
        
        return verification
    
    def get_pending_verification(
        self, 
        db: Session, 
        child_profile_id: int, 
        platform: str
    ) -> Optional[CoppaVerification]:
        """
        Get the pending COPPA verification for a child profile and platform.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            platform: Platform name (e.g., 'youtube')
            
        Returns:
            The pending verification or None if not found
        """
        verification = db.query(CoppaVerification).filter(
            CoppaVerification.child_profile_id == child_profile_id,
            CoppaVerification.platform == platform,
            CoppaVerification.verification_status == VerificationStatusEnum.PENDING
        ).order_by(CoppaVerification.created_at.desc()).first()
        
        return verification
    
    def get_verifications_for_child(
        self, 
        db: Session, 
        child_profile_id: int, 
        platform: Optional[str] = None
    ) -> List[CoppaVerification]:
        """
        Get all COPPA verifications for a child profile.
        
        Args:
            db: Database session
            child_profile_id: ID of the child profile
            platform: Optional platform to filter by
            
        Returns:
            List of COPPA verifications
        """
        query = db.query(CoppaVerification).filter(
            CoppaVerification.child_profile_id == child_profile_id
        )
        
        if platform:
            query = query.filter(CoppaVerification.platform == platform)
        
        return query.order_by(CoppaVerification.created_at.desc()).all()
    
    def verify(
        self, 
        db: Session, 
        verification_id: int, 
        notes: Optional[str] = None
    ) -> Optional[CoppaVerification]:
        """
        Mark a COPPA verification as verified.
        
        Args:
            db: Database session
            verification_id: ID of the verification to verify
            notes: Optional verification notes
            
        Returns:
            The updated verification or None if not found
        """
        verification = self.get(db, id=verification_id)
        if not verification:
            return None
        
        update_data = {
            "verification_status": VerificationStatusEnum.VERIFIED,
            "verified_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + datetime.timedelta(days=365)
        }
        
        if notes:
            update_data["verification_notes"] = notes
        
        return self.update(db, db_obj=verification, obj_in=update_data)
    
    def reject(
        self, 
        db: Session, 
        verification_id: int, 
        notes: Optional[str] = None
    ) -> Optional[CoppaVerification]:
        """
        Mark a COPPA verification as rejected.
        
        Args:
            db: Database session
            verification_id: ID of the verification to reject
            notes: Optional rejection notes
            
        Returns:
            The updated verification or None if not found
        """
        verification = self.get(db, id=verification_id)
        if not verification:
            return None
        
        update_data = {
            "verification_status": VerificationStatusEnum.REJECTED
        }
        
        if notes:
            update_data["verification_notes"] = notes
        
        return self.update(db, db_obj=verification, obj_in=update_data)