import json
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from .. import models, crud, auth, redis_client

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model=models.NotePublic, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: models.NoteCreate,
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_note = await crud.create_note(session=db, note_in=note_in, owner_id=current_user.id)
    
    redis = redis_client.get_redis_pool()
    user_cache_key = f"user_notes:{current_user.id}"
    await redis.delete(user_cache_key)
    
    if note_in.is_public:
        await redis.delete("public_notes_feed")
        
    return new_note


@router.get("/", response_model=List[models.NotePublic])
async def read_notes(
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    redis = redis_client.get_redis_pool()
    CACHE_KEY = f"user_notes:{current_user.id}"
    
    cached_data = await redis.get(CACHE_KEY)
    if cached_data:
        print(f"My Notes - Cache Found")
        return json.loads(cached_data)
    

    print(f"My Notes - Cache Not Found")
    notes = await crud.get_notes_by_owner(session=db, owner_id=current_user.id)
    notes_json = [note.model_dump(mode='json') for note in notes]
    await redis.set(CACHE_KEY, json.dumps(notes_json), ex=60)
    
    return notes


@router.get("/search", response_model=List[models.NotePublicWithUsername])
async def search_notes(
    q: str,
    offset: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    MAX_INTERNAL_LIMIT = 100
    
    if limit > MAX_INTERNAL_LIMIT:
        limit = MAX_INTERNAL_LIMIT

    return await crud.search_notes(
        session=db, 
        query=q, 
        owner_id=current_user.id, 
        offset=offset, 
        limit=limit
    )


@router.get("/public", response_model=List[models.NotePublicWithUsername])
async def read_public_notes(
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    redis = redis_client.get_redis_pool()
    CACHE_KEY = "public_notes_feed"
    
    cached_data = await redis.get(CACHE_KEY)
    if cached_data:
        print("Public Feed - Cache Found")
        return json.loads(cached_data)
    
    print("Public Feed - Cache not Found")
    notes = await crud.get_public_notes(session=db)
    notes_json = [note.model_dump(mode='json') for note in notes]
    await redis.set(CACHE_KEY, json.dumps(notes_json), ex=60)
    
    return notes