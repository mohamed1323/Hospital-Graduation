import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from .config import Config

class DataPreprocessor:
    def __init__(self):
        """Initialize the preprocessor"""
        self.scaler = self._load_scaler()
        self.label_encoders = self._load_label_encoders()
        self.feature_names = self._load_feature_names()
        
        # Define feature groups
        self.categorical_features = ['gender', 'primary_diagnosis', 'discharge_to']
        self.numerical_features = ['age', 'num_procedures', 'days_in_hospital', 'comorbidity_score']
        self.required_features = self.numerical_features + self.categorical_features

    def _load_scaler(self) -> StandardScaler:
        """Load the fitted StandardScaler"""
        scaler_path = os.path.join(os.path.dirname(Config.MODEL_PATH), 'scaler.pkl')
        try:
            return joblib.load(scaler_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Scaler file not found at {scaler_path}. Please ensure the model is trained first.") from e

    def _load_label_encoders(self) -> Dict[str, Any]:
        """Load the fitted LabelEncoders"""
        encoders_path = os.path.join(os.path.dirname(Config.MODEL_PATH), 'label_encoders.pkl')
        try:
            return joblib.load(encoders_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Label encoders file not found at {encoders_path}. Please ensure the model is trained first.") from e

    def _load_feature_names(self) -> List[str]:
        """Load the feature names used during training"""
        feature_names_path = os.path.join(os.path.dirname(Config.MODEL_PATH), 'feature_names.pkl')
        try:
            return joblib.load(feature_names_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Feature names file not found at {feature_names_path}. Please ensure the model is trained first.") from e

    def validate_features(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate that all required features are present and have valid values
        """
        # Check for missing features
        missing_features = [feat for feat in self.required_features 
                          if feat not in data]
        
        if missing_features:
            return False, f"Missing required features: {', '.join(missing_features)}"
        
        # Validate feature values
        validation_errors = []
        
        # Numerical validations
        if not 0 <= data['age'] <= 120:
            validation_errors.append("Age must be between 0 and 120")
            
        if data['num_procedures'] < 0:
            validation_errors.append("Number of procedures cannot be negative")
            
        if data['days_in_hospital'] < 0:
            validation_errors.append("Days in hospital cannot be negative")
            
        if data['comorbidity_score'] < 0:
            validation_errors.append("Comorbidity score cannot be negative")
        
        # Categorical validations
        if data['gender'] not in self.label_encoders['gender'].classes_:
            valid_genders = ', '.join(self.label_encoders['gender'].classes_)
            validation_errors.append(f"Gender must be one of: {valid_genders}")
            
        if data['primary_diagnosis'] not in self.label_encoders['primary_diagnosis'].classes_:
            validation_errors.append("Invalid primary diagnosis code")
            
        if data['discharge_to'] not in self.label_encoders['discharge_to'].classes_:
            valid_destinations = ', '.join(self.label_encoders['discharge_to'].classes_)
            validation_errors.append(f"Discharge destination must be one of: {valid_destinations}")
        
        if validation_errors:
            return False, "; ".join(validation_errors)
        
        return True, ""

    def preprocess_features(self, data: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess features for model prediction
        """
        feature_vector = []
        
        # Process numerical features
        for feature in self.numerical_features:
            value = float(data.get(feature, 0))
            feature_vector.append(value)
        
        # Process categorical features
        for feature in self.categorical_features:
            value = data.get(feature, '')
            try:
                encoded_value = self.label_encoders[feature].transform([value])[0]
                feature_vector.append(encoded_value)
            except ValueError as e:
                raise ValueError(f"Invalid value for {feature}: {value}. Valid values are: {self.label_encoders[feature].classes_}") from e
        
        # Convert to numpy array and reshape
        X = np.array(feature_vector).reshape(1, -1)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        return X_scaled

    def get_contributing_factors(self, 
                               data: Dict[str, Any], 
                               feature_importances: np.ndarray,
                               top_n: int = 5) -> Dict[str, float]:
        """
        Identify factors contributing to the prediction
        """
        importance_dict = {}
        
        for feature, importance in zip(self.feature_names, feature_importances):
            value = data.get(feature, 0)
            
            # Calculate contribution
            if feature in self.categorical_features:
                base_contribution = importance
            else:
                base_contribution = abs(float(value) * importance)
            
            # Apply feature-specific weights
            if feature == 'comorbidity_score':
                base_contribution *= 1.3  # Higher weight for comorbidity
            elif feature == 'days_in_hospital':
                base_contribution *= 1.2 if float(value) > 7 else 1.0  # Weight for longer stays
            elif feature == 'primary_diagnosis':
                base_contribution *= 1.2  # Higher weight for primary diagnosis
            
            importance_dict[feature] = base_contribution
        
        # Sort and get top factors
        sorted_factors = dict(sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n])
        
        return sorted_factors

    def generate_recommendations(self, 
                               contributing_factors: Dict[str, float],
                               prediction_probability: float) -> Dict[str, List[str]]:
        """
        Generate recommendations based on risk level and contributing factors
        """
        recommendations = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        risk_level = self._get_risk_level(prediction_probability)
        top_factors = list(contributing_factors.items())
        
        for factor, importance in top_factors:
            if importance > 0.3 or risk_level == 'High':
                recommendations['high_priority'].extend(
                    self._get_factor_recommendations(factor, 'high', risk_level)
                )
            elif importance > 0.1 or risk_level == 'Medium':
                recommendations['medium_priority'].extend(
                    self._get_factor_recommendations(factor, 'medium', risk_level)
                )
            else:
                recommendations['low_priority'].extend(
                    self._get_factor_recommendations(factor, 'low', risk_level)
                )
        
        self._add_general_recommendations(recommendations, risk_level)
        return recommendations

    def _get_risk_level(self, probability: float) -> str:
        """Determine risk level from probability"""
        if probability < Config.RISK_THRESHOLDS['low']:
            return 'Low'
        elif probability < Config.RISK_THRESHOLDS['medium']:
            return 'Medium'
        return 'High'

    def _get_factor_recommendations(self, factor: str, importance: str, risk_level: str) -> List[str]:
        """Get specific recommendations for each factor"""
        base_recommendations = {
            'comorbidity_score': {
                'high': [
                    'Schedule comprehensive health assessment',
                    'Review and adjust all medications',
                    'Consider specialist consultations'
                ],
                'medium': [
                    'Schedule follow-up for major conditions',
                    'Review medication compliance',
                    'Monitor symptoms regularly'
                ],
                'low': [
                    'Maintain current treatment plans',
                    'Regular check-ups as scheduled',
                    'Report any new symptoms'
                ]
            },
            'days_in_hospital': {
                'high': [
                    'Create detailed post-discharge plan',
                    'Schedule 48-hour follow-up',
                    'Arrange home health services'
                ],
                'medium': [
                    'Schedule follow-up within 7 days',
                    'Review discharge instructions',
                    'Monitor recovery progress'
                ],
                'low': [
                    'Follow discharge instructions',
                    'Schedule routine follow-up',
                    'Monitor for complications'
                ]
            },
            'primary_diagnosis': {
                'high': [
                    'Urgent specialist consultation',
                    'Review treatment effectiveness',
                    'Consider additional testing'
                ],
                'medium': [
                    'Schedule specialist follow-up',
                    'Monitor specific symptoms',
                    'Review treatment plan'
                ],
                'low': [
                    'Continue prescribed treatment',
                    'Regular monitoring',
                    'Routine check-ups'
                ]
            },
            'num_procedures': {
                'high': [
                    'Close monitoring of procedure sites',
                    'Schedule post-procedure check-ups',
                    'Watch for complications'
                ],
                'medium': [
                    'Follow post-procedure care',
                    'Regular wound care if needed',
                    'Report unusual symptoms'
                ],
                'low': [
                    'Continue normal recovery',
                    'Basic wound care',
                    'Regular check-ups'
                ]
            }
        }
        
        recommendations = base_recommendations.get(factor, {}).get(importance, 
            ['Monitor and maintain current health management plan'])
        
        if risk_level == 'High':
            recommendations = [f"URGENT: {rec}" for rec in recommendations]
        
        return recommendations

    def _add_general_recommendations(self, recommendations: Dict[str, List[str]], risk_level: str):
        """Add general recommendations based on risk level"""
        general_recs = {
            'High': [
                'Schedule immediate follow-up',
                'Review all medications',
                'Set up daily monitoring',
                'Arrange support at home',
                'Consider home care'
            ],
            'Medium': [
                'Follow-up within 2 weeks',
                'Review medications',
                'Keep health diary',
                'Know emergency contacts',
                'Learn warning signs'
            ],
            'Low': [
                'Routine follow-up',
                'Continue medications',
                'Maintain healthy habits',
                'Regular exercise',
                'Balanced diet'
            ]
        }
        
        priority_level = 'high_priority' if risk_level == 'High' else \
                        'medium_priority' if risk_level == 'Medium' else \
                        'low_priority'
        
        recommendations[priority_level].extend(general_recs[risk_level])