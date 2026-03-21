from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from .deps import get_current_user, check_if_admin
from .utils_jwt import encode_jwt, validate_password, hash_password
from ...core.models.db_helper import get_db
from ...core.models.user import User, UserRole
from ...core.schemas.user import UserOut, UserCreate, Token, UserUpdate
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


# add pagination
@router.get("/users", response_model=dict)
async def read_users(
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    role: str = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await check_if_admin(current_user)

    stmt = select(User)

    if search:
        search_filter = f"%{search}%"
        stmt = stmt.where(User.username.ilike(search_filter))

    if role:
        role_upper = role.upper()
        try:
            role_enum_value = UserRole(role_upper)
            stmt = stmt.where(User.role == role_enum_value)
        except ValueError:
            pass

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return {
        "items": [UserOut.model_validate(u) for u in users],
        "total": total,
    }


@router.get("/users/{user_id}", response_model=UserOut)
async def read_user_by_id(
    user_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_if_admin(current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut.model_validate(user)


@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_if_admin(current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)

    new_password = update_data.get("password")
    if new_password:
        update_data["hashed_password"] = hash_password(new_password)
        del update_data["password"]

    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_if_admin(current_user)

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить самого себя")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()

    return {"message": "Пользователь успешно удален", "id": user_id}
