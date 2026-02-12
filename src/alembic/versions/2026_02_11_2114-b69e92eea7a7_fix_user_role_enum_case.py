"""fix user role enum case

Revision ID: b69e92eea7a7
Revises: 2c3d92899b21
Create Date: 2026-02-11 21:14:10.111337

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b69e92eea7a7"
down_revision: Union[str, Sequence[str], None] = "2c3d92899b21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Удаляем зависимость от enum
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20)")

    # 2. Удаляем старый enum
    op.execute("DROP TYPE IF EXISTS user_role_enum CASCADE")

    # 3. Создаём новый enum с правильными значениями
    op.execute("CREATE TYPE user_role_enum AS ENUM ('ADMIN', 'EDITOR', 'USER')")

    # 4. Конвертируем существующие данные (если есть)
    op.execute(
        """
               UPDATE users
               SET role = CASE role::text
                              WHEN 'ADMIN' THEN 'ADMIN'
                              WHEN 'EDITOR' THEN 'EDITOR'
                              WHEN 'USER' THEN 'USER'
                              WHEN 'admin' THEN 'ADMIN'
                              WHEN 'editor' THEN 'EDITOR'
                              WHEN 'user' THEN 'USER'
                              ELSE 'USER'
                   END
               """
    )

    # 5. Меняем тип обратно на enum с USING
    op.execute(
        """
               ALTER TABLE users
                   ALTER COLUMN role TYPE user_role_enum
                       USING role::text::user_role_enum
               """
    )


def downgrade() -> None:
    # Откат - возвращаем VARCHAR
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20)")
    op.execute("DROP TYPE IF EXISTS user_role_enum")
