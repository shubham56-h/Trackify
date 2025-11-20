from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    splits = db.relationship('Split', back_populates='owner', cascade='all, delete-orphan')
    assignment = db.relationship('UserSplitAssignment', back_populates='user', uselist=False)


class Split(db.Model):
    __tablename__ = 'splits'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', back_populates='splits')
    days = db.relationship('SplitDay', back_populates='split', order_by='SplitDay.position', cascade='all, delete-orphan')


class SplitDay(db.Model):
    __tablename__ = 'split_days'
    id = db.Column(db.Integer, primary_key=True)
    split_id = db.Column(db.Integer, db.ForeignKey('splits.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    muscle_groups = db.Column(db.String(255), nullable=True)

    split = db.relationship('Split', back_populates='days')


class UserSplitAssignment(db.Model):
    __tablename__ = 'user_split_assignments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    split_id = db.Column(db.Integer, db.ForeignKey('splits.id'), nullable=False)
    current_position = db.Column(db.Integer, default=0, nullable=False)
    last_completed_at = db.Column(db.Date, nullable=True)

    user = db.relationship('User', back_populates='assignment')
    split = db.relationship('Split')
    sessions = db.relationship('WorkoutSession', back_populates='assignment', cascade='all, delete-orphan')


class WorkoutSession(db.Model):
    __tablename__ = 'workout_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('user_split_assignments.id'), nullable=False)
    split_day_id = db.Column(db.Integer, db.ForeignKey('split_days.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    assignment = db.relationship('UserSplitAssignment', back_populates='sessions')
    split_day = db.relationship('SplitDay')
    sets = db.relationship('WorkoutSet', back_populates='session', cascade='all, delete-orphan')


class WorkoutSet(db.Model):
    __tablename__ = 'workout_sets'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('workout_sessions.id'), nullable=False)
    exercise_name = db.Column(db.String(120), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship('WorkoutSession', back_populates='sets')
