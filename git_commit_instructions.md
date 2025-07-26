# Git Commit Commands

After completing each task, you should commit your changes to the Git repository. Here are the commands to use after completing each task:

## After Task 1: Creating LOINC Documents
```bash
# Add the new LOINC chunk documents to Git
git add ./input/*.loinc-chunk.md
git add ./todo_1.md

# Commit the changes
git commit -m "Task 1: Created 10 random LOINC code documents for embedding"
```

## After Task 3: Creating Docker Container Management Script
```bash
# Add the Python script and shell wrapper to Git
git add ./check_services.py
git add ./check_services.sh
git add ./todo_3.md

# Make the scripts executable
chmod +x check_services.py check_services.sh

# Commit the changes
git commit -m "Task 3: Created script to check and start Docker containers"
```

## After Task 5: Writing Tests for Generating Embeddings
```bash
# Add the embedding test script to Git
git add ./test_embeddings.py
git add ./input/*.loinc-embed.txt
git add ./todo_5.md

# Make the script executable
chmod +x test_embeddings.py

# Commit the changes
git commit -m "Task 5: Added tests for generating embeddings from LOINC documents"
```

## After Task 7: Creating Qdrant Collection and Loading Embeddings
```bash
# Add the Qdrant collection test script to Git
git add ./test_qdrant_collection.py
git add ./todo_7.md

# Make the script executable
chmod +x test_qdrant_collection.py

# Commit the changes
git commit -m "Task 7: Created and populated Qdrant collection with LOINC embeddings"
```

## Final Project Commit
After completing all tasks, you may want to make a final commit that includes any remaining files and updates the main README:

```bash
# Add any remaining files
git add README.md
git add .

# Commit the changes
git commit -m "Completed all tasks for QdrantLoinc project"

# Push changes to the remote repository (if applicable)
git push origin main
```

Remember to run these commands from the root directory of the project: `/home/deenihl/git/ohdsi/QdrantLoinc`
