
import csv

with open('/home/deenihl/git/ohdsi/QdrantLoinc/input/loinc_sample.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        loinc_num = row[0]
        component = row[1]
        prop = row[2]
        time_aspct = row[3]
        system = row[4]
        scale_typ = row[5]
        method_typ = row[6]
        klass = row[7]
        long_common_name = row[9]
        short_name = row[10]
        external_copyright_notice = row[11]
        status = row[12]

        content = f"""
# LOINC Code: {loinc_num}

## Block 1: Primary Code Identification
LOINC Code: {loinc_num}
Long Common Name: {long_common_name}
Short Name: {short_name}
Display Name: {long_common_name}
Status: {status}

## Block 2: Clinical Terminology and Classification
Component: {component}
Property: {prop}
Time Aspect: {time_aspct}
System: {system}
Scale Type: {scale_typ}
Method Type: {method_typ}
Class: {klass}

## Block 3: Technical Definition and Measurement
Definition: {long_common_name}
Measurement Type: {prop}
Units: 
Normal Range: 
Calculation: 

## Block 4: Clinical Context and Applications
Clinical Use: 
Associated Conditions: 
Clinical Significance: 
Diagnostic Applications: 
Panel Associations: 

## Block 5: Related Laboratory Tests
Panel Members: 
Related LOINC Codes: 
Commonly Ordered With: 
Workflow Relationships: 

## Block 6: Synonyms and Alternative Names
Synonyms: 
Abbreviations: 
Legacy Terms: 
International Variants: 
Common Names: 

## Block 7: Specimen and Collection Information
Specimen Type: {system}
Collection Method: 
Container: 
Stability: 
Special Instructions: 

## Block 8: Quality and Standardization
Method Standardization: 
Quality Control: 
Analytical Variables: 
Precision: 
Interference: 

## Block 9: Regulatory and Administrative
Copyright: {external_copyright_notice}
Version Information: 
Usage Rights: 
Mapping Standards: 
System Integration: 

## Block 10: Cross-References and External Mappings
SNOMED CT: 
ICD Codes: 
CPT Codes: 
UCUM Units: 
External IDs: 
"""
        with open(f"/home/deenihl/git/ohdsi/QdrantLoinc/input/{loinc_num}.loinc-chunk.md", "w") as out_file:
            out_file.write(content)
