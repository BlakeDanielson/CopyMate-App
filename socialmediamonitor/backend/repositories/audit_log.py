from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta

from backend.repositories.base import BaseRepository
from backend.models.content import AuditLog
from backend.models.base import AuditActionType


class AuditLogRepository(BaseRepository[AuditLog, dict, dict]):
    """
    Repository for AuditLog operations.
    """
    def __init__(self):
        super().__init__(AuditLog)
        
    def log_action(
        self, 
        db: Session, 
        action: AuditActionType, 
        parent_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry for an action.
        
        Args:
            db: Database session
            action: Type of action being performed
            parent_id: ID of the parent user (optional)
            resource_type: Type of resource affected (optional)
            resource_id: ID of the resource affected (optional)
            details: Additional details about the action (optional)
            ip_address: IP address of the request (optional)
            user_agent: User agent of the request (optional)
            
        Returns:
            The created audit log entry
        """
        log_data = {
            "action": action,
            "parent_id": parent_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        return self.create(db, obj_in=log_data)
    
    def get_logs_for_parent(
        self, 
        db: Session, 
        parent_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific parent user.
        
        Args:
            db: Database session
            parent_id: ID of the parent user
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of audit logs for the parent user
        """
        return db.query(AuditLog).filter(
            AuditLog.parent_id == parent_id
        ).order_by(
            AuditLog.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_logs_by_action(
        self, 
        db: Session, 
        action: AuditActionType, 
        days: int = 30,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific action type within a time period.
        
        Args:
            db: Database session
            action: Type of action to filter by
            days: Number of days to look back
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of audit logs for the specified action
        """
        start_date = datetime.now() - timedelta(days=days)
        
        return db.query(AuditLog).filter(
            AuditLog.action == action,
            AuditLog.created_at >= start_date
        ).order_by(
            AuditLog.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_logs_for_resource(
        self, 
        db: Session, 
        resource_type: str,
        resource_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific resource.
        
        Args:
            db: Database session
            resource_type: Type of resource
            resource_id: ID of the resource
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of audit logs for the specified resource
        """
        return db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(
            AuditLog.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_error_logs(
        self, 
        db: Session, 
        days: int = 7,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get system error logs within a time period.
        
        Args:
            db: Database session
            days: Number of days to look back
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of system error logs
        """
        start_date = datetime.now() - timedelta(days=days)
        
        return db.query(AuditLog).filter(
            AuditLog.action == AuditActionType.SYSTEM_ERROR,
            AuditLog.created_at >= start_date
        ).order_by(
            AuditLog.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def list_with_date_filter(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        date_filters: Dict[str, datetime] = None,
        **kwargs
    ) -> List[AuditLog]:
        """
        Get audit logs with date range filters and other criteria.
        
        Args:
            db: Database session
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            date_filters: Dictionary of date filters (e.g., {"created_at__gte": start_date})
            **kwargs: Additional filter criteria
            
        Returns:
            List of matching audit logs
        """
        query = db.query(self.model)
        
        # Apply standard filters
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        # Apply date range filters
        if date_filters:
            for key, value in date_filters.items():
                if "__" in key:
                    field_name, operator = key.split("__")
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        if operator == "gte":
                            query = query.filter(field >= value)
                        elif operator == "lte":
                            query = query.filter(field <= value)
                        elif operator == "gt":
                            query = query.filter(field > value)
                        elif operator == "lt":
                            query = query.filter(field < value)
        
        # Order by created_at descending
        query = query.order_by(desc(self.model.created_at))
        
        return query.offset(skip).limit(limit).all()
    
    def count_by_action_type(
        self,
        db: Session,
        parent_id: Optional[int] = None,
        start_date: Optional[datetime] = None
    ) -> List[Tuple[AuditActionType, int]]:
        """
        Count audit logs grouped by action type.
        
        Args:
            db: Database session
            parent_id: Optional parent user ID to filter by
            start_date: Optional start date to filter by
            
        Returns:
            List of tuples containing action type and count
        """
        query = db.query(AuditLog.action, func.count(AuditLog.id))
        
        # Apply filters
        filters = []
        if parent_id is not None:
            filters.append(AuditLog.parent_id == parent_id)
        if start_date is not None:
            filters.append(AuditLog.created_at >= start_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Group by action type
        query = query.group_by(AuditLog.action)
        
        return query.all()
    
    def count_by_resource_type(
        self,
        db: Session,
        parent_id: Optional[int] = None,
        start_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        Count audit logs grouped by resource type.
        
        Args:
            db: Database session
            parent_id: Optional parent user ID to filter by
            start_date: Optional start date to filter by
            
        Returns:
            Dictionary mapping resource type to count
        """
        query = db.query(AuditLog.resource_type, func.count(AuditLog.id))
        
        # Apply filters
        filters = []
        if parent_id is not None:
            filters.append(AuditLog.parent_id == parent_id)
        if start_date is not None:
            filters.append(AuditLog.created_at >= start_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Group by resource type and filter out None values
        query = query.filter(AuditLog.resource_type.isnot(None))
        query = query.group_by(AuditLog.resource_type)
        
        # Convert to dictionary
        result = {}
        for resource_type, count in query.all():
            result[resource_type] = count
        
        return result
    
    def count_by_day(
        self,
        db: Session,
        parent_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        Count audit logs grouped by day.
        
        Args:
            db: Database session
            parent_id: Optional parent user ID to filter by
            start_date: Optional start date to filter by
            end_date: Optional end date to filter by
            
        Returns:
            Dictionary mapping date string (YYYY-MM-DD) to count
        """
        # Use database-specific date truncation function
        date_trunc = func.date_trunc('day', AuditLog.created_at)
        
        query = db.query(date_trunc, func.count(AuditLog.id))
        
        # Apply filters
        filters = []
        if parent_id is not None:
            filters.append(AuditLog.parent_id == parent_id)
        if start_date is not None:
            filters.append(AuditLog.created_at >= start_date)
        if end_date is not None:
            filters.append(AuditLog.created_at <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Group by day
        query = query.group_by(date_trunc)
        
        # Convert to dictionary
        result = {}
        for date_obj, count in query.all():
            date_str = date_obj.strftime('%Y-%m-%d')
            result[date_str] = count
        
        return result