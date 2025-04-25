from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.subscribed_channel import SubscribedChannelRepository
from backend.repositories.linked_account import LinkedAccountRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.schemas.content import (
    SubscribedChannelCreate, SubscribedChannelResponse, SubscribedChannelBase
)


router = APIRouter(
    prefix="/subscribed_channels",
    tags=["subscribed_channels"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
subscribed_channel_repo = SubscribedChannelRepository()
linked_account_repo = LinkedAccountRepository()
audit_log_repo = AuditLogRepository()


@router.get("/", response_model=List[SubscribedChannelResponse])
async def read_subscribed_channels(
    skip: int = 0,
    limit: int = 100,
    linked_account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve subscribed channels.
    
    Optionally filter by linked_account_id.
    """
    # If linked_account_id is provided, verify that it belongs to the current user
    if linked_account_id:
        linked_account = linked_account_repo.get(db, id=linked_account_id)
        if not linked_account:
            raise HTTPException(status_code=404, detail="Linked account not found")
        
        # Get the child profile and verify it belongs to the current user
        if linked_account.child_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this linked account"
            )
        
        channels = subscribed_channel_repo.list(db, skip=skip, limit=limit, linked_account_id=linked_account_id)
    else:
        # Get all channels for all linked accounts belonging to the current user's children
        channels = []
        for child_profile in current_user.child_profiles:
            for linked_account in child_profile.linked_accounts:
                child_channels = subscribed_channel_repo.list(
                    db, skip=skip, limit=limit, linked_account_id=linked_account.id
                )
                channels.extend(child_channels)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESS,
        parent_id=current_user.id,
        resource_type="subscribed_channel",
        resource_id=None,
        details={"count": len(channels), "linked_account_id": linked_account_id}
    )
    
    return channels


@router.get("/{channel_id}", response_model=SubscribedChannelResponse)
async def read_subscribed_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific subscribed channel by ID.
    """
    channel = subscribed_channel_repo.get(db, id=channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Subscribed channel not found")
    
    # Verify that the channel belongs to the current user
    linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
    if linked_account.child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this channel"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESS,
        parent_id=current_user.id,
        resource_type="subscribed_channel",
        resource_id=channel_id,
        details={}
    )
    
    return channel


@router.delete("/{channel_id}", response_model=SubscribedChannelResponse)
async def delete_subscribed_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Delete a subscribed channel.
    """
    channel = subscribed_channel_repo.get(db, id=channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Subscribed channel not found")
    
    # Verify that the channel belongs to the current user
    linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
    if linked_account.child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this channel"
        )
    
    deleted_channel = subscribed_channel_repo.delete(db, id=channel_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_DELETED,
        parent_id=current_user.id,
        resource_type="subscribed_channel",
        resource_id=channel_id,
        details={}
    )
    
    return deleted_channel