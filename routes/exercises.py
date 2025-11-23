from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Exercise

exercises_bp = Blueprint('exercises', __name__, url_prefix='/api/exercises')


@exercises_bp.route('/<muscle_group>/<specific_muscle>', methods=['GET'])
@jwt_required()
def get_exercises(muscle_group, specific_muscle):
    """Get all exercises for a specific muscle"""
    user_id = int(get_jwt_identity())
    
    # Get default exercises + user's custom exercises
    exercises = Exercise.query.filter(
        Exercise.muscle_group == muscle_group,
        Exercise.specific_muscle == specific_muscle,
        db.or_(
            Exercise.is_default == True,
            Exercise.created_by == user_id
        )
    ).order_by(Exercise.is_default.desc(), Exercise.name).all()
    
    result = [{
        'id': ex.id,
        'name': ex.name,
        'is_default': ex.is_default
    } for ex in exercises]
    
    return jsonify({'exercises': result}), 200


@exercises_bp.route('', methods=['POST'])
@jwt_required()
def create_exercise():
    """Create a custom exercise"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    name = data.get('name')
    muscle_group = data.get('muscle_group')
    specific_muscle = data.get('specific_muscle')
    
    if not name or not muscle_group or not specific_muscle:
        return jsonify({'message': 'name, muscle_group, and specific_muscle required'}), 400
    
    exercise = Exercise(
        name=name,
        muscle_group=muscle_group,
        specific_muscle=specific_muscle,
        is_default=False,
        created_by=user_id
    )
    db.session.add(exercise)
    db.session.commit()
    
    return jsonify({
        'id': exercise.id,
        'name': exercise.name,
        'message': 'Exercise created successfully'
    }), 201
