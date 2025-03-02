from mongoengine import (
    Document, StringField, IntField, FloatField,
    DateTimeField, ReferenceField, BooleanField
)
from datetime import datetime
from .user import User

class Patient(Document):
    # Patient Information
    medical_record_number = StringField(required=True, unique=True)
    user = ReferenceField(User, required=True)  # Link to user account if exists
    
    # Model Features
    age = IntField(required=True, min_value=0, max_value=120)
    gender = StringField(required=True)
    primary_diagnosis = StringField(required=True)
    num_procedures = IntField(required=True, min_value=0)
    days_in_hospital = IntField(required=True, min_value=0)
    comorbidity_score = FloatField(required=True, min_value=0)
    discharge_to = StringField(required=True)
    readmitted = BooleanField(default=False)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'patients',
        'indexes': [
            'medical_record_number',
            'user',
            'primary_diagnosis',
            'readmitted'
        ]
    }

    def to_dict(self) -> dict:
        """Convert patient object to dictionary"""
        return {
            'id': str(self.id),
            'medical_record_number': self.medical_record_number,
            'user_id': str(self.user.id) if self.user else None,
            'age': self.age,
            'gender': self.gender,
            'primary_diagnosis': self.primary_diagnosis,
            'num_procedures': self.num_procedures,
            'days_in_hospital': self.days_in_hospital,
            'comorbidity_score': self.comorbidity_score,
            'discharge_to': self.discharge_to,
            'readmitted': self.readmitted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def save(self, *args, **kwargs):
        """Update timestamp on save"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super(Patient, self).save(*args, **kwargs)

    def to_feature_vector(self) -> dict:
        """Convert patient data to feature vector for ML model"""
        return {
            'age': self.age,
            'gender': self.gender,
            'primary_diagnosis': self.primary_diagnosis,
            'num_procedures': self.num_procedures,
            'days_in_hospital': self.days_in_hospital,
            'comorbidity_score': self.comorbidity_score,
            'discharge_to': self.discharge_to
        }

data = {
    'age': 65,
    'gender': 'M',
    'primary_diagnosis': 'diagnosis_code',
    'num_procedures': 2,
    'days_in_hospital': 5,
    'comorbidity_score': 3,
    'discharge_to': 'home'
} 