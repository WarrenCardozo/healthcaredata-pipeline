# cleaner.py

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_data(df):
    """Apply quality checks, auto-fix, and return (cleaned_df, cleaning_summary)."""
    summary = {}
    original_len = len(df)
    summary['rows_loaded'] = original_len

    # Remove duplicates
    if 'PatientID' in df.columns:
        df = df.drop_duplicates(subset='PatientID')
    else:
        df = df.drop_duplicates()
    dupes_removed = original_len - len(df)
    summary['duplicates_removed'] = dupes_removed
    logging.info(f"Removed {dupes_removed} duplicates")

    # Fix impossible ages
    after_dupes = len(df)
    if 'Age' in df.columns:
        df = df[(df['Age'] >= 18) & (df['Age'] <= 45)]
    age_removed = after_dupes - len(df)
    summary['invalid_age_removed'] = age_removed
    logging.info(f"Removed {age_removed} rows with invalid age")

    # Fix impossible LOS
    after_age = len(df)
    if 'LOS' in df.columns:
        df = df[df['LOS'] >= 2]
    los_removed = after_age - len(df)
    summary['invalid_los_removed'] = los_removed
    logging.info(f"Removed {los_removed} rows with invalid LOS")

    summary['rows_after_cleaning'] = len(df)
    summary['total_rows_removed']  = original_len - len(df)

    # ── Imputation — track every filled cell ─────────────────────────────────
    imputation_log = []   # list of dicts: {patient_id, column, original, imputed_value, method}

    id_col = 'PatientID' if 'PatientID' in df.columns else None

    # Numeric columns — impute with median
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        missing_idx = df.index[df[col].isna()]
        if len(missing_idx) == 0:
            continue
        col_median = round(df[col].median(), 2)
        for idx in missing_idx:
            imputation_log.append({
                'patient_id':    str(df.at[idx, id_col]) if id_col else str(idx),
                'column':        col,
                'original':      'missing',
                'imputed_value': col_median,
                'method':        'median',
            })
        df[col] = df[col].fillna(col_median)
        logging.info(f"Imputed {len(missing_idx)} missing value(s) in '{col}' with median ({col_median})")

    # Categorical columns — impute with mode
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        missing_idx = df.index[df[col].isna()]
        if len(missing_idx) == 0:
            continue
        mode_value = df[col].mode()
        if len(mode_value) == 0:
            continue
        fill_val = mode_value.iloc[0]
        for idx in missing_idx:
            imputation_log.append({
                'patient_id':    str(df.at[idx, id_col]) if id_col else str(idx),
                'column':        col,
                'original':      'missing',
                'imputed_value': fill_val,
                'method':        'mode',
            })
        df[col] = df[col].fillna(fill_val)
        logging.info(f"Imputed {len(missing_idx)} missing value(s) in '{col}' with mode ('{fill_val}')")

    summary['imputation_log'] = imputation_log
    logging.info(f"Cleaned data: {len(df)} rows remaining | {len(imputation_log)} value(s) imputed")
    return df, summary
