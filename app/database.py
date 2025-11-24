from typing import AsyncGenerator 
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from .config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
