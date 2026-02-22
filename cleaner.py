# cleaner.py

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_data(df):
    """Apply Task 6 quality checks and auto-fix"""
    original_len = len(df)
    
    # Remove duplicates (check for PatientID column, fallback to all columns)
    if 'PatientID' in df.columns:
        df = df.drop_duplicates(subset='PatientID')
    else:
        df = df.drop_duplicates()
    logging.info(f"Removed {original_len - len(df)} duplicates")
    
    # Fix impossible ages (if Age column exists)
    if 'Age' in df.columns:
        before_age = len(df)
        df = df[(df['Age'] >= 18) & (df['Age'] <= 45)]
        logging.info(f"Removed {before_age - len(df)} rows with invalid age")
    
    # Fix impossible LOS (if LOS column exists)
    if 'LOS' in df.columns:
        before_los = len(df)
        # overwrite the LOS column with LOS >= 2
        df = df[df['LOS'] >= 2]
        logging.info(f"Removed {before_los - len(df)} rows with invalid LOS")
    
    # Handle missing values
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) > 0:
        for col in numeric_cols:
            # 1. Count how many missing values exist before the fix
            missing_count = df[col].isna().sum()
            
            if missing_count > 0:
                # 2. Calculate the median
                col_median = df[col].median()
                
                # 3. Fill the missing values
                df[col] = df[col].fillna(col_median)
                
                # 4. Log the specific change
                logging.info(f"Imputed {missing_count} missing values in '{col}' using median ({col_median})")


    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        for col in categorical_cols:
            mode_value = df[col].mode()
            if len(mode_value) > 0:
                df[col] = df[col].fillna(mode_value.iloc[0])
    
    logging.info(f"✓ Cleaned data: {len(df)} rows remaining")
    return df
