from fastapi import FastAPI
from contextlib import asynccontextmanager

from .routers import auth, notes 
from . import database
from . import redis_client

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client.get_redis_pool()
    yield
    print("Application is shutting down...")
    await redis_client.close_redis_pool()
    await database.engine.dispose()

app = FastAPI(
    title="SecureNote API",
    description="A secure note-taking API with JWT Auth and Docker.",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware( # to be changed in production level
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to SecureNote API! Visit /docs for documentation."}