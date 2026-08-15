from langchain_community.document_loaders import PyMuPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama


# =========================
# 1. LLM
# =========================

llm = ChatOllama(
    model="gemma3:4b"
)


# =========================
# 2. Embedding Model
# =========================

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# =========================
# 3. Load PDF
# =========================

loader = PyMuPDFLoader(
    r"E:\learning\Agentic ai\documents\Call_CV.pdf"
)

documents = loader.load()


# =========================
# 4. Split Documents
# =========================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

print("Number of chunks:", len(chunks))


# =========================
# 5. Create ChromaDB
# =========================

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    collection_name="my_cv"
)

print("Documents stored in ChromaDB")


# =========================
# 6. Create Retriever
# =========================

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)


# =========================
# 7. User Question
# =========================

query = "What work experience does Arbaz have?"


# =========================
# 8. Retrieve Relevant Chunks
# =========================

results = retriever.invoke(query)

print("\nRelevant chunks:\n")

for i, doc in enumerate(results):
    print(f"--- Chunk {i + 1} ---")
    print(doc.page_content)


# =========================
# 9. Create Context
# =========================

context = "\n\n".join(
    doc.page_content
    for doc in results
)


# =========================
# 10. Send Context + Question to LLM
# =========================

prompt = f"""
You are a helpful assistant.

Answer the question using ONLY the information
provided in the context.

If the answer is not available in the context,
say "I don't know based on the provided document."

Context:
{context}

Question:
{query}

Answer:
"""


# =========================
# 11. Generate Answer
# =========================

response = llm.invoke(prompt)


# =========================
# 12. Print Final Answer
# =========================

print("\nFinal Answer:")
print(response.content)