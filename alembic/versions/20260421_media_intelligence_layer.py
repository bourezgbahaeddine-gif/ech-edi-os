"""Add Media Intelligence Layer tables.

Revision ID: 20260421_media_intelligence_layer
Revises: 20260317_document_intel_workspace
Create Date: 2026-04-21
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260421_media_intelligence_layer"
down_revision = "20260317_document_intel_workspace"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mil_entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_name", sa.String(length=255), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False, server_default="topic"),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("aliases_json", sa.JSON(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("mention_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trust_context_json", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_name", "entity_type", name="uq_mil_entities_name_type"),
    )
    op.create_index("ix_mil_entities_entity_type", "mil_entities", ["entity_type"])
    op.create_index("ix_mil_entities_normalized_name", "mil_entities", ["normalized_name"])
    op.create_index("ix_mil_entities_last_seen_at", "mil_entities", ["last_seen_at"])
    op.create_index("ix_mil_entity_type_mentions", "mil_entities", ["entity_type", "mention_count"])

    op.create_table(
        "mil_entity_edges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_entity_id", sa.Integer(), nullable=False),
        sa.Column("target_entity_id", sa.Integer(), nullable=False),
        sa.Column("edge_type", sa.String(length=32), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="0"),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["source_entity_id"], ["mil_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["mil_entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_entity_id", "target_entity_id", "edge_type", name="uq_mil_entity_edge"),
    )
    op.create_index("ix_mil_entity_edges_source_entity_id", "mil_entity_edges", ["source_entity_id"])
    op.create_index("ix_mil_entity_edges_target_entity_id", "mil_entity_edges", ["target_entity_id"])
    op.create_index("ix_mil_entity_edges_edge_type", "mil_entity_edges", ["edge_type"])
    op.create_index("ix_mil_entity_edges_last_seen_at", "mil_entity_edges", ["last_seen_at"])
    op.create_index("ix_mil_entity_edge_type_weight", "mil_entity_edges", ["edge_type", "weight"])

    op.create_table(
        "mil_source_trust_scores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_components_json", sa.JSON(), nullable=False),
        sa.Column("last_calculated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id"),
    )
    op.create_index("ix_mil_source_trust_scores_source_id", "mil_source_trust_scores", ["source_id"])
    op.create_index("ix_mil_source_trust_scores_score", "mil_source_trust_scores", ["score"])
    op.create_index("ix_mil_source_trust_scores_last_calculated_at", "mil_source_trust_scores", ["last_calculated_at"])

    op.create_table(
        "mil_clusters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cluster_key", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("dominant_entity", sa.String(length=255), nullable=True),
        sa.Column("article_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_diversity_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("velocity_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("target_surface", sa.String(length=48), nullable=False, server_default="editorial_sidebar"),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cluster_key"),
    )
    op.create_index("ix_mil_clusters_cluster_key", "mil_clusters", ["cluster_key"])
    op.create_index("ix_mil_clusters_dominant_entity", "mil_clusters", ["dominant_entity"])
    op.create_index("ix_mil_clusters_target_surface", "mil_clusters", ["target_surface"])
    op.create_index("ix_mil_clusters_last_seen_at", "mil_clusters", ["last_seen_at"])
    op.create_index("ix_mil_clusters_created_at", "mil_clusters", ["created_at"])
    op.create_index("ix_mil_clusters_updated_at", "mil_clusters", ["updated_at"])
    op.create_index("ix_mil_clusters_velocity_last_seen", "mil_clusters", ["velocity_score", "last_seen_at"])

    op.create_table(
        "mil_cluster_articles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cluster_id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["mil_clusters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cluster_id", "article_id", name="uq_mil_cluster_article"),
    )
    op.create_index("ix_mil_cluster_articles_cluster_id", "mil_cluster_articles", ["cluster_id"])
    op.create_index("ix_mil_cluster_articles_article_id", "mil_cluster_articles", ["article_id"])
    op.create_index("ix_mil_cluster_article_cluster_weight", "mil_cluster_articles", ["cluster_id", "weight"])

    op.create_table(
        "mil_signals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("signal_code", sa.String(length=64), nullable=False),
        sa.Column("signal_type", sa.String(length=64), nullable=False),
        sa.Column("triage_action", sa.String(length=16), nullable=False, server_default="suggest"),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("explanation_json", sa.JSON(), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("target_surface", sa.String(length=48), nullable=False, server_default="editorial_sidebar"),
        sa.Column("related_entity_id", sa.Integer(), nullable=True),
        sa.Column("related_story_id", sa.Integer(), nullable=True),
        sa.Column("related_event_id", sa.Integer(), nullable=True),
        sa.Column("related_cluster_id", sa.Integer(), nullable=True),
        sa.Column("created_from_job_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("dismissed_at", sa.DateTime(), nullable=True),
        sa.Column("dismissed_by", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.ForeignKeyConstraint(["dismissed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["related_cluster_id"], ["mil_clusters.id"]),
        sa.ForeignKeyConstraint(["related_entity_id"], ["mil_entities.id"]),
        sa.ForeignKeyConstraint(["related_event_id"], ["event_memo_items.id"]),
        sa.ForeignKeyConstraint(["related_story_id"], ["stories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("signal_code"),
    )
    op.create_index("ix_mil_signals_signal_code", "mil_signals", ["signal_code"])
    op.create_index("ix_mil_signals_signal_type", "mil_signals", ["signal_type"])
    op.create_index("ix_mil_signals_triage_action", "mil_signals", ["triage_action"])
    op.create_index("ix_mil_signals_priority", "mil_signals", ["priority"])
    op.create_index("ix_mil_signals_target_surface", "mil_signals", ["target_surface"])
    op.create_index("ix_mil_signals_related_entity_id", "mil_signals", ["related_entity_id"])
    op.create_index("ix_mil_signals_related_story_id", "mil_signals", ["related_story_id"])
    op.create_index("ix_mil_signals_related_event_id", "mil_signals", ["related_event_id"])
    op.create_index("ix_mil_signals_related_cluster_id", "mil_signals", ["related_cluster_id"])
    op.create_index("ix_mil_signals_created_from_job_id", "mil_signals", ["created_from_job_id"])
    op.create_index("ix_mil_signals_created_at", "mil_signals", ["created_at"])
    op.create_index("ix_mil_signals_updated_at", "mil_signals", ["updated_at"])
    op.create_index("ix_mil_signals_dismissed_at", "mil_signals", ["dismissed_at"])
    op.create_index("ix_mil_signals_dismissed_by", "mil_signals", ["dismissed_by"])
    op.create_index("ix_mil_signals_status", "mil_signals", ["status"])
    op.create_index("ix_mil_signal_triage_status_created", "mil_signals", ["triage_action", "status", "created_at"])
    op.create_index("ix_mil_signal_surface_status_created", "mil_signals", ["target_surface", "status", "created_at"])

    op.create_table(
        "mil_signal_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("competitor_item_id", sa.Integer(), nullable=True),
        sa.Column("support_kind", sa.String(length=32), nullable=False, server_default="article"),
        sa.Column("support_ref", sa.String(length=255), nullable=True),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"]),
        sa.ForeignKeyConstraint(["competitor_item_id"], ["competitor_xray_items.id"]),
        sa.ForeignKeyConstraint(["signal_id"], ["mil_signals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "signal_id",
            "article_id",
            "source_id",
            "competitor_item_id",
            "support_kind",
            name="uq_mil_signal_source_support",
        ),
    )
    op.create_index("ix_mil_signal_sources_signal_id", "mil_signal_sources", ["signal_id"])
    op.create_index("ix_mil_signal_sources_article_id", "mil_signal_sources", ["article_id"])
    op.create_index("ix_mil_signal_sources_source_id", "mil_signal_sources", ["source_id"])
    op.create_index("ix_mil_signal_sources_competitor_item_id", "mil_signal_sources", ["competitor_item_id"])
    op.create_index("ix_mil_signal_sources_support_kind", "mil_signal_sources", ["support_kind"])
    op.create_index("ix_mil_signal_sources_created_at", "mil_signal_sources", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_mil_signal_sources_created_at", table_name="mil_signal_sources")
    op.drop_index("ix_mil_signal_sources_support_kind", table_name="mil_signal_sources")
    op.drop_index("ix_mil_signal_sources_competitor_item_id", table_name="mil_signal_sources")
    op.drop_index("ix_mil_signal_sources_source_id", table_name="mil_signal_sources")
    op.drop_index("ix_mil_signal_sources_article_id", table_name="mil_signal_sources")
    op.drop_index("ix_mil_signal_sources_signal_id", table_name="mil_signal_sources")
    op.drop_table("mil_signal_sources")

    op.drop_index("ix_mil_signal_surface_status_created", table_name="mil_signals")
    op.drop_index("ix_mil_signal_triage_status_created", table_name="mil_signals")
    op.drop_index("ix_mil_signals_status", table_name="mil_signals")
    op.drop_index("ix_mil_signals_dismissed_by", table_name="mil_signals")
    op.drop_index("ix_mil_signals_dismissed_at", table_name="mil_signals")
    op.drop_index("ix_mil_signals_updated_at", table_name="mil_signals")
    op.drop_index("ix_mil_signals_created_at", table_name="mil_signals")
    op.drop_index("ix_mil_signals_created_from_job_id", table_name="mil_signals")
    op.drop_index("ix_mil_signals_related_cluster_id", table_name="mil_signals")
    op.drop_index("ix_mil_signals_related_event_id", table_name="mil_signals")
    op.drop_index("ix_mil_signals_related_story_id", table_name="mil_signals")
    op.drop_index("ix_mil_signals_related_entity_id", table_name="mil_signals")
    op.drop_index("ix_mil_signals_target_surface", table_name="mil_signals")
    op.drop_index("ix_mil_signals_priority", table_name="mil_signals")
    op.drop_index("ix_mil_signals_triage_action", table_name="mil_signals")
    op.drop_index("ix_mil_signals_signal_type", table_name="mil_signals")
    op.drop_index("ix_mil_signals_signal_code", table_name="mil_signals")
    op.drop_table("mil_signals")

    op.drop_index("ix_mil_cluster_article_cluster_weight", table_name="mil_cluster_articles")
    op.drop_index("ix_mil_cluster_articles_article_id", table_name="mil_cluster_articles")
    op.drop_index("ix_mil_cluster_articles_cluster_id", table_name="mil_cluster_articles")
    op.drop_table("mil_cluster_articles")

    op.drop_index("ix_mil_clusters_velocity_last_seen", table_name="mil_clusters")
    op.drop_index("ix_mil_clusters_updated_at", table_name="mil_clusters")
    op.drop_index("ix_mil_clusters_created_at", table_name="mil_clusters")
    op.drop_index("ix_mil_clusters_last_seen_at", table_name="mil_clusters")
    op.drop_index("ix_mil_clusters_target_surface", table_name="mil_clusters")
    op.drop_index("ix_mil_clusters_dominant_entity", table_name="mil_clusters")
    op.drop_index("ix_mil_clusters_cluster_key", table_name="mil_clusters")
    op.drop_table("mil_clusters")

    op.drop_index("ix_mil_source_trust_scores_last_calculated_at", table_name="mil_source_trust_scores")
    op.drop_index("ix_mil_source_trust_scores_score", table_name="mil_source_trust_scores")
    op.drop_index("ix_mil_source_trust_scores_source_id", table_name="mil_source_trust_scores")
    op.drop_table("mil_source_trust_scores")

    op.drop_index("ix_mil_entity_edge_type_weight", table_name="mil_entity_edges")
    op.drop_index("ix_mil_entity_edges_last_seen_at", table_name="mil_entity_edges")
    op.drop_index("ix_mil_entity_edges_edge_type", table_name="mil_entity_edges")
    op.drop_index("ix_mil_entity_edges_target_entity_id", table_name="mil_entity_edges")
    op.drop_index("ix_mil_entity_edges_source_entity_id", table_name="mil_entity_edges")
    op.drop_table("mil_entity_edges")

    op.drop_index("ix_mil_entity_type_mentions", table_name="mil_entities")
    op.drop_index("ix_mil_entities_last_seen_at", table_name="mil_entities")
    op.drop_index("ix_mil_entities_normalized_name", table_name="mil_entities")
    op.drop_index("ix_mil_entities_entity_type", table_name="mil_entities")
    op.drop_table("mil_entities")
