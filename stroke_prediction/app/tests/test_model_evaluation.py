# tests/test_model_evaluation.py
import pytest
import numpy as np
import tensorflow as tf
import pandas as pd

def test_model_prediction(model, preprocessors, test_data):
    """Test model predictions and evaluate performance"""
    try:
        # Create DataFrame
        df = pd.DataFrame([test_data])
        
        # Handle 'Other' gender if present
        df.loc[df['gender'] == 'Other', 'gender'] = 'Female'
        
        # Encode categorical variables
        for col in ['gender', 'ever_married', 'Residence_type']:
            df[col] = preprocessors['label_encoders'][col].transform(df[col])
        
        # Create numerical features DataFrame
        numerical_cols = ['age', 'avg_glucose_level', 'bmi']
        df_numerical = df[numerical_cols].copy()
        
        # Handle missing values and scale
        df_numerical = pd.DataFrame(
            preprocessors['imputer'].transform(df_numerical),
            columns=numerical_cols
        )
        df_numerical = pd.DataFrame(
            preprocessors['scaler'].transform(df_numerical),
            columns=numerical_cols
        )
        
        # Update original DataFrame
        df[numerical_cols] = df_numerical
        
        # One-hot encode categorical variables
        df = pd.get_dummies(df, columns=['work_type', 'smoking_status'])
        
        # Ensure all expected columns exist
        expected_columns = [
            'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
            'Residence_type', 'avg_glucose_level', 'bmi',
            'work_type_Govt_job', 'work_type_Never_worked', 'work_type_Private',
            'work_type_Self-employed', 'work_type_children',
            'smoking_status_Unknown', 'smoking_status_formerly smoked',
            'smoking_status_never smoked', 'smoking_status_smokes'
        ]
        
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 0
                
        # Ensure columns are in correct order
        df = df[expected_columns]
        
        # Make prediction
        prediction = model.predict(df)
        
        # Assertions
        assert prediction is not None, "Model should return a prediction"
        assert isinstance(prediction, np.ndarray), "Prediction should be numpy array"
        assert len(prediction.shape) == 2, "Prediction should be 2D array"
        assert prediction.shape[1] == 1, "Prediction should have 1 output"
        assert 0 <= prediction[0][0] <= 1, "Prediction should be between 0 and 1"
        
    except Exception as e:
        pytest.fail(f"Prediction failed with error: {str(e)}")

def test_model_structure(model):
    """Test the model's architecture"""
    # Test basic model properties
    assert isinstance(model, tf.keras.Model), "Should be a Keras model"
    assert model.count_params() > 0, "Should have trainable parameters"
    
    # Test output layer shape
    output_shape = model.layers[-1].get_config()['units']
    assert output_shape == 1, "Output layer should have 1 unit"
    
    # Test if model is compiled
    assert model.optimizer is not None, "Should have optimizer"
    assert model.loss is not None, "Should have loss function"

def test_preprocessors(preprocessors):
    """Test the preprocessor components"""
    # Check required components
    assert 'scaler' in preprocessors, "Should have scaler"
    assert 'label_encoders' in preprocessors, "Should have label_encoders"
    assert 'imputer' in preprocessors, "Should have imputer"
    
    # Check label encoders
    label_encoders = preprocessors['label_encoders']
    required_encoders = ['gender', 'ever_married', 'Residence_type']
    for encoder in required_encoders:
        assert encoder in label_encoders, f"Should have {encoder} encoder"