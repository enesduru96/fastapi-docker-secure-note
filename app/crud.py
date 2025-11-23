from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from .models import User, UserCreate, UserPublic, RefreshToken, Note, NoteCreate, NotePublicWithUsername
from .auth import get_password_hash
from sqlalchemy import or_

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, user_data: UserCreate) -> UserPublic:
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=user_data.is_active,
        is_admin=user_data.is_admin
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return UserPublic.model_validate(db_user)

def create_db_refresh_token(session: Session, user_id: int, jti: str, expires_at: datetime) -> RefreshToken:
    db_token = RefreshToken(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at,
        is_used=False
    )
    
    session.add(db_token)
    session.commit()
    session.refresh(db_token)
    
    return db_token


def get_valid_refresh_token(session: Session, jti: str) -> Optional[RefreshToken]:
    statement = select(RefreshToken).where(
        RefreshToken.jti == jti,
        RefreshToken.is_used == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    )
    return session.exec(statement).first()

def mark_refresh_token_as_used(session: Session, token_id: int):
    token = session.get(RefreshToken, token_id)
    if token:
        token.is_used = True
        session.add(token)
        session.commit()
        

def create_note(session: Session, note_in: NoteCreate, owner_id: int) -> Note:
    db_note = Note(
        title=note_in.title,
        content=note_in.content,
        is_public=note_in.is_public,
        owner_id=owner_id
    )
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note

def get_notes_by_owner(session: Session, owner_id: int) -> list[Note]:
    statement = select(Note).where(Note.owner_id == owner_id)
    return session.exec(statement).all()

def get_public_notes(session: Session, limit: int = 100) -> list[NotePublicWithUsername]:
    statement = select(Note, User.username).join(User).where(Note.is_public == True).limit(limit)
    results = session.exec(statement).all()
    
    output_list = []
    for note, username in results:
        note_data = note.model_dump()
        note_data["owner_username"] = username
        output_list.append(NotePublicWithUsername(**note_data))
        
    return output_list

def search_notes(session: Session, query: str, owner_id: int) -> list[NotePublicWithUsername]:
    statement = (
        select(Note, User.username)
        .join(User)
        .where(
            or_(
                Note.owner_id == owner_id,
                Note.is_public == True
            )
        )
        .where(
            or_(
                Note.title.ilike(f"%{query}%"),
                Note.content.ilike(f"%{query}%")
            )
        )
    )
    
    results = session.exec(statement).all()
    
    output_list = []
    for note, username in results:
        note_data = note.model_dump()
        note_data["owner_username"] = username
        output_list.append(NotePublicWithUsername(**note_data))
        
    return output_list