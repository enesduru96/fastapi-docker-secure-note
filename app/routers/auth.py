from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from jose import jwt, JWTError

from ..database import get_session
from .. import crud, auth, models
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

# -----------------
# 1. REGISTER
# -----------------
@router.post("/register", response_model=models.UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: models.UserCreate, db: AsyncSession = Depends(get_session)):
    user = await crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )
    
    return await crud.create_user(db, user_data=user_in)


# -----------------
# 2. LOGIN
# -----------------
@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: AsyncSession = Depends(get_session)):
    user = await crud.get_user_by_email(db, email=form_data.username)
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    jti = auth.create_refresh_token_jti()
    expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).replace(tzinfo=None)


    await crud.create_db_refresh_token(
        session=db,
        user_id=user.id,
        jti=jti,
        expires_at=expires_at
    )
    
    refresh_token = auth.create_refresh_token(
        user_id=user.id,
        jti=jti,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return models.Token(access_token=access_token, refresh_token=refresh_token)


# -----------------
# 3. REFRESH ACCESS TOKEN
# -----------------
@router.post("/refresh", response_model=models.Token)
async def refresh_access_token(token_data: models.TokenRefreshRequest, db: AsyncSession = Depends(get_session)):
    try:
        payload = jwt.decode(token_data.refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        jti = payload.get("jti")
        user_id = payload.get("sub")
        
        if not jti or not user_id:
             raise HTTPException(status_code=401, detail="Invalid token payload.")

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    db_token = await crud.get_valid_refresh_token(db, jti=jti)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid, expired, or already used.",
        )


    # --- TOKEN ROTATION LOGIC ---
    
    await crud.mark_refresh_token_as_used(db, token_id=db_token.id)

    user = await db.get(models.User, int(user_id))
    if not user:
         raise HTTPException(status_code=404, detail="User not found.")

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    new_jti = auth.create_refresh_token_jti()
    new_expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).replace(tzinfo=None)

    await crud.create_db_refresh_token(
        session=db,
        user_id=user.id,
        jti=new_jti,
        expires_at=new_expires_at
    )
    
    new_refresh_token = auth.create_refresh_token(
        user_id=user.id,
        jti=new_jti,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return models.Token(access_token=access_token, refresh_token=new_refresh_token)