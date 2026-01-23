# from typing import List
#
# from sqlalchemy import String, Text
# from sqlalchemy.orm import Mapped, relationship
# from sqlalchemy.orm import mapped_column
#
# from .base import Base
# from .mixins.created_at import CreatedAtMixin
# from .mixins.int_id_pk import IntIdPkMixin
#
#
# class Tag(Base, IntIdPkMixin, CreatedAtMixin):
#
#     name: Mapped[str] = mapped_column(
#         String(50), nullable=True, unique=True, index=True
#     )
#     slug: Mapped[str] = mapped_column(
#         String(80), nullable=True, unique=True, index=True
#     )
#     description: Mapped[str | None] = mapped_column(Text, nullable=True)
#
#     # RELATIONSHIP
#     # posts: Mapped[List["Post"]] = relationship(
#     #     secondary="post_tag", back_populates="tags"
#     # )
#
#     def __repr__(self) -> str:
#         return f"<Tag id={self.id} name={self.name!r} slug={self.slug}>"
