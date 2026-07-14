from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Configure SQLite threading rules if using SQLite fallback
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def reinitialize_database(new_url: str):
    """Reinitializes the database engine and sessionmaker dynamically at runtime."""
    global engine, AsyncSessionLocal
    settings.DATABASE_URL = new_url
    c_args = {}
    if new_url.startswith("sqlite"):
        c_args["check_same_thread"] = False
    engine = create_async_engine(
        new_url,
        echo=settings.ENVIRONMENT == "development",
        connect_args=c_args,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

