from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables

from .routers import auth, notes 

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Application is shutting down...")

app = FastAPI(
    title="SecureNote API",
    description="A secure note-taking API with JWT Auth and Docker.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(notes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to SecureNote API! Visit /docs for documentation."}