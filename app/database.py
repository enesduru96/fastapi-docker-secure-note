from sqlmodel import create_engine, SQLModel, Session
from .config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session