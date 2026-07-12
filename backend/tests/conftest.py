import pytest
import os
import httpx
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.dependencies import get_db
from app.models.base import Base

# Setup async file-based SQLite database for testing to ensure multiple connections see the same tables
TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Apply the dependency override globally to the app to bypass standard PostgreSQL
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture(autouse=True)
async def setup_db():
    """Initializes in-memory database schema tables before each test run and cleanses them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Close engine and delete test.db file
    await test_engine.dispose()
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except Exception:  # pylint: disable=broad-exception-caught
            pass

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
