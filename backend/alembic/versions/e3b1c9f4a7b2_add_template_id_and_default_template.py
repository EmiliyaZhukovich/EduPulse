"""Add template_id to surveys and create a default survey template

Revision ID: e3b1c9f4a7b2
Revises: c8b24ea88135
Create Date: 2025-10-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3b1c9f4a7b2'
down_revision = 'd4f1c2b3a4e5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    title = 'Стандартный шаблон опроса'
    description = 'Автоматически созданный стандартный шаблон опроса'

    # Ensure a default template exists (reuse if already present)
    row = conn.execute(sa.text("SELECT id FROM survey_templates WHERE title = :title LIMIT 1"), {"title": title}).fetchone()
    if row is None:
        res = conn.execute(
            sa.text(
                "INSERT INTO survey_templates (title, description, is_active, created_at) VALUES (:title, :desc, true, now()) RETURNING id"
            ),
            {"title": title, "desc": description},
        )
        template_id = res.scalar()
    else:
        template_id = row[0]

    # Add template_id column to surveys (nullable initially)
    op.add_column('surveys', sa.Column('template_id', sa.Integer(), nullable=True))

    # Populate existing surveys with the default template id
    conn.execute(sa.text("UPDATE surveys SET template_id = :tid WHERE template_id IS NULL"), {"tid": template_id})

    # Create foreign key constraint to survey_templates.id
    op.create_foreign_key(
        'fk_surveys_template_id_survey_templates',
        'surveys',
        'survey_templates',
        ['template_id'],
        ['id'],
    )


def downgrade() -> None:
    conn = op.get_bind()
    title = 'Стандартный шаблон опроса'

    # Drop foreign key if present
    try:
        op.drop_constraint('fk_surveys_template_id_survey_templates', 'surveys', type_='foreignkey')
    except Exception:
        # best-effort drop
        pass

    # Drop the column
    try:
        op.drop_column('surveys', 'template_id')
    except Exception:
        pass

    # Remove the default template if it exists and has no dependant rows
    try:
        # Only delete the template with this title and which is present
        conn.execute(sa.text("DELETE FROM survey_templates WHERE title = :title"), {"title": title})
    except Exception:
        pass
