from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    mobile = data.get('mobile')
    
    if not email or not password or not name or not mobile:
        return jsonify({'message': 'email, password, name, and mobile are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'email already taken'}), 400

    u = User(
        email=email, 
        password_hash=generate_password_hash(password),
        name=name,
        mobile=mobile
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({'id': u.id, 'email': u.email, 'name': u.name}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'email and password required'}), 400
    u = User.query.filter_by(email=email).first()
    if not u or not check_password_hash(u.password_hash, password):
        return jsonify({'message': 'invalid credentials'}), 401
    # ensure 'sub' claim is a string, add name to additional claims
    token = create_access_token(identity=str(u.id), additional_claims={'name': u.name, 'email': u.email})
    return jsonify({'access_token': token})