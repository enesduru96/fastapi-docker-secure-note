import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_session
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine_test = create_async_engine(settings.DATABASE_URL, echo=False)

@pytest.fixture
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

@pytest.fixture
async def client(session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()