"""Pytest fixtures - test veritabanı ve API istemcisi."""
import os
import pytest
import asyncio
from pathlib import Path

# Test için ayrı DB kullan (app import edilmeden önce)
_test_db = Path(__file__).parent.parent / "data" / "test_smart_fridge.db"
os.environ["DATABASE_PATH"] = str(_test_db)
os.environ.setdefault("SESSION_SECRET", "test-secret-key-for-pytest")
os.environ["SMTP_ENABLED"] = "false"  # Testlerde dev_token dönsün, e-posta gönderilmesin

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    await init_db()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac
