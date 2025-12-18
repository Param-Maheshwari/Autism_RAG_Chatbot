import ollama
import chromadb
from neo4j import GraphDatabase
from colorama import Fore, Style, init

# 🟩 Initialize colorama for colored terminal text
init(autoreset=True)

# 🧠 Neo4j and Chroma configuration
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "team@026"
CHROMA_PATH = "./chroma_db"

# 🗃️ Initialize ChromaDB (persistent client)
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection("autism_papers")
    print(Fore.GREEN + "✅ Connected to ChromaDB successfully.")
except Exception as e:
    print(Fore.RED + f"❌ Failed to connect to ChromaDB: {e}")
    exit(1)

# 🧩 Initialize Neo4j driver
try:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    print(Fore.GREEN + "✅ Connected to Neo4j successfully.")
except Exception as e:
    print(Fore.RED + f"❌ Failed to connect to Neo4j: {e}")
    exit(1)


# 🔍 Automatically detect installed Qwen model in Ollama
def get_qwen_model():
    try:
        models = ollama.list().get("models", [])
        for m in models:
            model_name = m.get("model") or m.get("name") or ""
            if "qwen" in model_name.lower():
                return model_name
    except Exception as e:
        print(Fore.RED + f"⚠️ Ollama model detection failed: {e}")
    return None


MODEL = get_qwen_model()
if not MODEL:
    print(Fore.RED + "❌ No Qwen model found in Ollama.")
    print(Fore.YELLOW + "👉 Run this to install one:")
    print(Fore.WHITE + "   ollama pull qwen2.5:3b")
    exit(1)
else:
    print(Fore.CYAN + f"🧠 Using Qwen model: {MODEL}")


# 🧬 Retrieve hybrid context (from ChromaDB + Neo4j)
def get_hybrid_context(query):
    context_texts = []

    # 1️⃣ From ChromaDB (vector retrieval)
    try:
        results = collection.query(query_texts=[query], n_results=2)
        for doc in results.get("documents", [[]])[0]:
            context_texts.append(doc)
    except Exception as e:
        print(Fore.RED + f"⚠️ Error querying ChromaDB: {e}")

    # 2️⃣ From Neo4j (graph reasoning)
    try:
        with neo4j_driver.session() as session:
            records = session.run("""
                MATCH (s:Section)
                WHERE toLower(s.text) CONTAINS toLower($query)
                RETURN s.text LIMIT 2
            """, query=query)
            for record in records:
                context_texts.append(record["s.text"])
    except Exception as e:
        print(Fore.RED + f"⚠️ Error querying Neo4j: {e}")

    if not context_texts:
        return "No context found in databases."
    return "\n\n".join(context_texts[:4])


# 💬 Query the hybrid RAG system (LLM + data context)
def query_hybrid(question):
    print(Fore.CYAN + "\n🔎 Fetching relevant context...\n")
    combined_context = get_hybrid_context(question)

    prompt = f"Question: {question}\n\nContext:\n{combined_context}"

    print(Fore.MAGENTA + "🤖 Sending query to Qwen...\n")

    try:
        response = ollama.chat(model=MODEL, messages=[
            {"role": "system", "content": "You are a helpful assistant summarizing autism research."},
            {"role": "user", "content": prompt}
        ])
        answer = response.get("message", {}).get("content", "⚠️ No answer generated.")
        print(Fore.GREEN + "💬 Answer:\n" + Style.RESET_ALL + answer)
    except Exception as e:
        print(Fore.RED + f"❌ Ollama query failed: {e}")


# 🚀 Main interactive chat loop
def main():
    print(Fore.MAGENTA + "\n🤖 Hybrid RAG System — Ask about Autism Research")
    print(Fore.WHITE + "Type 'exit' or 'quit' to stop.\n")

    while True:
        question = input(Fore.YELLOW + "Ask your question: ").strip()
        if question.lower() in ["exit", "quit"]:
            print(Fore.CYAN + "👋 Goodbye!")
            break
        elif question:
            query_hybrid(question)
        else:
            print(Fore.RED + "⚠️ Please enter a valid question.")


if __name__ == "__main__":
    main()
