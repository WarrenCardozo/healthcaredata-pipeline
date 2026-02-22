# Healthcare Data Analysis Pipeline

An end-to-end automated pipeline for processing healthcare patient data with quality checks, statistical analysis, visualization, and ethics auditing.

## Overview

This pipeline automates the complete workflow from raw data ingestion to PDF report generation:

```
Raw Data (CSV) → Load → Clean → Analyze → Visualize → Ethics Audit → PDF Report
```

## Features

- **Data Loading**: Supports CSV and Excel files with error handling
- **Data Cleaning**: Automatic duplicate removal, outlier detection, and missing value imputation
- **Statistical Analysis**: Basic statistics, rates, and group comparisons
- **Visualization**: Automatic generation of histograms, bar charts, and pie charts
- **Ethics Auditing**: Privacy checks, bias detection, and fairness analysis
- **PDF Reporting**: Publication-quality reports with all findings

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd healthcare-pipeline
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the pipeline on a data file:

```bash
python pipeline.py <input_file.csv> [output_report.pdf]
```

Example:
```bash
python pipeline.py maternity_master.csv report.pdf
```

### Sample Data Files

Three sample datasets are included:

1. **maternity_master.csv** - Clean, balanced dataset
2. **maternity_biased.csv** - Dataset with selection bias (mostly urban patients)
3. **maternity_missing.csv** - Dataset with missing values

### Running on Sample Data

```bash
# Clean data
python pipeline.py maternity_master.csv report_clean.pdf

# Biased data (will flag selection bias)
python pipeline.py maternity_biased.csv report_biased.pdf

# Missing data (will handle imputation)
python pipeline.py maternity_missing.csv report_missing.pdf
```

### Consent Simulator

Simulate ICMR-compliant informed consent workflow:

```bash
python consent_simulator.py
```

## Project Structure

```
.
├── loader.py              # Data loading module
├── cleaner.py             # Data cleaning module
├── analyzer.py            # Statistical analysis module
├── visualizer.py          # Visualization generation
├── ethics_auditor.py      # Ethics and bias checking
├── report_generator.py    # PDF report generation
├── pipeline.py            # Main pipeline script
├── consent_simulator.py   # Consent workflow simulator
├── requirements.txt       # Python dependencies
├── maternity_master.csv   # Sample clean data
├── maternity_biased.csv   # Sample biased data
├── maternity_missing.csv  # Sample data with missing values
└── README.md             # This file
```

## Pipeline Modules

### 1. Data Loader (`loader.py`)
- Loads CSV/Excel files
- Error handling and logging
- Returns pandas DataFrame

### 2. Data Cleaner (`cleaner.py`)
- Removes duplicate records
- Filters invalid ages (18-45 range)
- Filters invalid LOS (≥2 days)
- Imputes missing values (median for numeric, mode for categorical)

### 3. Analyzer (`analyzer.py`)
- Basic statistics (total patients, average age, average LOS)
- Complication and readmission rates
- Group comparisons by delivery type
- LOS and complication rates by delivery type

### 4. Visualizer (`visualizer.py`)
- Age distribution histogram
- Delivery type bar chart
- Complications pie chart
- LOS distribution histogram

### 5. Ethics Auditor (`ethics_auditor.py`)
Checks for:
- **Privacy violations**: Identifiable data (names, SSN, etc.)
- **Selection bias**: Underrepresentation of rural patients (<30%)
- **Measurement bias**: Large differences in complication rates (>30%)
- **Group disparity**: Significant LOS differences between groups (>2 days)
- **Sample size**: Minimum 30 patients
- **Data quality**: Missing data percentage (>10%)

### 6. Report Generator (`report_generator.py`)
- Generates PDF reports with:
  - Basic statistics
  - Key metrics
  - Group comparisons
  - Visualizations
  - Ethics audit results with flags

## Automated Deployment

The pipeline can be run automatically using GitHub Actions. The workflow file (`.github/workflows/pipeline.yml`) is configured to:

- Run daily at midnight UTC
- Support manual triggers
- Process all three sample datasets
- Upload generated reports as artifacts

## Expected Data Format

The pipeline expects CSV files with the following columns:

- `PatientID`: Unique patient identifier
- `Age`: Patient age (18-45)
- `DeliveryType`: Type of delivery (Vaginal, C-Section)
- `LOS`: Length of stay in days (≥2)
- `Complications`: Yes/No
- `Readmitted`: Yes/No
- `Location`: Urban/Rural

## Output

The pipeline generates:

1. **PDF Report** (`report.pdf`): Comprehensive analysis report
2. **Visualizations** (`plots/` directory):
   - `age_histogram.png`
   - `delivery_bar.png`
   - `complications_pie.png`
   - `los_histogram.png`

 

## Ethics & Compliance

This pipeline implements checks based on:
- ICMR guidelines for informed consent
- FDA Class II device requirements
- Fairness and bias detection principles
- Privacy protection standards

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
2. **File not found**: Check that the CSV file path is correct
3. **Empty report**: Verify the data file has valid rows after cleaning
4. **Missing visualizations**: Check that required columns exist in the data

### Logging

The pipeline uses Python's logging module. Set log level to DEBUG for detailed output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is provided as-is for educational and research purposes.

## Contact

For questions or issues, please open an issue in the repository.
