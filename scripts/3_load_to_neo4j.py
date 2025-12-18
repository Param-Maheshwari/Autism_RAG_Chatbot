from neo4j import GraphDatabase
import json
import os
from tqdm import tqdm

URI = "neo4j://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "team@026"
JSON_FOLDER = "./data/processed_json"

class Neo4jLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS
                FOR (s:Section) REQUIRE s.name IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS
                FOR (d:Document) REQUIRE d.file_name IS UNIQUE
            """)

    def load_document(self, data):
        with self.driver.session() as session:
            try:
                file_name = data.get("file_name", "unknown")
                text = data.get("Sections", {}).get("FullText", {}).get("text", "").strip()

                if not text:
                    print(f"⚠️ Skipping {file_name} — missing text.")
                    return

                section_name = f"{file_name}_FullText"

                # Use MERGE instead of CREATE for idempotency
                session.run("""
                    MERGE (d:Document {file_name: $file_name})
                    MERGE (s:Section {name: $section_name})
                    SET s.text = $text
                    MERGE (d)-[:HAS_SECTION]->(s)
                """, file_name=file_name, section_name=section_name, text=text)

            except Exception as e:
                print(f"❌ Error loading document {data.get('file_name', '?')}: {e}")

def main():
    loader = Neo4jLoader()
    loader.create_constraints()

    added, skipped = 0, 0
    print("⚙️ Loading all papers into Neo4j...")

    for filename in tqdm(os.listdir(JSON_FOLDER)):
        if not filename.endswith(".json"):
            continue

        try:
            with open(os.path.join(JSON_FOLDER, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
            loader.load_document(data)
            added += 1
        except Exception as e:
            print(f"❌ Failed {filename}: {e}")
            skipped += 1

    loader.close()
    print(f"\n✅ Added {added} papers to Neo4j.")
    print(f"⚠️ Skipped {skipped} invalid files.")

if __name__ == "__main__":
    main()
