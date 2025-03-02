from functools import wraps
from flask import request, jsonify, current_app
from http import HTTPStatus
import jwt
from app.models.user import User

def token_required(f):
    """Decorator to verify JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), HTTPStatus.UNAUTHORIZED

        try:
            # Decode token
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.objects(id=payload['user_id']).first()

            if not current_user:
                return jsonify({'error': 'Invalid token'}), HTTPStatus.UNAUTHORIZED

            if not current_user.is_active:
                return jsonify({'error': 'Account is disabled'}), HTTPStatus.FORBIDDEN

            # Add user to request context
            request.current_user = current_user
            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), HTTPStatus.UNAUTHORIZED
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), HTTPStatus.UNAUTHORIZED

    return decorated

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = request.current_user

        if not current_user or current_user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), HTTPStatus.FORBIDDEN

        return f(*args, **kwargs)

    return decorated

def doctor_required(f):
    """Decorator to check if user is a doctor"""
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = request.current_user

        if not current_user or current_user.role not in ['doctor', 'admin']:
            return jsonify({'error': 'Doctor privileges required'}), HTTPStatus.FORBIDDEN

        return f(*args, **kwargs)

    return decorated 