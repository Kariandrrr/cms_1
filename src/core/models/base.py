import sys

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.orm import Mapped, mapped_column

# Проверяем, запущен ли скрипт через Alembic
is_alembic_running = "alembic" in sys.modules or "alembic" in sys.argv[0]

if is_alembic_running:
    # Для Alembic используем абсолютные импорты
    from core.config import settings
    from utils import camel_case_to_snake_case
else:
    # Для обычного запуска сервера используем относительные импорты
    from ..config import settings
    from ...utils import camel_case_to_snake_case


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)

    @declared_attr
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    id: Mapped[int] = mapped_column(primary_key=True)
