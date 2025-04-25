from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import Base, engine
from backend.routers import api_router
from backend.celery_worker import celery_app


# Create all tables if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(api_router)


@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {
        "message": "GuardianLens API",
        "version": settings.api_version,
        "docs_url": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "api_version": settings.api_version,
    }


@app.get("/celery-status")
async def celery_status():
    """
    Check Celery worker status.
    """
    try:
        # Ping Celery to check if it's running
        i = celery_app.control.inspect()
        availability = i.ping()
        
        if not availability:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "message": "No Celery workers available"
                }
            )
        
        # Get active tasks
        active_tasks = i.active()
        scheduled_tasks = i.scheduled()
        
        return {
            "status": "ok",
            "workers": list(availability.keys()),
            "active_tasks": active_tasks,
            "scheduled_tasks": scheduled_tasks
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": f"Error connecting to Celery: {str(e)}"
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)