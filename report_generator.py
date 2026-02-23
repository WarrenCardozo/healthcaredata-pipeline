# report_generator.py

from fpdf import FPDF
import logging
import os
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize(text):
    """Make text safe for fpdf Latin-1 fonts."""
    replacements = {
        '\u2014': '--', '\u2013': '-',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2265': '>=', '\u2264': '<=',
        '\u00b1': '+/-',
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    # Strip anything still outside Latin-1
    return text.encode('latin-1', errors='replace').decode('latin-1')


class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Healthcare Data Analysis Report', 0, 1, 'C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, title):
        self.set_font('Arial', 'B', 13)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 9, sanitize(title), ln=True, fill=True)
        self.ln(2)

    def body_line(self, text):
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, sanitize(text), ln=True)

    def flag_line(self, flag_text):
        """Render a PASS/FAIL ethics flag with colour coding."""
        # Detect indent BEFORE stripping
        indent = 6 if flag_text.startswith('  ') else 0
        text = sanitize(flag_text).strip()

        if text.startswith('FAIL'):
            self.set_text_color(180, 0, 0)
            self.set_font('Arial', 'B', 10)
        else:
            self.set_text_color(0, 130, 0)
            self.set_font('Arial', '', 10)

        if indent:
            self.set_x(self.get_x() + indent)
        self.multi_cell(0, 7, text)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def summary_line(self, passed, failed):
        """Render the PASS/FAIL summary with each word colour-coded."""
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(self.get_string_width('Summary:  ') + 2, 8, 'Summary:  ')
        self.set_text_color(0, 130, 0)
        pass_label = f"{passed} PASS"
        self.cell(self.get_string_width(pass_label) + 4, 8, pass_label)
        self.set_text_color(0, 0, 0)
        self.cell(self.get_string_width('  |  ') + 2, 8, '  |  ')
        self.set_text_color(180, 0, 0)
        fail_label = f"{failed} FAIL"
        self.cell(self.get_string_width(fail_label) + 2, 8, fail_label, ln=True)
        self.set_text_color(0, 0, 0)


def _write_hipaa_ndhm_file(flags, output_path):
    """Write a plain-text violation report for HIPAA/NDHM failures."""
    violation_flags = [f for f in flags if any(k in f for k in ('HIPAA', 'NDHM', 'PRIVACY')) and f.startswith('FAIL')]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    lines = [
        "=" * 60,
        "HIPAA / NDHM COMPLIANCE VIOLATION REPORT",
        f"Generated: {timestamp}",
        "=" * 60, "",
    ]

    if violation_flags:
        lines.append(f"STATUS: {len(violation_flags)} VIOLATION(S) DETECTED\n")
        for i, v in enumerate(violation_flags, 1):
            lines.append(f"{i}. {v}")
        lines += [
            "",
            "RECOMMENDED ACTIONS:",
            "  - Remove or pseudonymise all identified PHI/PII columns",
            "  - Re-run the ethics audit after de-identification",
            "  - Consult your Data Protection Officer before sharing data",
            "  - For India deployments: verify NDHM / DPDP Act compliance",
            "  - For US deployments: verify HIPAA Safe Harbour / Expert Determination",
        ]
    else:
        lines += [
            "STATUS: NO HIPAA / NDHM VIOLATIONS DETECTED",
            "",
            "The dataset does not contain recognisable PHI or NDHM identifier columns.",
            "Continue to verify contextual re-identification risk before sharing.",
        ]

    lines += ["", "=" * 60, "END OF REPORT", "=" * 60]
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    logging.info(f"HIPAA/NDHM compliance report written to: {output_path}")


