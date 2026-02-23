# ethics_auditor.py

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def audit_ethics(df):
    """Run all ethics checks. Every check returns either PASS or FAIL."""
    flags = []

    # ── HIPAA ─────────────────────────────────────────────────────────────────
    hipaa_keywords = [
        'PatientName', 'Name', 'SSN', 'SocialSecurity', 'Email',
        'Phone', 'Address', 'Contact', 'IDNumber', 'DOB', 'DateOfBirth',
        'Zip', 'ZipCode', 'FaxNumber', 'AccountNumber', 'CertificateLicense',
        'VehicleID', 'DeviceID', 'WebURL', 'IPAddress', 'BiometricID',
        'FullFacePhoto', 'UniqueIdentifier'
    ]
    hipaa_found = [col for col in df.columns if any(k.lower() in col.lower() for k in hipaa_keywords)]
    if hipaa_found:
        flags.append(f"FAIL [HIPAA] Protected Health Information detected in columns: {', '.join(hipaa_found)}")
    else:
        flags.append("PASS [HIPAA] No PHI column names detected")

    # ── NDHM ──────────────────────────────────────────────────────────────────
    ndhm_keywords = [
        'AadhaarNumber', 'Aadhaar', 'ABHA', 'HealthID', 'PAN',
        'MobileNumber', 'Mobile', 'VoterID', 'PassportNumber', 'RationCard'
    ]
    ndhm_found = [col for col in df.columns if any(k.lower() in col.lower() for k in ndhm_keywords)]
    if ndhm_found:
        flags.append(f"FAIL [NDHM] Indian health identity data detected in columns: {', '.join(ndhm_found)}")
    else:
        flags.append("PASS [NDHM] No NDHM personal identifier columns detected")

    # ── PRIVACY (combined sweep) ───────────────────────────────────────────────
    all_pii = list(set(hipaa_found + ndhm_found))
    if all_pii:
        flags.append(f"FAIL [PRIVACY] Identifiable columns present -- de-identify before sharing: {', '.join(all_pii)}")
    else:
        flags.append("PASS [PRIVACY] Dataset appears de-identified -- no PII column names found")

    # ── SELECTION BIAS ────────────────────────────────────────────────────────
    if 'Location' in df.columns:
        location_counts = df['Location'].value_counts()
        total = len(df)
        rural_pct = (location_counts.get('Rural', 0) / total) * 100
        urban_pct = (location_counts.get('Urban', 0) / total) * 100

        if rural_pct < 30:
            flags.append(f"FAIL [SELECTION BIAS] Rural patients = {rural_pct:.1f}% -- recommended >=30% for a representative sample")
        else:
            flags.append(f"PASS [SELECTION BIAS] Rural representation adequate at {rural_pct:.1f}%")

        if urban_pct > 70:
            flags.append(f"FAIL [SELECTION BIAS] Urban patients = {urban_pct:.1f}% -- rural/suburban groups may be underrepresented")
        else:
            flags.append(f"PASS [SELECTION BIAS] Urban concentration within acceptable range at {urban_pct:.1f}%")
    else:
        flags.append("FAIL [SELECTION BIAS] 'Location' column missing -- geographic bias cannot be assessed")

    # ── MEASUREMENT BIAS ──────────────────────────────────────────────────────
    if 'DeliveryType' in df.columns and 'Complications' in df.columns:
        comp_by_delivery = df.groupby('DeliveryType')['Complications'].apply(
            lambda x: (x == 'Yes').sum() / len(x) * 100 if len(x) > 0 else 0
        )
        if len(comp_by_delivery) >= 2:
            rates = comp_by_delivery.values
            diff = abs(rates[0] - rates[1])
            if diff > 30:
                flags.append(f"FAIL [MEASUREMENT BIAS] {diff:.1f}% complication-rate gap between delivery types -- possible measurement inconsistency")
            else:
                flags.append(f"PASS [MEASUREMENT BIAS] Complication-rate difference between delivery types is {diff:.1f}% (within 30% threshold)")
        else:
            flags.append("FAIL [MEASUREMENT BIAS] Fewer than 2 delivery types present -- cross-group comparison not possible")
    else:
        flags.append("FAIL [MEASUREMENT BIAS] 'DeliveryType' or 'Complications' column missing -- check cannot be performed")

    # ── GROUP FAIRNESS / DISPARITY ────────────────────────────────────────────
    if 'Location' in df.columns and 'LOS' in df.columns:
        los_by_loc = df.groupby('Location')['LOS'].mean()
        if 'Urban' in los_by_loc.index and 'Rural' in los_by_loc.index:
            diff_los = abs(los_by_loc['Urban'] - los_by_loc['Rural'])
            if diff_los > 2:
                flags.append(f"FAIL [GROUP DISPARITY] Urban vs Rural LOS difference = {diff_los:.1f} days -- equity concern")
            else:
                flags.append(f"PASS [GROUP DISPARITY] Urban vs Rural LOS difference = {diff_los:.1f} days (within 2-day threshold)")
        elif len(los_by_loc) >= 2:
            locs = los_by_loc.index.tolist()
            diff_los = abs(los_by_loc[locs[0]] - los_by_loc[locs[1]])
            label = f"{locs[0]} vs {locs[1]}"
            if diff_los > 2:
                flags.append(f"FAIL [GROUP DISPARITY] {label} LOS difference = {diff_los:.1f} days -- equity concern")
            else:
                flags.append(f"PASS [GROUP DISPARITY] {label} LOS difference = {diff_los:.1f} days (within 2-day threshold)")
        else:
            flags.append("FAIL [GROUP DISPARITY] Insufficient location groups -- LOS disparity cannot be assessed")
    else:
        flags.append("FAIL [GROUP DISPARITY] 'Location' or 'LOS' column missing -- disparity check cannot be performed")

    # ── SAMPLE SIZE ───────────────────────────────────────────────────────────
    n = len(df)
    if n < 30:
        flags.append(f"FAIL [SAMPLE SIZE] Only {n} patients -- minimum of 30 recommended for statistical validity")
    else:
        flags.append(f"PASS [SAMPLE SIZE] {n} patients -- adequate for statistical analysis")

    # ── MISSING DATA ──────────────────────────────────────────────────────────
    missing_per_col   = df.isnull().sum()
    total_missing     = missing_per_col.sum()
    cols_with_missing = missing_per_col[missing_per_col > 0]

    if total_missing == 0:
        flags.append("PASS [DATA QUALITY] No missing values detected across all columns")
    else:
        missing_pct = (total_missing / (len(df) * len(df.columns))) * 100
        if missing_pct > 10:
            flags.append(f"FAIL [DATA QUALITY] {missing_pct:.1f}% overall missing data -- exceeds 10% threshold, may introduce bias")
        else:
            flags.append(f"PASS [DATA QUALITY] {missing_pct:.2f}% overall missing data -- within acceptable range, imputation applied")

        # Per-column breakdown
        for col, n_missing in cols_with_missing.items():
            col_pct = (n_missing / len(df)) * 100
            dtype   = 'numeric' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical'
            impute  = 'median' if dtype == 'numeric' else 'mode'
            if col_pct > 10:
                flags.append(f"  FAIL [MISSING] '{col}' ({dtype}): {n_missing} value(s) missing ({col_pct:.1f}%) -- imputed with {impute}")
            else:
                flags.append(f"  PASS [MISSING] '{col}' ({dtype}): {n_missing} value(s) missing ({col_pct:.1f}%) -- imputed with {impute}")

    # ── CONSENT TRACEABILITY ──────────────────────────────────────────────────
    consent_cols = [c for c in df.columns if 'consent' in c.lower()]
    if not consent_cols:
        flags.append("FAIL [CONSENT] No consent-tracking column found -- ensure ICMR/HIPAA consent is recorded externally")
    else:
        for col in consent_cols:
            col_lower = df[col].astype(str).str.strip().str.lower()
            consented     = (col_lower == 'yes').sum()
            not_consented = (col_lower == 'no').sum()
            unknown       = len(df) - consented - not_consented
            total         = len(df)

            if not_consented > 0:
                flags.append(
                    f"FAIL [CONSENT] '{col}': {not_consented} of {total} patient(s) did NOT consent "
                    f"-- these records must be excluded from analysis"
                )
                # List the patient IDs that denied consent if a PatientID column exists
                if 'PatientID' in df.columns:
                    denied_ids = df.loc[col_lower == 'no', 'PatientID'].tolist()
                    flags.append(f"  FAIL [CONSENT] Denied consent -- PatientID(s): {', '.join(str(i) for i in denied_ids)}")
            else:
                flags.append(f"PASS [CONSENT] '{col}': All {consented} patient(s) consented")

            if unknown > 0:
                flags.append(
                    f"  FAIL [CONSENT] '{col}': {unknown} record(s) have unrecognised consent value "
                    f"(expected Yes/No) -- treat as not consented until confirmed"
                )

    # ── SUMMARY LOG ──────────────────────────────────────────────────────────
    failed = sum(1 for f in flags if f.startswith('FAIL') or f.startswith('  FAIL'))
    passed = sum(1 for f in flags if f.startswith('PASS') or f.startswith('  PASS'))
    logging.info(f"Ethics audit complete -- PASS: {passed} | FAIL: {failed}")

    return flags