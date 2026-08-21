import sys
import os
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def resolve_pdf_path(target_path: str = None) -> Path:
    """Finds the target PDF using explicit arguments, default paths, or workspace discovery."""
    candidates = []
    if target_path:
        candidates.append(Path(target_path))
    
    # Common local search locations
    base_dir = Path(__file__).resolve().parent
    candidates.extend([
        base_dir / "documents" / "Call_CV.pdf",
        base_dir.parent / "documents" / "Call_CV.pdf",
        base_dir / "Market Intelligence Research Agent" / "Eclectik_Research_Intelligence_Brief.pdf",
        base_dir / "Call_CV.pdf"
    ])
    
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    # Search for any PDF in workspace
    for found in base_dir.rglob("*.pdf"):
        return found

    return None


def run_pdf_chatbot(pdf_path: str = None, user_query: str = None):
    print("=" * 65)
    print("📄 [PDF CHATBOT] RAG Pipeline with LangChain, Chroma & Ollama")
    print("=" * 65)

    resolved_path = resolve_pdf_path(pdf_path)
    if not resolved_path:
        print("❌ Error: No PDF document found to index.")
        print("Please provide a PDF file path as an argument: python Pdf_chatbot.py <path_to_pdf>")
        return

    print(f"📖 Loading PDF: {resolved_path.name} ({resolved_path})")

    # =========================
    # 1. Embedding Model
    # =========================
    print("⏳ Initializing SentenceTransformers embeddings...")
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # =========================
    # 2. Load PDF & Split
    # =========================
    loader = PyMuPDFLoader(str(resolved_path))
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} page(s) from document.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️ Created {len(chunks)} text chunk(s).")

    # =========================
    # 3. Create ChromaDB VectorStore
    # =========================
    collection_name = f"doc_{abs(hash(str(resolved_path))) % 100000}"
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        collection_name=collection_name
    )
    print("💾 Chunks successfully stored in ChromaDB vector store.")

    # =========================
    # 4. Create Retriever
    # =========================
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    # =========================
    # 5. User Question & Retrieval
    # =========================
    query = user_query or "What are the primary findings, experience, and key summary points in this document?"
    print(f"\n❓ Question: {query}")

    results = retriever.invoke(query)
    print(f"\n🔎 Retrieved {len(results)} relevant context chunk(s):")
    for i, doc in enumerate(results, 1):
        print(f"--- Chunk {i} ---")
        print(doc.page_content[:200] + ("..." if len(doc.page_content) > 200 else ""))

    context = "\n\n".join(doc.page_content for doc in results)

    # =========================
    # 6. LLM Generation
    # =========================
    prompt = f"""
You are a helpful and precise assistant.

Answer the question using ONLY the information provided in the context below.
If the answer cannot be determined from the context, say "I don't know based on the provided document."

Context:
{context}

Question:
{query}

Answer:
"""
    try:
        llm = ChatOllama(model="gemma3:4b")
        response = llm.invoke(prompt)
        print("\n" + "=" * 65)
        print("💡 [FINAL ANSWER]")
        print("=" * 65)
        print(response.content)
    except Exception as e:
        print(f"\n⚠️ Note: Local Ollama generation skipped ({e}).")
        print("To run local generation, ensure Ollama is running (`ollama serve` and `ollama run gemma3:4b`).")
        print("\nRetrieved Context Summary:")
        print(context[:400] + "...")


if __name__ == "__main__":
    cli_pdf = sys.argv[1] if len(sys.argv) > 1 else None
    cli_query = sys.argv[2] if len(sys.argv) > 2 else None
    run_pdf_chatbot(cli_pdf, cli_query)