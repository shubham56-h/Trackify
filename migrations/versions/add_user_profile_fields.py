"""add user profile fields

Revision ID: add_user_profile_fields
Revises: 4796174fb204
Create Date: 2025-01-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_profile_fields'
down_revision = '4796174fb204'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('mobile', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('age', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('height', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('weight', sa.Float(), nullable=True))
    
    # Update existing users with default values
    op.execute("UPDATE users SET name = 'User', mobile = '0000000000' WHERE name IS NULL")
    
    # Make name and mobile non-nullable after setting defaults
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('name', nullable=False)
        batch_op.alter_column('mobile', nullable=False)


def downgrade():
    # Remove the new columns
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('weight')
        batch_op.drop_column('height')
        batch_op.drop_column('age')
        batch_op.drop_column('mobile')
        batch_op.drop_column('name')
