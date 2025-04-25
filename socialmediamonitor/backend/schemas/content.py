from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime
from backend.models.base import RiskCategory

class SubscribedChannelBase(BaseModel):
    linked_account_id: int
    channel_id: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    topic_details: Optional[Any] = None

class SubscribedChannelCreate(SubscribedChannelBase):
    pass

class SubscribedChannelResponse(SubscribedChannelBase):
    id: int
    last_fetched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AnalyzedVideoBase(BaseModel):
    channel_id: int
    video_platform_id: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    published_at: Optional[datetime] = None
    duration: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None

class AnalyzedVideoCreate(AnalyzedVideoBase):
    pass

class AnalyzedVideoResponse(AnalyzedVideoBase):
    id: int
    fetched_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AnalysisResultBase(BaseModel):
    channel_id: Optional[int] = None
    video_id: Optional[int] = None
    risk_category: RiskCategory
    severity: Optional[str] = None
    flagged_text: Optional[str] = None
    keywords_matched: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    marked_not_harmful: bool = False
    marked_not_harmful_at: Optional[datetime] = None
    marked_not_harmful_by: Optional[int] = None

class AnalysisResultCreate(AnalysisResultBase):
    pass

class AnalysisResultResponse(AnalysisResultBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True