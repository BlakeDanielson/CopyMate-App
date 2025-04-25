import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import json
from jose import jwt, JWTError # For signing state
import googleapiclient.discovery
import googleapiclient.errors

from app import crud, models, schemas
from app.api import deps
from app.config import settings
from app.core.oauth_utils import refresh_google_token

router = APIRouter()

# Helper to create the OAuth flow object
def create_google_flow() -> Flow:
    # Store client secrets directly or load from file if preferred
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            # "javascript_origins": [...] # Add if needed
        }
    }
    return Flow.from_client_config(
        client_config=client_config,
        scopes=settings.YOUTUBE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

# Helper to sign/encode state
def encode_state(data: Dict[str, Any]) -> str:
    # Simple JWT signing for state integrity
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Helper to get authenticated YouTube API client with token refresh
async def get_youtube_client(
    db: AsyncSession,
    profile_id: int,
    parent_id: int
) -> googleapiclient.discovery.Resource:
    """
    Gets an authenticated YouTube API client for the specified profile,
    automatically refreshing the access token if needed.
    
    Args:
        db: Database session
        profile_id: ID of the child profile
        parent_id: ID of the parent (for verification)
        
    Returns:
        Authenticated YouTube API client
        
    Raises:
        HTTPException: If profile not found, not linked, or auth fails
    """
    # Verify the profile belongs to the parent
    profile = await crud.crud_profile.get_profile(db, profile_id=profile_id, parent_id=parent_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found or not owned by user")

    # Get the linked YouTube account
    linked_account = await crud.crud_linked_account.get_linked_account_by_profile(
        db=db, profile_id=profile_id, provider="youtube"
    )
    if not linked_account:
        raise HTTPException(status_code=404, detail="No YouTube account linked to this profile")

    # Refresh the token if needed
    refreshed_account = await refresh_google_token(db=db, linked_account=linked_account)
    if not refreshed_account:
        raise HTTPException(
            status_code=401,
            detail="Failed to refresh YouTube access token. Please re-authenticate."
        )
    
    # Create credentials object from stored tokens
    try:
        credentials = Credentials(
            token=refreshed_account.access_token,
            refresh_token=refreshed_account.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=refreshed_account.scopes.split(" ") if refreshed_account.scopes else None,
            expiry=refreshed_account.expires_at
        )

        # Build the YouTube API client
        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        
    except Exception as e:
        print(f"Error creating YouTube client: {e}")  # Replace with proper logging
        raise HTTPException(status_code=500, detail=f"Failed to create YouTube client: {e}")

# Helper to decode/validate state
def decode_state(state: str) -> Dict[str, Any]:
    try:
        return jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

@router.get("/auth/url", response_model=Dict[str, str])
async def get_youtube_auth_url(
    profile_id: int, # Require profile_id to link
    current_user: models.ParentUser = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Generate the Google OAuth URL for linking a YouTube account to a specific child profile.
    """
    # Verify the profile belongs to the current user
    profile = await crud.crud_profile.get_profile(db, profile_id=profile_id, parent_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Child profile not found or not owned by user")

    flow = create_google_flow()
    # Generate a unique CSRF token (optional but recommended)
    csrf_token = str(uuid.uuid4())
    # Encode profile_id and CSRF token in state
    state_data = {"profile_id": profile_id, "csrf": csrf_token}
    state = encode_state(state_data)
    # Store csrf_token temporarily if needed for stricter validation (e.g., in Redis or session)

    authorization_url, generated_state = flow.authorization_url(
        access_type='offline', # Request refresh token
        prompt='consent',      # Force consent screen for refresh token
        state=state            # Pass our signed state
    )
    return {"authorization_url": authorization_url}

@router.get("/auth/callback")
async def youtube_auth_callback(
    request: Request, # Use Request to get full URL
    db: AsyncSession = Depends(deps.get_db),
    # state: str = Query(...), # State is extracted from request URL
    # code: str = Query(...),  # Code is extracted from request URL
    # scope: str = Query(...), # Scope is extracted from request URL
) -> Any:
    """
    Handle the callback from Google OAuth after user consent.
    Exchanges the code for tokens and links the account.
    """
    try:
        state_from_query = request.query_params.get('state')
        if not state_from_query:
             raise HTTPException(status_code=400, detail="Missing state parameter")

        # Decode and validate state
        decoded_state = decode_state(state_from_query)
        profile_id = decoded_state.get("profile_id")
        # csrf_token_from_state = decoded_state.get("csrf") # Validate CSRF if stored

        if not profile_id:
             raise HTTPException(status_code=400, detail="Invalid state: missing profile_id")

        # Validate CSRF token here if implemented

        flow = create_google_flow()
        # Pass the full URL to fetch_token to handle query params correctly
        flow.fetch_token(authorization_response=str(request.url))

        credentials = flow.credentials
        if not credentials or not credentials.valid:
             raise HTTPException(status_code=400, detail="Failed to fetch valid credentials")

        # Calculate expiry
        expires_at = credentials.expiry if credentials.expiry else None

        # Prepare data for DB
        linked_account_data = schemas.LinkedAccountCreate(
            provider="youtube",
            profile_id=profile_id,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token, # May be None
            expires_at=expires_at,
            scopes=" ".join(credentials.scopes) if credentials.scopes else None
        )

        # Create or update the linked account entry
        await crud.crud_linked_account.create_or_update_linked_account(
            db=db, obj_in=linked_account_data
        )

        # Redirect user back to frontend (replace with actual frontend URL)
        # Consider adding success/error status in redirect query params
        frontend_redirect_url = f"http://localhost:3000/link-success?profile_id={profile_id}" # Example
        return RedirectResponse(url=frontend_redirect_url)

    except RefreshError as e:
         raise HTTPException(status_code=400, detail=f"Error refreshing token: {e}")
    except Exception as e:
        # Log the error details
        print(f"OAuth Callback Error: {e}") # Replace with proper logging
        raise HTTPException(status_code=500, detail=f"An error occurred during OAuth callback: {e}")

@router.get("/videos", response_model=Dict[str, Any])
async def get_youtube_videos(
    profile_id: int,
    max_results: Optional[int] = Query(10, description="Maximum number of videos to return"),
    current_user: models.ParentUser = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get YouTube videos for a child profile.
    This endpoint automatically refreshes the OAuth token if needed.
    """
    try:
        # Get authenticated YouTube client with token refresh
        youtube = await get_youtube_client(db, profile_id, current_user.id)
        
        # Call the API - get the user's videos from their channel
        # This is just an example - adjust according to your requirements
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like",
            maxResults=max_results
        )
        response = request.execute()
        
        return {
            "videos": response.get("items", []),
            "total_results": response.get("pageInfo", {}).get("totalResults", 0),
            "next_page_token": response.get("nextPageToken")
        }
        
    except googleapiclient.errors.HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=f"YouTube API error: {e.reason}")
    except Exception as e:
        # Log the error details
        print(f"YouTube API Error: {e}")  # Replace with proper logging
        raise HTTPException(status_code=500, detail=f"An error occurred accessing YouTube API: {e}")

@router.get("/channel-info", response_model=Dict[str, Any])
async def get_youtube_channel_info(
    profile_id: int,
    current_user: models.ParentUser = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get YouTube channel information for a child profile.
    This endpoint automatically refreshes the OAuth token if needed.
    """
    try:
        # Get authenticated YouTube client with token refresh
        youtube = await get_youtube_client(db, profile_id, current_user.id)
        
        # Get the channel information (for "mine" - authenticated user)
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()
        
        if not response.get("items"):
            raise HTTPException(status_code=404, detail="No YouTube channel found for this account")
        
        return {
            "channel": response.get("items", [])[0],
        }
        
    except googleapiclient.errors.HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=f"YouTube API error: {e.reason}")
    except Exception as e:
        # Log the error details
        print(f"YouTube API Error: {e}")  # Replace with proper logging
        raise HTTPException(status_code=500, detail=f"An error occurred accessing YouTube API: {e}")