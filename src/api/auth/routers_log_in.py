from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.schemas.user import UserOut, UserCreate, Token
from ...core.models.db_helper import get_db
from ...crud.user import get_user_by_username, create_user
from .utils_jwt import encode_jwt, validate_password, hash_password
from ...core.models.user import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = await create_user(db, user_in)
    return UserOut.model_validate(new_user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not validate_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = {
        "sub": user.username,
        "role": user.role,
    }

    token = encode_jwt(payload)
    return Token(access_token=token)


@router.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    return {"message": "Database session injected successfully"}
