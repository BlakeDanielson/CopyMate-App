"""Health check endpoints for API status monitoring."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Try both import patterns for compatibility with local and Docker environments
try:
    from backend.utils.database import get_db
except ModuleNotFoundError:
    from utils.database import get_db

# Create router
router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
async def health_check():
    """Simple health check endpoint to verify API is running.
    
    Returns:
        dict: Status information
    """
    return {"status": "ok"}


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check that also verifies database connectivity.
    
    Args:
        db: Database session
        
    Returns:
        dict: Detailed status information including database connection status
    """
    db_status = "ok"
    
    try:
        # Simple query to verify database connection
        await db.execute("SELECT 1")
    except Exception as exc:
        db_status = f"error: {str(exc)}"
    
    return {
        "status": "ok",
        "services": {
            "api": "ok",
            "database": db_status,
        },
        "info": {
            "version": "0.1.0",
        }
    }