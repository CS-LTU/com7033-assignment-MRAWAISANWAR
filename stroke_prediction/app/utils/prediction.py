from keras.models import load_model # type: ignore
import numpy as np
import pandas as pd
import pickle
import os
from pathlib import Path

class StrokePredictor:
    def __init__(self):
        base_path = Path(os.path.dirname(__file__))
        models_path = base_path.parent / 'static' / 'models'
        
        # Load the model
        self.model = load_model(models_path / 'stroke_prediction_model_Best.keras')
        
        # Load preprocessors
        with open(models_path / 'preprocessors.pkl', 'rb') as f:
            preprocessors = pickle.load(f)
            self.scaler = preprocessors['scaler']
            self.label_encoders = preprocessors['label_encoders']
            self.imputer = preprocessors['imputer']
        
        # Define expected columns and their order
        self.EXPECTED_COLUMNS = [
            'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
            'Residence_type', 'avg_glucose_level', 'bmi',
            'work_type_Govt_job', 'work_type_Never_worked', 'work_type_Private',
            'work_type_Self-employed', 'work_type_children',
            'smoking_status_Unknown', 'smoking_status_formerly smoked',
            'smoking_status_never smoked', 'smoking_status_smokes'
        ]
        
        # Define numerical columns
        self.NUMERICAL_COLUMNS = ['age', 'avg_glucose_level', 'bmi']

    def _preprocess_data(self, data):
        """Preprocess patient data for prediction"""
        try:
            # Create DataFrame with one row
            df = pd.DataFrame([{
                'gender': data['gender'],
                'age': float(data['age']),
                'hypertension': int(data['hypertension']),
                'heart_disease': int(data['heart_disease']),
                'ever_married': data['ever_married'],
                'Residence_type': data['residence_type'].title(),
                'avg_glucose_level': float(data['avg_glucose_level']),
                'bmi': float(data['bmi']),
                'work_type': data['work_type'],
                'smoking_status': data['smoking_status']
            }])
            
            # Handle 'Other' gender
            df.loc[df['gender'] == 'Other', 'gender'] = 'Female'
            
            # Encode categorical variables
            for col in ['gender', 'ever_married', 'Residence_type']:
                df[col] = self.label_encoders[col].transform(df[col])
            
            # Create a separate DataFrame for numerical features
            numerical_df = df[self.NUMERICAL_COLUMNS].copy()
            
            # Handle missing values in numerical columns
            numerical_df = pd.DataFrame(
                self.imputer.transform(numerical_df),
                columns=self.NUMERICAL_COLUMNS
            )
            
            # Scale numerical features
            numerical_df = pd.DataFrame(
                self.scaler.transform(numerical_df),
                columns=self.NUMERICAL_COLUMNS
            )
            
            # Update original DataFrame with scaled values
            df[self.NUMERICAL_COLUMNS] = numerical_df
            
            # One-hot encode work_type and smoking_status
            df = pd.get_dummies(df, columns=['work_type', 'smoking_status'])
            
            # Add missing columns if any
            for col in self.EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = 0
            
            # Ensure columns are in correct order
            df = df[self.EXPECTED_COLUMNS]
            
            return df
            
        except Exception as e:
            print(f"Preprocessing error details: {str(e)}")  # For debugging
            raise ValueError(f"Error preprocessing data: {str(e)}")

    def validate_input(self, data):
        """Validate input data before prediction"""
        required_fields = [
            'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
            'residence_type', 'avg_glucose_level', 'bmi', 'work_type', 'smoking_status'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            if data[field] is None or str(data[field]).strip() == '':
                raise ValueError(f"Field cannot be empty: {field}")
        
        try:
            # Validate numeric fields
            age = float(data['age'])
            glucose = float(data['avg_glucose_level'])
            bmi = float(data['bmi'])
            hypertension = int(data['hypertension'])
            heart_disease = int(data['heart_disease'])
            
            # Range validations
            if not (0 <= age <= 120):
                raise ValueError("Age must be between 0 and 120")
            if not (0 <= glucose <= 300):
                raise ValueError("Glucose level must be between 0 and 300")
            if not (10 <= bmi <= 100):
                raise ValueError("BMI must be between 10 and 100")
            if hypertension not in [0, 1]:
                raise ValueError("Hypertension must be 0 or 1")
            if heart_disease not in [0, 1]:
                raise ValueError("Heart disease must be 0 or 1")
                
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {str(e)}")

    def predict_risk(self, patient_data):
        """Predict stroke risk for a patient"""
        try:
            # Validate input
            self.validate_input(patient_data)
            
            # Preprocess data
            processed_data = self._preprocess_data(patient_data)
            
            # Get prediction
            prediction = self.model.predict(processed_data)[0][0]
            
            # Convert to percentage and round appropriately
            risk_percentage = prediction * 100
            
            # Round based on value ranges
            if risk_percentage > 90:
                return 90.0  # Cap at 90% for very high risk
            elif risk_percentage < 0.01:
                return round(risk_percentage, 4)
            elif risk_percentage < 0.1:
                return round(risk_percentage, 3)
            elif risk_percentage < 1:
                return round(risk_percentage, 2)
            elif risk_percentage < 10:
                return round(risk_percentage, 1)
            else:
                return round(risk_percentage, 1)
            
        except Exception as e:
            print(f"Prediction error details: {str(e)}")  # For debugging
            raise ValueError(f"Prediction error: {str(e)}")