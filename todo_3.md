# Task 3: Create Docker Container Management Script

## Objective
Create a Python script that checks if the required docker containers (qdrant and deenihl/ollama-medcpt) are running and starts new ones if not. The script should ensure proper volume mounting for the qdrant container, connecting the `./data/` and `./input/` folders.

## Understanding
From the todo.gemini.md file, we need to create a script that:
1. Checks if the qdrant container is running
2. Checks if the deenihl/ollama-medcpt container is running
3. Starts new containers if either is not running
4. Ensures proper volume mounting for the qdrant container

## Plan

### Step 1: Research Container Requirements
1. **Qdrant Container**
   - Image: qdrant/qdrant
   - Required volume mounts:
     - `./data/` → Storage for vector embeddings
     - `./input/` → Input data for processing
   - Default port: 6333 (REST API), 6334 (gRPC)

2. **Ollama-MedCPT Container**
   - Image: deenihl/ollama-medcpt
   - Contains ollama service with locally registered model: oscardp96/medcpt-article
   - Default port: 11434 (Ollama API endpoint)

### Step 2: Implementation Approach
1. Design a Python script `check_services.py` that:
   - Uses Docker SDK for Python or subprocess to interact with Docker
   - Checks for running containers by name/image
   - Starts missing containers with appropriate parameters
   - Handles proper error messages and logging

### Step 3: Python Script Implementation

```python
#!/usr/bin/env python3
"""
check_services.py - Service availability checker for QdrantLoinc project

This script checks if required Docker containers (qdrant and ollama-medcpt)
are running and starts them if they are not available.
"""

import subprocess
import json
import os
import time
import sys
from pathlib import Path

# Container configuration
QDRANT_CONTAINER_NAME = "qdrant-loinc"
QDRANT_IMAGE = "qdrant/qdrant:latest"
QDRANT_PORT_REST = 6333
QDRANT_PORT_GRPC = 6334

OLLAMA_CONTAINER_NAME = "ollama-medcpt"
OLLAMA_IMAGE = "deenihl/ollama-medcpt:latest"
OLLAMA_PORT = 11434

# Ensure required directories exist
def ensure_dirs_exist():
    """Create data and input directories if they don't exist."""
    Path("./data").mkdir(exist_ok=True)
    Path("./input").mkdir(exist_ok=True)
    print("✅ Verified required directories exist")

# Get list of running containers
def get_running_containers():
    """Get a list of currently running Docker containers."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting container list: {e}")
        print(f"Error output: {e.stderr}")
        return []
    except FileNotFoundError:
        print("❌ Docker command not found. Is Docker installed and in your PATH?")
        sys.exit(1)

# Check if Docker is running
def check_docker_running():
    """Verify Docker daemon is running."""
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        print("✅ Docker is running")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker is not running. Please start Docker daemon first.")
        return False
    except FileNotFoundError:
        print("❌ Docker command not found. Is Docker installed and in your PATH?")
        return False

# Start Qdrant container
def start_qdrant_container():
    """Start the Qdrant container with appropriate volume mounts."""
    try:
        # Get absolute paths for volume mounts
        data_dir = os.path.abspath("./data")
        input_dir = os.path.abspath("./input")
        
        # Run the container
        subprocess.run([
            "docker", "run", 
            "-d",
            "--name", QDRANT_CONTAINER_NAME,
            "-p", f"{QDRANT_PORT_REST}:{QDRANT_PORT_REST}",
            "-p", f"{QDRANT_PORT_GRPC}:{QDRANT_PORT_GRPC}",
            "-v", f"{data_dir}:/qdrant/storage",
            "-v", f"{input_dir}:/input",
            QDRANT_IMAGE
        ], check=True)
        
        print(f"✅ Started Qdrant container: {QDRANT_CONTAINER_NAME}")
        print(f"   REST API available at: http://localhost:{QDRANT_PORT_REST}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Qdrant container: {e}")
        print(f"Error output: {e.stderr}")
        return False

# Start Ollama container
def start_ollama_container():
    """Start the Ollama MedCPT container."""
    try:
        subprocess.run([
            "docker", "run",
            "-d",
            "--name", OLLAMA_CONTAINER_NAME,
            "-p", f"{OLLAMA_PORT}:{OLLAMA_PORT}",
            OLLAMA_IMAGE
        ], check=True)
        
        print(f"✅ Started Ollama container: {OLLAMA_CONTAINER_NAME}")
        print(f"   Ollama API available at: http://localhost:{OLLAMA_PORT}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Ollama container: {e}")
        print(f"Error output: {e.stderr}")
        return False

# Wait for container to be ready
def wait_for_service(container_name, port, timeout=30):
    """Wait for a service to become available."""
    print(f"⏳ Waiting for {container_name} to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        # For Qdrant, check its health endpoint
        if container_name == QDRANT_CONTAINER_NAME:
            try:
                result = subprocess.run(
                    ["curl", "-s", f"http://localhost:{port}/health"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and "ok" in result.stdout.lower():
                    print(f"✅ {container_name} is ready!")
                    return True
            except:
                pass
        # For Ollama, check if it responds to API calls
        elif container_name == OLLAMA_CONTAINER_NAME:
            try:
                result = subprocess.run(
                    ["curl", "-s", f"http://localhost:{port}/api/version"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✅ {container_name} is ready!")
                    return True
            except:
                pass
                
        time.sleep(2)
    
    print(f"⚠️ Timed out waiting for {container_name} to be ready")
    return False

# Check and start containers as needed
def check_and_start_containers():
    """Check if required containers are running and start them if needed."""
    if not check_docker_running():
        return False
        
    running_containers = get_running_containers()
    
    # Check Qdrant container
    if QDRANT_CONTAINER_NAME not in running_containers:
        print(f"⚠️ Qdrant container '{QDRANT_CONTAINER_NAME}' is not running.")
        if start_qdrant_container():
            wait_for_service(QDRANT_CONTAINER_NAME, QDRANT_PORT_REST)
    else:
        print(f"✅ Qdrant container '{QDRANT_CONTAINER_NAME}' is already running")
        
    # Check Ollama container
    if OLLAMA_CONTAINER_NAME not in running_containers:
        print(f"⚠️ Ollama container '{OLLAMA_CONTAINER_NAME}' is not running.")
        if start_ollama_container():
            wait_for_service(OLLAMA_CONTAINER_NAME, OLLAMA_PORT)
    else:
        print(f"✅ Ollama container '{OLLAMA_CONTAINER_NAME}' is already running")
    
    return True

# Check container status
def check_container_status(container_name):
    """Check detailed status of a specific container."""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{json .State}}", container_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        state = json.loads(result.stdout)
        if state.get("Running", False):
            status = "running"
            if state.get("Health", {}).get("Status") == "healthy":
                status += " (healthy)"
            elif state.get("Health", {}).get("Status") == "unhealthy":
                status += " (unhealthy)"
        else:
            if state.get("ExitCode", 0) != 0:
                status = f"stopped (exit code: {state.get('ExitCode')})"
            else:
                status = "stopped"
                
        return status
    except subprocess.CalledProcessError:
        return "not found"
    except json.JSONDecodeError:
        return "unknown"

# Main function
def main():
    """Main entry point for the script."""
    print("🔍 Checking QdrantLoinc required services...")
    
    ensure_dirs_exist()
    if check_and_start_containers():
        # Final status check
        qdrant_status = check_container_status(QDRANT_CONTAINER_NAME)
        ollama_status = check_container_status(OLLAMA_CONTAINER_NAME)
        
        print("\n📊 Services Status Summary:")
        print(f"  - Qdrant ({QDRANT_CONTAINER_NAME}): {qdrant_status}")
        print(f"    REST API URL: http://localhost:{QDRANT_PORT_REST}")
        print(f"  - Ollama MedCPT ({OLLAMA_CONTAINER_NAME}): {ollama_status}")
        print(f"    API URL: http://localhost:{OLLAMA_PORT}")
    else:
        print("\n❌ Failed to ensure all services are running")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Step 4: Create a Shell Script Wrapper

In addition to the Python script, create a simple shell script wrapper `check_services.sh` for easier execution:

```bash
#!/bin/bash

