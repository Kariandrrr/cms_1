from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .deps import get_current_user, check_if_admin
from .utils_jwt import encode_jwt, validate_password
from ...core.models.db_helper import get_db
from ...core.models.user import User
from ...core.schemas.user import UserOut, UserCreate, Token
from ...crud.user import get_user_by_username, create_user

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
        "role": user.role.value,
    }

    token = encode_jwt(payload)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def read_current_user(
    current_user=Depends(get_current_user),
):
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role.value.lower(),
    )


@router.get("/users", response_model=list[UserOut])
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await check_if_admin(current_user)
    result = await db.execute(select(User))
    users = result.scalars().all()

    return users
