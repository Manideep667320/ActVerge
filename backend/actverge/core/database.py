from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from actverge.core.config import settings
from typing import AsyncGenerator

connect_args = {}
if "asyncpg" in settings.DATABASE_URL:
    connect_args = {"command_timeout": 5, "timeout": 5}
elif "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),
    future=True,
    connect_args=connect_args
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def init_db() -> None:
    try:
        async with engine.begin() as conn:
            from actverge.models import Task, Verdict, EvidencePackage, RecoveryAction, EscalationRequest
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        import logging
        logging.getLogger("actverge.database").warning(f"Database initialization notice: {e}")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
