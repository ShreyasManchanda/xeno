"""add insight_summary to campaigns

Revision ID: 003_insight_summary
Revises: 002c8c58f70a
Create Date: 2026-06-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_insight_summary"
down_revision: Union[str, None] = "002c8c58f70a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("insight_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("campaigns", "insight_summary")
