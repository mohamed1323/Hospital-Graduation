from flask import Blueprint, jsonify, request
from app.controllers.user import UserController
from http import HTTPStatus
from app.middleware.auth import token_required, admin_required

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        response, status_code = UserController.create_user(data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/login', methods=['POST'])
def login():
    """Login user and return token"""
    try:
        data = request.get_json()
        response, status_code = UserController.login(data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), HTTPStatus.UNAUTHORIZED
        
        token = auth_header.split(' ')[1]
        response, status_code = UserController.verify_token(token)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/', methods=['GET'])
@token_required
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        response, status_code = UserController.get_all_users()
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get user by ID"""
    try:
        response, status_code = UserController.get_user_by_id(user_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update user"""
    try:
        # Check if user is updating their own profile or is an admin
        current_user = request.current_user
        if str(current_user.id) != user_id and current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), HTTPStatus.FORBIDDEN

        data = request.get_json()
        response, status_code = UserController.update_user(user_id, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        response, status_code = UserController.delete_user(user_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR