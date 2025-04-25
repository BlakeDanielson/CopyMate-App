import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from backend.config import settings
from backend.models.base import PlatformType


def revoke_oauth_token(platform: str, token: str, token_type: str = "access_token") -> Dict[str, Any]:
    """
    Revoke an OAuth token for a specific platform.
    
    Args:
        platform: Platform name (e.g., 'youtube')
        token: The token to revoke
        token_type: The type of token ('access_token' or 'refresh_token')
        
    Returns:
        Dictionary containing the result of the revocation
        
    Raises:
        ValueError: If the platform is not supported or token revocation fails
    """
    if platform.lower() == PlatformType.YOUTUBE.value:
        return _revoke_google_token(token, token_type)
    else:
        raise ValueError(f"Unsupported platform: {platform}")


def _revoke_google_token(token: str, token_type: str = "access_token") -> Dict[str, Any]:
    """
    Revoke a Google OAuth token.
    
    Args:
        token: The token to revoke
        token_type: The type of token ('access_token' or 'refresh_token')
        
    Returns:
        Dictionary containing the result of the revocation
        
    Raises:
        ValueError: If token revocation fails
    """
    # Google's token revocation endpoint
    revocation_url = "https://oauth2.googleapis.com/revoke"
    
    # Prepare the request
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = urlencode({"token": token, "token_type_hint": token_type})
    
    # Send the request
    response = requests.post(revocation_url, headers=headers, data=data)
    
    # Check the response
    if response.status_code == 200:
        return {"status": "success", "message": "Token successfully revoked"}
    else:
        try:
            error_data = response.json()
            error_message = error_data.get("error_description", error_data.get("error", "Unknown error"))
        except:
            error_message = f"Failed to revoke token: HTTP {response.status_code}"
        
        raise ValueError(error_message)