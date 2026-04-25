"""Expand articles.original_url to TEXT.

Revision ID: 20260422_expand_article_original_url
Revises: 20260422_mil_operator_actions
Create Date: 2026-04-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260422_expand_article_original_url"
down_revision = "20260422_mil_operator_actions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "articles",
        "original_url",
        existing_type=sa.String(length=2048),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "articles",
        "original_url",
        existing_type=sa.Text(),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )
