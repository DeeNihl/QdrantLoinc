import csv
import ollama
from qdrant_client import QdrantClient, models

# Configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "oscardp96/medcpt-article"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "loinc"
LOINC_CSV_PATH = "/home/deenihl/git/ohdsi/QdrantLoinc/LOINC/Loinc/LoincTableCore/LoincTableCore.csv"
PART_CSV_PATH = "/home/deenihl/git/ohdsi/QdrantLoinc/LOINC/Loinc/AccessoryFiles/PartFile/Part.csv"

# Initialize clients
ollama_client = ollama.Client(host=OLLAMA_HOST)
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def get_embedding(text):
    response = ollama_client.embed(
        model=OLLAMA_MODEL,
        input=text
    )
    return response["embedding"]

def create_part_lookup():
    part_lookup = {}
    with open(PART_CSV_PATH, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            part_lookup[row['PartNumber']] = row['PartName']
    return part_lookup

def main():
    # Create part lookup table
    part_lookup = create_part_lookup()

    # Create Qdrant collection
    try:
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE), # Assuming embedding size is 768
        )
        print(f"Collection '{COLLECTION_NAME}' created.")
    except Exception as e:
        print(f"Could not create collection: {e}")
        # Exit if collection can't be created
        return

    # Process LOINC data
    with open(LOINC_CSV_PATH, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        points = []
        for i, row in enumerate(reader):
            # Get full names from part lookup
            component = row['COMPONENT']
            prop = part_lookup.get(row['PROPERTY'], row['PROPERTY'])
            time_aspct = part_lookup.get(row['TIME_ASPCT'], row['TIME_ASPCT'])
            system = part_lookup.get(row['SYSTEM'], row['SYSTEM'])
            scale_typ = part_lookup.get(row['SCALE_TYP'], row['SCALE_TYP'])
            method_typ = part_lookup.get(row['METHOD_TYP'], row['METHOD_TYP'])

            # Construct descriptive text
            text_to_embed = f"This LOINC term is for '{row['LONG_COMMON_NAME']}'. Component: {component}. Property: {prop}. Time Aspect: {time_aspct}. System: {system}. Scale: {scale_typ}. Method: {method_typ}. Class: {row['CLASS']}."

            # Generate embedding
            embedding = get_embedding(text_to_embed)

            # Prepare payload
            payload = {
                "Fully-Specified Name": row['LONG_COMMON_NAME'],
                "LOINC code": row['LOINC_NUM'],
                "Component": component,
                "Property": prop,
                "Time": time_aspct,
                "System": system,
                "Scale": scale_typ,
                "Method": method_typ,
            }

            # Create point for Qdrant
            points.append(models.PointStruct(
                id=i + 1,
                vector=embedding,
                payload=payload
            ))

            # Upsert in batches of 100
            if len(points) == 100:
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    wait=True,
                    points=points
                )
                points = []
                print(f"Upserted 100 points...")

        # Upsert any remaining points
        if points:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                wait=True,
                points=points
            )
            print(f"Upserted remaining {len(points)} points.")

if __name__ == "__main__":
    main()