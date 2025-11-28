import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings

# 1. Setup Embeddings (The "Translator" that turns text to numbers)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. Define Index Path (Where we save the "Brain" on disk)
INDEX_PATH = "faiss_index"

def get_vector_store():
    """
    Loads the Vector DB from disk if it exists, otherwise creates a new one.
    """
    if os.path.exists(INDEX_PATH):
        # Allow dangerous deserialization because we created the file ourselves
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        # Create an empty index to start
        return FAISS.from_texts(["Start of index"], embeddings)

def add_document_to_knowledge_base(text: str):
    """
    1. Splits text intelligently.
    2. Embeds it.
    3. Adds to FAISS index.
    4. Saves to disk.faiss_index
    """
    # Intelligent Splitting (Respects sentences/paragraphs)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text(text)
    
    # Load current index
    vector_store = get_vector_store()
    
    # Add new chunks
    vector_store.add_texts(chunks)
    
    # Save to disk immediately
    vector_store.save_local(INDEX_PATH)
    print(f"✅ Added {len(chunks)} chunks to knowledge base.")

def get_retriever():
    """
    Returns a 'Retriever' object that LangChain can use directly in chains.
    """
    vector_store = get_vector_store()
    # Search top 4 most relevant chunks
    return vector_store.as_retriever(search_kwargs={"k": 4})