from stroke_prediction.app.models.patient import Patient
from mongoengine import connect
import os
from dotenv import load_dotenv

load_dotenv()
connect(host=os.getenv("MONGO_URI"))

# Example: Add a test patient record
test_patient = Patient(
    patient_id="123456",
    name="John Doe",
    age=45,
    gender="Male",
    ever_married="Yes",
    work_type="Private",
    residence_type="Urban",
    heart_disease="Yes",
    hypertension="No",
    avg_glucose_level=105.4,
    bmi=26.3,
    smoking_status="Never Smoked",
    stroke_risk=15.5,
    created_by="admin"
)
test_patient.save()
