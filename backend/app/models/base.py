from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func
from app.config import get_settings

settings = get_settings()

# Lazy engine — created only when first accessed to avoid import-time
# failures when asyncpg is not installed
_engine = None
_async_session = None


def _get_engine():
    from sqlalchemy.ext.asyncio import create_async_engine
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    return _engine


def _get_async_session():
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    global _async_session
    if _async_session is None:
        _async_session = async_sessionmaker(_get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _async_session


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


async def get_db():
    AsyncSession = __import__("sqlalchemy.ext.asyncio", fromlist=["AsyncSession"]).AsyncSession
    session = _get_async_session()()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def init_db():
    async with _get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
