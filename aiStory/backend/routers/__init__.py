"""API route definitions for the application.

This module exports router instances from all API modules
to enable centralized router registration in the main app.
"""
from typing import List

from fastapi import APIRouter

# Import all router modules here
# Using import patterns that work in both local and Docker environments
try:
    # Try local imports first - needed for running as package
    from backend.routers import auth, health, photos, protected, stories
except ModuleNotFoundError:
    # If local imports fail, try direct imports for Docker environment
    from routers import auth, health, photos, protected, stories


def get_all_routers() -> List[APIRouter]:
    """
    Returns a list of all router instances to be included in the main app.
    
    As new router modules are added, they should be imported above and
    their router instances added to this list.
    
    Returns:
        List[APIRouter]: List of all router instances
    """
    return [
        health.router,
        auth.router,
        protected.router,
        photos.router,
        stories.router,
        # Add additional routers here as they are created
        # etc.
    ]


def register_all_routers(app, prefix: str = "") -> None:
    """
    Helper function to register all routers with the main application.
    
    Args:
        app: The FastAPI application instance
        prefix (str, optional): Global API prefix to apply to all routes.
    """
    for router in get_all_routers():
        app.include_router(router, prefix=prefix)