from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

# Create async engine instance
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Create sessionmaker
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False # Good default for FastAPI background tasks
)

# Dependency to get DB session (can be moved to api deps later)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session