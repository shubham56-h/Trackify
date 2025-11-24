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



@progress_bp.route("/workout-history", methods=["GET"])
@jwt_required()
def workout_history():
    """Get detailed history of all completed workouts with set-wise breakdown"""
    user_id = int(get_jwt_identity())
    
    # Get all completed sessions
    sessions = WorkoutSession.query.filter_by(
        user_id=user_id,
        completed=True
    ).order_by(WorkoutSession.ended_at.desc()).all()
    
    workouts = []
    for session in sessions:
        # Get all sets in this session, ordered by exercise and set number
        sets = WorkoutSet.query.filter_by(session_id=session.id).order_by(
            WorkoutSet.exercise_name, WorkoutSet.set_number
        ).all()
        
        # Group sets by exercise with detailed breakdown
        exercises_summary = {}
        for workout_set in sets:
            exercise_key = workout_set.exercise_id or workout_set.exercise_name
            exercise_name = workout_set.exercise_name
            
            if exercise_key not in exercises_summary:
                exercises_summary[exercise_key] = {
                    'name': exercise_name,
                    'sets': [],
                    'total_sets': 0,
                    'total_volume': 0,
                    'max_weight': 0
                }
            
            # Add individual set details
            exercises_summary[exercise_key]['sets'].append({
                'set_number': workout_set.set_number,
                'reps': workout_set.reps,
                'weight': workout_set.weight,
                'volume': workout_set.reps * workout_set.weight
            })
            
            exercises_summary[exercise_key]['total_sets'] += 1
            exercises_summary[exercise_key]['total_volume'] += workout_set.reps * workout_set.weight
            exercises_summary[exercise_key]['max_weight'] = max(
                exercises_summary[exercise_key]['max_weight'],
                workout_set.weight
            )
        
        # Calculate totals
        total_sets = len(sets)
        total_volume = sum(s.reps * s.weight for s in sets)
        total_exercises = len(exercises_summary)
        
        # Calculate duration
        duration_minutes = 0
        if session.started_at and session.ended_at:
            duration = session.ended_at - session.started_at
            duration_minutes = int(duration.total_seconds() / 60)
        
        # Get split day name
        split_day_name = "Workout"
        if session.split_day:
            split_day_name = session.split_day.name
        
        workouts.append({
            "session_id": session.id,
            "date": session.ended_at.strftime("%b %d, %Y") if session.ended_at else "Unknown",
            "day_name": split_day_name,
            "duration_minutes": duration_minutes,
            "exercises": list(exercises_summary.values()),
            "totals": {
                "exercises": total_exercises,
                "sets": total_sets,
                "volume": total_volume
            }
        })
    
    return jsonify({"workouts": workouts}), 200
