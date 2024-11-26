# Analyze_Dataset.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def analyze_stroke_dataset(file_path):
    """Analyze the raw stroke dataset and generate insights"""
    print("\n=== STROKE DATASET ANALYSIS ===")
    
    # Load dataset
    df = pd.read_csv(file_path)
    df['bmi'] = pd.to_numeric(df['bmi'], errors='coerce')
    
    # Output directory for plots
    output_dir = Path('Analysis_Outputs')
    output_dir.mkdir(exist_ok=True)
    
    # Basic Dataset Information
    print("\n1. BASIC INFORMATION")
    print("-" * 40)
    print(f"Total Records: {len(df):,}")
    print(f"Total Features: {len(df.columns)}")
    print("\nFeature Types:")
    print(df.dtypes)
    
    # Missing Values Analysis
    print("\n2. MISSING VALUES")
    print("-" * 40)
    missing = df.isnull().sum()
    missing_pct = (missing/len(df))*100
    missing_info = pd.DataFrame({
        'Missing Values': missing,
        'Percentage': missing_pct
    })
    print(missing_info[missing_info['Missing Values'] > 0])
    
    # Target Distribution
    print("\n3. STROKE DISTRIBUTION")
    print("-" * 40)
    stroke_dist = df['stroke'].value_counts()
    stroke_pct = df['stroke'].value_counts(normalize=True) * 100
    print("Counts:")
    print(stroke_dist)
    print("\nPercentages:")
    print(stroke_pct.round(2))
    
    # Save stroke distribution plot
    plt.figure(figsize=(8, 6))
    df['stroke'].value_counts().plot(kind='bar')
    plt.title('Stroke Distribution')
    plt.xlabel('Stroke')
    plt.ylabel('Count')
    plt.savefig(output_dir / 'stroke_distribution.png')
    plt.close()
    
    # Age Analysis
    print("\n4. AGE ANALYSIS")
    print("-" * 40)
    print("\nAge Statistics:")
    print(df['age'].describe().round(2))
    
    # Age distribution plot
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='age', hue='stroke', bins=30)
    plt.title('Age Distribution by Stroke')
    plt.savefig(output_dir / 'age_distribution.png')
    plt.close()
    
    # Medical Conditions Analysis
    print("\n5. MEDICAL CONDITIONS")
    print("-" * 40)
    conditions = ['hypertension', 'heart_disease']
    for condition in conditions:
        print(f"\n{condition.title()} Distribution:")
        cond_dist = df[condition].value_counts()
        cond_pct = df[condition].value_counts(normalize=True) * 100
        print("Count:")
        print(cond_dist)
        print("\nPercentage:")
        print(cond_pct.round(2))
        
        # Calculate stroke rate for each condition value
        stroke_rates = df.groupby(condition)['stroke'].mean() * 100
        print("\nStroke Rate:")
        print(stroke_rates.round(2))
    
    # Glucose Level Analysis
    print("\n6. GLUCOSE LEVEL ANALYSIS")
    print("-" * 40)
    print("\nGlucose Level Statistics:")
    print(df['avg_glucose_level'].describe().round(2))
    
    # Glucose distribution plot
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='avg_glucose_level', hue='stroke', bins=30)
    plt.title('Glucose Level Distribution by Stroke')
    plt.savefig(output_dir / 'glucose_distribution.png')
    plt.close()
    
    # BMI Analysis
    print("\n7. BMI ANALYSIS")
    print("-" * 40)
    print("\nBMI Statistics (excluding NA):")
    print(df['bmi'].describe().round(2))
    
    # BMI distribution plot
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df[df['bmi'].notna()], x='bmi', hue='stroke', bins=30)
    plt.title('BMI Distribution by Stroke')
    plt.savefig(output_dir / 'bmi_distribution.png')
    plt.close()
    
    # Categorical Variables Analysis
    print("\n8. CATEGORICAL VARIABLES")
    print("-" * 40)
    categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
    
    for col in categorical_cols:
        print(f"\n{col.upper()} Analysis:")
        # Distribution
        dist = df[col].value_counts()
        pct = df[col].value_counts(normalize=True) * 100
        # Stroke rate by category
        stroke_rate = df.groupby(col)['stroke'].mean() * 100
        
        analysis = pd.DataFrame({
            'Count': dist,
            'Percentage': pct,
            'Stroke_Rate': stroke_rate
        }).round(2)
        print(analysis)
        
        # Bar plot for stroke rate by category
        plt.figure(figsize=(10, 6))
        stroke_rate.plot(kind='bar')
        plt.title(f'Stroke Rate by {col}')
        plt.ylabel('Stroke Rate (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / f'stroke_rate_by_{col}.png')
        plt.close()
    
    # Correlation Analysis
    print("\n9. CORRELATION ANALYSIS")
    print("-" * 40)
    numeric_cols = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi', 'stroke']
    correlation_matrix = df[numeric_cols].corr()
    print("\nCorrelation with Stroke:")
    print(correlation_matrix['stroke'].sort_values(ascending=False).round(3))
    
    # Correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_heatmap.png')
    plt.close()
    
    print("\nAnalysis completed! Plots saved in 'analysis_outputs' directory.")

if __name__ == "__main__":
    analyze_stroke_dataset('ModelTrainingFiles/StrokeDataset.csv')