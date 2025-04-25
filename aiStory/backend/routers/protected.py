"""Protected endpoints demonstrating role-based authorization."""
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User
from backend.utils.auth import get_current_user, require_role, require_any_role
from backend.utils.database import get_db


# Create router
router = APIRouter(
    prefix="/protected",
    tags=["protected"],
)


@router.get("/auth-only")
async def auth_only_endpoint(current_user: User = Depends(get_current_user)):
    """Endpoint that requires authentication but no specific role.
    
    Args:
        current_user: Authenticated user from token
        
    Returns:
        dict: User info and message
    """
    return {
        "status": "success",
        "message": "You have access to this authenticated endpoint",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        }
    }


@router.get("/admin-only")
async def admin_only_endpoint(current_user: User = Depends(require_role("admin"))):
    """Endpoint that requires the admin role.
    
    Args:
        current_user: Admin user from token
        
    Returns:
        dict: Admin-specific data
    """
    return {
        "status": "success",
        "message": "You have access to this admin-only endpoint",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        },
        "admin_data": {
            "total_users": 42,  # Example data
            "system_status": "healthy"
        }
    }


@router.get("/moderator-or-admin")
async def mod_or_admin_endpoint(
    current_user: User = Depends(require_any_role(["admin", "moderator"]))
):
    """Endpoint that requires either moderator or admin role.
    
    Args:
        current_user: User with appropriate role from token
        
    Returns:
        dict: Moderator/admin data
    """
    return {
        "status": "success",
        "message": f"You have access to this endpoint with role: {current_user.role}",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        },
        "moderation_data": {
            "pending_approvals": 7,  # Example data
            "reported_content": 3
        }
    }


@router.get("/user-only")
async def user_only_endpoint(current_user: User = Depends(require_role("user"))):
    """Endpoint that requires the user role.
    
    Args:
        current_user: Regular user from token
        
    Returns:
        dict: User-specific data
    """
    return {
        "status": "success",
        "message": "You have access to this user-only endpoint",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        },
        "user_data": {
            "preferences": {"theme": "dark", "notifications": True},
            "recent_activity": ["viewed story", "created character"]
        }
    }