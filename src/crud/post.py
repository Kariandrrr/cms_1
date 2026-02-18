from datetime import datetime
from typing import List

from fastapi import HTTPException
from slugify import slugify
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.models.post import Post
from ..core.models.user import User
from ..core.schemas.post import PostCreate, PostUpdate


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none()


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    result = await db.execute(select(Post).where(Post.slug == slug))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


# for admin
async def get_posts(
    db: AsyncSession,
    *,
    search: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    for_admin: bool = False,
) -> List[Post]:
    stmt = select(Post).order_by(Post.updated_at.desc())
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Post.title.ilike(pattern),
                Post.content.ilike(pattern),
                Post.summary.ilike(pattern),
            )
        )
    if status and not for_admin:
        stmt = stmt.where(Post.status == status)
    elif not for_admin:
        stmt = stmt.where(Post.status == "published")
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_post(db: AsyncSession, post_in: PostCreate, author: User) -> Post:
    base_slug = slugify(post_in.title)
    slug = base_slug
    counter = 1

    while True:
        existing = await get_post_by_slug(db, slug)
        if not existing:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    published_at = datetime.now() if post_in.status == "published" else None
    db_post = Post(
        title=post_in.title,
        slug=slug,
        content=post_in.content,
        summary=post_in.summary,
        status=post_in.status,
        published_at=published_at,
        author_id=author.id,
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post


async def update_post(
    db: AsyncSession, post: Post, post_update: PostUpdate, current_user: User
) -> Post:
    if current_user.role.value == "EDITOR" and post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own posts")
    elif current_user.role.value not in ("ADMIN", "EDITOR"):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to edit posts"
        )

    update_data = post_update.model_dump(exclude_unset=True)

    if "title" in update_data and update_data["title"] != post.title:
        new_base_slug = slugify(update_data["title"])

        slug = new_base_slug
        counter = 1
        while True:
            existing = await get_post_by_slug(db, slug)
            if not existing or existing.id == post.id:
                break
            slug = f"{new_base_slug}-{counter}"
            counter += 1

        update_data["slug"] = slug

    if update_data.get("status") == "published" and not post.published_at:
        update_data["published_at"] = datetime.now()

    if update_data.get("status") != "published" and post.published_at:
        update_data["published_at"] = None

    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)

    return post


async def delete_post(db: AsyncSession, post: Post, current_user: User) -> None:
    if current_user.role.value == "EDITOR" and post.author_id != current_user.id:
        raise PermissionError("Редактор может удалять только свои посты")

    await db.delete(post)
    await db.commit()
