from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, WorkoutSet, WorkoutSession
from sqlalchemy.sql import func
from datetime import datetime, timedelta

progress_bp = Blueprint("progress", __name__, url_prefix='/api/progress')


@progress_bp.route("/best-lifts", methods=["GET"])
@jwt_required()
def best_lifts():
    """Step 6: Progress dashboard - Best lifts"""
    user_id = int(get_jwt_identity())
    
    # Get best weight for each exercise
    results = (
        db.session.query(
            WorkoutSet.exercise_name,
            func.max(WorkoutSet.weight).label("max_weight"),
            func.max(WorkoutSet.reps).label("max_reps")
        )
        .join(WorkoutSession, WorkoutSession.id == WorkoutSet.session_id)
        .filter(WorkoutSession.user_id == user_id)
        .filter(WorkoutSession.completed == True)
        .group_by(WorkoutSet.exercise_name)
        .all()
    )
    
    data = [
        {
            "exercise": r[0],
            "max_weight": float(r[1]) if r[1] else 0,
            "max_reps": int(r[2]) if r[2] else 0
        }
        for r in results
    ]
    
    return jsonify({"best_lifts": data}), 200


@progress_bp.route("/volume", methods=["GET"])
@jwt_required()
def volume_graph():
    """Step 6: Progress dashboard - Volume tracking"""
    user_id = int(get_jwt_identity())
    
    # Calculate total volume per day (weight × reps)
    results = (
        db.session.query(
            func.date(WorkoutSession.started_at).label("date"),
            func.sum(WorkoutSet.weight * WorkoutSet.reps).label("volume")
        )
        .join(WorkoutSet, WorkoutSet.session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == user_id)
        .filter(WorkoutSession.completed == True)
        .group_by(func.date(WorkoutSession.started_at))
        .order_by(func.date(WorkoutSession.started_at))
        .all()
    )
    
    data = [
        {
            "date": str(r[0]),
            "volume": float(r[1]) if r[1] else 0
        }
        for r in results
    ]
    
    return jsonify({"volume": data}), 200


@progress_bp.route("/heatmap", methods=["GET"])
@jwt_required()
def heatmap():
    """Step 6: Progress dashboard - Workout heatmap"""
    user_id = int(get_jwt_identity())
    
    # Get workout count per day
    results = (
        db.session.query(
            func.date(WorkoutSession.started_at).label("date"),
            func.count(WorkoutSession.id).label("count")
        )
        .filter(WorkoutSession.user_id == user_id)
        .filter(WorkoutSession.completed == True)
        .group_by(func.date(WorkoutSession.started_at))
        .order_by(func.date(WorkoutSession.started_at))
        .all()
    )
    
    data = [
        {
            "date": str(r[0]),
            "count": int(r[1])
        }
        for r in results
    ]
    
    return jsonify({"heatmap": data}), 200


@progress_bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    """Overall stats summary"""
    user_id = int(get_jwt_identity())
    
    # Total workouts
    total_workouts = WorkoutSession.query.filter_by(
        user_id=user_id,
        completed=True
    ).count()
    
    # Total sets
    total_sets = (
        db.session.query(func.count(WorkoutSet.id))
        .join(WorkoutSession)
        .filter(WorkoutSession.user_id == user_id)
        .filter(WorkoutSession.completed == True)
        .scalar()
    )
    
    # Get all workout sessions
    sessions = (
        WorkoutSession.query
        .filter_by(user_id=user_id, completed=True)
        .order_by(WorkoutSession.started_at.desc())
        .all()
    )
    
    # Calculate current streak and longest streak
    current_streak = 0
    longest_streak = 0
    workout_dates = []
    
    if sessions:
        # Get unique workout dates
        dates = sorted(set([s.started_at.date() for s in sessions]), reverse=True)
        workout_dates = [d.isoformat() for d in dates]
        
        # Calculate current streak
        today = datetime.now().date()
        current_streak = 0
        
        # Check if there's a workout today or yesterday (to maintain streak)
        if dates and (dates[0] == today or dates[0] == today - timedelta(days=1)):
            current_streak = 1
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i + 1]).days == 1:
                    current_streak += 1
                else:
                    break
        
        # Calculate longest streak
        temp_streak = 1
        for i in range(len(dates) - 1):
            if (dates[i] - dates[i + 1]).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
        longest_streak = max(longest_streak, temp_streak)
    
    return jsonify({
        "total_workouts": total_workouts,
        "total_sets": total_sets or 0,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "workout_dates": workout_dates
    }), 200
