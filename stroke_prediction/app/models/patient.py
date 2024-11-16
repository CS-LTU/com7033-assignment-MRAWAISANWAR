# app/models/patient.py
from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, EnumField
from datetime import datetime

class Patient(Document):
    # Identification and Demographic Information
    patient_id = StringField(required=True, unique=True, min_value=6, max_value=6)
    name = StringField(required=True)
    age = IntField(required=True, min_value=5)
    gender = StringField(required=True, choices=["Male", "Female", "Other"])
    
    # Medical and Lifestyle Information
    ever_married = StringField(required=True, choices=["Yes", "No"])
    work_type = StringField(required=True, choices=["Children", "Govt Job", "Never Worked", "Private", "Self-Employed"])
    residence_type = StringField(required=True, choices=["Rural", "Urban"])
    heart_disease = StringField(required=True, choices=["Yes", "No"])
    hypertension = StringField(required=True, choices=["Yes", "No"])
    
    # Health Metrics
    avg_glucose_level = FloatField(required=True, min_value=0)
    bmi = FloatField(required=True, min_value=0)
    smoking_status = StringField(required=True, choices=["Smokes", "Formerly Smoked", "Never Smoked", "Unknown"])
    stroke_risk = FloatField(required=True, min_value=0, max_value=100)
    
    # Metadata
    record_entry_date = DateTimeField(default=datetime.now, required=True)
    created_by = StringField(required=True)
    updated_at = DateTimeField()
    updated_by = StringField()

    # Meta class for collection name and ordering
    meta = {
        'collection': 'patients',
        'ordering': ['-record_entry_date']  # Orders by newest records first
    }
