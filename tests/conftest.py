import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db import Base, get_session
from main import app

# Override the dependency
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def initialized_app(monkeypatch):
    # Point at in-memory SQLite
    monkeypatch.setenv("TESTING", "true")

    # Create engine & sessionmaker for tests
    from app.db import DATABASE_URL
    engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    TestingSession = async_sessionmaker(engine, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Override FastAPI’s get_session to use TestingSession
    async def _get_test_session():
        async with TestingSession() as session:
            yield session

    app.dependency_overrides[get_session] = _get_test_session
    return app
