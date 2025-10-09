import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer

def _capping_outliers(series, factor=1.5):
    """Helper function to cap outliers using the IQR method."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    # Capping: values outside bounds are replaced by the bounds
    return np.where(series < lower_bound, lower_bound, np.where(series > upper_bound, upper_bound, series))


def imtiaz_analyze(df, max_one_hot_categories=10, perform_outlier_capping=True, perform_scaling=True):
    """
    Performs comprehensive automated preprocessing (Cleaning, Imputation, Capping, Encoding, Scaling) 
    and Exploratory Data Analysis (EDA) on a DataFrame.

    :param df: Input Pandas DataFrame.
    :param max_one_hot_categories: Threshold for One-Hot Encoding (<= limit) vs Label Encoding (> limit).
    :param perform_outlier_capping: If True, uses IQR to cap outliers in numerical columns.
    :param perform_scaling: If True, applies StandardScaler to final numerical columns.
    :return: The fully processed, model-ready DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        print("Error: Please pass a valid Pandas DataFrame.")
        return None

    df_processed = df.copy() 
    print("=============================================")
    print("      ImtiazAnalysis: Pipeline Starting")
    print("=============================================")
    
    # ---------------------------------------------
    # 1. Cleaning: Duplicates & Types
    # ---------------------------------------------
    print("\n\n--- 1. Data Cleaning: Duplicates & Types ---")
    n_duplicates = df_processed.duplicated().sum()
    if n_duplicates > 0:
        print(f"Warning: Found {n_duplicates} duplicate row(s). Removing...")
        df_processed.drop_duplicates(inplace=True)
        print(f"New Shape: {df_processed.shape}")
    else:
        print("No duplicate rows found.")
    
    # Identify initial types
    numerical_cols = df_processed.select_dtypes(include=np.number).columns
    categorical_cols = df_processed.select_dtypes(include=['object', 'category']).columns

    # ---------------------------------------------
    # 2. Smart Imputation (Handling Missing Values)
    # ---------------------------------------------
    print("\n\n--- 2. Smart Imputation (Handling Missing Values) ---")
    
    # Numerical Imputation (Median)
    if len(numerical_cols) > 0 and df_processed[numerical_cols].isnull().any().any():
        num_imputer = SimpleImputer(strategy='median')
        df_processed[numerical_cols] = num_imputer.fit_transform(df_processed[numerical_cols])
        print(f"Numerical missing values imputed using: Median in {len(numerical_cols)} column(s).")
        
    # Categorical Imputation (Mode/Most Frequent)
    if len(categorical_cols) > 0 and df_processed[categorical_cols].isnull().any().any():
        cat_imputer = SimpleImputer(strategy='most_frequent')
        df_processed[categorical_cols] = cat_imputer.fit_transform(df_processed[categorical_cols])
        print(f"Categorical missing values imputed using: Mode in {len(categorical_cols)} column(s).")

    if not df_processed.isnull().any().any():
        print("All missing values successfully handled.")

    # ---------------------------------------------
    # 3. Outlier Capping (Preprocessing)
    # ---------------------------------------------
    if perform_outlier_capping and len(numerical_cols) > 0:
        print("\n\n--- 3. Outlier Capping (IQR Method) ---")
        for col in numerical_cols:
            df_processed[col] = _capping_outliers(df_processed[col])
        print("Outliers in numerical columns capped to IQR boundaries (1.5 * IQR).")
    
    # ---------------------------------------------
    # 4. Statistical Summary & Visualization (EDA)
    # ---------------------------------------------
    print("\n\n--- 4. Statistical Summary & Visualization ---")
    sns.set_style("whitegrid")
    
    if len(numerical_cols) > 0:
        print("\nNumerical Columns Descriptive Statistics:")
        print(df_processed[numerical_cols].describe(percentiles=[.25, .50, .75, .95]).T)
    
    if len(categorical_cols) > 0:
        print("\nCategorical Columns Unique Counts:")
        for col in categorical_cols:
            print(f"- {col}: {df_processed[col].nunique()} unique values")
            if df_processed[col].nunique() < 10:
                print(f"  Top 5 Counts:\n{df_processed[col].value_counts().head(5)}")

    # Numerical Plots (Distribution & Outliers)
    for col in numerical_cols:
        if df_processed[col].nunique() > 10:
            plt.figure(figsize=(12, 4))
            plt.subplot(1, 2, 1)
            sns.histplot(df_processed[col].dropna(), kde=True, color='skyblue')
            plt.title(f'Distribution of {col}')
            plt.subplot(1, 2, 2)
            sns.boxplot(y=df_processed[col], color='lightcoral')
            plt.title(f'Box Plot of {col}')
            plt.tight_layout()
            plt.show()

    # Correlation Heatmap
    if len(numerical_cols) >= 2:
        plt.figure(figsize=(10, 8))
        sns.heatmap(df_processed[numerical_cols].corr(), annot=True, cmap='viridis', fmt=".2f")
        plt.title('Correlation Heatmap')
        plt.show()
        
    # ---------------------------------------------
    # 5. Automatic Categorical Encoding
    # ---------------------------------------------
    print("\n\n--- 5. Automatic Categorical Encoding ---")
    
    one_hot_cols = []
    label_cols = []
    categorical_cols = df_processed.select_dtypes(include=['object', 'category']).columns
    
    for col in categorical_cols:
        n_unique = df_processed[col].nunique()
        if n_unique <= max_one_hot_categories and n_unique > 1:
            one_hot_cols.append(col)
        elif n_unique > max_one_hot_categories:
            label_cols.append(col)
            
    if one_hot_cols:
        print(f"Applying One-Hot Encoding (<= {max_one_hot_categories}) to: {one_hot_cols}")
        df_processed = pd.get_dummies(df_processed, columns=one_hot_cols, drop_first=True)
        
    if label_cols:
        print(f"Applying Label Encoding (> {max_one_hot_categories}) to: {label_cols}")
        le = LabelEncoder()
        for col in label_cols:
            df_processed[col] = le.fit_transform(df_processed[col].astype(str))
            
    # ---------------------------------------------
    # 6. Feature Scaling (StandardScaler)
    # ---------------------------------------------
    if perform_scaling:
        print("\n\n--- 6. Feature Scaling (StandardScaler) ---")
        final_numerical_cols = df_processed.select_dtypes(include=np.number).columns
        cols_to_scale = [col for col in final_numerical_cols if col not in label_cols]
        
        if cols_to_scale:
            scaler = StandardScaler()
            df_processed[cols_to_scale] = scaler.fit_transform(df_processed[cols_to_scale])
            print(f"Applied StandardScaler to {len(cols_to_scale)} numerical features.")
        else:
             print("No numerical columns found to apply StandardScaler.")
            

    print("\n=============================================")
    print(f"      ImtiazAnalysis: Pipeline Complete. Final Shape: {df_processed.shape} ✅")
    print("=============================================")
    
    return df_processed