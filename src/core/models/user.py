from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from . import Post
from .base import Base
from .mixins.created_at import CreatedAtMixin
from .mixins.int_id_pk import IntIdPkMixin


if TYPE_CHECKING:
    from . import Post


class User(Base, IntIdPkMixin, CreatedAtMixin):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[bytes] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")  # admin, editor, user
    is_active: Mapped[bool] = mapped_column(default=True)

    posts: Mapped[List["Post"]] = relationship(back_populates="author")
