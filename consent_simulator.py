# consent_simulator.py

from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def simulate_consent_workflow(patient_id):
    """Simulate ICMR-compliant informed consent"""
    print(f"\n{'='*60}")
    print(f"INFORMED CONSENT WORKFLOW FOR PATIENT {patient_id}")
    print(f"{'='*60}")
    
    # Step 1: Information disclosure
    print("\n1. INFORMATION DISCLOSURE")
    print("   - Your data will be used for research to improve maternity outcomes")
    print("   - Data will be anonymized (no name, no contact info)")
    print("   - You can withdraw consent anytime")
    print("   - Data will be stored securely and used only for approved research")
    print("   - Results may be published in anonymized form")
    
    # Step 2: Patient consent
    print("\n2. PATIENT CONSENT")
    consent = input("   DO YOU CONSENT? (yes/no): ").strip().lower()
    
    if consent == 'yes':
        consent_id = f"C{patient_id}-{datetime.now().strftime('%Y')}"
        consent_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n   ✓ Consent recorded")
        print(f"   Consent ID: {consent_id}")
        print(f"   Date: {consent_date}")
        print(f"   Status: ACTIVE")
        
        logging.info(f"Consent granted for Patient {patient_id} - ID: {consent_id}")
        return True
    else:
        print("\n   ✗ Consent denied - data will NOT be used")
        print("   Patient data will be excluded from analysis")
        
        logging.warning(f"Consent denied for Patient {patient_id}")
        return False

def batch_consent_simulation(patient_ids):
    """Simulate consent for multiple patients"""
    consented = []
    denied = []
    
    for patient_id in patient_ids:
        if simulate_consent_workflow(patient_id):
            consented.append(patient_id)
        else:
            denied.append(patient_id)
        print("\n")
    
    print(f"\n{'='*60}")
    print("CONSENT SUMMARY")
    print(f"{'='*60}")
    print(f"Total Patients: {len(patient_ids)}")
    print(f"Consented: {len(consented)} ({len(consented)/len(patient_ids)*100:.1f}%)")
    print(f"Denied: {len(denied)} ({len(denied)/len(patient_ids)*100:.1f}%)")
    
    if consented:
        print(f"\nConsented Patient IDs: {', '.join(map(str, consented))}")
    if denied:
        print(f"Denied Patient IDs: {', '.join(map(str, denied))}")
    
    return consented, denied

if __name__ == "__main__":
    # Example usage
    print("CONSENT SIMULATOR - ICMR Compliant Workflow")
    print("="*60)
    
    # Single patient example
    patient_id = input("\nEnter Patient ID (or press Enter for example): ").strip()
    if not patient_id:
        patient_id = 12345
    
    simulate_consent_workflow(int(patient_id))
