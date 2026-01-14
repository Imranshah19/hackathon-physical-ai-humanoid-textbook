"""Add user_profile table for personalization

Revision ID: 002_user_profile
Revises: 001_initial
Create Date: 2026-01-08

Source: FR-007, FR-008, FR-009, FR-010, FR-011, FR-012
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "002_user_profile"
down_revision: Union[str, None] = None  # Adjust based on existing migrations
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_profile table and trigger for auto-creation."""

    # Create user_profile table
    op.create_table(
        "user_profile",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "software_background",
            postgresql.ARRAY(sa.String(50)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "hardware_access",
            postgresql.ARRAY(sa.String(50)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("experience_level", sa.String(20), nullable=True),
        sa.Column(
            "profile_completed",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_reminded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Create indexes
    op.create_index("idx_profile_user", "user_profile", ["user_id"], unique=True)
    op.create_index("idx_profile_experience", "user_profile", ["experience_level"])
    op.create_index("idx_profile_completed", "user_profile", ["profile_completed"])

    # Create trigger function to auto-create profile on user registration
    # Note: This assumes better-auth creates a "user" table
    op.execute("""
        CREATE OR REPLACE FUNCTION create_user_profile()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO user_profile (id, user_id, created_at, updated_at)
            VALUES (gen_random_uuid(), NEW.id, NOW(), NOW())
            ON CONFLICT (user_id) DO NOTHING;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger (will be attached to better-auth user table)
    # Note: Run after better-auth migrations create the "user" table
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user') THEN
                CREATE TRIGGER after_user_insert
                AFTER INSERT ON "user"
                FOR EACH ROW
                EXECUTE FUNCTION create_user_profile();
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    """Remove user_profile table and trigger."""

    # Drop trigger if exists
    op.execute("""
        DROP TRIGGER IF EXISTS after_user_insert ON "user";
    """)

    # Drop trigger function
    op.execute("""
        DROP FUNCTION IF EXISTS create_user_profile();
    """)

    # Drop indexes
    op.drop_index("idx_profile_completed", table_name="user_profile")
    op.drop_index("idx_profile_experience", table_name="user_profile")
    op.drop_index("idx_profile_user", table_name="user_profile")

    # Drop table
    op.drop_table("user_profile")
