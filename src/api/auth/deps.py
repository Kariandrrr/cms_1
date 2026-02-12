from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.schemas.user import UserInDB
from ...crud.user import get_user_by_username
from .utils_jwt import decode_jwt
from ...core.models.db_helper import get_db
from ...core.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = await get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def editor_or_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def user_only(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user
