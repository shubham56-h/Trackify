from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Split, SplitDay, UserSplitAssignment

splits_bp = Blueprint('splits', __name__, url_prefix='/api/splits')


@splits_bp.route('', methods=['POST'])
@jwt_required()
def create_split():
    """Step 2: Create your split - Choose days and assign muscle groups"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = data.get('name')
    days = data.get('days', [])
    
    if not name or not days:
        return jsonify({'message': 'name and days required'}), 400

    split = Split(owner_id=user_id, name=name)
    db.session.add(split)
    db.session.flush()

    for idx, day in enumerate(days):
        sd = SplitDay(
            split_id=split.id,
            position=idx,
            name=day.get('name'),
            muscle_groups=day.get('muscle_groups')
        )
        db.session.add(sd)

    # Auto-assign this split to the user
    assignment = UserSplitAssignment(
        user_id=user_id,
        split_id=split.id,
        current_position=0
    )
    db.session.add(assignment)
    db.session.commit()

    return jsonify({
        'id': split.id,
        'name': split.name,
        'assignment_id': assignment.id
    }), 201


@splits_bp.route('', methods=['GET'])
@jwt_required()
def get_splits():
    """Get all splits for the user"""
    user_id = int(get_jwt_identity())
    splits = Split.query.filter_by(owner_id=user_id).all()
    
    result = []
    for split in splits:
        result.append({
            'id': split.id,
            'name': split.name,
            'days': [{
                'id': day.id,
                'position': day.position,
                'name': day.name,
                'muscle_groups': day.muscle_groups
            } for day in split.days]
        })
    
    return jsonify({'splits': result}), 200


@splits_bp.route('/assign', methods=['POST'])
@jwt_required()
def assign_split():
    """Assign or switch to a different split"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    split_id = data.get('split_id')
    
    if not split_id:
        return jsonify({'message': 'split_id required'}), 400
    
    # Check if user already has an assignment
    existing = UserSplitAssignment.query.filter_by(user_id=user_id).first()
    
    if existing:
        existing.split_id = split_id
        existing.current_position = 0
    else:
        existing = UserSplitAssignment(
            user_id=user_id,
            split_id=split_id,
            current_position=0
        )
        db.session.add(existing)
    
    db.session.commit()
    return jsonify({
        'assignment_id': existing.id,
        'current_position': existing.current_position
    }), 200
