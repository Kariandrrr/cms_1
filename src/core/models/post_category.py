from sqlalchemy import Column, ForeignKey, Integer, Table
from .base import Base

post_category = Table(
    "post_category",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categorys.id"), primary_key=True),
)
