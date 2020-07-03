"""empty message

Revision ID: 0d0ebcd199a3
Revises: 
Create Date: 2020-07-02 22:28:37.336773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d0ebcd199a3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('entries',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('entry', sa.String(), nullable=True),
    sa.Column('entry_date', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('public_key', sa.LargeBinary(), nullable=True),
    sa.Column('private_key', sa.LargeBinary(), nullable=True),
    sa.Column('access_tokens', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('entries')
    # ### end Alembic commands ###
