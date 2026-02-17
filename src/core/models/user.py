from __future__ import annotations

from enum import Enum as PyEnum
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Enum, LargeBinary
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import validates

from .base import Base
from .mixins.created_at import CreatedAtMixin
from .mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from . import Post


class UserRole(PyEnum):
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    USER = "USER"


class User(Base, IntIdPkMixin, CreatedAtMixin):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum"), default=UserRole.USER
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    @validates("role")
    def validate_role(self, key, value):
        if isinstance(value, str):
            if value.upper() == "USER":
                return UserRole.USER
            elif value.upper() == "ADMIN":
                return UserRole.ADMIN
            elif value.upper() == "EDITOR":
                return UserRole.EDITOR
        return value

    posts: Mapped[List["Post"]] = relationship(back_populates="author")
