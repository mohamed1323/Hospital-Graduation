import joblib
import numpy as np
from typing import Dict, Any, Tuple
import os
from .config import Config
from .data_preprocessing import DataPreprocessor

class ModelManager:
    def __init__(self):
        """Initialize the model manager"""
        self.model = self._load_model()
        self.preprocessor = DataPreprocessor()
        self.risk_thresholds = Config.RISK_THRESHOLDS

    def _load_model(self):
        """Load the trained model"""
        try:
            return joblib.load(Config.MODEL_PATH)
        except FileNotFoundError:
            raise ValueError(f"Model file not found at {Config.MODEL_PATH}")
        except Exception as e:
            raise ValueError(f"Error loading model: {str(e)}")

    def predict(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Make a prediction using the loaded model
        """
        try:
            # Validate features
            is_valid, error_message = self.preprocessor.validate_features(data)
            if not is_valid:
                return {
                    'error': error_message,
                    'status': 'failed'
                }, 400

            # Preprocess features
            X = self.preprocessor.preprocess_features(data)

            # Make prediction
            prediction_proba = self.model.predict_proba(X)[0][1]  # Probability of readmission
            
            # Get feature importances
            feature_importances = self._get_feature_importances()
            
            # Get contributing factors
            contributing_factors = self.preprocessor.get_contributing_factors(
                data, feature_importances
            )
            
            # Generate recommendations
            recommendations = self.preprocessor.generate_recommendations(
                contributing_factors, prediction_proba
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(prediction_proba)
            
            # Prepare response
            response = {
                'status': 'completed',
                'readmission_probability': float(prediction_proba),
                'risk_level': risk_level,
                'confidence_score': self._calculate_confidence(prediction_proba),
                'contributing_factors': contributing_factors,
                'recommendations': recommendations,
                'model_version': Config.MODEL_VERSION
            }
            
            return response, 200

        except Exception as e:
            return {
                'error': f"Prediction failed: {str(e)}",
                'status': 'failed'
            }, 500

    def _get_feature_importances(self) -> np.ndarray:
        """Get feature importance scores from the model"""
        try:
            # For tree-based models
            if hasattr(self.model, 'feature_importances_'):
                return self.model.feature_importances_
            # For linear models
            elif hasattr(self.model, 'coef_'):
                return np.abs(self.model.coef_[0])
            else:
                # Return equal importance if model doesn't provide importance scores
                return np.ones(len(Config.REQUIRED_FEATURES)) / len(Config.REQUIRED_FEATURES)
        except Exception:
            # Fallback to equal importance
            return np.ones(len(Config.REQUIRED_FEATURES)) / len(Config.REQUIRED_FEATURES)

    def _determine_risk_level(self, probability: float) -> str:
        """Determine risk level based on probability thresholds"""
        if probability < self.risk_thresholds['low']:
            return 'Low'
        elif probability < self.risk_thresholds['medium']:
            return 'Medium'
        else:
            return 'High'

    def _calculate_confidence(self, probability: float) -> float:
        """
        Calculate confidence score
        Higher confidence for probabilities closer to 0 or 1
        """
        return 1 - 2 * abs(0.5 - probability) 