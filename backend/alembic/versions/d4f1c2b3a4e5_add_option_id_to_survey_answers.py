"""add option_id to survey_answers

Revision ID: d4f1c2b3a4e5
Revises: c8b24ea88135
Create Date: 2025-10-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd4f1c2b3a4e5'
down_revision = 'c8b24ea88135'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add option_id column to survey_answers and create FK to question_options
    op.add_column('survey_answers', sa.Column('option_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'survey_answers_option_id_fkey',
        'survey_answers',
        'question_options',
        ['option_id'],
        ['id']
    )


def downgrade() -> None:
    # Drop FK and column
    op.drop_constraint('survey_answers_option_id_fkey', 'survey_answers', type_='foreignkey')
    op.drop_column('survey_answers', 'option_id'
)
