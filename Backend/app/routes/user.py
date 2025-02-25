from flask import Blueprint, jsonify, request
from app.models.user import User
from http import HTTPStatus

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('username') or not data.get('email'):
            return jsonify({
                'error': 'Username and email are required'
            }), HTTPStatus.BAD_REQUEST

        # Check if user already exists
        if User.objects(username=data['username']).first():
            return jsonify({
                'error': 'Username already exists'
            }), HTTPStatus.CONFLICT

        if User.objects(email=data['email']).first():
            return jsonify({
                'error': 'Email already exists'
            }), HTTPStatus.CONFLICT

        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.save()

        return jsonify(user.to_dict()), HTTPStatus.CREATED

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/', methods=['GET'])
def get_users():
    try:
        users = User.objects.all()
        return jsonify([user.to_dict() for user in users]), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({
                'error': 'User not found'
            }), HTTPStatus.NOT_FOUND

        return jsonify(user.to_dict()), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        user = User.objects(id=user_id).first()
        
        if not user:
            return jsonify({
                'error': 'User not found'
            }), HTTPStatus.NOT_FOUND

        # Check username uniqueness if it's being updated
        if data.get('username') and data['username'] != user.username:
            if User.objects(username=data['username']).first():
                return jsonify({
                    'error': 'Username already exists'
                }), HTTPStatus.CONFLICT

        # Check email uniqueness if it's being updated
        if data.get('email') and data['email'] != user.email:
            if User.objects(email=data['email']).first():
                return jsonify({
                    'error': 'Email already exists'
                }), HTTPStatus.CONFLICT

        # Update fields
        if data.get('username'):
            user.username = data['username']
        if data.get('email'):
            user.email = data['email']

        user.save()
        return jsonify(user.to_dict()), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({
                'error': 'User not found'
            }), HTTPStatus.NOT_FOUND

        user.delete()
        return jsonify({
            'message': 'User deleted successfully'
        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR 