from pydantic import BaseModel
from datetime import datetime


class UserStatistics(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int


class PostStatistics(BaseModel):
    total_posts: int
    published_posts: int
    draft_posts: int
    achieved_posts: int
    average_posts_per_user: float


class DashboardStatistics(BaseModel):
    users: UserStatistics
    posts: PostStatistics
    last_updated: datetime


class UserPersonalStatistics(BaseModel):
    my_total_posts: int
    my_published_posts: int
    my_draft_posts: int
    my_last_post_date: datetime | None
    first_post_date: datetime | None
