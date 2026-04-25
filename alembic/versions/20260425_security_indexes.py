"""Add missing security/readiness indexes.

Revision ID: 20260425_security_indexes
Revises: 20260422_expand_article_original_url
Create Date: 2026-04-25 12:15:00
"""

from alembic import op


revision = "20260425_security_indexes"
down_revision = "20260422_expand_article_original_url"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_articles_source_id ON articles (source_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_editorial_drafts_parent_draft_id "
        "ON editorial_drafts (parent_draft_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_social_tasks_created_by_user_id "
        "ON social_tasks (created_by_user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_social_posts_created_by_user_id "
        "ON social_posts (created_by_user_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_social_posts_created_by_user_id")
    op.execute("DROP INDEX IF EXISTS ix_social_tasks_created_by_user_id")
    op.execute("DROP INDEX IF EXISTS ix_editorial_drafts_parent_draft_id")
    op.execute("DROP INDEX IF EXISTS ix_articles_source_id")
