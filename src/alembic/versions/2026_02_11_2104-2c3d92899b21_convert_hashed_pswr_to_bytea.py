"""convert hashed_pswr to bytea

Revision ID: 2c3d92899b21
Revises: ac19084939f1
Create Date: 2026-02-11 21:04:58.061527

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2c3d92899b21"
down_revision: Union[str, Sequence[str], None] = "ac19084939f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ALTER COLUMN hashed_password TYPE BYTEA USING "
        "decode(hashed_password, 'escape')"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE users ALTER COLUMN hashed_password TYPE VARCHAR(255) USING "
        "encode(hashed_password, 'escape')"
    )
