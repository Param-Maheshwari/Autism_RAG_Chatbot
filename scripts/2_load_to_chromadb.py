import os
import json
import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm

DB_PATH = "./chroma_db"
JSON_FOLDER = "./data/processed_json"

def main():
    print("🚀 Loading all JSON files into ChromaDB...")

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection("autism_research_papers")

    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    added, skipped = 0, 0

    for filename in tqdm(os.listdir(JSON_FOLDER)):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(JSON_FOLDER, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Safe key access
            text = data.get("Sections", {}).get("FullText", {}).get("text", "").strip()
            if not text:
                print(f"⚠️ Skipping {filename} — empty or missing text.")
                skipped += 1
                continue

            # Avoid duplicates
            collection.add(
                documents=[text],
                metadatas=[{"source": filename}],
                ids=[filename]
            )
            added += 1

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            skipped += 1

    print(f"\n✅ Loaded {added} papers into ChromaDB.")
    print(f"⚠️ Skipped {skipped} invalid or empty files.")

if __name__ == "__main__":
    main()
