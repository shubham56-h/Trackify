from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, UserSplitAssignment, WorkoutSession, WorkoutSet, SplitDay
from datetime import datetime, date

today_bp = Blueprint("today", __name__, url_prefix='/api/today')


@today_bp.route("", methods=["GET"])
@jwt_required()
def get_today():
    """Step 3: Today screen - Shows today's workout"""
    user_id = int(get_jwt_identity())
    
    assignment = UserSplitAssignment.query.filter_by(user_id=user_id).first()
    if not assignment:
        return jsonify({"message": "No split assigned. Create a split first."}), 404
    
    split = assignment.split
    if not split.days:
        return jsonify({"message": "Split has no days configured"}), 400
    
    # Get current day based on position
    current_day = None
    for day in split.days:
        if day.position == assignment.current_position:
            current_day = day
            break
    
    if not current_day:
        current_day = split.days[0]
        assignment.current_position = 0
        db.session.commit()
    
    # Check if there's an active session
    active_session = WorkoutSession.query.filter_by(
        user_id=user_id,
        completed=False
    ).first()
    
    return jsonify({
        "today": {
            "day_name": current_day.name,
            "muscle_groups": current_day.muscle_groups,
            "split_day_id": current_day.id
        },
        "active_session": {
            "id": active_session.id,
            "started_at": active_session.started_at.isoformat()
        } if active_session else None,
        "assignment": {
            "id": assignment.id,
            "current_position": assignment.current_position,
            "split": {
                "id": split.id,
                "name": split.name,
                "is_template": split.is_template,
                "days": [{
                    "id": day.id,
                    "position": day.position,
                    "name": day.name,
                    "muscle_groups": day.muscle_groups
                } for day in sorted(split.days, key=lambda d: d.position)]
            }
        }
    }), 200


@today_bp.route("/start", methods=["POST"])
@jwt_required()
def start_workout():
    """Step 3: Start Workout"""
    user_id = int(get_jwt_identity())
    
    assignment = UserSplitAssignment.query.filter_by(user_id=user_id).first()
    if not assignment:
        return jsonify({"message": "No split assigned"}), 404
    
    # Check if already has active session
    active_session = WorkoutSession.query.filter_by(
        user_id=user_id,
        completed=False
    ).first()
    
    if active_session:
        return jsonify({
            "message": "Workout already in progress",
            "session_id": active_session.id
        }), 200
    
    # Get current day
    split = assignment.split
    current_day = None
    for day in split.days:
        if day.position == assignment.current_position:
            current_day = day
            break
    
    if not current_day:
        return jsonify({"message": "Invalid split configuration"}), 400
    
    # Create new session
    session = WorkoutSession(
        user_id=user_id,
        assignment_id=assignment.id,
        split_day_id=current_day.id,
        started_at=datetime.utcnow(),
        completed=False
    )
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        "message": "Workout started",
        "session_id": session.id,
        "day_name": current_day.name
    }), 201


