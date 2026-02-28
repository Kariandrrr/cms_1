from datetime import datetime
from typing import Optional

from sqlalchemy import select, or_, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.models.post import Post
from ..core.schemas.post import PostFilterParams


async def get_posts_with_filters(
    db: AsyncSession,
    *,
    filters: PostFilterParams,
    current_user_id: int | None = None,
):
    stmt = select(Post)

    if filters.search:
        pattern = f"%{filters.search}%"
        stmt = stmt.where(
            or_(
                Post.title.ilike(pattern),
                Post.content.ilike(pattern),
                Post.summary.ilike(pattern),
            )
        )

    if filters.status:
        stmt = stmt.where(Post.status == filters.status)
    else:
        if not current_user_id:
            stmt = stmt.where(Post.status == "published")

    if filters.author_id:
        stmt = stmt.where(Post.author_id == filters.author_id)

    date_conditions = []
    if filters.published_at:
        date_conditions.append(Post.published_at >= filters.published_at)
    if filters.created_at:
        date_conditions.append(Post.created_at >= filters.created_at)
    if date_conditions:
        stmt = stmt.where(and_(*date_conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0

    sort_column = getattr(Post, filters.sort_by, Post.created_at)
    if filters.sort_order == "desc":
        stmt = stmt.order_by(desc(sort_column))
    else:
        stmt = stmt.order_by(sort_column)

    stmt = stmt.offset(filters.skip).limit(filters.limit)

    result = await db.execute(stmt)
    items = result.scalars().all()

    filters_applied = filters.model_dump(
        exclude={"skip", "limit", "sort_by", "sort_order"}
    )
    filters_applied = {k: v for k, v in filters_applied.items() if v is not None}
    return items, total, filters_applied


async def get_published_posts(
    db: AsyncSession,
    *,
    search: str | None = None,
    author_id: int | None = None,
    published_at: datetime | None = None,
    created_at: datetime | None = None,
    sort_by: str = "published_at",
    sort_order: str = "desc",
    limit: int = 10,
    offset: int = 0,
) -> list[Post]:
    stmt = select(Post).where(Post.status == "published")

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Post.title.ilike(pattern),
                Post.content.ilike(pattern),
                Post.summary.ilike(pattern),
            )
        )
        if author_id:
            stmt = stmt.where(Post.author_id == author_id)
        if published_at:
            stmt = stmt.where(Post.published_at >= published_at)
        if created_at:
            stmt = stmt.where(Post.created_at >= created_at)

        sort_column = getattr(Post, sort_by, Post.published_at)
        if sort_order == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(sort_column)
        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


# posts of author
async def get_author_posts(
    db: AsyncSession,
    author_id: int,
    *,
    search: str | None = None,
    status: str | None = None,
    published_at: datetime | None = None,
    created_at: datetime | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 10,
    offset: int = 0,
) -> list[Post]:
    stmt = select(Post).where(Post.author_id == author_id)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Post.title.ilike(pattern),
                Post.content.ilike(pattern),
                Post.summary.ilike(pattern),
            )
        )

    if status:
        stmt = stmt.where(Post.status == status)

    if published_at:
        stmt = stmt.where(Post.published_at >= published_at)
    if created_at:
        stmt = stmt.where(Post.created_at >= created_at)

    sort_column = getattr(Post, sort_by, Post.created_at)
    if sort_order == "desc":
        stmt = stmt.order_by(desc(sort_column))
    else:
        stmt = stmt.order_by(sort_column)

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def count_posts(
    db: AsyncSession,
    *,
    status: str | None = None,
    author_id: int | None = None,
    search: str | None = None,
    published_at: datetime | None = None,
    created_at: datetime | None = None,
) -> int:
    stmt = select(func.count()).select_from(Post)

    if status:
        stmt = stmt.where(Post.status == status)

    if author_id:
        stmt = stmt.where(Post.author_id == author_id)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Post.title.ilike(pattern),
                Post.content.ilike(pattern),
                Post.summary.ilike(pattern),
            )
        )

    if published_at:
        stmt = stmt.where(Post.published_at >= published_at)

    if created_at:
        stmt = stmt.where(Post.created_at >= created_at)

    return await db.scalar(stmt) or 0


async def get_posts_status(
    db: AsyncSession,
    *,
    author_id: int | None = None,
) -> dict:
    total = await count_posts(db)
    published = await count_posts(db, status="published")
    drafts = await count_posts(db, status="draft")

    if author_id:
        author_total = await count_posts(db, author_id=author_id)
        author_published = await count_posts(
            db, author_id=author_id, status="published"
        )
        author_drafts = await count_posts(db, author_id=author_id, status="draft")

        return {
            "total": total,
            "published": published,
            "drafts": drafts,
            "author": {
                "total": author_total,
                "published": author_published,
                "drafts": author_drafts,
            },
        }

    return {
        "total": total,
        "published": published,
        "drafts": drafts,
    }


async def get_posts_archive(
    db: AsyncSession,
    *,
    year: Optional[int] = None,
    month: Optional[int] = None,
    author_id: Optional[int] = None,
) -> list[Post]:

    stmt = select(Post).where(Post.status == "published")

    if year:
        stmt = stmt.where(
            and_(
                func.extract("year", Post.published_at) == year,
            )
        )

        if month:
            stmt = stmt.where(func.extract("month", Post.published_at) == month)

    if author_id:
        stmt = stmt.where(Post.author_id == author_id)

    stmt = stmt.order_by(desc(Post.published_at))

    result = await db.execute(stmt)
    return result.scalars().all()
