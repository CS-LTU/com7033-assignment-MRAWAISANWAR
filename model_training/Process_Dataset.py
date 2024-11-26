# Process_Dataset.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import pickle
import warnings
import os
from pathlib import Path
warnings.filterwarnings('ignore')

class StrokeDataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.imputer = SimpleImputer(strategy='median')
        self.feature_ranges = {}
        self.processed_columns = [
            'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
            'Residence_type', 'avg_glucose_level', 'bmi',
            'work_type_Govt_job', 'work_type_Never_worked', 'work_type_Private',
            'work_type_Self-employed', 'work_type_children',
            'smoking_status_Unknown', 'smoking_status_formerly smoked',
            'smoking_status_never smoked', 'smoking_status_smokes'
        ]

    def clean_dataset(self, df):
        """Clean the dataset by handling missing values and invalid entries"""
        print("Cleaning dataset...")
        initial_size = len(df)
        
        # Create a copy (To avoid modifying the original)
        df = df.copy()
        
        # Handle missing BMI values
        df['bmi'] = pd.to_numeric(df['bmi'], errors='coerce')
        
        # Remove extreme outliers
        df = df[
            (df['age'] >= 0) & (df['age'] <= 100) &  # Realistic age range
            (df['avg_glucose_level'] >= 50) & (df['avg_glucose_level'] <= 300)  # Realistic glucose range
        ]
        
        # Handle 'Other' gender
        df.loc[df['gender'] == 'Other', 'gender'] = 'Female'
        
        print(f"Records removed: {initial_size - len(df)} ({((initial_size - len(df))/initial_size)*100:.2f}%)")
        return df

    def encode_categorical(self, df, fit=True):
        """Encode categorical variables"""
        df = df.copy()
        
        # Label encoding for binary/ordinal categories
        categorical_cols = ['gender', 'ever_married', 'Residence_type']
        for col in categorical_cols:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[col] = self.label_encoders[col].transform(df[col])
        
        # One-hot encoding for nominal categories
        df = pd.get_dummies(df, columns=['work_type', 'smoking_status'])
        
        return df

    def scale_numerical(self, df, fit=True):
        """Scale numerical features"""
        df = df.copy()
        numerical_cols = ['age', 'avg_glucose_level', 'bmi']
        
        # Impute missing values
        if fit:
            df[numerical_cols] = self.imputer.fit_transform(df[numerical_cols])
        else:
            df[numerical_cols] = self.imputer.transform(df[numerical_cols])
        
        # Scale features
        if fit:
            df[numerical_cols] = self.scaler.fit_transform(df[numerical_cols])
        else:
            df[numerical_cols] = self.scaler.transform(df[numerical_cols])
            
        return df

    def process_dataset(self, input_path, output_path=None, is_training=True):
        """Main processing function"""
        print("\nProcessing Stroke Dataset...")
        print("="*50)
        
        # Load dataset
        df = pd.read_csv(input_path)
        print(f"Initial records: {len(df)}")
        
        # Store original feature ranges if training
        if is_training:
            self.feature_ranges = {
                'age': {'min': df['age'].min(), 'max': df['age'].max()},
                'bmi': {'min': df['bmi'].min(), 'max': df['bmi'].max()},
                'glucose': {'min': df['avg_glucose_level'].min(), 'max': df['avg_glucose_level'].max()}
            }
        
        # Clean dataset
        df = self.clean_dataset(df)
        
        # Store target if training
        if is_training:
            target = df['stroke'].copy()
            df = df.drop(['stroke', 'id'] if 'id' in df.columns else ['stroke'], axis=1)
        else:
            if 'id' in df.columns:
                df = df.drop('id', axis=1)
                
        # Apply preprocessing
        df = self.encode_categorical(df, fit=is_training)
        df = self.scale_numerical(df, fit=is_training)
        
        # Ensure all expected columns exist
        for col in self.processed_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Select only the required columns (in correct order)
        df = df[self.processed_columns]
        
        # Save preprocessors if training
        if is_training:
            # Create directory if it doesn't exist
            os.makedirs('stroke_prediction/app/static/models', exist_ok=True)
            
            preprocessors = {
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'imputer': self.imputer,
                'feature_ranges': self.feature_ranges
            }
            with open('stroke_prediction/app/static/models/preprocessors.pkl', 'wb') as f:
                pickle.dump(preprocessors, f)
            print("\nPreprocessors saved!")
            
            # Save processed dataset
            if output_path:
                processed_df = pd.concat([df, target], axis=1)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                processed_df.to_csv(output_path, index=False)
                print(f"Processed dataset saved to: {output_path}")
            
            return df, target
        
        return df

    def print_dataset_stats(self, df, target=None):
        """Print dataset statistics"""
        print("\nDataset Statistics:")
        print("="*50)
        print(f"Total features: {len(df.columns)}")
        if target is not None:
            print(f"Stroke cases: {target.sum()}")
            print(f"Stroke percentage: {(target.mean()*100):.2f}%")
        print("\nFeature names:")
        for col in df.columns:
            print(f"- {col}")

if __name__ == "__main__":
    # Initialize processor
    processor = StrokeDataProcessor()
    
    # Process training dataset
    X, y = processor.process_dataset(
        input_path='ModelTrainingFiles/StrokeDataset.csv',
        output_path='ModelTrainingFiles/ProcessedStrokeDataset.csv',
        is_training=True
    )
    
    # Print statistics
    processor.print_dataset_stats(X, y)