"""seed roles de base

Revision ID: bd97e515673d
Revises: db3452db8542
Create Date: 2026-07-21 16:00:09.433656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd97e515673d'
down_revision: Union[str, Sequence[str], None] = 'db3452db8542'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("nom", sa.String),
    )
    op.bulk_insert(
        roles_table,
        [
            {"nom": "student"},
            {"nom": "company"},
            {"nom": "program_manager"},
            {"nom": "admin"},
        ],
    )

def downgrade() -> None:
    op.execute("DELETE FROM roles")