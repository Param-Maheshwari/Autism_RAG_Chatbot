
---

## 🧠 Data Pipeline Overview

### 1️⃣ Raw Data (`data/papers/`)
- Contains **PDF research papers** related to autism spectrum disorder.
- These files are:
  - Large in size
  - Often copyrighted
  - Not suitable for version control

➡️ **Ignored by Git** and expected to be provided locally by the user.

---

### 2️⃣ Processed Text (`data/processed_json/`)
- Output of `1_extract_papers.py`
- Each PDF is converted into structured JSON:
  - Cleaned text
  - Metadata (title, authors, year, etc.)
- Used as the input for vector and graph databases

➡️ **Ignored by Git** because it is:
- Derived data
- Fully reproducible from the raw PDFs

---

### 3️⃣ Vector Database (`chroma_db/`)
- Created by `2_load_to_chromadb.py`
- Stores:
  - Text embeddings
  - Index files
  - SQLite metadata
- Used for **semantic similarity search**

➡️ **Ignored by Git** because:
- It can be regenerated at any time
- Binary database files do not version well
- GitHub size limits would be exceeded

---

### 4️⃣ Knowledge Graph (Neo4j)
- Created by `3_load_to_neo4j.py`
- Extracts entities, concepts, and relationships from processed text
- Enables:
  - Structured reasoning
  - Relationship-aware retrieval

➡️ Neo4j data lives **outside the repository** in a running database instance.

---

## 🔍 Hybrid RAG Retrieval

The script `4_run_hybrid_rag.py`:
- Retrieves documents from **ChromaDB** (semantic similarity)
- Traverses **Neo4j** for related concepts
- Combines both sources to generate grounded responses

This approach improves:
- Factual accuracy
- Context depth
- Cross-paper reasoning

---

## 🚫 Why Data Is Ignored in Git

This repository intentionally **does NOT track data or databases**.

Reasons:
- GitHub file size limits
- Copyright restrictions
- Reproducibility over storage
- Cleaner commit history

### `.gitignore` includes:
```gitignore
venv/
chroma_db/
data/papers/
data/processed_json/
__pycache__/
*.pyc
