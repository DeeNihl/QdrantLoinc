# Task 5: Write Tests for Generating Embeddings

## Objective
Write tests that call the ollama-medcpt container's ollama endpoint to generate embeddings for one or more LOINC chunk documents. Save these embeddings as `<loinc>.loinc-embed.txt` files.

## Understanding
From the project files:
1. The **embeddingmodel.gemini.md** file explains that the docker container deenihl/ollama-medcpt contains an ollama service with the locally registered model oscardp96/medcpt-article.
2. We need to generate embeddings for the LOINC documents created in Task 1 (`<loinc>.loinc-chunk.md` files).
3. The embeddings need to be saved in files named `<loinc>.loinc-embed.txt`.

## Plan

### Step 1: Research Embedding Generation Process
1. **Understanding the Ollama API**
   - The Ollama API allows embedding generation via HTTP POST request
   - Endpoint: `http://localhost:11434/api/embed`
   - Request format:
     ```json
     {
       "model": "oscardp96/medcpt-article",
       "input": "Text to be embedded"
     }
     ```
   - Response format:
     ```json
     {
       "embedding": [0.1, 0.2, ...],
       "dim": 1536
     }
     ```

2. **Document Processing Requirements**
   - Need to read each LOINC chunk document
   - Send the document content to the Ollama API
   - Save the resulting embedding vector

### Step 2: Test Implementation Approach
1. Create a Python script `test_embeddings.py` that:
   - Finds all LOINC chunk documents in the input directory
   - Reads their contents
   - Makes API calls to the Ollama embedding endpoint
   - Saves the embedding vectors to corresponding output files
   - Includes proper error handling and logging

### Step 3: Python Test Script Implementation

