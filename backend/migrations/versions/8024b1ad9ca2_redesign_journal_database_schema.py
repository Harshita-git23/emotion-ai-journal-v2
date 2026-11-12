
"""Safely redesign the journal database schema.

Revision ID: 8024b1ad9ca2
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "8024b1ad9ca2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create new tables first.

    op.create_table(
        "pattern_insights",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pattern_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("date_range_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_range_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_feedback", sa.String(20), nullable=False),
        sa.Column("algorithm_version", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "user_feedback IN ('unreviewed', 'confirmed', 'rejected')",
            name="valid_pattern_feedback",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_pattern_insights_user_id",
        "pattern_insights",
        ["user_id"],
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("user_id", "name", name="unique_user_tag"),
    )
    op.create_index("ix_tags_user_id", "tags", ["user_id"])

    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("experience_id", sa.Integer(), nullable=False),
        sa.Column("model_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "model_type IN ('text', 'speech')",
            name="valid_analysis_model_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'skipped')",
            name="valid_analysis_status",
        ),
        sa.ForeignKeyConstraint(
            ["experience_id"], ["experiences.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_analysis_runs_experience_id",
        "analysis_runs",
        ["experience_id"],
    )

    op.create_table(
        "experience_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("experience_id", sa.Integer(), nullable=False),
        sa.Column("action_name", sa.String(150), nullable=False),
        sa.Column("outcome", sa.String(30), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome_recorded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "outcome IN ('helped', 'a_bit', 'did_not_help') OR outcome IS NULL",
            name="valid_action_outcome",
        ),
        sa.ForeignKeyConstraint(
            ["experience_id"], ["experiences.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_experience_actions_experience_id",
        "experience_actions",
        ["experience_id"],
    )

    op.create_table(
        "experience_tags",
        sa.Column("experience_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["experience_id"], ["experiences.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["tags.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("experience_id", "tag_id"),
    )

    op.create_table(
        "voice_assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("experience_id", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("transcription_status", sa.String(20), nullable=False),
        sa.Column("retention_consent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "transcription_status IN ('pending', 'completed', 'failed', 'skipped')",
            name="valid_transcription_status",
        ),
        sa.CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="valid_audio_duration",
        ),
        sa.CheckConstraint(
            "file_size_bytes > 0",
            name="valid_audio_file_size",
        ),
        sa.ForeignKeyConstraint(
            ["experience_id"], ["experiences.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(
        "ix_voice_assets_experience_id",
        "voice_assets",
        ["experience_id"],
    )

    # 2. Preserve old helped text before removing the old column.
    op.execute(
        sa.text("""
            INSERT INTO experience_actions (
                experience_id,
                action_name,
                notes,
                recorded_at
            )
            SELECT
                id,
                'Legacy reflection',
                helped,
                COALESCE(occurred_at, created_at, CURRENT_TIMESTAMP)
            FROM experiences
            WHERE helped IS NOT NULL AND TRIM(helped) != ''
        """)
    )

    # 3. Add new experience columns while allowing existing rows to be updated.
    with op.batch_alter_table("experiences") as batch_op:
        batch_op.add_column(sa.Column("content", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("input_mode", sa.String(20), nullable=True))
        batch_op.add_column(
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.alter_column(
            "situation",
            existing_type=sa.Text(),
            nullable=True,
        )
        batch_op.drop_column("helped")
        batch_op.alter_column(
            "title",
            existing_type=sa.String(200),                nullable=True,
        )

    # Preserve old situation as the initial free-text content.
    op.execute(
        sa.text("""
            UPDATE experiences
            SET content = situation,
                input_mode = 'text',
                updated_at = created_at
        """)
    )

    with op.batch_alter_table("experiences") as batch_op:
        batch_op.alter_column(
            "input_mode",
            existing_type=sa.String(20),
            nullable=False,
        )
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )

    # 4. Add new emotion-observation fields.
    with op.batch_alter_table("emotion_observations") as batch_op:
        batch_op.add_column(
            sa.Column("analysis_run_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("feedback_status", sa.String(30), nullable=True)
        )
        batch_op.add_column(
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True)
        )

    # Translate old confirmation values without guessing.
    op.execute(
        sa.text("""
            UPDATE emotion_observations
            SET feedback_status = CASE
                WHEN source = 'user_reported' THEN 'not_applicable'
                WHEN is_confirmed = 1 THEN 'confirmed'
                ELSE 'pending'
            END,
            created_at = (
                SELECT experiences.created_at
                FROM experiences
                WHERE experiences.id = emotion_observations.experience_id
            )
        """)
    )

    with op.batch_alter_table(
        "emotion_observations",
        recreate="always",
    ) as batch_op:
        batch_op.alter_column(
            "feedback_status",
            existing_type=sa.String(30),
            nullable=False,
        )
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )
        batch_op.create_index(
            "ix_emotion_observations_analysis_run_id",
            ["analysis_run_id"],
        )
        batch_op.create_foreign_key(
            "fk_emotion_observations_analysis_run_id_analysis_runs",
            "analysis_runs",
            ["analysis_run_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.drop_column("is_confirmed")


def downgrade() -> None:
    raise NotImplementedError(
        "This data-preserving redesign cannot be safely reversed automatically. "
        "Restore the pre-migration database backup if rollback is required."
    )
