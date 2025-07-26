#!/usr/bin/env python3
"""
fetch-loincwebpages.py

A comprehensive test script for the LoincTools class.
This script demonstrates how to:
1. Fetch LOINC webpages from loinc.org
2. Process CSV data files
3. Create organized data files
4. Handle multiple LOINC codes efficiently

Usage:
    python fetch-loincwebpages.py
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List

# Import our LoincTools class
try:
    from loinc_tools import LoincTools
except ImportError:
    print("Error: Could not import LoincTools. Make sure loinc_tools.py is in the same directory.")
    sys.exit(1)


def setup_directories(base_folder: str) -> Dict[str, str]:
    """
    Set up the directory structure for LOINC data processing.
    
    Think of this as organizing your filing cabinet before starting work.
    
    Args:
        base_folder (str): Base directory for all LOINC operations
        
    Returns:
        dict: Dictionary containing paths to different folders
    """
    directories = {
        'base': base_folder,
        'input': os.path.join(base_folder, 'input'),
        'csv_data': os.path.join(base_folder, 'LOINC'),
        'output': os.path.join(base_folder, 'output'),
        'logs': os.path.join(base_folder, 'logs')
    }
    
    # Create all directories
    for dir_path in directories.values():
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created/verified directory: {dir_path}")
    
    return directories


def get_sample_loinc_codes() -> Dict[str, str]:
    """
    Return a sample set of LOINC codes for testing.
    
    These are real LOINC codes that represent common laboratory tests.
    Think of these as test cases covering different types of medical measurements.
    
    Returns:
        dict: Sample LOINC codes with descriptions
    """
    return {
        "1234-5": "Sample glucose test",
        "789-8": "Sample hemoglobin test", 
        "33747-0": "Sample phenotype",
        "11502-2": "Sample laboratory report",
        "15074-8": "Sample glucose measurement"
    }


def demonstrate_single_fetch(tools: LoincTools, loinc_code: str, input_folder: str) -> None:
    """
    Demonstrate fetching a single LOINC webpage.
    
    This is like checking out one specific book from the library.
    
    Args:
        tools (LoincTools): The LoincTools instance
        loinc_code (str): The LOINC code to fetch
        input_folder (str): Where to store the fetched data
    """
    print(f"\n🔍 Demonstrating single fetch for LOINC: {loinc_code}")
    print("-" * 50)
    
    success = tools.Fetch(loinc_code, input_folder)
    
    if success:
        # Check if the file was created
        expected_file = Path(input_folder) / f"{loinc_code}.loinc-web.json"
        if expected_file.exists():
            file_size = expected_file.stat().st_size
            print(f"✓ File created successfully: {expected_file}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print("⚠ File was not found after fetch operation")
    else:
        print(f"✗ Failed to fetch LOINC code: {loinc_code}")


def demonstrate_batch_fetch(tools: LoincTools, loinc_codes: Dict[str, str], input_folder: str) -> None:
    """
    Demonstrate fetching multiple LOINC webpages in batch.
    
    This is like processing a list of library requests all at once.
    
    Args:
        tools (LoincTools): The LoincTools instance
        loinc_codes (dict): Dictionary of LOINC codes to fetch
        input_folder (str): Where to store the fetched data
    """
    print(f"\n📦 Demonstrating batch fetch for {len(loinc_codes)} LOINC codes")
    print("-" * 50)
    
    results = tools.FetchMany(loinc_codes, input_folder)
    
    # Analyze results
    successful = [loinc for loinc, success in results.items() if success]
    failed = [loinc for loinc, success in results.items() if not success]
    
    print(f"\n📊 Batch fetch results:")
    print(f"  ✓ Successful: {len(successful)} codes")
    print(f"  ✗ Failed: {len(failed)} codes")
    
    if failed:
        print(f"  Failed codes: {', '.join(failed)}")
    
    # Verify files were created
    print(f"\n📋 Verifying created files:")
    for loinc in successful:
        expected_file = Path(input_folder) / f"{loinc}.loinc-web.json"
        if expected_file.exists():
            file_size = expected_file.stat().st_size
            print(f"  ✓ {loinc}: {file_size:,} bytes")
        else:
            print(f"  ⚠ {loinc}: File not found")


def demonstrate_csv_processing(tools: LoincTools, csv_folder: str, input_folder: str) -> None:
    """
    Demonstrate CSV file processing capabilities.
    
    This is like indexing and cross-referencing multiple databases.
    
    Args:
        tools (LoincTools): The LoincTools instance
        csv_folder (str): Folder containing CSV files
        input_folder (str): Where to store processed data
    """
    print(f"\n📈 Demonstrating CSV processing")
    print("-" * 50)
    
    # Check if CSV folder exists and has content
    csv_path = Path(csv_folder)
    if not csv_path.exists():
        print(f"⚠ CSV folder does not exist: {csv_folder}")
        print("  Creating sample CSV structure for demonstration...")
        create_sample_csv_structure(csv_folder)
    
    # Collect and index CSV files
    print("Indexing CSV files...")
    csv_index = tools.CollectCSVs(csv_folder, makesamples=True)
    
    print(f"📊 CSV indexing results:")
    print(f"  Total LOINC codes found: {len(csv_index)}")
    
    # Process a few sample LOINC codes
    sample_codes = list(csv_index.keys())[:3]  # First 3 codes
    
    for loinc in sample_codes:
        print(f"\n🔬 Processing LOINC: {loinc}")
        
        # Get CSV data as JSON
        csv_data = tools.GetCsvRowsAsJson(csv_folder, loinc)
        print(f"  Found data in {len(csv_data)} CSV files")
        
        # Create data file
        success = tools.CreateLoincDataFile(input_folder, loinc)
        if success:
            data_file = Path(input_folder) / f"{loinc}.loinc-csv.json"
            if data_file.exists():
                file_size = data_file.stat().st_size
                print(f"  ✓ Created data file: {file_size:,} bytes")


def create_sample_csv_structure(csv_folder: str) -> None:
    """
    Create a sample CSV structure for demonstration purposes.
    
    This creates mock data that mimics real LOINC CSV files.
    
    Args:
        csv_folder (str): Folder to create sample structure in
    """
    csv_path = Path(csv_folder)
    csv_path.mkdir(parents=True, exist_ok=True)
    
    # Sample data structure
    sample_data = [
        {
            'filename': 'LoincTable.csv',
            'headers': ['LOINC_NUM', 'COMPONENT', 'PROPERTY', 'TIME_ASPCT', 'SYSTEM', 'SCALE_TYP', 'METHOD_TYP'],
            'rows': [
                ['1234-5', 'Glucose', 'MCnc', 'Pt', 'Ser/Plas', 'Qn', 'Test strip'],
                ['789-8', 'Hemoglobin', 'MCnc', 'Pt', 'Bld', 'Qn', 'Automated count'],
                ['33747-0', 'Phenotype', 'Find', 'Pt', 'XXX', 'Nom', 'Observed']
            ]
        },
        {
            'filename': 'PartFile.csv', 
            'headers': ['LOINC_NUM', 'PART_NUMBER', 'PART_NAME', 'PART_TYPE'],
            'rows': [
                ['1234-5', 'LP12345-6', 'Glucose', 'COMPONENT'],
                ['789-8', 'LP67890-1', 'Hemoglobin', 'COMPONENT'],
                ['33747-0', 'LP33747-9', 'Phenotype', 'COMPONENT']
            ]
        }
    ]
    
    # Create sample CSV files
    import csv
    for data in sample_data:
        csv_file = csv_path / data['filename']
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(data['headers'])
            writer.writerows(data['rows'])
        
        print(f"  📄 Created sample file: {csv_file}")


def create_comprehensive_report(directories: Dict[str, str]) -> None:
    """
    Create a comprehensive report of all operations performed.
    
    Think of this as creating a summary document of all your research activities.
    
    Args:
        directories (dict): Dictionary of directory paths
    """
    print(f"\n📋 Creating comprehensive report")
    print("-" * 50)
    
    report_data = {
        'operation_summary': 'LOINC Data Processing Report',
        'directories': directories,
        'files_created': {},
        'statistics': {}
    }
    
    # Analyze each directory
    for dir_name, dir_path in directories.items():
        if dir_name == 'base':
            continue
            
        path_obj = Path(dir_path)
        if path_obj.exists():
            files = list(path_obj.glob('*'))
            report_data['files_created'][dir_name] = {
                'count': len(files),
                'files': [str(f.name) for f in files if f.is_file()]
            }
    
    # Save report
    report_file = Path(directories['logs']) / 'processing_report.json'
    
    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Report saved to: {report_file}")


def main():
    """
    Main function that orchestrates the entire LOINC data processing workflow.
    
    This is like conducting a symphony - each part plays its role in creating
    the complete musical performance.
    """
    print("🔬 LOINC Tools Demonstration Script")
    print("=" * 60)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fetch and process LOINC data')
    parser.add_argument('--base-folder', default='./loinc_data',
                       help='Base folder for LOINC operations (default: ./loinc_data)')
    parser.add_argument('--single-fetch', 
                       help='Fetch a single LOINC code (e.g., 1234-5)')
    parser.add_argument('--skip-batch', action='store_true',
                       help='Skip batch fetch demonstration')
    parser.add_argument('--skip-csv', action='store_true', 
                       help='Skip CSV processing demonstration')
    
    args = parser.parse_args()
    
    # Set up directories
    print("📁 Setting up directory structure...")
    directories = setup_directories(args.base_folder)
    
    # Initialize LoincTools
    print("\n🛠 Initializing LoincTools...")
    tools = LoincTools()
    
    # Get sample LOINC codes
    sample_codes = get_sample_loinc_codes()
    
    try:
        # Single fetch demonstration
        if args.single_fetch:
            demonstrate_single_fetch(tools, args.single_fetch, directories['input'])
        else:
            # Use first sample code
            first_code = list(sample_codes.keys())[0]
            demonstrate_single_fetch(tools, first_code, directories['input'])
        
        # Batch fetch demonstration
        if not args.skip_batch:
            demonstrate_batch_fetch(tools, sample_codes, directories['input'])
        
        # CSV processing demonstration
        if not args.skip_csv:
            demonstrate_csv_processing(tools, directories['csv_data'], directories['input'])
        
        # Create comprehensive report
        create_comprehensive_report(directories)
        
        print(f"\n🎉 All demonstrations completed successfully!")
        print(f"📂 Check the results in: {directories['base']}")
        
    except KeyboardInterrupt:
        print(f"\n⚠ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
