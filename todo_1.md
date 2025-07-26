# Task 1: Create 10 Random LOINC Code Documents for Embedding

## Objective
Based on the embeddingmodel.gemini.md and loinc_vectorization_guide.gemini.md, create 10 random LOINC code documents formatted for embedding. Each document should follow the naming convention `<loinc-code>.loinc-chunk.md` and be stored in the `./input` directory.

## Understanding
From the files reviewed:
1. **embeddingmodel.gemini.md** explains the embedding process using the docker container deenihl/ollama-medcpt and the model oscardp96/medcpt-article.
2. **loinc_vectorization_guide.gemini.md** provides a structured 10-block framework for organizing LOINC code information for vector embeddings.
3. We have access to LOINC code samples in `./input/loinc_sample.csv`.

## Plan

### Step 1: Data Selection
1. Select 10 random LOINC codes from the loinc_sample.csv file
   - Choose a diverse set representing different types of tests/measurements
   - Ensure the codes are active (status = "ACTIVE")
   - Note the following fields for each selected code:
     - LOINC Code (1st column)
     - Long Common Name (10th column)
     - Component (2nd column)
     - Property (3rd column)
     - Time Aspect (4th column)
     - System (5th column)
     - Scale Type (6th column)
     - Method Type (7th column)
     - Class (8th column)

### Step 2: Document Creation Process
For each selected LOINC code, create a structured document following the 10-block framework:

1. **Block 1: Primary Code Identification**
   - LOINC Code
   - Long Common Name
   - Short Name
   - Display Name
   - Status

2. **Block 2: Clinical Terminology and Classification**
   - Component
   - Property
   - Time Aspect
   - System
   - Scale Type
   - Method Type
   - Class

3. **Block 3: Technical Definition and Measurement**
   - Definition
   - Measurement methodology
   - Units of measurement
   - Reference ranges (if available)

4. **Block 4: Clinical Context and Applications**
   - Primary clinical uses
   - Associated conditions (based on test type)
   - Clinical significance

5. **Block 5: Related Laboratory Tests**
   - Tests commonly ordered together
   - Panel memberships (if applicable)

6. **Block 6: Synonyms and Alternative Names**
   - Official synonyms
   - Common abbreviations

7. **Block 7: Specimen and Collection Information**
   - Specimen type
   - Collection methods (based on System type)

8. **Block 8: Quality and Standardization**
   - Quality control considerations
   - Analytical variables

9. **Block 9: Regulatory and Administrative**
   - Copyright information
   - Version details

10. **Block 10: Cross-References and External Mappings**
    - SNOMED CT associations (if available)
    - Related coding systems

### Step 3: Document Creation Implementation
1. Parse the loinc_sample.csv file to extract the 10 selected LOINC codes and their properties
2. For each code:
   - Create a markdown file named `<loinc-code>.loinc-chunk.md` in the ./input directory
   - Structure the document using the 10 blocks as headers
   - Fill in available information from the sample data
   - Add placeholder text where specific information is not available
   - Ensure each block contains sufficient content (100-500 tokens)

### Step 4: Quality Assurance
1. Verify each document follows the standardized structure
2. Check for consistency across all 10 documents
3. Ensure file naming follows the convention `<loinc-code>.loinc-chunk.md`
4. Confirm all files are saved in the ./input directory

## Implementation Code

A Python script will be created to:
1. Read the loinc_sample.csv file
2. Randomly select 10 active LOINC codes
3. Extract their properties
4. Generate structured markdown documents
5. Save them to the ./input directory

