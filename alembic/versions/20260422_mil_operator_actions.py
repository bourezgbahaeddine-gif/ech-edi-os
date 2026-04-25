"""Add MIL operator action columns.

Revision ID: 20260422_mil_operator_actions
Revises: 20260421_media_intelligence_layer
Create Date: 2026-04-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260422_mil_operator_actions"
down_revision = "20260421_media_intelligence_layer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("mil_signals", sa.Column("useful_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("mil_signals", sa.Column("useful_last_marked_at", sa.DateTime(), nullable=True))
    op.add_column("mil_signals", sa.Column("useful_last_marked_by", sa.Integer(), nullable=True))
    op.add_column("mil_signals", sa.Column("snoozed_until", sa.DateTime(), nullable=True))
    op.create_index("ix_mil_signals_useful_last_marked_at", "mil_signals", ["useful_last_marked_at"], unique=False)
    op.create_index("ix_mil_signals_snoozed_until", "mil_signals", ["snoozed_until"], unique=False)
    op.create_foreign_key(
        "fk_mil_signals_useful_last_marked_by_users",
        "mil_signals",
        "users",
        ["useful_last_marked_by"],
        ["id"],
    )
    op.alter_column("mil_signals", "useful_count", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_mil_signals_useful_last_marked_by_users", "mil_signals", type_="foreignkey")
    op.drop_index("ix_mil_signals_snoozed_until", table_name="mil_signals")
    op.drop_index("ix_mil_signals_useful_last_marked_at", table_name="mil_signals")
    op.drop_column("mil_signals", "snoozed_until")
    op.drop_column("mil_signals", "useful_last_marked_by")
    op.drop_column("mil_signals", "useful_last_marked_at")
    op.drop_column("mil_signals", "useful_count")