# check_services.sh - Shell wrapper for check_services.py

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to script directory to ensure proper path resolution
cd "$SCRIPT_DIR"

# Execute the Python script
python3 check_services.py

# Exit with the same code as the Python script
exit $?
```

### Step 5: Testing and Validation
1. Test the script when both containers are already running
2. Test the script when both containers are stopped
3. Test the script when one container is running and one is stopped
4. Verify proper volume mounting for the qdrant container
5. Confirm both services are accessible via their respective ports

## Implementation Features

1. **Robust Error Handling**
   - Checks if Docker daemon is running
   - Handles errors when containers fail to start
   - Provides clear error messages

2. **Service Readiness**
   - Waits for containers to be fully operational
   - Tests service endpoints to confirm availability
   - Sets a reasonable timeout period

3. **Proper Volume Mounting**
   - Mounts `./data/` to `/qdrant/storage` for persistent storage
   - Mounts `./input/` to `/input` for access to LOINC documents

4. **Detailed Status Reporting**
   - Shows container status (running/stopped)
   - Displays container health when available
   - Provides access URLs for services

5. **Directory Management**
   - Creates required directories if they don't exist
   - Uses absolute paths to ensure proper volume mounting

## Expected Output

When running the script, users should see output similar to:

```
🔍 Checking QdrantLoinc required services...
✅ Verified required directories exist
✅ Docker is running
⚠️ Qdrant container 'qdrant-loinc' is not running.
✅ Started Qdrant container: qdrant-loinc
   REST API available at: http://localhost:6333
⏳ Waiting for qdrant-loinc to be ready...
✅ qdrant-loinc is ready!
⚠️ Ollama container 'ollama-medcpt' is not running.
✅ Started Ollama container: ollama-medcpt
   Ollama API available at: http://localhost:11434
⏳ Waiting for ollama-medcpt to be ready...
✅ ollama-medcpt is ready!

📊 Services Status Summary:
  - Qdrant (qdrant-loinc): running
    REST API URL: http://localhost:6333
  - Ollama MedCPT (ollama-medcpt): running
    API URL: http://localhost:11434
```

## Next Steps
After completing this task:
1. Make the scripts executable: `chmod +x check_services.py check_services.sh`
2. Test the scripts to ensure they work as expected
3. Commit changes as specified in Task 4
4. Proceed to Task 5 (writing tests for generating embeddings)
