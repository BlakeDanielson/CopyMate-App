from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.subscribed_channel import SubscribedChannelRepository
from backend.repositories.analyzed_video import AnalyzedVideoRepository
from backend.repositories.analysis_result import AnalysisResultRepository
from backend.repositories.child_profile import ChildProfileRepository
from backend.repositories.linked_account import LinkedAccountRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType, RiskCategory
from backend.schemas.content import (
    SubscribedChannelResponse, AnalyzedVideoResponse, AnalysisResultResponse,
    SubscribedChannelCreate, AnalyzedVideoCreate, AnalysisResultCreate
)


router = APIRouter(
    prefix="/content",
    tags=["content"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
subscribed_channel_repo = SubscribedChannelRepository()
analyzed_video_repo = AnalyzedVideoRepository()
analysis_result_repo = AnalysisResultRepository()
child_profile_repo = ChildProfileRepository()
linked_account_repo = LinkedAccountRepository()
audit_log_repo = AuditLogRepository()


# Helper function to check if a user has access to a linked account
def check_user_access_to_linked_account(
    db: Session, user_id: int, linked_account_id: int
) -> bool:
    """
    Check if a user has access to a linked account.
    
    Args:
        db: Database session
        user_id: ID of the user
        linked_account_id: ID of the linked account
        
    Returns:
        True if the user has access, False otherwise
    """
    linked_account = linked_account_repo.get(db, id=linked_account_id)
    if not linked_account:
        return False
    
    child_profile = child_profile_repo.get(db, id=linked_account.child_profile_id)
    if not child_profile:
        return False
    
    return child_profile.parent_id == user_id


# Subscribed Channels Endpoints

@router.get("/channels/", response_model=List[SubscribedChannelResponse])
async def read_subscribed_channels(
    skip: int = 0,
    limit: int = 100,
    linked_account_id: Optional[int] = None,
    child_profile_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve subscribed channels.
    
    Users should only be able to see channels linked to their own children's accounts.
    """
    # If linked_account_id is provided, check if the user has access to it
    if linked_account_id:
        if not check_user_access_to_linked_account(db, current_user.id, linked_account_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access channels linked to your own children's accounts"
            )
        
        channels = subscribed_channel_repo.list(
            db, skip=skip, limit=limit, linked_account_id=linked_account_id
        )
    # If child_profile_id is provided, check if it belongs to the current user
    elif child_profile_id:
        child_profile = child_profile_repo.get(db, id=child_profile_id)
        if not child_profile or child_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access channels linked to your own children's profiles"
            )
        
        # Get all linked accounts for this child profile
        linked_accounts = linked_account_repo.list(db, child_profile_id=child_profile_id)
        linked_account_ids = [account.id for account in linked_accounts]
        
        if not linked_account_ids:
            return []
        
        # Get channels for all linked accounts
        channels = []
        for account_id in linked_account_ids:
            account_channels = subscribed_channel_repo.list(
                db, skip=skip, limit=limit, linked_account_id=account_id
            )
            channels.extend(account_channels)
    else:
        # Get all child profiles for the current user
        child_profiles = child_profile_repo.list(db, parent_id=current_user.id)
        child_profile_ids = [profile.id for profile in child_profiles]
        
        if not child_profile_ids:
            return []
        
        # Get all linked accounts for these child profiles
        linked_accounts = []
        for profile_id in child_profile_ids:
            profile_accounts = linked_account_repo.list(db, child_profile_id=profile_id)
            linked_accounts.extend(profile_accounts)
        
        linked_account_ids = [account.id for account in linked_accounts]
        
        if not linked_account_ids:
            return []
        
        # Get channels for all linked accounts
        channels = []
        for account_id in linked_account_ids:
            account_channels = subscribed_channel_repo.list(
                db, skip=skip, limit=limit, linked_account_id=account_id
            )
            channels.extend(account_channels)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="subscribed_channel",
        resource_id=None,
        details={
            "count": len(channels),
            "linked_account_id": linked_account_id if linked_account_id else "all",
            "child_profile_id": child_profile_id if child_profile_id else "all"
        }
    )
    
    return channels


@router.get("/channels/{channel_id}", response_model=SubscribedChannelResponse)
async def read_subscribed_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific subscribed channel by ID.
    
    Users should only be able to access channels linked to their own children's accounts.
    """
    db_channel = subscribed_channel_repo.get(db, id=channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Subscribed channel not found")
    
    # Check if the user has access to the linked account
    if not check_user_access_to_linked_account(db, current_user.id, db_channel.linked_account_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access channels linked to your own children's accounts"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="subscribed_channel",
        resource_id=channel_id,
        details={}
    )
    
    return db_channel


# Analyzed Videos Endpoints

@router.get("/videos/", response_model=List[AnalyzedVideoResponse])
async def read_analyzed_videos(
    skip: int = 0,
    limit: int = 100,
    channel_id: Optional[int] = None,
    flagged_only: bool = False,
    risk_category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve analyzed videos.
    
    Users should only be able to see videos from channels linked to their own children's accounts.
    """
    # If channel_id is provided, check if the user has access to it
    if channel_id:
        db_channel = subscribed_channel_repo.get(db, id=channel_id)
        if not db_channel:
            raise HTTPException(status_code=404, detail="Subscribed channel not found")
        
        if not check_user_access_to_linked_account(db, current_user.id, db_channel.linked_account_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access videos from channels linked to your own children's accounts"
            )
        
        videos = analyzed_video_repo.list(
            db, skip=skip, limit=limit, channel_id=channel_id
        )
    else:
        # Get all child profiles for the current user
        child_profiles = child_profile_repo.list(db, parent_id=current_user.id)
        child_profile_ids = [profile.id for profile in child_profiles]
        
        if not child_profile_ids:
            return []
        
        # Get all linked accounts for these child profiles
        linked_accounts = []
        for profile_id in child_profile_ids:
            profile_accounts = linked_account_repo.list(db, child_profile_id=profile_id)
            linked_accounts.extend(profile_accounts)
        
        linked_account_ids = [account.id for account in linked_accounts]
        
        if not linked_account_ids:
            return []
        
        # Get all channels for these linked accounts
        channels = []
        for account_id in linked_account_ids:
            account_channels = subscribed_channel_repo.list(db, linked_account_id=account_id)
            channels.extend(account_channels)
        
        channel_ids = [channel.id for channel in channels]
        
        if not channel_ids:
            return []
        
        # Get videos for all channels
        videos = []
        for ch_id in channel_ids:
            channel_videos = analyzed_video_repo.list(
                db, skip=skip, limit=limit, channel_id=ch_id
            )
            videos.extend(channel_videos)
    
    # If flagged_only is True, filter videos to only include those with analysis results
    if flagged_only:
        flagged_video_ids = set()
        for video in videos:
            results = analysis_result_repo.list(db, video_id=video.id)
            
            # If risk_category is provided, filter by that category
            if risk_category:
                try:
                    risk_cat_enum = RiskCategory[risk_category.upper()]
                    results = [r for r in results if r.risk_category == risk_cat_enum]
                except KeyError:
                    # Invalid risk category, ignore the filter
                    pass
            
            if results:
                flagged_video_ids.add(video.id)
        
        videos = [v for v in videos if v.id in flagged_video_ids]
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="analyzed_video",
        resource_id=None,
        details={
            "count": len(videos),
            "channel_id": channel_id if channel_id else "all",
            "flagged_only": flagged_only,
            "risk_category": risk_category if risk_category else "all"
        }
    )
    
    return videos


@router.get("/videos/{video_id}", response_model=AnalyzedVideoResponse)
async def read_analyzed_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific analyzed video by ID.
    
    Users should only be able to access videos from channels linked to their own children's accounts.
    """
    db_video = analyzed_video_repo.get(db, id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Analyzed video not found")
    
    # Get the channel for this video
    db_channel = subscribed_channel_repo.get(db, id=db_video.channel_id)
    if not db_channel:
        raise HTTPException(status_code=404, detail="Subscribed channel not found")
    
    # Check if the user has access to the linked account
    if not check_user_access_to_linked_account(db, current_user.id, db_channel.linked_account_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access videos from channels linked to your own children's accounts"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="analyzed_video",
        resource_id=video_id,
        details={}
    )
    
    return db_video


# Analysis Results Endpoints

@router.get("/results/", response_model=List[AnalysisResultResponse])
async def read_analysis_results(
    skip: int = 0,
    limit: int = 100,
    video_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    risk_category: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve analysis results.
    
    Users should only be able to see results for videos from channels linked to their own children's accounts.
    """
    # Build filter criteria
    filter_criteria = {}
    
    # If video_id is provided, check if the user has access to it
    if video_id:
        db_video = analyzed_video_repo.get(db, id=video_id)
        if not db_video:
            raise HTTPException(status_code=404, detail="Analyzed video not found")
        
        db_channel = subscribed_channel_repo.get(db, id=db_video.channel_id)
        if not db_channel:
            raise HTTPException(status_code=404, detail="Subscribed channel not found")
        
        if not check_user_access_to_linked_account(db, current_user.id, db_channel.linked_account_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access results for videos from channels linked to your own children's accounts"
            )
        
        filter_criteria["video_id"] = video_id
    
    # If channel_id is provided, check if the user has access to it
    elif channel_id:
        db_channel = subscribed_channel_repo.get(db, id=channel_id)
        if not db_channel:
            raise HTTPException(status_code=404, detail="Subscribed channel not found")
        
        if not check_user_access_to_linked_account(db, current_user.id, db_channel.linked_account_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access results for channels linked to your own children's accounts"
            )
        
        filter_criteria["channel_id"] = channel_id
    else:
        # Get all child profiles for the current user
        child_profiles = child_profile_repo.list(db, parent_id=current_user.id)
        child_profile_ids = [profile.id for profile in child_profiles]
        
        if not child_profile_ids:
            return []
        
        # Get all linked accounts for these child profiles
        linked_accounts = []
        for profile_id in child_profile_ids:
            profile_accounts = linked_account_repo.list(db, child_profile_id=profile_id)
            linked_accounts.extend(profile_accounts)
        
        linked_account_ids = [account.id for account in linked_accounts]
        
        if not linked_account_ids:
            return []
        
        # Get all channels for these linked accounts
        channels = []
        for account_id in linked_account_ids:
            account_channels = subscribed_channel_repo.list(db, linked_account_id=account_id)
            channels.extend(account_channels)
        
        channel_ids = [channel.id for channel in channels]
        
        if not channel_ids:
            return []
        
        # We'll filter by channel IDs in the query
        # But we need to handle this specially since we have multiple IDs
        
    # Add risk category filter if provided
    if risk_category:
        try:
            risk_cat_enum = RiskCategory[risk_category.upper()]
            filter_criteria["risk_category"] = risk_cat_enum
        except KeyError:
            # Invalid risk category, ignore the filter
            pass
    
    # Add severity filter if provided
    if severity:
        if severity in ["low", "medium", "high"]:
            filter_criteria["severity"] = severity
    
    # Get results based on filters
    if "channel_id" in filter_criteria or "video_id" in filter_criteria:
        # Simple case: filtering by a single channel or video
        results = analysis_result_repo.list(db, skip=skip, limit=limit, **filter_criteria)
    else:
        # Complex case: filtering by multiple channels
        results = []
        for ch_id in channel_ids:
            ch_filter = filter_criteria.copy()
            ch_filter["channel_id"] = ch_id
            channel_results = analysis_result_repo.list(db, skip=skip, limit=limit, **ch_filter)
            results.extend(channel_results)
            
            # Respect the limit across all channels
            if len(results) >= limit:
                results = results[:limit]
                break
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="analysis_result",
        resource_id=None,
        details={
            "count": len(results),
            "video_id": video_id if video_id else "all",
            "channel_id": channel_id if channel_id else "all",
            "risk_category": risk_category if risk_category else "all",
            "severity": severity if severity else "all"
        }
    )
    
    return results


@router.get("/results/{result_id}", response_model=AnalysisResultResponse)
async def read_analysis_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific analysis result by ID.
    
    Users should only be able to access results for videos from channels linked to their own children's accounts.
    """
    db_result = analysis_result_repo.get(db, id=result_id)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    # Check if the user has access to the channel
    db_channel = subscribed_channel_repo.get(db, id=db_result.channel_id)
    if not db_channel:
        raise HTTPException(status_code=404, detail="Subscribed channel not found")
    
    if not check_user_access_to_linked_account(db, current_user.id, db_channel.linked_account_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access results for videos from channels linked to your own children's accounts"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESSED,
        parent_id=current_user.id,
        resource_type="analysis_result",
        resource_id=result_id,
        details={}
    )
    
    return db_result


@router.put("/results/{result_id}/mark-not-harmful", response_model=AnalysisResultResponse)
async def mark_result_not_harmful(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Mark an analysis result as not harmful.
    
    Users should only be able to mark results for videos from channels linked to their own children's accounts.
    """
    db_result = analysis_result_repo.get(db, id=result_id)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    # Check if the user has access to the channel
    db_channel = subscribed_channel_repo.get(db, id=db_result.channel_id)
    if not db_channel:
        raise HTTPException(status_code=404, detail="Subscribed channel not found")
    
    if not check_user_access_to_linked_account(db, current_user.id, db_channel.linked_account_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only mark results for videos from channels linked to your own children's accounts"
        )
    
    # Update the result
    update_data = {
        "marked_not_harmful": True,
        "marked_not_harmful_at": datetime.now(),
        "marked_not_harmful_by": current_user.id
    }
    
    updated_result = analysis_result_repo.update(db, db_obj=db_result, obj_in=update_data)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.MARK_NOT_HARMFUL,
        parent_id=current_user.id,
        resource_type="analysis_result",
        resource_id=result_id,
        details={
            "risk_category": db_result.risk_category.value,
            "video_id": db_result.video_id,
            "channel_id": db_result.channel_id
        }
    )
    
    return updated_result