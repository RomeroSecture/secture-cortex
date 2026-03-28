"""SQLAlchemy async engine and session configuration."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session.

    Endpoints must call `await db.commit()` explicitly after writes.
    Any uncommitted transaction is rolled back on cleanup to return
    a clean connection to the pool.
    """
    session = async_session()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
