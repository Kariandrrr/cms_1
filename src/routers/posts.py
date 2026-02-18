from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.auth.deps import get_current_user, get_current_active_user
from ..core.models.db_helper import get_db
from ..core.models.user import User
from ..core.schemas.post import PostCreate, PostUpdate, PostOut
from ..crud.post import (
    get_post_by_id,
    get_posts,
    create_post,
    update_post,
    delete_post,
    get_post_by_slug,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostOut])
async def list_posts(
    search: str | None = Query(
        None, description="Поиск по заголовку/содержимому/анонсу"
    ),
    status: str | None = Query(None, description="draft / published"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_active_user),
):
    is_admin_or_editor = current_user and current_user.role in ("ADMIN", "EDITOR")

    posts = await get_posts(
        db,
        search=search,
        status=status,
        limit=limit,
        offset=offset,
        for_admin=is_admin_or_editor,
    )
    return posts


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if current_user.role.value == "EDITOR":
        if post.author_id != current_user.id and post.status != "published":
            raise HTTPException(status_code=403, detail="You can't edit this post")
    return post


@router.get("/slug/{slug}", response_model=PostOut)
async def get_post_by_slug_public(slug: str, db: AsyncSession = Depends(get_db)):
    post = await get_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.status != "published":
        raise HTTPException(status_code=403, detail="Post is not published")
    return post


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.value not in ("ADMIN", "EDITOR"):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    created = await create_post(db, post_in, author=current_user)
    return created


@router.put("/{post_id}", response_model=PostOut)
async def update_existing_post(
    post_id: int,
    post_update: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if current_user.role.value == "EDITOR" and post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can't edit this post")

    updated = await update_post(db, post, post_update, current_user)
    return updated


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await delete_post(db, post, current_user)
    return None
