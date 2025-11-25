import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_session
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app import redis_client

engine_test = create_async_engine(
    settings.DATABASE_URL, 
    echo=False,
    poolclass=NullPool 
)

@pytest.fixture(scope="function")
async def session():
    connection = await engine_test.connect()
    
    transaction = await connection.begin()

    async_session = sessionmaker(
        bind=connection, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
    
    await transaction.rollback()
    
    await connection.close()

@pytest.fixture(scope="function")
async def client(session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()
    
@pytest.fixture(autouse=True)
async def clear_redis():
    redis = redis_client.get_redis_pool()
    await redis.flushdb()
    yield
    await redis_client.close_redis_pool()