from mongoengine import connect
from datetime import datetime, timedelta
import random
from faker import Faker
from app.models.patient import Patient
from app.utils.prediction import StrokePredictor

fake = Faker(['en_us'])  # Using Indian English locale as it's closest to Pakistani names
fake.seed_instance(42)   # For reproducibility
predictor = StrokePredictor()

CREATORS = ['MadCkull', 'Awais Anwar', 'Nida Yasir', 'Dr. Irfan', 'Dr. Hassan', 
            'Dr. Muqaddas', 'Dr. Laraib', 'Dr. Kinza', 'Dr. Atiqa', 'Dr. Nadeem']


def customize_name():
    """Generate Pakistani-style name using Faker"""
    name = fake.name().split()
    # Take first and last name only
    return f"{name[0]} {name[-1]}"

def generate_health_metrics(age):
    if age < 18:
        bmi = round(random.uniform(18.5, 24.9), 1)
        glucose = round(random.uniform(70, 100), 1)
    elif age < 40:
        bmi = round(random.uniform(20.0, 27.0), 1)
        glucose = round(random.uniform(80, 140), 1)
    else:
        bmi = round(random.uniform(22.0, 32.0), 1)
        glucose = round(random.uniform(90, 180), 1)
    return bmi, glucose

def get_work_type(age):
    if age < 18:
        return "Children"
    elif age < 23:
        return random.choice(["Never Worked", "Private"])
    else:
        return random.choice(["Govt Job", "Private", "Self-Employed"])

def generate_patient_data():
    age = random.randint(15, 115)
    gender = random.choice(["Male", "Female"])
    bmi, glucose = generate_health_metrics(age)
    work_type = get_work_type(age)
    
    data = {
        'gender': gender,
        'age': str(age),
        'hypertension': str(random.randint(0, 1)),
        'heart_disease': str(random.randint(0, 1)),
        'ever_married': 'Yes' if age > 22 and random.random() > 0.3 else 'No',
        'residence_type': random.choice(['Urban', 'Rural']),
        'avg_glucose_level': str(glucose),
        'bmi': str(bmi),
        'work_type': work_type,
        'smoking_status': random.choice(['Never Smoked', 'Formerly Smoked', 'Smokes', 'Unknown'])
    }
    
    risk = predictor.predict_risk(data)
    
    return Patient(
        patient_id=str(random.randint(400000000, 499999999)),
        name=customize_name(),
        age=age,
        gender=gender,
        ever_married=data['ever_married'],
        work_type=work_type,
        residence_type=data['residence_type'],
        heart_disease='Yes' if data['heart_disease'] == '1' else 'No',
        hypertension='Yes' if data['hypertension'] == '1' else 'No',
        avg_glucose_level=glucose,
        bmi=bmi,
        smoking_status=data['smoking_status'],
        stroke_risk=risk,
        record_entry_date=datetime.now() - timedelta(days=random.randint(0, 3*365)),
        created_by=random.choice(CREATORS)
    )

def generate_database(num_records=5460):
    connect('stroke_prediction')
    
    for _ in range(num_records):
        try:
            patient = generate_patient_data()
            patient.save()
        except Exception as e:
            print(f"Error generating patient: {str(e)}")
    
    print(f"Successfully generated {num_records} patient records")

if __name__ == "__main__":
    generate_database()