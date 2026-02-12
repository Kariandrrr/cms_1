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
    try:
        payload = decode_jwt(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    user = await get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
