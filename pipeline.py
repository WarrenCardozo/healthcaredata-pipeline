# pipeline.py

from loader import load_data
from cleaner import clean_data
from analyzer import analyze_data
from visualizer import create_visualizations
from ethics_auditor import audit_ethics
from report_generator import generate_pdf_report
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline(input_file, output_file='report.pdf'):
    """Execute full pipeline"""
    print("="*50)
    print("HEALTHCARE DATA PIPELINE")
    print("="*50)
    
    # Step 1: Load
    print("\n[Step 1/6] Loading data...")
    df = load_data(input_file)
    if df is None:
        print("[ERROR] Pipeline failed at data loading step")
        return False
    
    # Step 2: Clean
    print("\n[Step 2/6] Cleaning data...")
    df_clean = clean_data(df)
    if df_clean is None or len(df_clean) == 0:
        print("[ERROR] Pipeline failed: No data remaining after cleaning")
        return False
    
    # Step 3: Analyze
    print("\n[Step 3/6] Analyzing data...")
    results = analyze_data(df_clean)
    
    # Step 4: Visualize
    print("\n[Step 4/6] Creating visualizations...")
    plots = create_visualizations(df_clean)
    
    # Step 5: Ethics audit
    print("\n[Step 5/6] Running ethics audit...")
    flags = audit_ethics(df_clean)
    
    # Step 6: Generate report
    print("\n[Step 6/6] Generating PDF report...")
    generate_pdf_report(results, flags, plots, output_file)
    
    print("\n" + "="*50)
    print("[SUCCESS] PIPELINE COMPLETE")
    print(f"[SUCCESS] Report saved to: {output_file}")
    print("="*50)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <data_file.csv> [output_report.pdf]")
        print("\nExample: python pipeline.py maternity_master.csv report.pdf")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'report.pdf'
    
    success = run_pipeline(input_file, output_file)
    sys.exit(0 if success else 1)
