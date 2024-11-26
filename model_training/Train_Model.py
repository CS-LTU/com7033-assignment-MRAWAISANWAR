import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from imblearn.over_sampling import SMOTE
import tensorflow as tf
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from tensorflow.keras.callbacks import ( # type: ignore
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
)

class StrokeModelTrainer:
    def __init__(self, processed_data_path, model_dir='stroke_prediction/app/static/models'):
        self.data_path = processed_data_path
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = Path('Training_Outputs')  # Output directory for plots
        self.history = None
        self.best_model = None
        self.metrics = {}

        self.output_dir.mkdir(exist_ok=True)
        
        # Set random seeds
        np.random.seed(42)
        tf.random.set_seed(42)

    def load_data(self):
        """Load and split the processed dataset"""
        print("Loading and preparing data...")
        df = pd.read_csv(self.data_path)
        
        # Split features and target
        X = df.drop('stroke', axis=1)
        y = df['stroke']
        
        # Split into train, validation, and test sets
        X_temp, self.X_test, y_temp, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
            X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp
        )
        
        print(f"Training set shape: {self.X_train.shape}")
        print(f"Validation set shape: {self.X_val.shape}")
        print(f"Test set shape: {self.X_test.shape}")
        
        # Handle class imbalance using SMOTE
        smote = SMOTE(random_state=42)
        self.X_train_balanced, self.y_train_balanced = smote.fit_resample(self.X_train, self.y_train)
        print(f"Balanced training set shape: {self.X_train_balanced.shape}")

    def build_model(self, input_dim):
        """Build the neural network model"""
        model = Sequential([
            # Input layer with batch normalization
            Dense(128, input_dim=input_dim, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            # Hidden layers
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            # Output layer
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        
        return model

    def train_model(self, epochs=200, batch_size=32):
        """Train the model with early stopping and learning rate reduction"""
        print("\nTraining model...")
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_auc',
                patience=100,
                restore_best_weights=True,
                mode='max'
            ),
            ModelCheckpoint(
                self.model_dir / 'stroke_prediction_model_Best.keras',
                monitor='val_auc',
                save_best_only=True,
                mode='max'
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=10,
                min_lr=0.00001
            )
        ]
        
        # Build and train model
        model = self.build_model(self.X_train.shape[1])
        
        self.history = model.fit(
            self.X_train_balanced, self.y_train_balanced,
            validation_data=(self.X_val, self.y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Load best model
        self.best_model = tf.keras.models.load_model(
            self.model_dir / 'stroke_prediction_model_Best.keras'
        )

    def evaluate_model(self):
        """Evaluate the model's performance"""
        print("\nEvaluating model...")
        
        # Predictions
        y_pred_proba = self.best_model.predict(self.X_test)
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Calculate metrics
        self.metrics = {
            'accuracy': accuracy_score(self.y_test, y_pred),
            'precision': precision_score(self.y_test, y_pred),
            'recall': recall_score(self.y_test, y_pred),
            'f1': f1_score(self.y_test, y_pred),
            'auc_roc': roc_auc_score(self.y_test, y_pred_proba)
        }
        
        # Print results
        print("\nModel Performance Metrics:")
        for metric, value in self.metrics.items():
            print(f"{metric.upper()}: {value:.4f}")
        
        print("\nClassification Report:")
        print(classification_report(self.y_test, y_pred))
        
        # Save metrics
        with open(self.model_dir / 'model_metrics.json', 'w') as f:
            json.dump(self.metrics, f, indent=4)

    def plot_training_history(self):
        """Plot and save training history"""

        # Plot accuracy
        plt.figure(figsize=(10, 6))
        plt.plot(self.history.history['accuracy'])
        plt.plot(self.history.history['val_accuracy'])
        plt.title('Model Accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='lower right')
        plt.savefig(self.output_dir / 'accuracy.png')
        plt.close()
        
        # Plot loss
        plt.figure(figsize=(10, 6))
        plt.plot(self.history.history['loss'])
        plt.plot(self.history.history['val_loss'])
        plt.title('Model Loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='upper right')
        plt.savefig(self.output_dir / 'loss.png')
        plt.close()
        
        # Plot AUC
        plt.figure(figsize=(10, 6))
        plt.plot(self.history.history['auc'])
        plt.plot(self.history.history['val_auc'])
        plt.title('Model AUC')
        plt.ylabel('AUC')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='lower right')
        plt.savefig(self.output_dir / 'auc.png')
        plt.close()

    def test_model_predictions(self):
        """Test model predictions on sample cases"""
        print("\nTesting model predictions on sample cases...")
        
        # Sample test cases (with Scaled Values)
        test_cases = [
            {
                'gender': 1,
                'age': 2.1,
                'hypertension': 1,
                'heart_disease': 1,
                'ever_married': 1,
                'Residence_type': 1,
                'avg_glucose_level': 1.5,
                'bmi': 0.8,
                'work_type_Private': 1,
                'work_type_Self-employed': 0,
                'work_type_Govt_job': 0,
                'work_type_Never_worked': 0,
                'work_type_children': 0,
                'smoking_status_smokes': 1,
                'smoking_status_formerly smoked': 0,
                'smoking_status_never smoked': 0,
                'smoking_status_Unknown': 0
            },
            {
                'gender': 0,
                'age': -1.2,
                'hypertension': 0,
                'heart_disease': 0,
                'ever_married': 0,
                'Residence_type': 0,
                'avg_glucose_level': -0.8,
                'bmi': -0.5,
                'work_type_Private': 1,
                'work_type_Self-employed': 0,
                'work_type_Govt_job': 0,
                'work_type_Never_worked': 0,
                'work_type_children': 0,
                'smoking_status_never smoked': 1,
                'smoking_status_formerly smoked': 0,
                'smoking_status_smokes': 0,
                'smoking_status_Unknown': 0
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            X_test = pd.DataFrame([case])
            prediction = self.best_model.predict(X_test)[0][0]
            print(f"\nTest Case {i}:")
            print(f"Predicted Stroke Probability: {prediction:.4f}")
            print(f"Risk Level: {self.get_risk_level(prediction)}")

    @staticmethod
    def get_risk_level(probability):
        """Convert probability to risk level"""
        if probability < 0.2:
            return "Low"
        elif probability < 0.4:
            return "Moderate"
        elif probability < 0.6:
            return "High"
        elif probability < 0.8:
            return "Very High"
        else:
            return "Critical"

    def train_and_evaluate(self):
        """Main method to train and evaluate the model"""
        print("Starting model training process...")
        print("=" * 50)
        
        # Training process
        self.load_data()
        self.train_model()
        self.evaluate_model()
        self.plot_training_history()
        self.test_model_predictions()
        
        print("\nTraining process completed successfully!")
        print(f"Model and metrics saved in: {self.model_dir}")

if __name__ == "__main__":
    trainer = StrokeModelTrainer(
        processed_data_path='ModelTrainingFiles/ProcessedStrokeDataset.csv'
    )
    trainer.train_and_evaluate()