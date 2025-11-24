from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import or_, func, text
from .models import User, UserCreate, UserPublic, RefreshToken, Note, NoteCreate, NotePublicWithUsername

async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    return result.first()


async def create_user(session: AsyncSession, user_data: UserCreate) -> UserPublic:
    from .auth import get_password_hash
    
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=user_data.is_active,
        is_admin=user_data.is_admin
    )
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    
    return UserPublic.model_validate(db_user)


async def create_db_refresh_token(session: AsyncSession, user_id: int, jti: str, expires_at: datetime) -> RefreshToken:
    db_token = RefreshToken(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at,
        is_used=False
    )
    
    session.add(db_token)
    await session.commit()
    await session.refresh(db_token)
    
    return db_token

async def get_valid_refresh_token(session: AsyncSession, jti: str) -> Optional[RefreshToken]:
    statement = select(RefreshToken).where(
        RefreshToken.jti == jti,
        RefreshToken.is_used == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    )
    result = await session.exec(statement)
    return result.first()


async def mark_refresh_token_as_used(session: AsyncSession, token_id: int):
    token = await session.get(RefreshToken, token_id)
    if token:
        token.is_used = True
        session.add(token)
        await session.commit()
        

async def create_note(session: AsyncSession, note_in: NoteCreate, owner_id: int) -> Note:
    db_note = Note(
        title=note_in.title,
        content=note_in.content,
        is_public=note_in.is_public,
        owner_id=owner_id
    )
    session.add(db_note)
    await session.commit()
    await session.refresh(db_note)
    return db_note

async def get_notes_by_owner(session: AsyncSession, owner_id: int) -> List[Note]:
    statement = select(Note).where(Note.owner_id == owner_id)
    result = await session.exec(statement)
    return result.all()

async def get_public_notes(session: AsyncSession, limit: int = 100) -> List[NotePublicWithUsername]:
    statement = (
        select(Note, User.username)
        .join(User)
        .where(Note.is_public == True)
        .limit(limit)
    )
    
    result = await session.exec(statement)
    results = result.all()
    
    output_list = []
    for note, username in results:
        note_data = note.model_dump()
        note_data["owner_username"] = username
        output_list.append(NotePublicWithUsername(**note_data))
        
    return output_list

async def search_notes(session: AsyncSession, query: str, owner_id: int, offset: int, limit: int) -> list[NotePublicWithUsername]:
    

    search_vector = func.to_tsvector('english', func.coalesce(Note.title, '') + ' ' + func.coalesce(Note.content, ''))     # to prevent NULL
    search_query = func.websearch_to_tsquery('english', query)
    
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
                search_vector.op("@@")(search_query)
            )
            .order_by(func.ts_rank(search_vector, search_query).desc()) # order by relevance
            .offset(offset)
            .limit(limit)
        )
    
    result = await session.exec(statement)
    results = result.all()
    
    output_list = []
    for note, username in results:
        note_data = note.model_dump()
        note_data["owner_username"] = username
        output_list.append(NotePublicWithUsername(**note_data))
        
    return output_list