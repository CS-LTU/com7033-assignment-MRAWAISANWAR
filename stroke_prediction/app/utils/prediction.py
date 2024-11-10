# app/utils/prediction.py
from keras.models import load_model
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os

class StrokePredictor:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), '../static/models/stroke_prediction_model.keras')
        self.model = load_model(model_path)
        
        # Define expected columns and their order
        self.EXPECTED_COLUMNS = [
            'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
            'Residence_type', 'avg_glucose_level', 'bmi',
            'work_type_Govt_job', 'work_type_Never_worked', 'work_type_Private',
            'work_type_Self-employed', 'work_type_children',
            'smoking_status_Unknown', 'smoking_status_formerly smoked',
            'smoking_status_never smoked', 'smoking_status_smokes'
        ]
        
        # Initialize encoders
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()

    def _preprocess_data(self, data):
        """Preprocess a single patient's data for prediction"""
        try:
            # Create a DataFrame with one row
            df = pd.DataFrame([{
                'gender': data['gender'],
                'age': float(data['age']),
                'hypertension': int(data['hypertension']),
                'heart_disease': int(data['heart_disease']),
                'ever_married': data['ever_married'],
                'Residence_type': data['residence_type'].title(),  # Convert to match model's expectation
                'avg_glucose_level': float(data['avg_glucose_level']),
                'bmi': float(data['bmi']),
                'work_type': data['work_type'],
                'smoking_status': data['smoking_status']
            }])
            
            # Encode categorical variables
            categorical_cols = ['gender', 'ever_married', 'Residence_type']
            for col in categorical_cols:
                df[col] = self.label_encoder.fit_transform(df[col])
            
            # One-hot encode work_type and smoking_status
            df = pd.get_dummies(df, columns=['work_type', 'smoking_status'])
            
            # Add missing columns if any
            for col in self.EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = 0
                    
            # Ensure columns are in correct order
            df = df[self.EXPECTED_COLUMNS]
            
            # Scale features
            scaled_features = self.scaler.fit_transform(df)
            
            return scaled_features
            
        except Exception as e:
            raise ValueError(f"Error preprocessing data: {str(e)}")

    def predict_risk(self, patient_data):
        """Predict stroke risk for a patient"""
        try:
            # Preprocess the data
            processed_data = self._preprocess_data(patient_data)
            
            # Make prediction
            prediction = self.model.predict(processed_data)
            
            # Convert to risk percentage
            risk_percentage = int(prediction[0][0] * 100)
            
            # Ensure risk is between 0 and 100
            risk_percentage = max(0, min(100, risk_percentage))
            
            return risk_percentage
            
        except Exception as e:
            raise ValueError(f"Prediction error: {str(e)}")