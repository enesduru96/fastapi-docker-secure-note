from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database import get_session
from .. import models, crud, auth

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model=models.NotePublic, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: models.NoteCreate,
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    return await crud.create_note(session=db, note_in=note_in, owner_id=current_user.id)


@router.get("/", response_model=List[models.NotePublic])
async def read_notes(
    db: AsyncSession = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    return await crud.get_notes_by_owner(session=db, owner_id=current_user.id)

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
    return await crud.get_public_notes(session=db)