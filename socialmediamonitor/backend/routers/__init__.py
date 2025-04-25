from fastapi import APIRouter

from backend.routers.auth import router as auth_router
from backend.routers.parent_user import router as parent_user_router
from backend.routers.child_profile import router as child_profile_router
from backend.routers.linked_account import router as linked_account_router
from backend.routers.content import router as content_router
from backend.routers.alert import router as alert_router
from backend.routers.audit_log import router as audit_log_router
from backend.routers.oauth import router as oauth_router
from backend.routers.oauth_explanation import router as oauth_explanation_router
from backend.routers.coppa_verification import router as coppa_verification_router
from backend.routers.subscribed_channel import router as subscribed_channel_router
from backend.routers.analyzed_video import router as analyzed_video_router
from backend.routers.analysis_result import router as analysis_result_router
from backend.routers.scan import router as scan_router
from backend.routers.notification import router as notification_router


# Create a router instance for all API endpoints
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(parent_user_router)
api_router.include_router(child_profile_router)
api_router.include_router(linked_account_router)
api_router.include_router(content_router)
api_router.include_router(alert_router)
api_router.include_router(audit_log_router)
api_router.include_router(oauth_router)
api_router.include_router(oauth_explanation_router)
api_router.include_router(coppa_verification_router)
api_router.include_router(subscribed_channel_router)
api_router.include_router(analyzed_video_router)
api_router.include_router(analysis_result_router)
api_router.include_router(scan_router)
api_router.include_router(notification_router)