@today_bp.route("/add-set", methods=["POST"])
@jwt_required()
def add_set():
    """Step 4: During workout - Add sets"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    exercise_id = data.get("exercise_id")
    exercise_name = data.get("exercise_name")  # Fallback for backward compatibility
    reps = data.get("reps")
    weight = data.get("weight")
    
    if (not exercise_id and not exercise_name) or reps is None or weight is None:
        return jsonify({"message": "exercise_id (or exercise_name), reps, and weight required"}), 400
    
    # Get active session
    session = WorkoutSession.query.filter_by(
        user_id=user_id,
        completed=False
    ).first()
    
    if not session:
        return jsonify({"message": "No active workout session. Start a workout first."}), 404
    
    # If exercise_id provided, get the exercise name from database
    if exercise_id:
        from models import Exercise
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return jsonify({"message": "Exercise not found"}), 404
        exercise_name = exercise.name
    
    # Count existing sets for this exercise in this session
    if exercise_id:
        set_count = WorkoutSet.query.filter_by(
            session_id=session.id,
            exercise_id=exercise_id
        ).count()
    else:
        set_count = WorkoutSet.query.filter_by(
            session_id=session.id,
            exercise_name=exercise_name
        ).count()
    
    workout_set = WorkoutSet(
        session_id=session.id,
        exercise_id=exercise_id,
        exercise_name=exercise_name,
        set_number=set_count + 1,
        reps=int(reps),
        weight=float(weight)
    )
    db.session.add(workout_set)
    db.session.commit()
    
    return jsonify({
        "message": "Set added",
        "set": {
            "id": workout_set.id,
            "exercise_id": workout_set.exercise_id,
            "exercise_name": workout_set.exercise_name,
            "set_number": workout_set.set_number,
            "reps": workout_set.reps,
            "weight": workout_set.weight
        }
    }), 201


@today_bp.route("/finish", methods=["POST"])
@jwt_required()
def finish_workout():
    """Step 5: Finish workout - Mark as completed and move to next day"""
    user_id = int(get_jwt_identity())
    
    # Get active session
    session = WorkoutSession.query.filter_by(
        user_id=user_id,
        completed=False
    ).first()
    
    if not session:
        return jsonify({"message": "No active workout session"}), 404
    
    # Mark session as completed
    session.completed = True
    session.ended_at = datetime.utcnow()
    
    # Update assignment
    assignment = session.assignment
    assignment.last_completed_at = date.today()
    
    # Move to next day
    split = assignment.split
    total_days = len(split.days)
    assignment.current_position = (assignment.current_position + 1) % total_days
    
    db.session.commit()
    
    # Get next day info
    next_day = None
    for day in split.days:
        if day.position == assignment.current_position:
            next_day = day
            break
    
    return jsonify({
        "message": "Workout completed!",
        "next_day": {
            "name": next_day.name if next_day else "Unknown",
            "muscle_groups": next_day.muscle_groups if next_day else None
        }
    }), 200


@today_bp.route("/cancel", methods=["POST"])
@jwt_required()
def cancel_workout():
    """Cancel active workout - Delete session and all sets without moving to next day"""
    user_id = int(get_jwt_identity())
    
    # Get active session
    session = WorkoutSession.query.filter_by(
        user_id=user_id,
        completed=False
    ).first()
    
    if not session:
        return jsonify({"message": "No active workout session"}), 404
    
    # Delete the session (cascade will delete all sets)
    db.session.delete(session)
    db.session.commit()
    
    return jsonify({
        "message": "Workout cancelled successfully"
    }), 200


@today_bp.route("/exercise-history/<int:exercise_id>", methods=["GET"])
@jwt_required()
def get_exercise_history(exercise_id):
    """Get past performance data for a specific exercise"""
    user_id = int(get_jwt_identity())
    
    # Get exercise details
    from models import Exercise
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        return jsonify({"message": "Exercise not found"}), 404
    
    # Get last 3 completed sessions for this exercise
    past_sessions = db.session.query(WorkoutSession).join(
        WorkoutSet, WorkoutSession.id == WorkoutSet.session_id
    ).filter(
        WorkoutSession.user_id == user_id,
        WorkoutSession.completed == True,
        db.or_(
            WorkoutSet.exercise_id == exercise_id,
            db.func.lower(WorkoutSet.exercise_name) == exercise.name.lower()  # Fallback for old data
        )
    ).distinct().order_by(WorkoutSession.ended_at.desc()).limit(3).all()
    
    history = []
    for session in past_sessions:
        # Get all sets for this exercise in this session
        sets = WorkoutSet.query.filter(
            WorkoutSet.session_id == session.id,
            db.or_(
                WorkoutSet.exercise_id == exercise_id,
                db.func.lower(WorkoutSet.exercise_name) == exercise.name.lower()
            )
        ).order_by(WorkoutSet.set_number).all()
        
        if sets:
            history.append({
                "date": session.ended_at.strftime("%b %d, %Y") if session.ended_at else "Unknown",
                "timestamp": session.ended_at.isoformat() if session.ended_at else None,
                "total_sets": len(sets),
                "sets": [
                    {
                        "set_number": s.set_number,
                        "reps": s.reps,
                        "weight": s.weight,
                        "volume": s.reps * s.weight
                    } for s in sets
                ],
                "total_volume": sum(s.reps * s.weight for s in sets),
                "max_weight": max(s.weight for s in sets)
            })
    
    return jsonify({
        "exercise_id": exercise_id,
        "exercise_name": exercise.name,
        "history": history
    }), 200


@today_bp.route("/session-summary", methods=["GET"])
@jwt_required()
def get_session_summary():
    """Get summary of current workout session"""
    user_id = int(get_jwt_identity())
    
    # Get active session
    session = WorkoutSession.query.filter_by(
        user_id=user_id,
        completed=False
    ).first()
    
    if not session:
        return jsonify({"message": "No active workout session"}), 404
    
    # Get all sets in this session
    sets = WorkoutSet.query.filter_by(session_id=session.id).all()
    
    # Group sets by exercise
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
        
        exercises_summary[exercise_key]['sets'].append({
            'set_number': workout_set.set_number,
            'reps': workout_set.reps,
            'weight': workout_set.weight
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
    if session.started_at:
        duration = datetime.utcnow() - session.started_at
        duration_minutes = int(duration.total_seconds() / 60)
    
    return jsonify({
        "session_id": session.id,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "duration_minutes": duration_minutes,
        "exercises": list(exercises_summary.values()),
        "totals": {
            "exercises": total_exercises,
            "sets": total_sets,
            "volume": total_volume
        }
    }), 200
