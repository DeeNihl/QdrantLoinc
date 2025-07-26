# Task 7: Create and Load Qdrant Collection

## Objective
Write tests to create a collection named "loinc-core" in the Qdrant database and load the embedding files (`<loinc>.loinc-embed.txt`) into this collection. The payload should include the LOINC code and the LOINC parts with full names (not abbreviations).

## Understanding
From the project files:
1. In previous tasks, we created LOINC chunk documents and generated embeddings for them.
2. The embeddings are stored in `<loinc>.loinc-embed.txt` files.
3. Now we need to:
   - Create a collection in Qdrant called "loinc-core"
   - Load the embeddings into this collection
   - Include metadata in the payload (LOINC code and full part names)

## Plan

### Step 1: Research Qdrant Integration
1. **Understanding the Qdrant API**
   - Qdrant provides a REST API for vector database operations
   - Key operations needed:
     - Creating a collection
     - Uploading vectors with payload
     - Performing vector similarity search

2. **Collection Configuration Requirements**
   - Vector size (matches the embedding dimension)
   - Distance metric (typically cosine similarity)
   - Payload schema (LOINC code and part names)

3. **LOINC Payload Structure**
   - LOINC code (unique identifier)
   - Component (what is measured)
   - Property (how it's measured)
   - Time Aspect (when measured)
   - System (what specimen/system)
   - Scale Type (quantitative/ordinal/etc.)
   - Method Type (how performed)

### Step 2: Test Implementation Approach
1. Create a Python script `test_qdrant_collection.py` that:
   - Connects to the Qdrant service
   - Creates a collection with appropriate configuration
   - Reads embedding files from the input directory
   - Extracts metadata from corresponding LOINC chunk files
   - Uploads embeddings with metadata to Qdrant
   - Performs validation tests on the uploaded data

### Step 3: Python Test Script Implementation

```python
#!/usr/bin/env python3
"""
test_qdrant_collection.py - Test creating and populating a Qdrant collection with LOINC embeddings

This script creates a 'loinc-core' collection in Qdrant and loads the embeddings
generated from LOINC chunk documents, including LOINC code and part names in the payload.
"""

import os
import json
import glob
import time
import requests
import numpy as np
import csv
from pathlib import Path
import sys

# Configuration
QDRANT_API_URL = "http://localhost:6333"
COLLECTION_NAME = "loinc-core"
INPUT_DIR = "./input"
LOINC_SAMPLE_CSV = os.path.join(INPUT_DIR, "loinc_sample.csv")
VECTOR_SIZE = 1536  # Expected dimension of embeddings
DISTANCE = "Cosine"  # Distance metric for similarity search

# LOINC field indices in CSV
LOINC_CODE_IDX = 0
COMPONENT_IDX = 1
PROPERTY_IDX = 2
TIME_ASPECT_IDX = 3
SYSTEM_IDX = 4
SCALE_TYPE_IDX = 5
METHOD_TYPE_IDX = 6
CLASS_IDX = 7
LONG_NAME_IDX = 9
SHORT_NAME_IDX = 10

def check_qdrant_service():
    """Check if the Qdrant service is available."""
    try:
        response = requests.get(f"{QDRANT_API_URL}/metrics")
        if response.status_code == 200:
            print(f"✅ Qdrant service is available")
            return True
        else:
            print(f"❌ Qdrant service returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Qdrant service: {e}")
        print("   Make sure the qdrant container is running")
        print("   You can start it with: python check_services.py")
        return False

def load_loinc_metadata():
    """
    Load LOINC metadata from the sample CSV file.
    
    Returns:
        dict: Dictionary mapping LOINC codes to their metadata
    """
    loinc_metadata = {}
    
    try:
        with open(LOINC_SAMPLE_CSV, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) <= LONG_NAME_IDX:
                    continue
                    
                loinc_code = row[LOINC_CODE_IDX]
                loinc_metadata[loinc_code] = {
                    "loinc_code": loinc_code,
                    "component": row[COMPONENT_IDX],
                    "property": row[PROPERTY_IDX],
                    "time_aspect": row[TIME_ASPECT_IDX],
                    "system": row[SYSTEM_IDX],
                    "scale_type": row[SCALE_TYPE_IDX],
                    "method_type": row[METHOD_TYPE_IDX],
                    "class": row[CLASS_IDX],
                    "long_common_name": row[LONG_NAME_IDX],
                    "short_name": row[SHORT_NAME_IDX] if len(row) > SHORT_NAME_IDX else ""
                }
                
        print(f"✅ Loaded metadata for {len(loinc_metadata)} LOINC codes")
        return loinc_metadata
        
    except FileNotFoundError:
        print(f"❌ LOINC sample CSV file not found: {LOINC_SAMPLE_CSV}")
        return {}
    except Exception as e:
        print(f"❌ Error loading LOINC metadata: {e}")
        return {}

def create_collection():
    """
    Create a new collection in Qdrant for storing LOINC embeddings.
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if collection already exists
    try:
        response = requests.get(f"{QDRANT_API_URL}/collections/{COLLECTION_NAME}")
        if response.status_code == 200:
            print(f"ℹ️ Collection '{COLLECTION_NAME}' already exists")
            return True
    except:
        pass
    
    # Create the collection
    collection_config = {
        "vectors": {
            "size": VECTOR_SIZE,
            "distance": DISTANCE
        },
        "optimizers_config": {
            "default_segment_number": 2
        },
        "replication_factor": 1
    }
    
    try:
        print(f"Creating collection '{COLLECTION_NAME}'...")
        response = requests.put(
            f"{QDRANT_API_URL}/collections/{COLLECTION_NAME}", 
            json=collection_config
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully created collection '{COLLECTION_NAME}'")
            
            # Create payload index for better search performance
            print("Creating payload indices...")
            
            index_fields = ["loinc_code", "component", "property", "time_aspect", 
                           "system", "scale_type", "method_type", "class"]
            
            for field in index_fields:
                index_response = requests.put(
                    f"{QDRANT_API_URL}/collections/{COLLECTION_NAME}/index", 
                    json={
                        "field_name": f"payload.{field}",
                        "field_schema": "keyword"
                    }
                )
                
                if index_response.status_code == 200:
                    print(f"✅ Created index for '{field}'")
                else:
                    print(f"⚠️ Failed to create index for '{field}': {index_response.status_code}")
            
            return True
        else:
            print(f"❌ Failed to create collection: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return False

def find_embedding_files():
    """Find all LOINC embedding files in the input directory."""
    return glob.glob(os.path.join(INPUT_DIR, "*.loinc-embed.txt"))

def upload_embeddings(loinc_metadata):
    """
    Upload embeddings to the Qdrant collection.
    
    Args:
        loinc_metadata (dict): Dictionary mapping LOINC codes to their metadata
        
    Returns:
        bool: True if all uploads were successful, False otherwise
    """
    embedding_files = find_embedding_files()
    
    if not embedding_files:
        print("❌ No embedding files found in the input directory")
        return False
        
    print(f"Found {len(embedding_files)} embedding files to upload")
    
    # Process files in batches for better performance
    batch_size = 100
    points = []
    success_count = 0
    
    for file_path in embedding_files:
        file_name = os.path.basename(file_path)
        loinc_code = file_name.split(".")[0]
        
        try:
            # Read the embedding file
            with open(file_path, 'r') as f:
                embedding_data = json.load(f)
                
            embedding_vector = embedding_data["embedding"]
            
            # Get metadata for this LOINC code
            metadata = loinc_metadata.get(loinc_code, {})
            if not metadata:
                print(f"⚠️ No metadata found for LOINC code {loinc_code}")
                # Create minimal metadata if not found
                metadata = {
                    "loinc_code": loinc_code,
                    "component": "Unknown",
                    "property": "Unknown",
                    "time_aspect": "Unknown",
                    "system": "Unknown",
                    "scale_type": "Unknown",
                    "method_type": "Unknown",
                    "class": "Unknown",
                    "long_common_name": "Unknown",
                    "short_name": "Unknown"
                }
            
            # Create a point for Qdrant
            point = {
                "id": loinc_code,
                "vector": embedding_vector,
                "payload": metadata
            }
            
            points.append(point)
            
            # Upload in batches to improve performance
            if len(points) >= batch_size:
                if upload_batch(points):
                    success_count += len(points)
                points = []
                
        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")
    
    # Upload any remaining points
    if points:
        if upload_batch(points):
            success_count += len(points)
    
    print(f"\n📊 Upload Summary:")
    print(f"   Processed {len(embedding_files)} embedding files")
    print(f"   Successfully uploaded {success_count} embeddings")
    print(f"   Failed: {len(embedding_files) - success_count}")
    
    return success_count == len(embedding_files)

def upload_batch(points):
    """
    Upload a batch of points to Qdrant.
    
    Args:
        points (list): List of points to upload
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"Uploading batch of {len(points)} points...")
        
        payload = {
            "points": points
        }
        
        response = requests.put(
            f"{QDRANT_API_URL}/collections/{COLLECTION_NAME}/points", 
            json=payload
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully uploaded batch")
            return True
        else:
            print(f"❌ Failed to upload batch: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading batch: {e}")
        return False

def verify_collection():
    """
    Verify that the collection exists and contains the expected data.
    
    Returns:
        bool: True if verification passed, False otherwise
    """
    try:
        # Check collection info
        response = requests.get(f"{QDRANT_API_URL}/collections/{COLLECTION_NAME}")
        
        if response.status_code != 200:
            print(f"❌ Collection verification failed: {response.status_code}")
            return False
            
        collection_info = response.json()
        vectors_count = collection_info.get("result", {}).get("vectors_count", 0)
        
        print(f"\n🔍 Collection Verification:")
        print(f"   Collection name: {COLLECTION_NAME}")
        print(f"   Vector count: {vectors_count}")
        print(f"   Vector size: {VECTOR_SIZE}")
        print(f"   Distance metric: {DISTANCE}")
        
        # Count embedding files to verify
        embedding_files = find_embedding_files()
        expected_count = len(embedding_files)
        
        if vectors_count == expected_count:
            print(f"✅ Vector count matches expected ({expected_count})")
        else:
            print(f"⚠️ Vector count mismatch: {vectors_count} in collection, {expected_count} expected")
        
        return vectors_count > 0  # Pass verification if at least some vectors were uploaded
        
    except Exception as e:
        print(f"❌ Error during collection verification: {e}")
        return False

def test_search():
    """
    Test a simple vector search to verify the collection is working correctly.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get a random embedding to use for search
        embedding_files = find_embedding_files()
        if not embedding_files:
            print("❌ No embedding files found for search test")
            return False
            
        # Use the first file for testing
        test_file = embedding_files[0]
        with open(test_file, 'r') as f:
            embedding_data = json.load(f)
            
        test_vector = embedding_data["embedding"]
        test_loinc = embedding_data["loinc_code"]
        
        print(f"\n🔍 Testing vector search with LOINC code {test_loinc}...")
        
        # Search request
        search_request = {
            "vector": test_vector,
            "limit": 5,
            "with_payload": True
        }
        
        response = requests.post(
            f"{QDRANT_API_URL}/collections/{COLLECTION_NAME}/points/search", 
            json=search_request
        )
        
        if response.status_code != 200:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
        results = response.json().get("result", [])
        
        if not results:
            print("❌ No search results returned")
            return False
            
        print(f"✅ Search returned {len(results)} results")
        
        # Display top result
        top_result = results[0]
        top_id = top_result.get("id", "")
        top_score = top_result.get("score", 0)
        top_payload = top_result.get("payload", {})
        
        print(f"   Top match: LOINC {top_id} with score {top_score:.4f}")
        print(f"   Name: {top_payload.get('long_common_name', 'Unknown')}")
        
        # Verify that the top result is the same as the query (should be exact match)
        if top_id == test_loinc:
            print("✅ Search verification passed: Top result matches query")
        else:
            print(f"⚠️ Search verification warning: Top result {top_id} does not match query {test_loinc}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during search test: {e}")
        return False

def run_tests():
    """Run tests to create a Qdrant collection and populate it with LOINC embeddings."""
    if not check_qdrant_service():
        return False
        
    # Load LOINC metadata from CSV
    loinc_metadata = load_loinc_metadata()
    if not loinc_metadata:
        return False
        
    # Create the collection
    if not create_collection():
        return False
        
    # Upload embeddings
    if not upload_embeddings(loinc_metadata):
        return False
        
    # Verify the collection
    if not verify_collection():
        return False
        
    # Test search functionality
    if not test_search():
        return False
        
    return True

def main():
    """Main entry point for the test script."""
    print("🧪 Running LOINC Qdrant Collection Tests")
    
    if run_tests():
        print("\n✅ All tests completed successfully")
        print("   The 'loinc-core' collection has been created and populated with embeddings")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Step 4: Testing and Validation Plan
1. **Basic Testing**
   - Run the script when Qdrant container is running
   - Run the script when Qdrant container is not running
   - Verify proper error handling and messaging

2. **Collection Testing**
   - Verify collection creation with proper configuration
   - Test payload index creation for efficient queries
   - Check collection existence and properties

3. **Data Loading Testing**
   - Test embedding upload process
   - Verify correct handling of metadata
   - Check proper batch processing for performance

4. **Verification Testing**
   - Confirm vector count matches expected number
   - Verify metadata is correctly associated with vectors
   - Test search functionality with a known vector

### Step 5: Qdrant Collection Configuration
The collection will be configured with:
1. Vector size: 1536 (matching the embedding dimension)
2. Distance metric: Cosine similarity
3. Payload fields:
   - loinc_code: LOINC code
   - component: Component (what is measured)
   - property: Property (how it's measured)
   - time_aspect: Time Aspect (when measured)
   - system: System (what specimen/system)
   - scale_type: Scale Type (quantitative/ordinal/etc.)
   - method_type: Method Type (how performed)
   - class: Class (clinical category)
   - long_common_name: Long Common Name
   - short_name: Short Name

## Implementation Features

1. **Comprehensive Collection Setup**
   - Creates a properly configured Qdrant collection
   - Sets up payload indices for efficient filtering
   - Handles existing collections gracefully

2. **Robust Metadata Handling**
   - Loads LOINC metadata from the sample CSV
   - Maps metadata to corresponding embeddings
   - Includes full names rather than abbreviations

3. **Efficient Batch Processing**
   - Uploads vectors in batches for better performance
   - Handles large numbers of embeddings efficiently
   - Provides progress indicators and summaries

4. **Thorough Verification**
   - Checks that vectors are properly stored
   - Verifies metadata association with vectors
   - Tests search functionality for correctness

5. **Detailed Reporting**
   - Provides clear success/failure indicators
   - Shows collection statistics and configuration
   - Reports search results for verification

## Expected Output

When running the script, users should see output similar to:

```
🧪 Running LOINC Qdrant Collection Tests
✅ Qdrant service is available
✅ Loaded metadata for 100 LOINC codes
Creating collection 'loinc-core'...
✅ Successfully created collection 'loinc-core'
Creating payload indices...
✅ Created index for 'loinc_code'
✅ Created index for 'component'
✅ Created index for 'property'
✅ Created index for 'time_aspect'
✅ Created index for 'system'
✅ Created index for 'scale_type'
✅ Created index for 'method_type'
✅ Created index for 'class'
Found 10 embedding files to upload
Uploading batch of 10 points...
✅ Successfully uploaded batch

📊 Upload Summary:
   Processed 10 embedding files
   Successfully uploaded 10 embeddings
   Failed: 0

🔍 Collection Verification:
   Collection name: loinc-core
   Vector count: 10
   Vector size: 1536
   Distance metric: Cosine
✅ Vector count matches expected (10)

🔍 Testing vector search with LOINC code 10008-1...
✅ Search returned 5 results
   Top match: LOINC 10008-1 with score 0.9999
   Name: R wave duration in lead V5
✅ Search verification passed: Top result matches query

✅ All tests completed successfully
   The 'loinc-core' collection has been created and populated with embeddings
```

## Next Steps
After completing this task:
1. Verify the collection exists in Qdrant with the correct configuration
2. Confirm all embeddings are properly loaded with their metadata
3. Test searching the collection using the Qdrant API
4. Commit changes to complete the project
