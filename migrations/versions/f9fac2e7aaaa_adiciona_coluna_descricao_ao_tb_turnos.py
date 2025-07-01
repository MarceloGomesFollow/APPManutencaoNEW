"""Cria tabela tb_turnos com campo descricao

Revision ID: f9fac2e7aaaa
Revises: 
Create Date: 2025-06-23 19:36:43.841744
"""

from alembic import op
import sqlalchemy as sa

# Identificadores da revisão
revision = 'f9fac2e7aaaa'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'tb_turnos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        # Aqui você pode adicionar mais colunas do seu modelo, se houver
    )

def downgrade():
    op.drop_table('tb_turnos')
