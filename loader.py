# loader.py

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(file_path):
    """Load CSV/Excel with error handling"""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file type")
        
        logging.info(f" Loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logging.error(f"✗ Failed to load {file_path}: {e}")
        return None
