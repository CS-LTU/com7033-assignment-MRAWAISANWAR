import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle
import json
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve
)
from imblearn.over_sampling import SMOTE

class StrokeModelEvaluator:
    def __init__(self):
        self.model_path = 'stroke_prediction/app/static/models/stroke_prediction_model_Best.keras'
        self.preprocessor_path = 'stroke_prediction/app/static/models/preprocessors.pkl'
        self.output_dir = Path('ModelEvaluationResults')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load model and preprocessors
        print("Loading model and preprocessors...")
        self.model = tf.keras.models.load_model(self.model_path)
        with open(self.preprocessor_path, 'rb') as f:
            self.preprocessors = pickle.load(f)

    def preprocess_data(self, data_path):
        """Preprocess the data using saved preprocessors"""
        print("\nPreprocessing data...")
        
        # Read the data
        df = pd.read_csv(data_path)
        
        # Clean dataset
        df['bmi'] = pd.to_numeric(df['bmi'], errors='coerce')
        df = df[
            (df['age'] >= 0) & (df['age'] <= 100) &
            (df['avg_glucose_level'] >= 50) & (df['avg_glucose_level'] <= 300)
        ]
        df.loc[df['gender'] == 'Other', 'gender'] = 'Female'
        
        # Store target
        target = df['stroke'].copy() if 'stroke' in df.columns else None
        df = df.drop(['stroke', 'id'] if 'id' in df.columns else ['id'], axis=1)
        
        # Apply preprocessing steps using saved preprocessors
        # Label encoding
        for col, encoder in self.preprocessors['label_encoders'].items():
            df[col] = encoder.transform(df[col])
        
        # One-hot encoding
        df = pd.get_dummies(df, columns=['work_type', 'smoking_status'])
        
        # Numerical scaling
        numerical_cols = ['age', 'avg_glucose_level', 'bmi']
        df[numerical_cols] = self.preprocessors['imputer'].transform(df[numerical_cols])
        df[numerical_cols] = self.preprocessors['scaler'].transform(df[numerical_cols])
        
        # Ensure all expected columns are present
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
                
        # Reorder columns to match training data
        df = df[expected_columns]
        
        return df, target

    def evaluate_model(self, X, y):
        """Comprehensive model evaluation"""
        print("\nEvaluating model...")
        
        # Get predictions
        y_pred_proba = self.model.predict(X)
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred),
            'recall': recall_score(y, y_pred),
            'f1': f1_score(y, y_pred),
            'auc_roc': roc_auc_score(y, y_pred_proba)
        }
        
        # Save metrics
        with open(self.output_dir / 'evaluation_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=4)
        
        # Print metrics
        print("\nModel Performance Metrics:")
        for metric, value in metrics.items():
            print(f"{metric.upper()}: {value:.4f}")
        
        # Print classification report
        print("\nClassification Report:")
        print(classification_report(y, y_pred))
        
        # Plot confusion matrix
        self.plot_confusion_matrix(y, y_pred)
        
        # Plot ROC curve
        self.plot_roc_curve(y, y_pred_proba)
        
        # Plot Precision-Recall curve
        self.plot_precision_recall_curve(y, y_pred_proba)
        
        # Plot prediction distribution
        self.plot_prediction_distribution(y_pred_proba, y)
        
        # Feature importance analysis
        self.analyze_feature_importance(X)

    def plot_confusion_matrix(self, y_true, y_pred):
        """Plot and save confusion matrix"""
        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig(self.output_dir / 'confusion_matrix.png')
        plt.close()

    def plot_roc_curve(self, y_true, y_pred_proba):
        """Plot and save ROC curve"""
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        auc = roc_auc_score(y_true, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC curve (AUC = {auc:.3f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc='lower right')
        plt.savefig(self.output_dir / 'roc_curve.png')
        plt.close()

    def plot_precision_recall_curve(self, y_true, y_pred_proba):
        """Plot and save Precision-Recall curve"""
        precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.savefig(self.output_dir / 'precision_recall_curve.png')
        plt.close()

    def plot_prediction_distribution(self, y_pred_proba, y_true):
        """Plot and save prediction probability distribution"""
        plt.figure(figsize=(10, 6))
        sns.histplot(data=pd.DataFrame({
            'Probability': y_pred_proba.flatten(),
            'Actual': y_true
        }), x='Probability', hue='Actual', bins=50)
        plt.title('Prediction Probability Distribution')
        plt.savefig(self.output_dir / 'prediction_distribution.png')
        plt.close()

    def analyze_feature_importance(self, X):
        """Calculate feature importance using variance of predictions"""
        print("\nCalculating feature importance...")
        
        importance_scores = {}
        baseline_pred = self.model.predict(X).mean()
        
        for feature in X.columns:
            # Create a copy of the feature
            X_modified = X.copy()
            # Shuffle the feature to break its relationship with target
            X_modified[feature] = np.random.permutation(X_modified[feature])
            # Get new predictions
            new_pred = self.model.predict(X_modified).mean()
            # Calculate importance as absolute difference from baseline
            importance_scores[feature] = abs(baseline_pred - new_pred)
        
        # Create DataFrame of importance scores
        importance_df = pd.DataFrame({
            'Feature': list(importance_scores.keys()),
            'Importance': list(importance_scores.values())
        }).sort_values('Importance', ascending=False)
        
        # Plot feature importance
        plt.figure(figsize=(12, 8))
        plt.barh(importance_df['Feature'], importance_df['Importance'])
        plt.xlabel('Importance Score')
        plt.title('Feature Importance Analysis')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'feature_importance.png')
        plt.close()
        
        # Save feature importance to CSV
        importance_df.to_csv(self.output_dir / 'feature_importance.csv', index=False)
        print("Feature importance analysis completed!")

    def run_evaluation(self, data_path):
        """Main method to run the evaluation"""
        print("Starting model evaluation process...")
        print("=" * 50)
        
        # Process data
        X, y = self.preprocess_data(data_path)
        
        if y is None:
            raise ValueError("Target variable 'stroke' not found in the dataset!")
        
        # Evaluate model
        self.evaluate_model(X, y)
        
        print("\nEvaluation completed successfully!")
        print(f"Results saved in: {self.output_dir}")

if __name__ == "__main__":
    # Use raw string for Windows path
    data_path = r'ModelTrainingFiles/StrokeDataset.csv'
    evaluator = StrokeModelEvaluator()
    evaluator.run_evaluation(data_path)