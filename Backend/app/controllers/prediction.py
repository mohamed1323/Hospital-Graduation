from typing import Dict, Any, Tuple
from http import HTTPStatus
import numpy as np
from app.models.prediction import Prediction  # You'll need to create this model
from app.utils.model_loader import load_model  # You'll need to create this utility

class PredictionController:
    @staticmethod
    def process_prediction(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Process a medical prediction request
        """
        try:
            # Validate input data
            required_fields = ['patient_data']  # Add specific required fields based on your model
            if not all(field in data for field in required_fields):
                return {
                    'error': f'Missing required fields: {", ".join(required_fields)}'
                }, HTTPStatus.BAD_REQUEST

            # Load the ML model (you'll need to implement this)
            model = load_model()

            # Preprocess the data (implement preprocessing based on your needs)
            processed_data = np.array(data['patient_data'])

            # Make prediction
            prediction_result = model.predict(processed_data)

            # Create prediction record
            prediction = Prediction(
                patient_data=data['patient_data'],
                prediction_result=prediction_result.tolist(),
                confidence_score=float(np.max(prediction_result)),  # Adjust based on your model output
                timestamp=datetime.utcnow()
            )
            prediction.save()

            return {
                'prediction': prediction_result.tolist(),
                'confidence': float(np.max(prediction_result)),
                'prediction_id': str(prediction.id)
            }, HTTPStatus.OK

        except ValueError as e:
            return {'error': f'Invalid input data: {str(e)}'}, HTTPStatus.BAD_REQUEST
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}, HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def get_prediction_history(user_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get prediction history for a user
        """
        try:
            predictions = Prediction.objects(user_id=user_id).order_by('-timestamp')
            return {
                'predictions': [pred.to_dict() for pred in predictions]
            }, HTTPStatus.OK
        except Exception as e:
            return {'error': f'Failed to fetch prediction history: {str(e)}'}, HTTPStatus.INTERNAL_SERVER_ERROR

    @staticmethod
    def get_prediction_by_id(prediction_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get a specific prediction by ID
        """
        try:
            prediction = Prediction.objects(id=prediction_id).first()
            if not prediction:
                return {'error': 'Prediction not found'}, HTTPStatus.NOT_FOUND
            return prediction.to_dict(), HTTPStatus.OK
        except Exception as e:
            return {'error': f'Failed to fetch prediction: {str(e)}'}, HTTPStatus.INTERNAL_SERVER_ERROR 