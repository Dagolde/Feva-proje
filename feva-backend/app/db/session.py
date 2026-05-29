from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # Connection pool settings for concurrent request handling (Requirement 9.2)
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,       # seconds to wait for a connection before raising
    pool_recycle=1800,     # recycle connections after 30 minutes
    pool_pre_ping=True,    # verify connections before use (handles stale connections)
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
