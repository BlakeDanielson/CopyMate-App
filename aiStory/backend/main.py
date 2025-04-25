"""Main module for the AI Story Creator backend FastAPI application."""
import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Import based on whether we're running locally or in Docker
try:
    # Try local imports first
    from backend.config import settings
    from backend.routers import register_all_routers
    from backend.utils.database import create_database_tables, init_db, verify_database_connection, close_db_connection
except ModuleNotFoundError:
    # If local imports fail, try direct imports for Docker environment
    from config import settings
    from routers import register_all_routers
    from utils.database import create_database_tables, init_db, verify_database_connection, close_db_connection

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version=settings.version,
    description="Backend API for AI Story Creator",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register all routers with prefix
register_all_routers(app, prefix=settings.api_prefix)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Custom exception handler for validation errors."""
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        }
        errors.append(error_detail)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for any unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.debug else "Please contact support"
        }
    )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next) -> Any:
    """Middleware to log all requests and responses."""
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize resources when the application starts."""
    logger.info("Starting application...")
    try:
        # Initialize database connection
        logger.info("Initializing database connection")
        await init_db()
        
        # Verify database connection is working
        logger.info("Verifying database connection")
        await verify_database_connection()
        
        # Create database tables (for development)
        if settings.debug:
            logger.info("Running in debug mode - creating database tables")
            await create_database_tables()
        
        # Initialize additional resources here
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the application shuts down."""
    logger.info("Shutting down application...")
    try:
        # Close database connections
        logger.info("Closing database connections")
        await close_db_connection()
        
        # Add other cleanup tasks here
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        # Don't re-raise here to ensure graceful shutdown


if __name__ == "__main__":
    """Run the application directly with Uvicorn if executed as a script."""
    import uvicorn
    
    # Determine the module path based on environment
    try:
        # Try importing as a module to check if we're in a package
        import backend
        module_path = "backend.main:app"
    except ImportError:
        # We're not in a package, use direct module name
        module_path = "main:app"
        
    uvicorn.run(
        module_path,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )