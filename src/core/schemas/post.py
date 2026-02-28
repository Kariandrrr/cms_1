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


# FOR FILTRATION
class PostFilterParams(BaseModel):
    search: str | None = Field(default=None, description="Поиск по заголовку и содержимому")

    # columns
    status: str | None = Field(
        default=None, pattern="^(draft|published)$", description="Фильтр по статусу"
    )
    author_id: int | None = Field(default=None, description="Фильтр по ID автора")

    # dates
    published_at: datetime | None = Field(
        default=None, description="Начальная дата публикации (включительно)"
    )
    created_at: datetime | None = Field(
        default=None, description="Начальная дата создания (включительно)"
    )

    # pagination
    skip: int = Field(default=0, ge=0, description="Количество пропускаемых записей")
    limit: int = Field(
        default=10, ge=1, le=100, description="Максимальное количество записей"
    )

    sort_by: str = Field(
        default="created_at",
        pattern="^(created_at|updated_at|published_at|title|status)$",
        description="Поле для сортировки",
    )
    sort_order: str = Field(
        default="desc", pattern="^(asc|desc)$", description="Направление сортировки"
    )

    class Config:
        extra = "forbid"
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class PostListResponse(BaseModel):
    items: list[PostOut | PostPublic]
    total: int
    skip: int
    limit: int
    filters_applied: dict

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class PostPage(BaseModel):
    items: list[PostOut]
    total: int
    page: int
    pages: int
    limit: int
