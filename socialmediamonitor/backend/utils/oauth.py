import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import jwt
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from backend.config import settings
from backend.models.base import PlatformType


def generate_state_token(child_profile_id: int, platform: str, parent_id: int) -> str:
    """
    Generate a secure state token for OAuth flow.
    
    Args:
        child_profile_id: ID of the child profile
        platform: Platform name (e.g., 'youtube')
        parent_id: ID of the parent user
        
    Returns:
        Encoded JWT token containing state information
    """
    payload = {
        "child_profile_id": child_profile_id,
        "platform": platform,
        "parent_id": parent_id,
        "timestamp": datetime.utcnow().isoformat(),
        "nonce": secrets.token_hex(16)  # Add randomness to prevent CSRF
    }
    
    # Sign the token with the app's secret key
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token


def decode_state_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a state token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Dictionary containing the decoded state information
        
    Raises:
        ValueError: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check if the token is too old (e.g., older than 1 hour)
        token_time = datetime.fromisoformat(payload["timestamp"])
        if datetime.utcnow() - token_time > timedelta(hours=1):
            raise ValueError("State token has expired")
            
        return payload
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid state token: {str(e)}")


def create_youtube_oauth_flow(redirect_uri: Optional[str] = None) -> Flow:
    """
    Create a Google OAuth flow for YouTube.
    
    Args:
        redirect_uri: Optional override for the redirect URI
        
    Returns:
        Google OAuth Flow object
    """
    client_config = {
        "web": {
            "client_id": settings.youtube_client_id,
            "client_secret": settings.youtube_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri or settings.youtube_redirect_uri]
        }
    }
    
    # Create the flow using the client config
    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
        redirect_uri=redirect_uri or settings.youtube_redirect_uri
    )
    
    return flow


def generate_authorization_url(child_profile_id: int, platform: str, parent_id: int) -> Dict[str, str]:
    """
    Generate an authorization URL for the specified platform.
    
    Args:
        child_profile_id: ID of the child profile
        platform: Platform name (e.g., 'youtube')
        parent_id: ID of the parent user
        
    Returns:
        Dictionary containing the authorization URL and state token
        
    Raises:
        ValueError: If the platform is not supported
    """
    # Generate a state token
    state = generate_state_token(child_profile_id, platform, parent_id)
    
    if platform.lower() == PlatformType.YOUTUBE.value:
        # Create the OAuth flow
        flow = create_youtube_oauth_flow()
        
        # Generate the authorization URL
        auth_url, _ = flow.authorization_url(
            access_type="offline",  # Get a refresh token
            include_granted_scopes="true",  # Include any previously granted scopes
            prompt="consent",  # Force the consent screen to appear
            state=state  # Include the state token
        )
        
        return {
            "authorization_url": auth_url,
            "state": state
        }
    else:
        raise ValueError(f"Unsupported platform: {platform}")


def exchange_code_for_tokens(platform: str, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
    """
    Exchange an authorization code for access and refresh tokens.
    
    Args:
        platform: Platform name (e.g., 'youtube')
        code: Authorization code from the OAuth callback
        redirect_uri: Optional override for the redirect URI
        
    Returns:
        Dictionary containing token information
        
    Raises:
        ValueError: If the platform is not supported or token exchange fails
    """
    if platform.lower() == PlatformType.YOUTUBE.value:
        # Create the OAuth flow
        flow = create_youtube_oauth_flow(redirect_uri)
        
        # Exchange the code for tokens
        flow.fetch_token(code=code)
        
        # Get the credentials
        credentials = flow.credentials
        
        # Build the YouTube API client to get the channel info
        youtube = build('youtube', 'v3', credentials=credentials)
        channels_response = youtube.channels().list(part='snippet', mine=True).execute()
        
        # Extract the channel ID and username
        channel_id = None
        channel_title = None
        if channels_response.get('items'):
            channel_id = channels_response['items'][0]['id']
            channel_title = channels_response['items'][0]['snippet']['title']
        
        # Calculate token expiry
        expiry = None
        if credentials.expiry:
            expiry = credentials.expiry
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expiry": expiry,
            "platform_account_id": channel_id,
            "platform_username": channel_title,
            "metadata": {
                "scopes": credentials.scopes,
                "id_token": credentials.id_token
            }
        }
    else:
        raise ValueError(f"Unsupported platform: {platform}")


def refresh_access_token(platform: str, refresh_token: str) -> Dict[str, Any]:
    """
    Refresh an expired access token using a refresh token.
    
    Args:
        platform: Platform name (e.g., 'youtube')
        refresh_token: The refresh token to use
        
    Returns:
        Dictionary containing the new token information
        
    Raises:
        ValueError: If the platform is not supported or token refresh fails
    """
    if platform.lower() == PlatformType.YOUTUBE.value:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        # Create credentials from the refresh token
        credentials = Credentials(
            None,  # No access token
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.youtube_client_id,
            client_secret=settings.youtube_client_secret
        )
        
        # Refresh the credentials
        credentials.refresh(Request())
        
        # Calculate token expiry
        expiry = None
        if credentials.expiry:
            expiry = credentials.expiry
        
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token or refresh_token,  # Keep the old refresh token if a new one isn't provided
            "token_expiry": expiry
        }
    else:
        raise ValueError(f"Unsupported platform: {platform}")