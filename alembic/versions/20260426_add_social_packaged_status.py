"""Add social_packaged to newsstatus enum.

Revision ID: 20260426_add_social_packaged_status
Revises: 20260426_add_newsroom_roles
Create Date: 2026-04-26 15:10:00
"""

from alembic import op


revision = "20260426_add_social_packaged_status"
down_revision = "20260426_add_newsroom_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE newsstatus ADD VALUE IF NOT EXISTS 'social_packaged'")


def downgrade() -> None:
    # PostgreSQL enum value removal is intentionally skipped to avoid destructive casts.
    pass
