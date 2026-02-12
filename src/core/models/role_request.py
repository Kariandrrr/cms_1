from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from .base import Base
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column


class RoleRequest(Base):
    id: Mapped = Column(Integer, primary_key=True, index=True)
    user_id: Mapped = Column(Integer, ForeignKey("users.id"))
    requested_role: Mapped = Column(String)
    status: Mapped = Column(
        Enum("pending", "approved", "rejected", name="role_request_status"),
        default="pending",
    )
    created_at: Mapped = Column(DateTime, default=func.now())
    updated_at: Mapped = Column(DateTime, onupdate=func.now())
