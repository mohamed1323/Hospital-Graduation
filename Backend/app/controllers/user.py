from app.models.user import User
from http import HTTPStatus
from typing import Dict, Any, Tuple, Union, List
from datetime import datetime, timedelta
import jwt
from flask import current_app

class UserController:
    @staticmethod
    def create_user(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Create a new user
        """
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return {'error': 'Username, email, and password are required'}, HTTPStatus.BAD_REQUEST

        # Check if user already exists
        if User.objects(username=data['username']).first():
            return {'error': 'Username already exists'}, HTTPStatus.CONFLICT

        if User.objects(email=data['email']).first():
            return {'error': 'Email already exists'}, HTTPStatus.CONFLICT

        try:
            user = User(
                username=data['username'],
                email=data['email'],
                full_name=data.get('full_name', ''),
                role=data.get('role', 'user')
            )
            user.set_password(data['password'])
            user.save()
            
            # Generate token
            token = UserController.generate_token(user)
            
            response = user.to_dict()
            response['token'] = token
            return response, HTTPStatus.CREATED
        except Exception as e:
            return {'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def login(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Authenticate user and return token
        """
        if not data or not all(k in data for k in ['username', 'password']):
            return {'error': 'Username and password are required'}, HTTPStatus.BAD_REQUEST

        try:
            # Find user by username or email
            user = User.objects(username=data['username']).first() or \
                  User.objects(email=data['username']).first()

            if not user or not user.check_password(data['password']):
                return {'error': 'Invalid credentials'}, HTTPStatus.UNAUTHORIZED

            if not user.is_active:
                return {'error': 'Account is disabled'}, HTTPStatus.FORBIDDEN

            # Generate token
            token = UserController.generate_token(user)
            
            response = user.to_dict()
            response['token'] = token
            return response, HTTPStatus.OK

        except Exception as e:
            return {'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def generate_token(user: User) -> str:
        """
        Generate JWT token for user
        """
        payload = {
            'user_id': str(user.id),
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_token(token: str) -> Tuple[Dict[str, Any], int]:
        """
        Verify JWT token and return user info
        """
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.objects(id=payload['user_id']).first()
            
            if not user:
                return {'error': 'User not found'}, HTTPStatus.NOT_FOUND
                
            if not user.is_active:
                return {'error': 'Account is disabled'}, HTTPStatus.FORBIDDEN
                
            return user.to_dict(), HTTPStatus.OK
            
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}, HTTPStatus.UNAUTHORIZED
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}, HTTPStatus.UNAUTHORIZED

    @staticmethod
    def get_all_users() -> Tuple[Union[List[Dict[str, Any]], Dict[str, str]], int]:
        """
        Get all users
        """
        try:
            users = User.objects.all()
            return [user.to_dict() for user in users], HTTPStatus.OK
        except Exception as e:
            return {'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def get_user_by_id(user_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get a user by ID
        """
        try:
            user = User.objects(id=user_id).first()
            if not user:
                return {'error': 'User not found'}, HTTPStatus.NOT_FOUND
            return user.to_dict(), HTTPStatus.OK
        except Exception as e:
            return {'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def update_user(user_id: str, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Update a user
        """
        try:
            user = User.objects(id=user_id).first()
            if not user:
                return {'error': 'User not found'}, HTTPStatus.NOT_FOUND

            # Check username uniqueness if it's being updated
            if data.get('username') and data['username'] != user.username:
                if User.objects(username=data['username']).first():
                    return {'error': 'Username already exists'}, HTTPStatus.CONFLICT

            # Check email uniqueness if it's being updated
            if data.get('email') and data['email'] != user.email:
                if User.objects(email=data['email']).first():
                    return {'error': 'Email already exists'}, HTTPStatus.CONFLICT

            # Update password if provided
            if data.get('password'):
                user.set_password(data['password'])

            # Update other fields
            for field in ['username', 'email', 'full_name', 'role', 'is_active']:
                if field in data:
                    setattr(user, field, data[field])

            user.save()
            return user.to_dict(), HTTPStatus.OK
        except Exception as e:
            return {'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def delete_user(user_id: str) -> Tuple[Dict[str, str], int]:
        """
        Delete a user
        """
        try:
            user = User.objects(id=user_id).first()
            if not user:
                return {'error': 'User not found'}, HTTPStatus.NOT_FOUND

            user.delete()
            return {'message': 'User deleted successfully'}, HTTPStatus.OK
        except Exception as e:
            return {'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR 