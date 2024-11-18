import sys
import os
sys.path.append(os.path.abspath('D:/Other/Projects/StrokeWatch/com7033-assignment-MRAWAISANWAR'))

from stroke_prediction.app.utils.prediction import StrokePredictor

def predict_stroke_risk(patient_data=None):
    try:
        # Initialize predictor
        stroke_predictor = StrokePredictor()
        
        # Use default test patient if no data provided
        if patient_data is None:
            patient_data = {
                'gender': 'Male',
                'age': '45',
                'hypertension': '1',
                'heart_disease': '0',
                'ever_married': 'Yes',
                'residence_type': 'Urban',
                'avg_glucose_level': '110',
                'bmi': '28.6',
                'work_type': 'Self-employed',
                'smoking_status': 'formerly smoked'
            }
        
        # Validate input data
        print("\nValidating patient data...")
        stroke_predictor.validate_input(patient_data)

        # Get prediction
        print("Making prediction...")
        risk_percentage = stroke_predictor.predict_risk(patient_data)
        
        # Print formatted results
        print("\nPrediction Results:")
        print("-" * 40)
        print(f"Patient Profile:")
        print(f"- Age: {patient_data['age']}")
        print(f"- Gender: {patient_data['gender']}")
        print(f"- Health Conditions: {'Hypertension' if patient_data['hypertension'] == '1' else 'No Hypertension'}, "
              f"{'Heart Disease' if patient_data['heart_disease'] == '1' else 'No Heart Disease'}")
        print(f"- Lifestyle: {patient_data['smoking_status']}, BMI: {patient_data['bmi']}")
        print(f"\nPredicted Stroke Risk: {risk_percentage:.2f}%")
        
        # Determine risk level
        if risk_percentage < 1:
            risk_level = "Very Low"
        elif risk_percentage < 5:
            risk_level = "Low"
        elif risk_percentage < 15:
            risk_level = "Moderate"
        elif risk_percentage < 30:
            risk_level = "High"
        else:
            risk_level = "Very High"
        
        print(f"Risk Level: {risk_level}")
        
        return risk_percentage
        
    except Exception as e:
        print(f"\nError occurred during prediction:")
        print(f"Error message: {str(e)}")
        return None

if __name__ == "__main__":
    os.system('clear')
    # Test with default patient
    print("Testing with default patient data:")
    default_result = predict_stroke_risk()
    
    # Test with a high-risk patient
    print("\n\nTesting with high-risk patient data:")
    high_risk_patient = {
        'gender': 'Male',
        'age': '75',
        'hypertension': '1',
        'heart_disease': '1',
        'ever_married': 'Yes',
        'residence_type': 'Urban',
        'avg_glucose_level': '210',
        'bmi': '32.5',
        'work_type': 'Private',
        'smoking_status': 'smokes'
    }
    high_risk_result = predict_stroke_risk(high_risk_patient)
    
    # Test with a low-risk patient
    print("\n\nTesting with low-risk patient data:")
    low_risk_patient = {
        'gender': 'Female',
        'age': '25',
        'hypertension': '0',
        'heart_disease': '0',
        'ever_married': 'No',
        'residence_type': 'Rural',
        'avg_glucose_level': '85',
        'bmi': '22.1',
        'work_type': 'Private',
        'smoking_status': 'never smoked'
    }
    low_risk_result = predict_stroke_risk(low_risk_patient)