```python
# Code structure for generating LOINC documents
import csv
import random
import os
from pathlib import Path

# Function to read LOINC sample data
def read_loinc_sample(file_path):
    loinc_data = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[12] == "ACTIVE":  # Only select active codes
                loinc_data.append(row)
    return loinc_data

# Function to create a structured LOINC document
def create_loinc_document(loinc_entry, output_path):
    loinc_code = loinc_entry[0]
    component = loinc_entry[1]
    property_type = loinc_entry[2]
    time_aspect = loinc_entry[3]
    system = loinc_entry[4]
    scale_type = loinc_entry[5]
    method_type = loinc_entry[6]
    class_type = loinc_entry[7]
    long_name = loinc_entry[9]
    short_name = loinc_entry[10]
    
    # Create document content using the 10-block framework
    content = f"""# LOINC Code {loinc_code} Documentation

## Block 1: Primary Code Identification
LOINC Code: {loinc_code}
Long Common Name: {long_name}
Short Name: {short_name}
Display Name: {long_name}
Status: ACTIVE

## Block 2: Clinical Terminology and Classification
Component: {component}
Property: {property_type}
Time Aspect: {time_aspect}
System: {system}
Scale Type: {scale_type}
Method Type: {method_type}
Class: {class_type}

## Block 3: Technical Definition and Measurement
Definition: Measurement of {component} in {system}
Measurement Type: {property_type} measurement of {component}
Units: Based on {property_type} type
Normal Range: Varies by laboratory and population

## Block 4: Clinical Context and Applications
Clinical Use: Assessment and monitoring of {component} levels
Associated Conditions: Conditions related to abnormal {component} levels
Clinical Significance: Helps in diagnosis and monitoring of diseases affecting {component} levels
Diagnostic Applications: Used in the evaluation of {system}-related conditions
Panel Associations: May be included in comprehensive {system} assessment panels

## Block 5: Related Laboratory Tests
Panel Members: Often grouped with other {system} tests
Related LOINC Codes: Other codes measuring {component} with different methods or in different systems
Commonly Ordered With: Other tests evaluating {system} function or status
Workflow Relationships: Part of {system} assessment workflow

## Block 6: Synonyms and Alternative Names
Synonyms: {component} measurement, {component} test
Abbreviations: Common clinical abbreviations for {component}
Legacy Terms: Historical names for {component} measurement
International Variants: Similar terminology used internationally
Common Names: Commonly used terms for this test in clinical settings

## Block 7: Specimen and Collection Information
Specimen Type: {system}
Collection Method: Standard collection procedure for {system}
Container: Appropriate container for {system} collection
Stability: Storage recommendations for {system} specimens
Special Instructions: Any special handling requirements for {component} measurement

## Block 8: Quality and Standardization
Method Standardization: Standards for {method_type} measurement
Quality Control: Recommended QC procedures for {component} measurement
Analytical Variables: Factors affecting {component} measurement accuracy
Precision: Precision specifications for {method_type}
Interference: Known substances that may interfere with {component} measurement

## Block 9: Regulatory and Administrative
Copyright: LOINC® is copyright © 1995-2025, Regenstrief Institute, Inc.
Version Information: LOINC version information
Usage Rights: According to LOINC license terms
Mapping Standards: Follows standard LOINC mapping guidelines
System Integration: Implementation notes for health information systems

## Block 10: Cross-References and External Mappings
SNOMED CT: Related SNOMED CT codes for {component} measurement
ICD Codes: Related diagnostic codes when {component} measurement is relevant
CPT Codes: Procedure codes associated with this measurement
UCUM Units: Standard units of measurement
External IDs: Other system identifiers for this test
"""

    # Save the document
    file_path = os.path.join(output_path, f"{loinc_code}.loinc-chunk.md")
    with open(file_path, 'w') as file:
        file.write(content)
    
    return file_path

# Main function to generate 10 random LOINC documents
def generate_loinc_documents(input_file, output_dir, num_documents=10):
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Read LOINC sample data
    loinc_data = read_loinc_sample(input_file)
    
    # Randomly select 10 LOINC codes
    selected_loinc = random.sample(loinc_data, min(num_documents, len(loinc_data)))
    
    # Create documents for each selected code
    created_files = []
    for loinc_entry in selected_loinc:
        file_path = create_loinc_document(loinc_entry, output_dir)
        created_files.append(file_path)
    
    return created_files

# Execute the document generation
input_file = "./input/loinc_sample.csv"
output_dir = "./input"
created_files = generate_loinc_documents(input_file, output_dir)
print(f"Created {len(created_files)} LOINC documents in {output_dir}")
```

## Expected Output
10 markdown files in the ./input directory, named according to the convention `<loinc-code>.loinc-chunk.md`, each containing structured information about the LOINC code following the 10-block framework.

## Next Steps
After completing this task:
1. Verify all 10 files have been correctly generated and stored in the ./input directory
2. Commit changes as specified in Task 2
3. Proceed to Task 3 (creating a Python script to check for docker containers)
