from flask import Blueprint, jsonify, request
from app.controllers.prediction import PredictionController
from app.middleware.auth import token_required, doctor_required
from http import HTTPStatus

bp = Blueprint('predictions', __name__, url_prefix='/api/predictions')

@bp.route('/', methods=['POST'])
@token_required
@doctor_required
def create_prediction():
    """
    Create a new prediction (doctors only)
    """
    try:
        data = request.get_json()
        # Add current user to the request data
        data['user_id'] = str(request.current_user.id)
        response, status_code = PredictionController.process_prediction(data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/history/<user_id>', methods=['GET'])
@token_required
def get_prediction_history(user_id):
    """
    Get prediction history for a user
    Users can only view their own predictions
    Doctors and admins can view any user's predictions
    """
    try:
        current_user = request.current_user
        if str(current_user.id) != user_id and current_user.role not in ['doctor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), HTTPStatus.FORBIDDEN

        response, status_code = PredictionController.get_prediction_history(user_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/<prediction_id>', methods=['GET'])
@token_required
def get_prediction(prediction_id):
    """
    Get a specific prediction
    Users can only view their own predictions
    Doctors and admins can view any prediction
    """
    try:
        response, status_code = PredictionController.get_prediction_by_id(prediction_id)
        
        # Check authorization
        if status_code == HTTPStatus.OK:
            current_user = request.current_user
            prediction_user_id = response.get('user_id')
            
            if str(current_user.id) != prediction_user_id and current_user.role not in ['doctor', 'admin']:
                return jsonify({'error': 'Unauthorized'}), HTTPStatus.FORBIDDEN
        
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR 