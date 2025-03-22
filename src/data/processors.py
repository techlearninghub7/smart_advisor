# src/data/processors.py
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_documents(documents):
    """Split documents into chunks."""
    print(f"Processing {len(documents)} documents...")
    if not documents:
        print("No documents to process.")
        return []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"Processed into {len(chunks)} chunks.")
    return chunks