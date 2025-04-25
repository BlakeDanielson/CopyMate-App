"""Database utilities for connecting to and working with the database."""
import logging
from typing import AsyncGenerator, Dict, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

# Try both import patterns for compatibility with local and Docker environments
try:
    from backend.config import settings
except ModuleNotFoundError:
    from config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Global variables for database connections
engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker] = None


async def init_db() -> None:
    """Initialize database connection and session factory.
    
    This function should be called during application startup.
    It sets up the database engine and session factory based on configuration.
    """
    global engine, async_session_maker
    
    logger.info("Initializing database connection")
    
    # Get appropriate database URL based on environment
    database_url = settings.get_database_url()
    engine_args: Dict[str, any] = {
        "echo": settings.db_echo,
    }
    
    # Only add pool settings for PostgreSQL, not for SQLite
    # Get URL as string for type checking
    db_url_str = database_url
    if db_url_str.startswith("postgresql"):
        engine_args.update({
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_pre_ping": True,  # Enable connection health checks
            "pool_recycle": 300,    # Recycle connections after 5 minutes
        })
    
    # Create engine with proper configuration
    engine = create_async_engine(database_url, **engine_args)
    
    logger.info(f"Database engine initialized with {database_url[:database_url.find('@') if '@' in database_url else 10]}***")
    
    # Create session factory
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    logger.info(f"Database initialized with {database_url_str}")


async def verify_database_connection() -> bool:
    """Verify database connection by executing a simple query.
    
    Returns:
        bool: True if connection is successful
        
    Raises:
        Exception: If connection fails
    """
    global engine
    
    if not engine:
        await init_db()
        
    try:
        # Try a simple SELECT 1 query to verify connection
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            one = result.scalar()
            if one != 1:
                raise ValueError("Database connection test returned unexpected result")
            
        logger.info("Database connection verified successfully")
        return True
    except Exception as e:
        logger.error(f"Database connection verification failed: {str(e)}")
        raise


async def close_db_connection() -> None:
    """Close database connections.
    
    This function should be called during application shutdown.
    """
    global engine
    
    if engine:
        logger.info("Closing database connections")
        await engine.dispose()
        logger.info("Database connections closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database session.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        ```python
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
        ```
    """
    global async_session_maker
    
    if not async_session_maker:
        await init_db()
        
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error in session: {str(e)}")
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in database session: {str(e)}")
            raise
        finally:
            await session.close()


async def create_database_tables() -> None:
    """Create all database tables if they don't exist.
    
    This is used for testing and development. In production,
    use Alembic migrations instead.
    """
    global engine
    
    if not engine:
        await init_db()
    
    # Try both import patterns for compatibility with local and Docker environments
    try:
        from backend.models.base import Base
        models_package = "backend.models"
    except ModuleNotFoundError:
        from models.base import Base
        models_package = "models"
    
    logger.info("Creating database tables")
    async with engine.begin() as conn:
        # Import all models to ensure they're registered with metadata
        # This is a circular import but only used during app startup
        # pylint: disable=import-outside-toplevel, unused-import
        if models_package == "backend.models":
            from backend.models import base  # noqa
        else:
            from models import base  # noqa
        
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")