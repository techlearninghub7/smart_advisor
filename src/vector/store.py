# src/vector/store.py
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from src.config import Config
import os

def initialize_vector_store(documents=None):
    """Initialize or load the vector store."""
    try:
        print("Attempting to initialize vector store...")
        print(f"Documents provided: {documents is not None and len(documents) > 0}")
        print(f"GOOGLE_API_KEY: {Config.GOOGLE_API_KEY[:5]}... (partial for security)")

        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing.")

        embedding = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=Config.GOOGLE_API_KEY
        )
        print("Embedding object created successfully.")

        vectorstore = None
        if documents and len(documents) > 0:
            
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embedding,
                persist_directory=Config.VECTORSTORE_DIR
            )
            print(f"Vector store created at {Config.VECTORSTORE_DIR}")
        elif os.path.exists(Config.VECTORSTORE_DIR):
            
            vectorstore = Chroma(
                persist_directory=Config.VECTORSTORE_DIR,
                embedding_function=embedding
            )
            print(f"Vector store loaded from {Config.VECTORSTORE_DIR}")
        else:
            print(f"Warning: {Config.VECTORSTORE_DIR} does not exist, and no documents provided.")
            os.makedirs(Config.VECTORSTORE_DIR, exist_ok=True)
            print(f"Created directory {Config.VECTORSTORE_DIR}")

        return vectorstore
    except Exception as e:
        print(f"Error initializing vector store: {str(e)}")
        return None

def update_vector_store(vectorstore, documents):
    """Add new documents to the existing vector store."""
    if vectorstore:
        print(f"Updating vector store with {len(documents)} documents...")
        vectorstore.add_documents(documents)
        print("Vector store updated successfully.")
    else:
        print("Cannot update vector store: vectorstore is None.")