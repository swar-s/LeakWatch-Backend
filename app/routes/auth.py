from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import db
import jwt
import datetime
from flask import current_app

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    if db.users.find_one({'email': email}):
        return jsonify({'error': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    user = {
        'name': name,
        'email': email,
        'password': hashed_password
    }
    db.users.insert_one(user)
    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Find user by email
    user = db.users.find_one({'email': email})
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Generate JWT token
    payload = {
        'user_id': str(user['_id']),
        'name': user['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    secret = current_app.config.get('SECRET_KEY', 'your-secret-key')
    token = jwt.encode(payload, secret, algorithm='HS256')

    return jsonify({'message': 'Login successful', 'token': token}), 200


@auth_bp.route('/dbtest', methods=['GET'])
def db_test():
    try:
        user_count = db.users.count_documents({})
        return jsonify({'status': 'success', 'user_count': user_count}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
