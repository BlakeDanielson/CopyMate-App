from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.analyzed_video import AnalyzedVideoRepository
from backend.repositories.subscribed_channel import SubscribedChannelRepository
from backend.repositories.linked_account import LinkedAccountRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType
from backend.schemas.content import (
    AnalyzedVideoCreate, AnalyzedVideoResponse, AnalyzedVideoBase
)


router = APIRouter(
    prefix="/analyzed_videos",
    tags=["analyzed_videos"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
analyzed_video_repo = AnalyzedVideoRepository()
subscribed_channel_repo = SubscribedChannelRepository()
linked_account_repo = LinkedAccountRepository()
audit_log_repo = AuditLogRepository()


@router.get("/", response_model=List[AnalyzedVideoResponse])
async def read_analyzed_videos(
    skip: int = 0,
    limit: int = 100,
    channel_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve analyzed videos.
    
    Optionally filter by channel_id.
    """
    # If channel_id is provided, verify that it belongs to the current user
    if channel_id:
        channel = subscribed_channel_repo.get(db, id=channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        # Get the linked account and verify it belongs to the current user
        linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
        if linked_account.child_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access videos for this channel"
            )
        
        videos = analyzed_video_repo.list(db, skip=skip, limit=limit, channel_id=channel_id)
    else:
        # Get all videos for all channels belonging to the current user's children
        videos = []
        for child_profile in current_user.child_profiles:
            for linked_account in child_profile.linked_accounts:
                for channel in linked_account.subscribed_channels:
                    channel_videos = analyzed_video_repo.list(
                        db, skip=skip, limit=limit, channel_id=channel.id
                    )
                    videos.extend(channel_videos)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESS,
        parent_id=current_user.id,
        resource_type="analyzed_video",
        resource_id=None,
        details={"count": len(videos), "channel_id": channel_id}
    )
    
    return videos


@router.get("/{video_id}", response_model=AnalyzedVideoResponse)
async def read_analyzed_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific analyzed video by ID.
    """
    video = analyzed_video_repo.get(db, id=video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Analyzed video not found")
    
    # Verify that the video belongs to the current user
    channel = subscribed_channel_repo.get(db, id=video.channel_id)
    linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
    if linked_account.child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this video"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESS,
        parent_id=current_user.id,
        resource_type="analyzed_video",
        resource_id=video_id,
        details={}
    )
    
    return video


@router.get("/by_platform_id/{platform_id}", response_model=AnalyzedVideoResponse)
async def read_analyzed_video_by_platform_id(
    platform_id: str,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific analyzed video by platform ID (e.g., YouTube video ID).
    """
    video = analyzed_video_repo.get_by_platform_id(db, platform_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Analyzed video not found")
    
    # Verify that the video belongs to the current user
    channel = subscribed_channel_repo.get(db, id=video.channel_id)
    linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
    if linked_account.child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this video"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESS,
        parent_id=current_user.id,
        resource_type="analyzed_video",
        resource_id=video.id,
        details={"platform_id": platform_id}
    )
    
    return video


@router.delete("/{video_id}", response_model=AnalyzedVideoResponse)
async def delete_analyzed_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Delete an analyzed video.
    """
    video = analyzed_video_repo.get(db, id=video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Analyzed video not found")
    
    # Verify that the video belongs to the current user
    channel = subscribed_channel_repo.get(db, id=video.channel_id)
    linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
    if linked_account.child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this video"
        )
    
    deleted_video = analyzed_video_repo.delete(db, id=video_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_DELETED,
        parent_id=current_user.id,
        resource_type="analyzed_video",
        resource_id=video_id,
        details={}
    )
    
    return deleted_video