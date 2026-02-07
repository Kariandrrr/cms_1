from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Literal


class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["admin", "editor", "user"] = "user"


# только для ответа клиенту
class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# для внутреннего использования
class UserInDB(BaseModel):
    id: int | None = None
    username: str
    hashed_password: bytes
    role: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
