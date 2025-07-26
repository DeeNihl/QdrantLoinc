#!/bin/bash

# Check for deenihl/ollama-medcpt container
if [ "$(docker ps -q -f name=deenihl/ollama-medcpt)" ]; then
    echo "Docker container 'deenihl/ollama-medcpt' is running."
else
    echo "Error: Docker container 'deenihl/ollama-medcpt' is not running." >&2
    echo "Please start it using: docker run -d --name deenihl/ollama-medcpt -p 11434:11434 deenihl/ollama-medcpt" >&2
fi

# Check Ollama API endpoint
if curl -s http://localhost:11434/ > /dev/null; then
    echo "Ollama service is accessible at http://localhost:11434."
else
    echo "Error: Could not connect to Ollama service at http://localhost:11434." >&2
fi
