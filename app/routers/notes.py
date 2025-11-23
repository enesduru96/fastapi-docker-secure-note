from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from ..database import get_session
from .. import models, crud, auth

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model=models.NotePublic, status_code=status.HTTP_201_CREATED)
def create_note(
    note_in: models.NoteCreate,
    db: Session = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_note(session=db, note_in=note_in, owner_id=current_user.id)


@router.get("/", response_model=List[models.NotePublic])
def read_notes(
    db: Session = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_notes_by_owner(session=db, owner_id=current_user.id)

@router.get("/search", response_model=List[models.NotePublicWithUsername])
def search_notes(
    q: str,
    db: Session = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.search_notes(session=db, query=q, owner_id=current_user.id)

@router.get("/public", response_model=List[models.NotePublicWithUsername])
def read_public_notes(
    db: Session = Depends(get_session),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_public_notes(session=db)