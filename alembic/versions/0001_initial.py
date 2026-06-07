"""initial: pgvector extension + tablas articles y clusters

Revision ID: 0001
Revises:
Create Date: 2026-06-07
"""

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "articles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        # embedding: se crea como Text y se convierte a vector(1536) abajo
        sa.Column("embedding", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )

    # Reemplazar la columna Text por vector(1536) real en postgres
    op.execute(
        "ALTER TABLE articles ALTER COLUMN embedding TYPE vector(1536) "
        "USING NULL::vector(1536)"
    )

    op.create_table(
        "clusters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("trend_score", sa.Float(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Índice ivfflat para búsqueda ANN sobre embeddings (se puede poblar luego)
    op.execute(
        "CREATE INDEX IF NOT EXISTS articles_embedding_idx "
        "ON articles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS articles_embedding_idx")
    op.drop_table("clusters")
    op.drop_table("articles")
    op.execute("DROP EXTENSION IF EXISTS vector")
