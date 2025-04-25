from fastapi import APIRouter
from app.api.v1.endpoints import auth, profiles, youtube # Import your endpoint modules

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(youtube.router, prefix="/youtube", tags=["youtube"])
# Include other endpoint routers here later
# api_router.include_router(users.router, prefix="/users", tags=["users"])