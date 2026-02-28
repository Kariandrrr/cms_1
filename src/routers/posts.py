from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.post_filter import get_posts_with_filters, get_posts_archive
from ..api.auth.deps import get_current_user
from ..core.models.db_helper import get_db
from ..core.models.user import User
from ..core.schemas.post import (
    PostCreate,
    PostUpdate,
    PostOut,
    PostPage,
    PostFilterParams,
)
from ..crud.post import (
    get_post_by_id,
    create_post,
    update_post,
    delete_post,
    get_post_by_slug,
)
from datetime import datetime

router = APIRouter(prefix="/posts", tags=["posts"])


def calculate_pages(total: int, limit: int) -> int:
    return (total + limit - 1) // limit if total > 0 else 0


@router.get("/", response_model=list[PostOut])
# async def list_posts(
#     search: str | None = Query(
#         None, description="Поиск по заголовку/содержимому/анонсу"
#     ),
#     status: str | None = Query(None, description="draft / published"),
#     limit: int = Query(20, ge=1, le=100),
#     offset: int = Query(0, ge=0),
#     db: AsyncSession = Depends(get_db),
#     current_user: User | None = Depends(get_current_active_user),
# ):
#     is_admin_or_editor = current_user and current_user.role in ("ADMIN", "EDITOR")
#
#     posts = await get_posts(
#         db,
#         search=search,
#         status=status,
#         limit=limit,
#         offset=offset,
#         for_admin=is_admin_or_editor,
#     )
#     return posts
async def list_posts(
    filters: PostFilterParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    is_staff = current_user and current_user.role.value in ("ADMIN", "EDITOR")
    if not is_staff:
        filters.status = "published"

    items, total, applied_filters = await get_posts_with_filters(
        db,
        filters=filters,
        current_user_id=current_user.id if current_user else None,
    )
    page_number = (filters.skip // filters.limit) + 1 if filters.limit > 0 else 1

    return PostPage(
        items=items,
        total=total,
        page=page_number,
        pages=calculate_pages(total, filters.limit),
        limit=filters.limit,
    )


@router.get("/my", response_model=PostPage)
async def get_my_posts(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = PostFilterParams(
        author_id=current_user.id,
        limit=limit,
        skip=skip,
        sort_by="created_at",
        sort_order="desc",
    )

    items, total, _ = await get_posts_with_filters(
        db,
        filters=filters,
        current_user_id=current_user.id,
    )

    page_number = (skip // limit) + 1 if limit > 0 else 1

    return PostPage(
        items=items,
        total=total,
        page=page_number,
        pages=calculate_pages(total, limit),
        limit=limit,
    )


@router.get("/archive", response_model=list[PostOut])
async def get_archive(
    year: int | None = Query(None, ge=2000, le=2100),
    month: int | None = Query(None, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
):
    posts = await get_posts_archive(db, year=year, month=month)
    return posts


@router.get("/{post_id}", response_model=PostOut)
@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status != "published":
        if not current_user:
            raise HTTPException(status_code=403, detail="Post is not published")

        if current_user.role.value == "EDITOR" and post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can't view this draft")
        elif current_user.role.value not in ("ADMIN", "EDITOR"):
            raise HTTPException(status_code=403, detail="Access denied")

    return post


@router.patch("/{post_id}/publish", response_model=PostOut)
async def publish_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "published"
    if post.published_at is None:
        post.published_at = datetime.now()

    await db.commit()
    await db.refresh(post)
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
