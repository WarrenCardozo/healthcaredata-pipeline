# analyzer.py

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_data(df):
    """Run Tasks 2-5 analysis"""
    results = {}
    
    # Task 2: Basic stats
    results['total_patients'] = len(df)
    
    if 'Age' in df.columns:
        results['avg_age'] = df['Age'].mean()
    else:
        results['avg_age'] = None
    
    if 'LOS' in df.columns:
        results['avg_los'] = df['LOS'].mean()
    else:
        results['avg_los'] = None
    
    # Task 3-4: Rates
    if 'DeliveryType' in df.columns:
        results['delivery_counts'] = df['DeliveryType'].value_counts().to_dict()
    else:
        results['delivery_counts'] = {}
    
    if 'Complications' in df.columns:
        complications_yes = (df['Complications'] == 'Yes').sum()
        results['complication_rate'] = (complications_yes / len(df)) * 100 if len(df) > 0 else 0
    else:
        results['complication_rate'] = None
    
    if 'Readmitted' in df.columns:
        # (df['Readmitted'] == 'Yes') creates a boolean series of True/False values 
        # .mean() of the boolean series is the readmission rate
        results['readmission_rate'] = (df['Readmitted'] == 'Yes').mean() * 100
    else:
        results['readmission_rate'] = None
    
    # Task 5: Group comparisons
    if 'DeliveryType' in df.columns and 'LOS' in df.columns:
        results['los_by_delivery'] = df.groupby('DeliveryType')['LOS'].agg(
        mean_los='mean',
        median_los='median',
        mode_los=lambda x: x.round(1).mode().iloc[0] if not x.mode().empty else None
        )
    else:
        results['los_by_delivery'] = {}
    
    if 'DeliveryType' in df.columns and 'Complications' in df.columns:
        comp_by_delivery = df.groupby('DeliveryType')['Complications'].apply(
            lambda x: (x == 'Yes').mean() * 100 if len(x) > 0 else 0
        )
        results['comp_by_delivery'] = comp_by_delivery.to_dict()
    else:
        results['comp_by_delivery'] = {}
    
    logging.info(" Analysis complete")
    return results
