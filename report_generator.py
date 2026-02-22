# report_generator.py

from fpdf import FPDF
import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_emojis(text):
    """Remove emojis and replace with text equivalents for PDF compatibility"""
    # Replace common emojis with text
    text = text.replace('⚠️', '[WARNING]')
    text = text.replace('ℹ️', '[INFO]')
    text = text.replace('✓', '[OK]')
    text = text.replace('✗', '[ERROR]')
    # Remove any remaining emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Healthcare Data Analysis Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(results, flags, plots, output_file='report.pdf'):
    """Create PDF with analysis + ethics audit"""
    pdf = PDFReport()
    pdf.add_page()
    pdf.ln(5)
    
    # Basic Stats (title comes from header)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '1. Basic Statistics', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Total Patients: {results['total_patients']}", ln=True)
    
    if results['avg_age'] is not None:
        pdf.cell(0, 10, f"Average Age: {results['avg_age']:.2f} years", ln=True)
    if results['avg_los'] is not None:
        pdf.cell(0, 10, f"Average LOS: {results['avg_los']:.2f} days", ln=True)
    pdf.ln(5)
    
    # Rates
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. Key Metrics', ln=True)
    pdf.set_font('Arial', '', 12)
    
    if results['complication_rate'] is not None:
        pdf.cell(0, 10, f"Complication Rate: {results['complication_rate']:.2f}%", ln=True)
    if results['readmission_rate'] is not None:
        pdf.cell(0, 10, f"Readmission Rate: {results['readmission_rate']:.2f}%", ln=True)
    
    if results['delivery_counts']:
        pdf.cell(0, 10, "Delivery Type Distribution:", ln=True)
        for delivery_type, count in results['delivery_counts'].items():
            pdf.cell(0, 10, f"  - {delivery_type}: {count}", ln=True)
    
    pdf.ln(5)
    
    # Group Comparisons
    if not results['los_by_delivery'].empty:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '3. Group Comparisons', ln=True)
        pdf.set_font('Arial', '', 12)
        
        if not results['los_by_delivery'].empty:
            pdf.cell(0, 10, "Average LOS by Delivery Type:", ln=True)
    
            for row in results['los_by_delivery'].itertuples():
                pdf.cell(0, 10, f"  - {row.Index}: Mean: {row.mean_los:.2f} days, Median: {row.median_los:.2f} days, Mode: {row.mode_los:.2f} days", ln=True)
        
        if results['comp_by_delivery']:
            pdf.cell(0, 10, "Complication Rate by Delivery Type:", ln=True)
            for delivery_type, comp_rate in results['comp_by_delivery'].items():
                pdf.cell(0, 10, f"  - {delivery_type}: {comp_rate:.2f}%", ln=True)
        
        pdf.ln(5)
    
    # Visualizations
    if plots:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '4. Visualizations', ln=True)
        pdf.set_font('Arial', '', 12)
        
        for plot in plots:
            if os.path.exists(plot):
                try:
                    pdf.image(plot, w=180)
                    pdf.ln(5)
                except Exception as e:
                    logging.warning(f"Could not add image {plot}: {e}")
                    pdf.cell(0, 10, f"[Image: {os.path.basename(plot)}]", ln=True)
    
    # Ethics Flags
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '5. Ethics Audit Results', ln=True)
    pdf.set_font('Arial', '', 12)
    
    if not flags:
        pdf.cell(0, 10, "[OK] No ethical issues detected", ln=True)
    else:
        critical_count = sum(1 for flag in flags if '⚠️' in flag or '[WARNING]' in flag)
        info_count = sum(1 for flag in flags if 'ℹ️' in flag or '[INFO]' in flag)
        
        pdf.cell(0, 10, f"Total Issues: {critical_count} critical, {info_count} informational", ln=True)
        pdf.ln(5)
        
        for flag in flags:
            flag_text = remove_emojis(flag)
            if '[WARNING]' in flag_text:
                pdf.set_text_color(255, 140, 0)  # Orange for warnings
            elif '[INFO]' in flag_text:
                pdf.set_text_color(0, 0, 255)  # Blue for info
            else:
                pdf.set_text_color(0, 0, 0)  # Black for others
            
            pdf.multi_cell(0, 8, flag_text)
            pdf.set_text_color(0, 0, 0)  # Reset to black
            pdf.ln(2)
    
    pdf.output(output_file)
    logging.info(f" Generated report: {output_file}")
