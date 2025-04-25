from typing import Dict, List, Optional
from backend.schemas.oauth_explanation import OAuthExplanation, DataAccessItem
from backend.models.base import PlatformType
from backend.models.user import ChildProfile


def get_platform_explanation(platform: str, child_profile: Optional[ChildProfile] = None) -> OAuthExplanation:
    """
    Generate platform-specific OAuth explanation.
    
    Args:
        platform: Platform name (e.g., 'youtube')
        child_profile: Optional child profile for age-specific information
        
    Returns:
        OAuthExplanation object with platform-specific details
        
    Raises:
        ValueError: If the platform is not supported
    """
    if platform.lower() == PlatformType.YOUTUBE.value:
        return _get_youtube_explanation(child_profile)
    else:
        raise ValueError(f"Unsupported platform: {platform}")


def _get_youtube_explanation(child_profile: Optional[ChildProfile] = None) -> OAuthExplanation:
    """
    Generate YouTube-specific OAuth explanation.
    
    Args:
        child_profile: Optional child profile for age-specific information
        
    Returns:
        OAuthExplanation object with YouTube-specific details
    """
    # Define the data access items
    data_accessed = [
        DataAccessItem(
            data_type="Subscriptions",
            description="The list of YouTube channels your child is subscribed to",
            example="Gaming channels, educational channels, etc.",
            is_required=True
        ),
        DataAccessItem(
            data_type="Channel Information",
            description="Public information about the subscribed channels",
            example="Channel name, description, subscriber count",
            is_required=True
        ),
        DataAccessItem(
            data_type="Recent Video Metadata",
            description="Titles and descriptions of recent public videos from subscribed channels",
            example="Video titles, descriptions (not the video content itself)",
            is_required=True
        )
    ]
    
    # Define the process steps
    process_steps = [
        {
            "step": "1",
            "title": "Parent Initiates",
            "description": "You (the parent) initiate the linking process from your GuardianLens dashboard"
        },
        {
            "step": "2",
            "title": "Child Consent",
            "description": "Your child logs in to their Google account and grants permission to GuardianLens"
        },
        {
            "step": "3",
            "title": "Data Analysis",
            "description": "GuardianLens analyzes the subscribed channels for potential risks"
        },
        {
            "step": "4",
            "title": "Dashboard Results",
            "description": "Results are displayed on your parent dashboard for your review"
        }
    ]
    
    # Define privacy notes
    privacy_notes = [
        "GuardianLens can only see public information about subscribed channels",
        "We cannot see private videos, watch history, or your child's comments",
        "We do not store the actual video content, only metadata (titles, descriptions)",
        "You can unlink the account at any time to revoke access",
        "All data is encrypted and stored securely"
    ]
    
    # Define age-specific information if child profile is provided
    age_specific_info = None
    if child_profile and child_profile.age is not None:
        if child_profile.age < 13:
            age_specific_info = {
                "title": "COPPA Compliance Information",
                "description": "Since your child is under 13, we require verifiable parental consent before linking their YouTube account. This is in compliance with the Children's Online Privacy Protection Act (COPPA).",
                "consent_required": "verifiable_parental_consent"
            }
        else:
            age_specific_info = {
                "title": "Teen Privacy Information",
                "description": "Since your child is 13 or older, they will need to provide their own consent by logging in to their Google account.",
                "consent_required": "child_consent"
            }
    
    return OAuthExplanation(
        platform="youtube",
        title="YouTube Account Linking",
        description="GuardianLens will analyze your child's YouTube subscriptions to identify potentially harmful channels. We only access public information and do not see private videos or watch history.",
        data_accessed=data_accessed,
        process_steps=process_steps,
        privacy_notes=privacy_notes,
        age_specific_info=age_specific_info
    )