from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_active_user
from backend.database import get_db
from backend.models.user import ParentUser
from backend.repositories.analysis_result import AnalysisResultRepository
from backend.repositories.analyzed_video import AnalyzedVideoRepository
from backend.repositories.subscribed_channel import SubscribedChannelRepository
from backend.repositories.linked_account import LinkedAccountRepository
from backend.repositories.audit_log import AuditLogRepository
from backend.models.base import AuditActionType, RiskCategory
from backend.schemas.content import (
    AnalysisResultCreate, AnalysisResultResponse, AnalysisResultBase
)


router = APIRouter(
    prefix="/analysis_results",
    tags=["analysis_results"],
    responses={404: {"description": "Not found"}},
)

# Initialize repositories
analysis_result_repo = AnalysisResultRepository()
analyzed_video_repo = AnalyzedVideoRepository()
subscribed_channel_repo = SubscribedChannelRepository()
linked_account_repo = LinkedAccountRepository()
audit_log_repo = AuditLogRepository()


@router.get("/", response_model=List[AnalysisResultResponse])
async def read_analysis_results(
    skip: int = 0,
    limit: int = 100,
    video_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    risk_category: Optional[RiskCategory] = None,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve analysis results.
    
    Optionally filter by video_id, channel_id, or risk_category.
    """
    # Build filter parameters
    filter_params = {}
    if video_id:
        # Verify that the video belongs to the current user
        video = analyzed_video_repo.get(db, id=video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        channel = subscribed_channel_repo.get(db, id=video.channel_id)
        linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
        if linked_account.child_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access analysis results for this video"
            )
        
        filter_params["video_id"] = video_id
    
    if channel_id:
        # Verify that the channel belongs to the current user
        channel = subscribed_channel_repo.get(db, id=channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
        if linked_account.child_profile.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access analysis results for this channel"
            )
        
        filter_params["channel_id"] = channel_id
    
    if risk_category:
        filter_params["risk_category"] = risk_category
    
    # If no filters are provided, get all results for all channels belonging to the current user's children
    if not filter_params:
        results = []
        for child_profile in current_user.child_profiles:
            for linked_account in child_profile.linked_accounts:
                for channel in linked_account.subscribed_channels:
                    channel_results = analysis_result_repo.list(
                        db, skip=skip, limit=limit, channel_id=channel.id
                    )
                    results.extend(channel_results)
    else:
        results = analysis_result_repo.list(db, skip=skip, limit=limit, **filter_params)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESS,
        parent_id=current_user.id,
        resource_type="analysis_result",
        resource_id=None,
        details={
            "count": len(results),
            "video_id": video_id,
            "channel_id": channel_id,
            "risk_category": risk_category.value if risk_category else None
        }
    )
    
    return results


@router.get("/{result_id}", response_model=AnalysisResultResponse)
async def read_analysis_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Get a specific analysis result by ID.
    """
    result = analysis_result_repo.get(db, id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    # Verify that the result belongs to the current user
    if result.video_id:
        video = analyzed_video_repo.get(db, id=result.video_id)
        channel = subscribed_channel_repo.get(db, id=video.channel_id)
    else:
        channel = subscribed_channel_repo.get(db, id=result.channel_id)
    
    linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
    if linked_account.child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this analysis result"
        )
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_ACCESS,
        parent_id=current_user.id,
        resource_type="analysis_result",
        resource_id=result_id,
        details={}
    )
    
    return result


@router.put("/{result_id}/mark_not_harmful", response_model=AnalysisResultResponse)
async def mark_result_not_harmful(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Mark an analysis result as not harmful.
    """
    result = analysis_result_repo.get(db, id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    # Verify that the result belongs to the current user
    if result.video_id:
        video = analyzed_video_repo.get(db, id=result.video_id)
        channel = subscribed_channel_repo.get(db, id=video.channel_id)
    else:
        channel = subscribed_channel_repo.get(db, id=result.channel_id)
    
    linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
    if linked_account.child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this analysis result"
        )
    
    # Update the result
    update_data = {
        "marked_not_harmful": True,
        "marked_not_harmful_at": "now()",  # Use SQL function for current timestamp
        "marked_not_harmful_by": current_user.id
    }
    
    updated_result = analysis_result_repo.update(db, db_obj=result, obj_in=update_data)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.MARK_NOT_HARMFUL,
        parent_id=current_user.id,
        resource_type="analysis_result",
        resource_id=result_id,
        details={
            "risk_category": result.risk_category.value,
            "video_id": result.video_id,
            "channel_id": result.channel_id
        }
    )
    
    return updated_result


@router.delete("/{result_id}", response_model=AnalysisResultResponse)
async def delete_analysis_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: ParentUser = Depends(get_current_active_user),
) -> Any:
    """
    Delete an analysis result.
    """
    result = analysis_result_repo.get(db, id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    # Verify that the result belongs to the current user
    if result.video_id:
        video = analyzed_video_repo.get(db, id=result.video_id)
        channel = subscribed_channel_repo.get(db, id=video.channel_id)
    else:
        channel = subscribed_channel_repo.get(db, id=result.channel_id)
    
    linked_account = linked_account_repo.get(db, id=channel.linked_account_id)
    if linked_account.child_profile.parent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this analysis result"
        )
    
    deleted_result = analysis_result_repo.delete(db, id=result_id)
    
    # Log the action
    audit_log_repo.log_action(
        db,
        action=AuditActionType.DATA_DELETED,
        parent_id=current_user.id,
        resource_type="analysis_result",
        resource_id=result_id,
        details={}
    )
    
    return deleted_result