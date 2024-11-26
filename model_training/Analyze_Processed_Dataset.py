# Analyze_Processed_Dataset.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def analyze_processed_dataset(file_path):
    """Analyze the processed stroke dataset and generate insights"""
    print("\nANALYZING PROCESSED STROKE DATASET")
    print("="*50)
    
    # Load DataSet (Processed)
    df = pd.read_csv(file_path)
    
    # Create output directory for plots
    output_dir = Path('Processed_Analysis_Outputs')
    output_dir.mkdir(exist_ok=True)
    
    # Basic Information
    print("\n1. DATASET OVERVIEW")
    print("-"*40)
    print(f"Total Records: {len(df):,}")
    print(f"Total Features: {len(df.columns)-1}")  # -1 for stroke column
    print(f"Stroke Cases: {df['stroke'].sum():,}")
    print(f"Stroke Percentage: {(df['stroke'].mean()*100):.2f}%")
    
    # Feature Statistics
    print("\n2. FEATURE STATISTICS")
    print("-"*40)
    stats = df.describe().round(3)
    print(stats)
    
    # Save feature statistics to CSV
    stats.to_csv(output_dir / 'feature_statistics.csv')
    
    # Feature Correlations with Target
    print("\n3. FEATURE CORRELATIONS WITH STROKE")
    print("-"*40)
    correlations = df.corr()['stroke'].sort_values(ascending=False)
    print("\nTop Positive Correlations:")
    print(correlations[correlations > 0][1:6])  # Top 5 positive correlations
    print("\nTop Negative Correlations:")
    print(correlations[correlations < 0][:5])   # Top 5 negative correlations
    
    # Correlation plot
    plt.figure(figsize=(12, 6))
    correlations[1:].sort_values().plot(kind='barh')
    plt.title('Feature Correlations with Stroke')
    plt.xlabel('Correlation Coefficient')
    plt.tight_layout()
    plt.savefig(output_dir / 'feature_correlations.png')
    plt.close()
    
    # Distribution Analysis
    print("\n4. FEATURE DISTRIBUTIONS")
    print("-"*40)
    
    # Plot distributions for numerical features
    numerical_features = df.select_dtypes(include=[np.number]).columns
    numerical_features = [col for col in numerical_features if col != 'stroke']
    
    n_cols = 3
    n_rows = (len(numerical_features) + n_cols - 1) // n_cols
    plt.figure(figsize=(15, 5*n_rows))
    
    for i, feature in enumerate(numerical_features, 1):
        plt.subplot(n_rows, n_cols, i)
        sns.histplot(data=df, x=feature, hue='stroke', bins=30)
        plt.title(f'{feature} Distribution')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'feature_distributions.png')
    plt.close()
    
    # Class Balance Analysis
    print("\n5. CLASS BALANCE ANALYSIS")
    print("-"*40)
    class_balance = df['stroke'].value_counts()
    print("\nClass Distribution:")
    print(class_balance)
    print("\nClass Percentages:")
    print((class_balance / len(df) * 100).round(2))
    
    # Class balance plot
    plt.figure(figsize=(8, 6))
    class_balance.plot(kind='bar')
    plt.title('Class Distribution')
    plt.xlabel('Stroke')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(output_dir / 'class_distribution.png')
    plt.close()
    
    # Feature Value Ranges
    print("\n6. FEATURE VALUE RANGES")
    print("-"*40)
    for column in df.columns:
        if column != 'stroke':
            print(f"\n{column}:")
            print(f"Min: {df[column].min():.3f}")
            print(f"Max: {df[column].max():.3f}")
            print(f"Mean: {df[column].mean():.3f}")
            print(f"Std: {df[column].std():.3f}")
    
    # Correlation Matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0, fmt='.2f')
    plt.title('Feature Correlation Matrix')
    plt.tight_layout()
    plt.savefig(output_dir / 'correlation_matrix.png')
    plt.close()
    
    # Binary Features Analysis
    binary_features = [col for col in df.columns if df[col].nunique() <= 2 and col != 'stroke']
    if binary_features:
        print("\n7. BINARY FEATURES ANALYSIS")
        print("-"*40)
        for col in binary_features:
            positive_rate = df[col].mean() * 100
            stroke_rate = df[df[col] == 1]['stroke'].mean() * 100
            print(f"\n{col}:")
            print(f"Positive Rate: {positive_rate:.2f}%")
            print(f"Stroke Rate when Positive: {stroke_rate:.2f}%")
    
    # Data Quality Check
    print("\n8. DATA QUALITY CHECK")
    print("-"*40)
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("\nMissing Values:")
        print(missing[missing > 0])
    else:
        print("No missing values found!")
    
    # Check for infinite values
    infinites = df.isin([np.inf, -np.inf]).sum()
    if infinites.sum() > 0:
        print("\nInfinite Values:")
        print(infinites[infinites > 0])
    else:
        print("No infinite values found!")
    
    print(f"\nAnalysis completed! Results saved in '{output_dir}' directory.")

if __name__ == "__main__":
    analyze_processed_dataset('ModelTrainingFiles/ProcessedStrokeDataset.csv')