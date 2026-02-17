from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from .base import Base
from .mixins.created_at import CreatedAtMixin
from .mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from . import User
    from . import Category
    from . import Tag


class Post(Base, IntIdPkMixin, CreatedAtMixin):
    title: Mapped[str] = mapped_column(String(200), index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # RELATIONSHIP
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="posts")
    categories: Mapped[List["Category"]] = relationship(
        secondary="post_category",
        back_populates="posts",
        passive_deletes=True,
    )
    tags: Mapped[List["Tag"]] = relationship(
        secondary="post_tag",
        back_populates="posts",
        passive_deletes=True,
    )
