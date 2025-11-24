"""add full text search index

Revision ID: 857c7201a9c7
Revises: c84ef9e6e3c6
Create Date: 2025-11-24 10:37:16.251076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '857c7201a9c7'
down_revision: Union[str, Sequence[str], None] = 'c84ef9e6e3c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX ix_note_content_fts ON note 
        USING GIN (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, '')));
    """)

def downgrade() -> None:
    op.execute("DROP INDEX ix_note_content_fts;")
