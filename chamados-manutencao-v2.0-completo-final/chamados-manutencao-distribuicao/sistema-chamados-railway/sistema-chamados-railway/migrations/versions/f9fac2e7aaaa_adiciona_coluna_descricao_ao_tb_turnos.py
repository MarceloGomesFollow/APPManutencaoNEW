"""Adiciona coluna descricao ao tb_turnos

Revision ID: f9fac2e7aaaa
Revises: 
Create Date: 2025-06-23 19:36:43.841744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9fac2e7aaaa'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    with op.batch_alter_table('tb_turnos') as batch_op:
        batch_op.add_column(sa.Column('descricao', sa.Text(), nullable=True))

def downgrade():
    with op.batch_alter_table('tb_turnos') as batch_op:
        batch_op.drop_column('descricao')