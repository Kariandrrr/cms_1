from datetime import datetime, timedelta

from sqlalchemy import func, and_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.models.post import Post
from ..core.models.user import User


async def get_admin_stat(db: AsyncSession) -> dict:
    now = datetime.now()
    month_ago = now - timedelta(days=30)
    week_ago = now - timedelta(days=7)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    users_stats = await db.execute(
        select(
            func.count(User.id).label("total_users"),
            func.sum(func.case((User.is_active == True, 1), else_=0)).label(
                "active_users"
            ),
            func.sum(func.case((User.created_at >= today_start, 1), else_=0)).label(
                "new_today"
            ),
            func.sum(func.case((User.created_at >= week_ago, 1), else_=0)).label(
                "new_week"
            ),
            func.sum(func.case((User.created_at >= month_ago, 1), else_=0)).label(
                "new_month"
            ),
        )
    )
    users_data = users_stats.first()

    posts_stats = await db.execute(
        select(
            select(
                func.count(Post.id).label("total_posts"),
                func.sum(func.case((Post.status == "published", 1), else_=0)).label(
                    "published"
                ),
                func.sum(func.case((Post.status == "draft", 1), else_=0)).label(
                    "draft"
                ),
                func.sum(func.case((Post.status == "archived", 1), else_=0)).label(
                    "archived"
                ),
            ).where(Post.status != "deleted")
        )
    )
    posts_data = posts_stats.first()

    total_users = users_data.total_users or 1
    total_posts = posts_data.total_posts or 0
    avg_posts = total_posts / total_users if total_users > 0 else 0

    return {
        "users": {
            "total_users": users_data.total_users or 0,
            "active_users": users_data.active_users or 0,
            "new_users_today": users_data.new_today or 0,
            "new_users_this_week": users_data.new_week or 0,
            "new_users_this_month": users_data.new_month or 0,
        },
        "posts": {
            "total_posts": posts_data.total_posts or 0,
            "published_posts": posts_data.published or 0,
            "draft_posts": posts_data.draft or 0,
            "archived_posts": posts_data.archived or 0,
            "total_views": posts_data.total_views or 0,
            "average_posts_per_user": round(avg_posts, 2),
        },
        "last_updated": now,
    }


async def get_user_stats(db: AsyncSession, user_id: int) -> dict:
    user_posts_stats = await db.execute(
        select(
            func.count(Post.id).label("total_posts"),
            func.sum(func.case((Post.status == "published", 1), else_=0)).label(
                "published"
            ),
            func.sum(func.case((Post.status == "draft", 1), else_=0)).label("draft"),
            func.max(Post.created_at).label("last_post_date"),
            func.min(Post.created_at).label("first_post_date"),
        ).where(and_(Post.author_id == user_id, Post.status != "deleted"))
    )
    posts_data = user_posts_stats.first()
    return {
        "my_total_posts": posts_data.total_posts or 0,
        "my_published_posts": posts_data.published or 0,
        "my_draft_posts": posts_data.draft or 0,
        "my_total_views": posts_data.total_views or 0,
        "my_last_post_date": posts_data.last_post_date,
        "my_first_post_date": posts_data.first_post_date,
    }
