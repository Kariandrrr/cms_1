from datetime import datetime

from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title: str = Field(
        ..., min_length=3, max_length=200, description="Заголовок статьи"
    )
    content: str = Field(
        ..., min_length=10, description="Основной HTML/Markdown контент"
    )
    summary: str | None = Field(None, max_length=500, description="Краткое описание")
    status: str = Field(
        default="draft",
        pattern="^(draft|published)$",
        description="Статус: draft или published",
    )


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200)
    content: str | None = Field(None, min_length=10)
    summary: str | None = Field(None, max_length=500)
    status: str | None = Field(None, pattern="^(draft|published)$")

    class Config:
        extra = "forbid"


class PostOut(PostBase):
    id: int
    slug: str
    author_id: int
    author_username: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class PostPublic(PostOut):
    author_username: str | None = None
