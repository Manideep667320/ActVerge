import os
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_actverge.db")

from actverge.api.main import app
from actverge.core.database import init_db

@pytest.fixture(autouse=True)
async def initialize_database():
    await init_db()
    yield

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
