from mongoengine import (
    Document, ReferenceField, DictField,
    DateTimeField, FloatField, StringField
)
from datetime import datetime
from .patient import Patient
from .user import User

class Prediction(Document):
    patient = ReferenceField(Patient, required=True)
    user = ReferenceField(User, required=True)  # User who requested the prediction
    
    # Input Data
    input_features = DictField(required=True)
    
    # Prediction Results
    readmission_probability = FloatField(required=True, min_value=0, max_value=1)
    risk_level = StringField(required=True, choices=['Low', 'Medium', 'High'])
    confidence_score = FloatField(required=True, min_value=0, max_value=1)
    
    # Important factors that contributed to the prediction
    contributing_factors = DictField()
    
    # Recommendations based on the prediction
    recommendations = DictField()
    
    # Metadata
    model_version = StringField(required=True)
    prediction_type = StringField(default='readmission')
    status = StringField(default='pending', choices=['pending', 'completed', 'failed'])
    error_message = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'predictions',
        'indexes': [
            'patient',
            'user',
            'created_at',
            'risk_level',
            'status'
        ],
        'ordering': ['-created_at']
    }

    def to_dict(self) -> dict:
        """Convert prediction object to dictionary"""
        return {
            'id': str(self.id),
            'patient_id': str(self.patient.id),
            'user_id': str(self.user.id),
            'input_features': self.input_features,
            'readmission_probability': self.readmission_probability,
            'risk_level': self.risk_level,
            'confidence_score': self.confidence_score,
            'contributing_factors': self.contributing_factors,
            'recommendations': self.recommendations,
            'model_version': self.model_version,
            'prediction_type': self.prediction_type,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def save(self, *args, **kwargs):
        """Update timestamp on save"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Prediction, self).save(*args, **kwargs) 