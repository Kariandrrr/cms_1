from typing import List, TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from .base import Base
from .mixins.created_at import CreatedAtMixin
from .mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from . import Post


class Category(Base, IntIdPkMixin, CreatedAtMixin):
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


posts: Mapped[List["Post"]] = relationship(
    secondary="post_category", back_populates="categories"
)
