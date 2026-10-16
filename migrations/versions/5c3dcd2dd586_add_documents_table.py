"""Add documents table with PyMuPDF metadata extraction support

Revision ID: 5c3dcd2dd586
Revises: 62509f9810df
Create Date: 2026-08-23 18:58:21.237186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c3dcd2dd586'
down_revision = '62509f9810df'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('uploaded_by', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('file_path', sa.String(length=500), nullable=False),
    sa.Column('file_type', sa.String(length=100), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.Column('paper_title', sa.String(length=500), nullable=True),
    sa.Column('paper_authors', sa.String(length=500), nullable=True),
    sa.Column('paper_abstract', sa.Text(), nullable=True),
    sa.Column('paper_keywords', sa.String(length=500), nullable=True),
    sa.Column('paper_conclusions', sa.Text(), nullable=True),
    sa.Column('paper_gaps', sa.Text(), nullable=True),
    sa.Column('page_count', sa.Integer(), nullable=True, server_default='1'),
    sa.Column('creation_date', sa.String(length=100), nullable=True),
    sa.Column('metadata_extracted', sa.Boolean(), nullable=True, server_default='false'),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('documents')