def generate_pdf_report(results, flags, plots, output_file='report.pdf', cleaning_summary=None):
    """Create PDF with analysis, cleaning summary, and full pass/fail ethics audit."""

    # Auto-generate HIPAA/NDHM violation file
    base_dir = os.path.dirname(output_file) or '.'
    hipaa_report_path = os.path.join(base_dir, 'hipaa_ndhm_violations.txt')
    _write_hipaa_ndhm_file(flags, hipaa_report_path)

    pdf = PDFReport()
    pdf.add_page()
    pdf.ln(2)

    # ── 1. Data Cleaning Summary ───────────────────────────────────────────────
    if cleaning_summary:
        pdf.section_title('1. Data Cleaning Summary')
        rows_loaded  = cleaning_summary.get('rows_loaded', 'N/A')
        rows_after   = cleaning_summary.get('rows_after_cleaning', 'N/A')
        total_removed = cleaning_summary.get('total_rows_removed', 'N/A')

        pdf.body_line(f"Rows loaded:              {rows_loaded}")
        pdf.body_line(f"Rows after cleaning:      {rows_after}")
        pdf.body_line(f"Total rows removed:       {total_removed}")

        if isinstance(rows_loaded, int) and isinstance(rows_after, int) and rows_loaded > 0:
            pct_kept = (rows_after / rows_loaded) * 100
            pdf.body_line(f"Data retained:            {pct_kept:.1f}%")

        pdf.ln(2)
        pdf.set_font('Arial', 'I', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 7, "Breakdown of removed rows:", ln=True)
        pdf.set_text_color(0, 0, 0)

        breakdown = [
            ('Duplicate records',       cleaning_summary.get('duplicates_removed', 0)),
            ('Invalid age (outside 18-45)', cleaning_summary.get('invalid_age_removed', 0)),
            ('Invalid LOS (< 2 days)',   cleaning_summary.get('invalid_los_removed', 0)),
        ]
        for label, count in breakdown:
            status = 'removed' if count > 0 else 'none found'
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 7, f"  {label}: {count} row(s) {status}", ln=True)

        pdf.ln(3)

    # ── 2. Basic Statistics ────────────────────────────────────────────────────
    pdf.section_title('2. Basic Statistics')
    pdf.body_line(f"Total Patients (post-cleaning): {results['total_patients']}")
    if results['avg_age'] is not None:
        pdf.body_line(f"Average Age:   {results['avg_age']:.2f} years")
    if results['avg_los'] is not None:
        pdf.body_line(f"Average LOS:   {results['avg_los']:.2f} days")
    pdf.ln(3)

    # ── 3. Key Metrics ────────────────────────────────────────────────────────
    pdf.section_title('3. Key Metrics')
    if results['complication_rate'] is not None:
        pdf.body_line(f"Complication Rate:  {results['complication_rate']:.2f}%")
    if results['readmission_rate'] is not None:
        pdf.body_line(f"Readmission Rate:   {results['readmission_rate']:.2f}%")
    if results['delivery_counts']:
        pdf.body_line("Delivery Type Distribution:")
        for dtype, count in results['delivery_counts'].items():
            pdf.body_line(f"    {dtype}: {count}")
    pdf.ln(3)

    # ── 4. Group Comparisons ──────────────────────────────────────────────────
    if not results['los_by_delivery'].empty:
        pdf.section_title('4. Group Comparisons')
        pdf.body_line("Average LOS by Delivery Type:")
        for row in results['los_by_delivery'].itertuples():
            pdf.body_line(
                f"    {row.Index}:  Mean {row.mean_los:.2f} d  |  "
                f"Median {row.median_los:.2f} d  |  Mode {row.mode_los:.2f} d"
            )
        if results['comp_by_delivery']:
            pdf.body_line("Complication Rate by Delivery Type:")
            for dtype, rate in results['comp_by_delivery'].items():
                pdf.body_line(f"    {dtype}: {rate:.2f}%")
        pdf.ln(3)

    # ── 5. Visualizations ────────────────────────────────────────────────────
    if plots:
        pdf.section_title('5. Visualizations')
        for plot in plots:
            if os.path.exists(plot):
                try:
                    pdf.image(plot, w=180)
                    pdf.ln(4)
                except Exception as e:
                    logging.warning(f"Could not add image {plot}: {e}")
                    pdf.body_line(f"[Image unavailable: {os.path.basename(plot)}]")

    # ── 6. Ethics & Compliance Audit ─────────────────────────────────────────
    pdf.add_page()
    pdf.section_title('6. Ethics & Compliance Audit Results')

    failed = sum(1 for f in flags if f.strip().startswith('FAIL'))
    passed = sum(1 for f in flags if f.strip().startswith('PASS'))

    pdf.summary_line(passed, failed)
    pdf.ln(3)

    # Group by category
    categories = {
        'HIPAA':            [],
        'NDHM':             [],
        'PRIVACY':          [],
        'SELECTION BIAS':   [],
        'MEASUREMENT BIAS': [],
        'GROUP DISPARITY':  [],
        'SAMPLE SIZE':      [],
        'DATA QUALITY':     [],
        'MISSING':          [],
        'CONSENT':          [],
        'OTHER':            [],
    }

    def _bucket(flag):
        fu = flag.upper()
        if '[HIPAA]' in fu:             return 'HIPAA'
        if '[NDHM]' in fu:              return 'NDHM'
        if '[PRIVACY]' in fu:           return 'PRIVACY'
        if '[SELECTION BIAS]' in fu:    return 'SELECTION BIAS'
        if '[MEASUREMENT BIAS]' in fu:  return 'MEASUREMENT BIAS'
        if '[GROUP DISPARITY]' in fu:   return 'GROUP DISPARITY'
        if '[SAMPLE SIZE]' in fu:       return 'SAMPLE SIZE'
        if '[DATA QUALITY]' in fu:      return 'DATA QUALITY'
        if '[MISSING]' in fu:           return 'MISSING'
        if '[CONSENT]' in fu:           return 'CONSENT'
        return 'OTHER'

    for flag in flags:
        categories[_bucket(flag)].append(flag)

    for cat, cat_flags in categories.items():
        if not cat_flags:
            continue
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, cat, ln=True, fill=True)
        pdf.ln(1)
        for flag in cat_flags:
            pdf.flag_line(flag)
        pdf.ln(2)

    # Footer note
    pdf.ln(3)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 6, f"HIPAA/NDHM violation report saved to: {hipaa_report_path}")
    pdf.set_text_color(0, 0, 0)

    pdf.output(output_file)
    logging.info(f"Generated report: {output_file}")