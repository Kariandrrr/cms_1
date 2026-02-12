"""changed role to enum

Revision ID: ac19084939f1
Revises: 5b67c72e7704
Create Date: 2026-02-11 20:59:37.378074

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ac19084939f1"
down_revision: Union[str, Sequence[str], None] = "5b67c72e7704"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создаем Enum тип
    user_role_enum = sa.Enum("ADMIN", "EDITOR", "USER", name="user_role_enum")
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # 2. Изменяем столбец с явным USING для конвертации данных
    op.execute(
        "ALTER TABLE users ALTER COLUMN role TYPE user_role_enum USING "
        "CASE role "
        "WHEN 'admin' THEN 'ADMIN'::user_role_enum "
        "WHEN 'editor' THEN 'EDITOR'::user_role_enum "
        "WHEN 'user' THEN 'USER'::user_role_enum "
        "END"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Возвращаем VARCHAR с обратной конвертацией
    op.execute(
        "ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20) USING "
        "CASE role "
        "WHEN 'ADMIN' THEN 'admin' "
        "WHEN 'EDITOR' THEN 'editor' "
        "WHEN 'USER' THEN 'user' "
        "END"
    )

    # 2. Удаляем Enum тип
    op.execute("DROP TYPE IF EXISTS user_role_enum")
