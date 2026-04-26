"""Add presenter and show_host roles to user_role enum.

Revision ID: 20260426_add_newsroom_roles
Revises: 20260425_security_indexes
Create Date: 2026-04-26 12:10:00
"""

from alembic import op


revision = "20260426_add_newsroom_roles"
down_revision = "20260425_security_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'presenter'")
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'show_host'")


def downgrade() -> None:
    # PostgreSQL enum value removal is intentionally skipped to avoid destructive casts.
    pass
