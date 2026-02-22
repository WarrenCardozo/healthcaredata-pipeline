import pandas as pd
import numpy as np
from datetime import date

def generate_patient_data(num_records=1000):
    """
    Generates a synthetic dataset for patient delivery data.
    """
    
    # Set random seed for reproducibility (remove this line if you want different data every time)
    np.random.seed(42)
    
    # 1. PatientID
    # Using a range of IDs to ensure uniqueness
    patient_ids = [f"PT{str(i).zfill(6)}" for i in range(1, num_records + 1)]
    
    # 2. Age
    # Realistic distribution: Normal distribution centered around 30
    # Clamped between 18 and 45
    ages = np.random.normal(loc=30, scale=5.5, size=num_records)
    ages = np.clip(ages, 18, 45).astype(int)
    
    # 3. DeliveryType
    # Distribution: ~70% Vaginal, ~30% C-Section
    delivery_types = np.random.choice(
        ['Vaginal', 'C-Section'], 
        size=num_records, 
        p=[0.70, 0.30]
    )
    
    # 4. LOS (Length of Stay in Days)
    # Logic: C-sections generally require longer stays (3-4 days) vs Vaginal (2 days)
    los = []
    for d in delivery_types:
        if d == 'C-Section':
            # Skewed towards 3 days, range 2-5
            discrete_stay = np.random.choice([2, 3, 4, 5], p=[0.1, 0.5, 0.3, 0.1])
            stay = discrete_stay + np.random.uniform(-0.5, 0.5)
        else:
            # Skewed towards 2 days, range 1-3
            stay = np.random.choice([1, 2, 3], p=[0.15, 0.7, 0.15])
        los.append(stay)
        
    # 5. Complications
    # Distribution: ~15% Yes, ~85% No
    complications = np.random.choice(
        ['Yes', 'No'], 
        size=num_records, 
        p=[0.15, 0.85]
    )
    
    # 6. Readmitted
    # Logic: Higher chance of readmission if complications exist
    readmitted = []
    for comp in complications:
        if comp == 'Yes':
            # 25% chance of readmission if complications
            status = np.random.choice(['Yes', 'No'], p=[0.25, 0.75])
        else:
            # 2% chance of readmission if no complications
            status = np.random.choice(['Yes', 'No'], p=[0.02, 0.98])
        readmitted.append(status)
    
    # 7. Location
    # Distribution: Heavy weight towards urban hospitals
    locations = np.random.choice(
        ['Urban', 'Suburban', 'Rural'], 
        size=num_records, 
        p=[0.6, 0.3, 0.1]
    )
    
    # Create DataFrame
    df = pd.DataFrame({
        'PatientID': patient_ids,
        'Age': ages,
        'DeliveryType': delivery_types,
        'LOS': los,
        'Complications': complications,
        'Readmitted': readmitted,
        'Location': locations
    })
    
    return df

if __name__ == "__main__":
    # Generate 1000 records
    df = generate_patient_data(1000)
    
    # Display first 10 rows
    print("--- First 10 Records ---")
    print(df.head(10))
    
    # Display value counts to verify distribution
    print("\n--- Distribution Check ---")
    print(f"Delivery Type:\n{df['DeliveryType'].value_counts(normalize=True)}")
    print(f"\nAvg LOS by Delivery Type:\n{df.groupby('DeliveryType')['LOS'].mean()}")
    
    df.to_csv('synthetic_patient_data.csv', index=False)