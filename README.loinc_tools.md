# LOINC Tools

A comprehensive Python toolkit for fetching and processing LOINC (Logical Observation Identifiers Names and Codes) data from loinc.org and local CSV files.

## 🎯 Purpose

Think of LOINC Tools as a **digital librarian** for medical laboratory data:
- **Web Scraper**: Downloads LOINC pages from loinc.org
- **File Organizer**: Manages local storage of fetched data  
- **CSV Processor**: Reads and indexes LOINC CSV databases
- **Data Converter**: Transforms CSV data to JSON format

## 📁 File Structure

```
loinc_tools/
├── loinc_tools.py          # Main LoincTools class
├── fetch-loincwebpages.py  # Test/demonstration script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Basic Usage

**Single LOINC fetch:**
```bash
python fetch-loincwebpages.py --single-fetch 1234-5
```

**Full demonstration:**
```bash
python fetch-loincwebpages.py
```

**Custom base folder:**
```bash
python fetch-loincwebpages.py --base-folder /path/to/data
```

### 3. Using the LoincTools Class

```python
from loinc_tools import LoincTools

# Initialize
tools = LoincTools()

# Fetch single LOINC webpage
tools.Fetch("1234-5", "./input")

# Fetch multiple LOINCs
loinc_dict = {"1234-5": "Glucose", "789-8": "Hemoglobin"}
tools.FetchMany(loinc_dict, "./input")

# Process CSV files
tools.CollectCSVs("./LOINC", makesamples=True)
csv_data = tools.GetCsvRowsAsJson("./LOINC", "1234-5")
tools.CreateLoincDataFile("./input", "1234-5")
```

## 🔧 Class Methods

| Method | Purpose | Analogy |
|--------|---------|---------|
| `Fetch()` | Download single LOINC webpage | Checking out one book from library |
| `FetchMany()` | Download multiple LOINCs with progress | Processing batch library requests |
| `CollectCSVs()` | Index all CSV files in folder structure | Creating library card catalog |
| `GetCsvRowsAsJson()` | Extract CSV data for specific LOINC | Looking up topic in reference books |
| `CreateLoincDataFile()` | Save processed data as JSON | Filing research results |

## 📊 Output Files

The tools create these file types:

- **`{loinc}.loinc-web.json`**: Downloaded webpage content
- **`{loinc}.loinc-csv.json`**: Processed CSV data
- **`processing_report.json`**: Summary of operations

## 🎛️ Configuration Parameters

### Environment Variables
- **`inputfolder`**: Where to store downloaded/processed files
- **`loincfolder`**: Root directory containing LOINC CSV files

### Configurable Resources
- **File naming format**: `{loinc}.loinc-csv.json` (customizable)
- **Progress bars**: Visual feedback for batch operations
- **Sample creation**: `makesamples=True/False`

## 📈 Data Flow Diagram

```
Web (loinc.org)     CSV Files
       ↓                ↓
   Fetch()        CollectCSVs()
       ↓                ↓
   JSON Files ←→ GetCsvRowsAsJson()
       ↓                ↓
CreateLoincDataFile() ←→ Index
       ↓
Final JSON Output
```

## ⚠️ Important Notes

- **File Format**: Despite method comments mentioning "markdown", files are saved as JSON for better data structure
- **Rate Limiting**: Small delays between requests to respect loinc.org servers
- **Error Handling**: Graceful failure handling with detailed error messages
- **Progress Tracking**: Visual progress bars for batch operations

## 🔍 Example Workflow

1. **Setup**: Create directory structure
2. **Fetch**: Download LOINC webpages 
3. **Index**: Build CSV file index
4. **Process**: Extract relevant CSV data
5. **Output**: Create structured JSON files
6. **Report**: Generate processing summary

## 🆘 Troubleshooting

**Common Issues:**
- **Network errors**: Check internet connection and loinc.org availability
- **File permissions**: Ensure write access to target directories
- **Missing CSV files**: Verify LOINC folder structure contains CSV files
- **Import errors**: Ensure all dependencies are installed

## 📋 Command Line Options

```bash
python fetch-loincwebpages.py [OPTIONS]

Options:
  --base-folder PATH    Base folder for operations (default: ./loinc_data)
  --single-fetch CODE   Fetch single LOINC code
  --skip-batch         Skip batch fetch demonstration  
  --skip-csv           Skip CSV processing demonstration
  --help               Show help message
```

## 🎯 Clear Unambiguous Statements

- ✅ **Files are saved as JSON**, not markdown despite some comments
- ✅ **Progress bars show real-time status** for all batch operations
- ✅ **Error handling is comprehensive** - operations continue even if individual items fail
- ✅ **CSV indexing is automatic** - no manual configuration required
- ✅ **Output structure is predictable** - consistent naming conventions used