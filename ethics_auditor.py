# ethics_auditor.py

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def audit_ethics(df):
    """Apply Day 2 Slides 5-10 checks"""
    flags = []
    
    # Privacy check (Slide 5)
    privacy_keywords = ['PatientName', 'Name', 'SSN', 'SocialSecurity', 'Email', 
                        'Phone', 'Address', 'Contact', 'IDNumber']
    privacy_found = [col for col in df.columns if any(keyword.lower() in col.lower() 
                                                      for keyword in privacy_keywords)]
    if privacy_found:
        flags.append(f"⚠️ PRIVACY VIOLATION: Identifiable data detected in columns: {', '.join(privacy_found)}")
    
    # Selection bias (Slide 6)
    if 'Location' in df.columns:
        location_counts = df['Location'].value_counts()
        total = len(df)
        if 'Rural' in location_counts.index:
            rural_pct = (location_counts['Rural'] / total) * 100
            if rural_pct < 30:
                flags.append(f"⚠️ SELECTION BIAS: Rural patients {rural_pct:.1f}% (should be >30%)")
        elif 'Urban' in location_counts.index:
            urban_pct = (location_counts['Urban'] / total) * 100
            if urban_pct > 70:
                flags.append(f"⚠️ SELECTION BIAS: Urban patients {urban_pct:.1f}% (rural representation may be insufficient)")
    
    # Measurement bias (Slide 6)
    if 'DeliveryType' in df.columns and 'Complications' in df.columns:
        comp_by_delivery = df.groupby('DeliveryType')['Complications'].apply(
            lambda x: (x == 'Yes').sum() / len(x) * 100 if len(x) > 0 else 0
        )
        if len(comp_by_delivery) >= 2:
            rates = comp_by_delivery.values
            diff = abs(rates[0] - rates[1])
            if diff > 30:
                flags.append(f"⚠️ MEASUREMENT BIAS: {diff:.1f}% complication rate difference between delivery types")
    
    # Group fairness (Slide 9)
    if 'Location' in df.columns and 'LOS' in df.columns:
        los_by_location = df.groupby('Location')['LOS'].mean()
        if len(los_by_location) >= 2:
            if 'Urban' in los_by_location.index and 'Rural' in los_by_location.index:
                diff_los = abs(los_by_location['Urban'] - los_by_location['Rural'])
                if diff_los > 2:
                    flags.append(f"⚠️ GROUP DISPARITY: {diff_los:.1f} day LOS difference between Urban and Rural patients")
            else:
                # Compare first two locations
                locations = los_by_location.index.tolist()
                if len(locations) >= 2:
                    diff_los = abs(los_by_location[locations[0]] - los_by_location[locations[1]])
                    if diff_los > 2:
                        flags.append(f"⚠️ GROUP DISPARITY: {diff_los:.1f} day LOS difference between {locations[0]} and {locations[1]} patients")
    
    # Sample size check
    if len(df) < 30:
        flags.append(f"⚠️ SMALL SAMPLE SIZE: Only {len(df)} patients (may affect statistical validity)")
    
    # Missing data check
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    if missing_pct > 10:
        flags.append(f"⚠️ DATA QUALITY: {missing_pct:.1f}% missing data (may introduce bias)")
    
    # FDA classification (Slide 8)
    flags.append("ℹ️ FDA CLASS II: Clinical decision support - requires validation")
    
    if len(flags) == 1:  # Only FDA classification
        logging.info("✓ Ethics audit: No critical issues detected")
    else:
        logging.warning(f"⚠️ Ethics audit: {len(flags) - 1} issue(s) detected")
    
    return flags
