"""Initial schema with all RAG chatbot tables.

Revision ID: 001
Revises:
Create Date: 2026-01-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # UserSession table
    op.create_table(
        "user_sessions",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("session_token", sa.String(64), unique=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "last_active_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("preferences", JSONB, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("idx_session_token", "user_sessions", ["session_token"])
    op.create_index("idx_session_last_active", "user_sessions", ["last_active_at"])

    # Conversation table
    op.create_table(
        "conversations",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("user_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("page_url", sa.String(512), nullable=False),
        sa.Column("page_title", sa.String(256)),
        sa.Column("selected_text", sa.Text),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("idx_conversation_session", "conversations", ["session_id"])
    op.create_index(
        "idx_conversation_created", "conversations", ["created_at"], postgresql_ops={"created_at": "DESC"}
    )

    # Message table
    op.create_table(
        "messages",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "conversation_id",
            UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("citations", JSONB, server_default=sa.text("'[]'::jsonb")),
        sa.Column("tokens_used", sa.Integer),
        sa.Column("latency_ms", sa.Integer),
        sa.Column("feedback", sa.String(16)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="check_role"),
        sa.CheckConstraint(
            "feedback IS NULL OR feedback IN ('up', 'down')", name="check_feedback"
        ),
    )
    op.create_index("idx_message_conversation", "messages", ["conversation_id"])
    op.create_index("idx_message_created", "messages", ["created_at"])

    # DocumentChunk table
    op.create_table(
        "document_chunks",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("source_url", sa.String(512), nullable=False),
        sa.Column("section_title", sa.String(256)),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("source_url", "chunk_index", name="uq_source_chunk"),
    )
    op.create_index("idx_chunk_source", "document_chunks", ["source_url"])
    op.create_index("idx_chunk_hash", "document_chunks", ["content_hash"])
    op.create_index("idx_chunk_updated", "document_chunks", ["updated_at"])

    # AnalyticsEvent table
    op.create_table(
        "analytics_events",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("page_url", sa.String(512)),
        sa.Column("query_hash", sa.String(64)),
        sa.Column("response_quality", sa.String(16)),
        sa.Column("latency_ms", sa.Integer),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("idx_analytics_type", "analytics_events", ["event_type"])
    op.create_index("idx_analytics_created", "analytics_events", ["created_at"])


def downgrade() -> None:
    op.drop_table("analytics_events")
    op.drop_table("document_chunks")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("user_sessions")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