```python
#!/usr/bin/env python3
"""
test_embeddings.py - Test generating embeddings for LOINC chunk documents

This script reads LOINC chunk documents, generates embeddings using the
ollama-medcpt container, and saves the embeddings to output files.
"""

import os
import json
import time
import requests
import numpy as np
import glob
from pathlib import Path
import sys

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/embed"
OLLAMA_MODEL = "oscardp96/medcpt-article"
INPUT_DIR = "./input"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def check_ollama_service():
    """Check if the Ollama service is available."""
    try:
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code == 200:
            print(f"✅ Ollama service is available")
            return True
        else:
            print(f"❌ Ollama service returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Ollama service: {e}")
        print("   Make sure the ollama-medcpt container is running")
        print("   You can start it with: python check_services.py")
        return False

def get_embedding(text, model=OLLAMA_MODEL, retries=MAX_RETRIES):
    """
    Generate embedding for the given text using Ollama API.
    
    Args:
        text (str): The text to embed
        model (str): The model to use for embedding
        retries (int): Number of retry attempts
        
    Returns:
        dict: API response containing embedding or None if failed
    """
    payload = {
        "model": model,
        "input": text
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(OLLAMA_API_URL, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ API returned status code {response.status_code}: {response.text}")
                if attempt < retries - 1:
                    print(f"   Retrying in {RETRY_DELAY} seconds... ({attempt+1}/{retries})")
                    time.sleep(RETRY_DELAY)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request error: {e}")
            if attempt < retries - 1:
                print(f"   Retrying in {RETRY_DELAY} seconds... ({attempt+1}/{retries})")
                time.sleep(RETRY_DELAY)
    
    return None

def find_loinc_chunk_files(directory=INPUT_DIR):
    """Find all LOINC chunk files in the specified directory."""
    return glob.glob(os.path.join(directory, "*.loinc-chunk.md"))

def process_loinc_file(file_path):
    """
    Process a single LOINC chunk file.
    
    Args:
        file_path (str): Path to the LOINC chunk file
        
    Returns:
        bool: True if successful, False otherwise
    """
    file_name = os.path.basename(file_path)
    loinc_code = file_name.split(".")[0]
    output_file = os.path.join(INPUT_DIR, f"{loinc_code}.loinc-embed.txt")
    
    print(f"Processing: {file_name}")
    
    try:
        # Read the content of the LOINC chunk file
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Generate embedding using Ollama API
        print(f"  Generating embedding...")
        result = get_embedding(content)
        
        if not result or "embedding" not in result:
            print(f"❌ Failed to generate embedding for {file_name}")
            return False
            
        # Save embedding to output file
        embedding = result["embedding"]
        embedding_dim = result.get("dim", len(embedding))
        
        with open(output_file, 'w') as f:
            # Write embedding as JSON with metadata
            output_data = {
                "loinc_code": loinc_code,
                "model": OLLAMA_MODEL,
                "embedding_dim": embedding_dim,
                "embedding": embedding,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            json.dump(output_data, f, indent=2)
            
        print(f"✅ Successfully saved embedding to {output_file}")
        print(f"   Embedding dimension: {embedding_dim}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_name}: {e}")
        return False

def run_tests():
    """Run embedding generation tests on LOINC chunk files."""
    if not check_ollama_service():
        return False
        
    chunk_files = find_loinc_chunk_files()
    if not chunk_files:
        print("❌ No LOINC chunk files found in the input directory")
        print(f"   Expected files with pattern: *.loinc-chunk.md in {INPUT_DIR}")
        return False
        
    print(f"Found {len(chunk_files)} LOINC chunk files to process")
    
    success_count = 0
    for file_path in chunk_files:
        if process_loinc_file(file_path):
            success_count += 1
            
    print(f"\n📊 Embedding Generation Summary:")
    print(f"   Processed {len(chunk_files)} LOINC chunk files")
    print(f"   Successfully generated {success_count} embeddings")
    print(f"   Failed: {len(chunk_files) - success_count}")
    
    return success_count == len(chunk_files)

def analyze_embeddings():
    """Analyze generated embeddings for basic validation."""
    embed_files = glob.glob(os.path.join(INPUT_DIR, "*.loinc-embed.txt"))
    
    if not embed_files:
        print("❌ No embedding files found for analysis")
        return
        
    print(f"\n📈 Embedding Analysis:")
    print(f"   Found {len(embed_files)} embedding files")
    
    # Sample analysis on first file
    with open(embed_files[0], 'r') as f:
        data = json.load(f)
        
    embedding = data["embedding"]
    embedding_np = np.array(embedding)
    
    print(f"   Sample embedding statistics (from {os.path.basename(embed_files[0])}):")
    print(f"     Dimension: {data['embedding_dim']}")
    print(f"     Min value: {np.min(embedding_np):.6f}")
    print(f"     Max value: {np.max(embedding_np):.6f}")
    print(f"     Mean value: {np.mean(embedding_np):.6f}")
    print(f"     Standard deviation: {np.std(embedding_np):.6f}")
    
    # Check for common issues
    if np.isnan(embedding_np).any():
        print("   ⚠️ Warning: NaN values detected in embedding")
    
    if np.all(embedding_np == 0):
        print("   ⚠️ Warning: All zero embedding detected")

def main():
    """Main entry point for the test script."""
    print("🧪 Running LOINC Embedding Generation Tests")
    
    if run_tests():
        analyze_embeddings()
        print("\n✅ All tests completed successfully")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Step 4: Testing and Validation Plan
1. **Basic Testing**
   - Run the script when ollama-medcpt container is running
   - Run the script when ollama-medcpt container is not running
   - Verify proper error handling and messaging

2. **Performance Testing**
   - Test with single document to measure embedding generation time
   - Test with multiple documents to check for performance issues

3. **Output Validation**
   - Verify structure of embedding files
   - Check dimensionality of generated embeddings
   - Perform basic statistical analysis on embeddings

### Step 5: Expected Output and File Format
The script should generate `<loinc>.loinc-embed.txt` files with the following JSON structure:

```json
{
  "loinc_code": "12345-6",
  "model": "oscardp96/medcpt-article",
  "embedding_dim": 1536,
  "embedding": [0.123, 0.456, ...],
  "generated_at": "2025-07-26 15:30:45"
}
```

## Implementation Features

1. **Robust Error Handling**
   - Checks if Ollama service is available
   - Handles API errors with retry mechanism
   - Provides clear error messages

2. **Comprehensive Testing**
   - Processes all LOINC chunk files in the input directory
   - Reports success/failure for each file
   - Provides a summary of test results

3. **Embedding Analysis**
   - Performs basic statistical analysis on embeddings
   - Checks for common embedding issues (NaN values, zero vectors)
   - Reports dimensionality and other properties

4. **Metadata Inclusion**
   - Saves LOINC code and model information with embeddings
   - Includes timestamp for tracking
   - Preserves dimensionality information

5. **Progress Reporting**
   - Shows real-time processing status
   - Provides clear success/failure indicators
   - Generates a comprehensive summary

## Expected Output

When running the script, users should see output similar to:

```
🧪 Running LOINC Embedding Generation Tests
✅ Ollama service is available
Found 10 LOINC chunk files to process
Processing: 10008-1.loinc-chunk.md
  Generating embedding...
✅ Successfully saved embedding to ./input/10008-1.loinc-embed.txt
   Embedding dimension: 1536
Processing: 100081-9.loinc-chunk.md
  Generating embedding...
✅ Successfully saved embedding to ./input/100081-9.loinc-embed.txt
   Embedding dimension: 1536
...

📊 Embedding Generation Summary:
   Processed 10 LOINC chunk files
   Successfully generated 10 embeddings
   Failed: 0

📈 Embedding Analysis:
   Found 10 embedding files
   Sample embedding statistics (from 10008-1.loinc-embed.txt):
     Dimension: 1536
     Min value: -0.163842
     Max value: 0.298761
     Mean value: 0.000124
     Standard deviation: 0.054876

✅ All tests completed successfully
```

## Next Steps
After completing this task:
1. Verify the script correctly generates embedding files
2. Check that the embedding files contain valid vectors
3. Commit changes as specified in Task 6
4. Proceed to Task 7 (creating a Qdrant collection and loading embeddings)
