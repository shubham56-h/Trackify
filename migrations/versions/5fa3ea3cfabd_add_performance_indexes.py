"""add_performance_indexes

Revision ID: 5fa3ea3cfabd
Revises: b14e04e1445b
Create Date: 2025-11-24 20:53:24.602684

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fa3ea3cfabd'
down_revision = 'b14e04e1445b'
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes for frequently queried fields to improve performance
    op.create_index('idx_workout_sessions_user_id', 'workout_sessions', ['user_id'])
    op.create_index('idx_workout_sessions_completed', 'workout_sessions', ['completed'])
    op.create_index('idx_workout_sets_session_id', 'workout_sets', ['session_id'])
    op.create_index('idx_workout_sets_exercise_id', 'workout_sets', ['exercise_id'])
    op.create_index('idx_exercises_muscle_group', 'exercises', ['muscle_group', 'specific_muscle'])


def downgrade():
    # Remove indexes
    op.drop_index('idx_exercises_muscle_group', 'exercises')
    op.drop_index('idx_workout_sets_exercise_id', 'workout_sets')
    op.drop_index('idx_workout_sets_session_id', 'workout_sets')
    op.drop_index('idx_workout_sessions_completed', 'workout_sessions')
    op.drop_index('idx_workout_sessions_user_id', 'workout_sessions')
