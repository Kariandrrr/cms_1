from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.auth.utils_jwt import hash_password
from ..core.models.user import User
from ..core.schemas.user import UserCreate


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed = hash_password(user_in.password)
    db_user = User(
        username=user_in.username,
        hashed_password=hashed,
        role=user_in.role,
        is_active=True,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
