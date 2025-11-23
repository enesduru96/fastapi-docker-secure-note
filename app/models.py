from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr


# ----------------------
# USER MODELS
# ----------------------
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    notes: List["Note"] = Relationship(back_populates="owner")

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int


# ----------------------
# TOKEN MODELS
# ----------------------
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class TokenRefreshRequest(SQLModel):
    refresh_token: str

class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    jti: str = Field(unique=True) # JWT ID
    expires_at: datetime
    is_used: bool = Field(default=False)


# ----------------------
# NOTE MODELS
# ----------------------
class NoteBase(SQLModel):
    title: str
    content: str
    is_public: bool = Field(default=False)

class Note(NoteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(index=True, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="notes")

class NoteCreate(NoteBase):
    pass

class NotePublic(NoteBase):
    id: int
    owner_id: int

class NotePublicWithUsername(NoteBase):
    id: int
    owner_id: int
    owner_username: str