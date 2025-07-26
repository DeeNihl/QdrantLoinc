"""
LoincTools: A comprehensive class for fetching and processing LOINC data.

This class provides methods to:
1. Fetch LOINC web pages and save them locally
2. Process CSV files containing LOINC data
3. Create indexed data structures for fast lookups
4. Generate JSON output files in specified formats
"""

import os
import json
import csv
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from tqdm import tqdm
import glob
import time
from urllib.parse import urljoin


class LoincTools:
    """
    A toolset for working with LOINC (Logical Observation Identifiers Names and Codes) data.
    
    Think of this class as a Swiss Army knife for LOINC data:
    - Web scraper: Downloads LOINC pages from loinc.org
    - File organizer: Manages local storage of fetched data
    - CSV processor: Reads and indexes LOINC CSV databases
    - Data converter: Transforms CSV data to JSON format
    """
    
    def __init__(self):
        """Initialize the LoincTools instance."""
        self.csv_index = {}  # Cache for CSV file indexing
        self.session = requests.Session()  # Reuse HTTP connections
        self.session.headers.update({
            'User-Agent': 'LoincTools/1.0 (Data Processing Tool)'
        })
    
    def Fetch(self, loinc: str, inputfolder: str) -> bool:
        """
        Fetch the contents of a LOINC webpage and store it locally.
        
        Think of this as downloading a single page from a digital library
        and filing it in your local folder system.
        
        Args:
            loinc (str): The LOINC code (e.g., "1234-5")
            inputfolder (str): Directory to store the downloaded content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure the input folder exists
            Path(inputfolder).mkdir(parents=True, exist_ok=True)
            
            # Construct the URL
            url = f"https://loinc.org/{loinc}"
            
            # Fetch the webpage
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Prepare the data to save
            webpage_data = {
                "loinc_code": loinc,
                "url": url,
                "fetch_timestamp": time.time(),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "content_length": len(response.text)
            }
            
            # Save as JSON file (despite the method comment mentioning markdown)
            filename = f"{loinc}.loinc-web.json"
            filepath = Path(inputfolder) / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(webpage_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Fetched LOINC {loinc} → {filepath}")
            return True
            
        except requests.RequestException as e:
            print(f"✗ Network error fetching LOINC {loinc}: {e}")
            return False
        except Exception as e:
            print(f"✗ Error processing LOINC {loinc}: {e}")
            return False
    
    def FetchMany(self, loincs: Dict[str, Any], inputfolder: str) -> Dict[str, bool]:
        """
        Fetch multiple LOINC webpages with progress tracking.
        
        Like processing a batch of library requests - we go through each one
        systematically and track our progress.
        
        Args:
            loincs (dict): Dictionary containing LOINC codes (keys are LOINC codes)
            inputfolder (str): Directory to store downloaded content
            
        Returns:
            dict: Results for each LOINC code (True/False for success/failure)
        """
        results = {}
        loinc_codes = list(loincs.keys())
        
        print(f"Fetching {len(loinc_codes)} LOINC webpages...")
        
        # Progress bar for visual feedback
        with tqdm(total=len(loinc_codes), desc="Fetching LOINCs") as pbar:
            for loinc in loinc_codes:
                results[loinc] = self.Fetch(loinc, inputfolder)
                pbar.update(1)
                # Small delay to be respectful to the server
                time.sleep(0.1)
        
        successful = sum(1 for success in results.values() if success)
        print(f"Completed: {successful}/{len(loinc_codes)} successful fetches")
        
        return results
    
    def CollectCSVs(self, loincfolder: str, makesamples: bool = False) -> Dict[str, List[str]]:
        """
        Find and index all CSV files in LOINC folder structure.
        
        Think of this as creating a card catalog for a library - we're indexing
        where each piece of information can be found.
        
        Args:
            loincfolder (str): Root folder containing LOINC CSV files
            makesamples (bool): Whether to create sample files for testing
            
        Returns:
            dict: Index mapping LOINC codes to their CSV file locations
        """
        print("Indexing CSV files in LOINC folder structure...")
        
        # Find all CSV files recursively
        csv_pattern = os.path.join(loincfolder, "**", "*.csv")
        csv_files = glob.glob(csv_pattern, recursive=True)
        
        print(f"Found {len(csv_files)} CSV files")
        
        # Build index with progress bar
        csv_index = {}
        with tqdm(total=len(csv_files), desc="Indexing CSVs") as pbar:
            for csv_file in csv_files:
                try:
                    # Read the first few rows to identify LOINC codes
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for i, row in enumerate(reader):
                            if i >= 100 and not makesamples:  # Limit sampling for performance
                                break
                            
                            # Look for LOINC code in common column names
                            loinc_code = None
                            for col in ['LOINC_NUM', 'LOINC', 'CODE', 'LOINC_CODE']:
                                if col in row and row[col]:
                                    loinc_code = str(row[col]).strip()
                                    break
                            
                            if loinc_code:
                                if loinc_code not in csv_index:
                                    csv_index[loinc_code] = []
                                if csv_file not in csv_index[loinc_code]:
                                    csv_index[loinc_code].append(csv_file)
                
                except Exception as e:
                    print(f"Warning: Could not process {csv_file}: {e}")
                
                pbar.update(1)
        
        # Store index for later use
        self.csv_index = csv_index
        
        print(f"Indexed {len(csv_index)} unique LOINC codes across {len(csv_files)} files")
        
        # Create samples if requested
        if makesamples:
            self._create_sample_files(loincfolder, csv_index)
        
        return csv_index
    
    def GetCsvRowsAsJson(self, loincfolder: str, loinc: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract CSV data for a specific LOINC code and return as JSON.
        
        Like looking up a specific topic in multiple reference books
        and collecting all the relevant information.
        
        Args:
            loincfolder (str): Root folder containing CSV files
            loinc (str): The LOINC code to search for
            
        Returns:
            dict: JSON object with CSV data organized by filename
        """
        if not self.csv_index:
            self.CollectCSVs(loincfolder)
        
        result = {}
        
        if loinc not in self.csv_index:
            print(f"LOINC code {loinc} not found in index")
            return result
        
        csv_files = self.csv_index[loinc]
        
        for csv_file in csv_files:
            try:
                csv_name = Path(csv_file).stem  # Filename without extension
                rows = []
                
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Check if this row contains our LOINC code
                        for col in ['LOINC_NUM', 'LOINC', 'CODE', 'LOINC_CODE']:
                            if col in row and str(row[col]).strip() == loinc:
                                rows.append(row)
                                break
                
                if rows:
                    result[csv_name] = rows
                    
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
        
        return result
    
    def CreateLoincDataFile(self, inputfolder: str, loinc: str, 
                           filenameformat: str = "{loinc}.loinc-csv.json") -> bool:
        """
        Create a JSON data file for a specific LOINC code.
        
        Args:
            inputfolder (str): Directory to save the file
            loinc (str): The LOINC code
            filenameformat (str): Format string for the filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the CSV data for this LOINC
            csv_data = self.GetCsvRowsAsJson(inputfolder, loinc)
            
            # Prepare the output data
            output_data = {
                "loinc_code": loinc,
                "creation_timestamp": time.time(),
                "csv_sources": csv_data,
                "total_records": sum(len(records) for records in csv_data.values())
            }
            
            # Create the filename
            filename = filenameformat.format(loinc=loinc)
            filepath = Path(inputfolder) / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Created data file: {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ Error creating data file for {loinc}: {e}")
            return False
    
    def GetLoincData(self, loincfolder: str, loinc: str) -> Dict[str, Any]:
        """
        Get comprehensive LOINC data by processing CSV files.
        
        This is like doing a complete research project on a specific topic -
        we gather data from multiple sources and compile it.
        
        Args:
            loincfolder (str): Root folder containing LOINC CSV files
            loinc (str): The LOINC code to process
            
        Returns:
            dict: Comprehensive data for the LOINC code
        """
        print(f"Processing LOINC data for {loinc}...")
        
        # Get CSV data
        csv_data = self.GetCsvRowsAsJson(loincfolder, loinc)
        
        # Create data file
        success = self.CreateLoincDataFile(loincfolder, loinc)
        
        return {
            "loinc_code": loinc,
            "csv_data": csv_data,
            "file_created": success,
            "record_count": sum(len(records) for records in csv_data.values())
        }
    
    def _create_sample_files(self, loincfolder: str, csv_index: Dict[str, List[str]]) -> None:
        """Create sample files for testing purposes."""
        sample_dir = Path(loincfolder) / "samples"
        sample_dir.mkdir(exist_ok=True)
        
        # Create a sample index file
        sample_index = dict(list(csv_index.items())[:10])  # First 10 items
        
        with open(sample_dir / "sample_index.json", 'w') as f:
            json.dump(sample_index, f, indent=2)
        
        print(f"Created sample files in {sample_dir}")
