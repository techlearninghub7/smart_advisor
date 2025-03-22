# src/data/loaders.py
import requests
import os
from io import BytesIO
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, CSVLoader, WebBaseLoader

def load_pdf_from_url(url):
    """Load PDF from a URL."""
    try:
        print(f"Attempting to load PDF from URL: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        pdf_file = BytesIO(response.content)
        loader = PyPDFLoader(pdf_file)
        docs = loader.load()
        print(f"Successfully loaded {len(docs)} pages from {url}")
        return docs
    except Exception as e:
        print(f"Error loading PDF from {url}: {str(e)}")
        return []

def load_documents(pdf_files, docx_files, csv_files, urls):
    """Load documents from various sources."""
    print("Starting document loading process...")
    documents = []
    
    for file in pdf_files or []:
        try:
            print(f"Processing uploaded PDF: {file.name}")
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())
            loader = PyPDFLoader(file.name)
            docs = loader.load()
            documents.extend(docs)
            os.remove(file.name)
            print(f"Loaded {len(docs)} pages from {file.name}")
        except Exception as e:
            print(f"Error loading PDF {file.name}: {str(e)}")

    for file in docx_files or []:
        try:
            print(f"Processing uploaded DOCX: {file.name}")
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())
            loader = Docx2txtLoader(file.name)
            docs = loader.load()
            documents.extend(docs)
            os.remove(file.name)
            print(f"Loaded {len(docs)} pages from {file.name}")
        except Exception as e:
            print(f"Error loading DOCX {file.name}: {str(e)}")

    for file in csv_files or []:
        try:
            print(f"Processing uploaded CSV: {file.name}")
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())
            loader = CSVLoader(file.name)
            docs = loader.load()
            documents.extend(docs)
            os.remove(file.name)
            print(f"Loaded {len(docs)} rows from {file.name}")
        except Exception as e:
            print(f"Error loading CSV {file.name}: {str(e)}")

    for url in urls or []:
        if url.lower().endswith('.pdf'):
            docs = load_pdf_from_url(url)
            documents.extend(docs)
        else:
            try:
                print(f"Processing URL: {url}")
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded {len(docs)} documents from {url}")
            except Exception as e:
                print(f"Error loading URL {url}: {str(e)}")

    print(f"Total documents loaded: {len(documents)}")
    return documents