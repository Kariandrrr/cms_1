from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.auth.deps import get_current_active_user, check_if_admin
from ..core.models import User, Post
from ..core.models.db_helper import get_db
from ..core.schemas.statistics import DashboardStatistics, UserPersonalStatistics
from ..crud.statistics import get_user_stats, get_admin_stat

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/dashboard", response_model=DashboardStatistics)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "ADMIN":
        return await get_admin_stat(db)

    full = await get_admin_stat(db)
    safe_data = {
        "users": {
            "total_users": full["users"]["total_users"],
            "active_users": 0,
            "new_users_today": 0,
            "new_users_this_week" "": 0,
            "new_users_this_month": 0,
        },
        "posts": full["posts"],
        "posts_by_day": full["posts_by_day"],
        "last_updated": full["last_updated"],
    }
    return safe_data


@router.get("/my-stats", response_model=UserPersonalStatistics)
async def get_my_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    stats = await get_user_stats(db, current_user.id)
    return stats


@router.get("/admin/full-report")
async def get_admin_full_report(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(check_if_admin),
):
    admin_stats = await get_admin_stat(db)
    result = await db.execute(
        select(
            User.id,
            User.username,
            User.created_at,
            func.count(Post.id).label("user_posts_count"),
            func.sum(case((Post.status == "published", 1), else_=0)).label(
                "user_published"
            ),
        )
        .outerjoin(Post, User.id == Post.author_id)
        .group_by(User.id)
        .order_by(func.count(Post.id).desc())
    )
    users_detail = [
        {
            "id": row.id,
            "username": row.username,
            "total_posts": row.user_posts_count or 0,
            "published_posts": row.user_published or 0,
        }
        for row in result.all()
    ]

    return {
        "general_stats": admin_stats,
        "users_detail": users_detail,
        "generated_at": datetime.now(),
    }
