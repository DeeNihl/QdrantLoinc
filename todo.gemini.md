1. based on @QdrantLoinc/embeddingmodel.gemini.md and  @QdrantLoinc/loinc_vectorization_guide.gemini.md  create 10 random loinc code documents for embedding. Name each document using the LOINC code (e.g. 788-0) in the filename like 788-0.loinc-chunk.md  aka <loinc>.loinc-chun.md. Store these in ./input  
2. Commit changes
3. create a python script that will check for both qdrant and  deenihl/ollama-medcpt docker containers to be running and start new  ones if not. remember to attach "./data/" and "./input/" folders as  volume mounts to the qdrant container. 
4. Commit changes
5. write tests that call the  ollama-medcpt container ollama endpoint and generate embeddings for  one or more of the <loinc>.loinc-chunk.md documents. Save these  embeddings as  <loinc>.loinc-embed.txt files 
6. Commit changes
7. write tests to create a collection named loinc-core in the qdrant database. load  the <loinc>.loinc-embed.txt files content to the loinc-core  collection with the payload including the LOINC code  and the LOINC  parts full names not abbreviation  
