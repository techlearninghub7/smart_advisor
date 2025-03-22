# RAG Chatbot Application

This is a Retrieval-Augmented Generation (RAG) chatbot built with Streamlit, LangChain, and the Gemini model from Google. It leverages a vector database (Chroma) to enhance responses with external knowledge.

## Prerequisites
- Python 3.8+
- Install dependencies: `pip install -r requirements.txt`
- Set `GOOGLE_API_KEY` in `.env`

## Setup
1. Clone the repository.
2. Create a `.env` file with your Google API key.
3. Run `streamlit run app.py` to start the app.

## Features
- Upload PDFs, DOCX, CSVs, and URLs to build a knowledge base.
- Chat with the assistant using retrieved context.
- View and clear chat history.

## Development
- Structure follows a modular design with `src/` directory.
- Test locally in VS Code using the provided entry point.

## D:\AI Projects\tiaa_wma_chabot\
│
├── static\
│   └── logo.png           # Company logo (optional, fallback to placeholder)
├── .env                   # Environment variables
├── app.py                 # Entry point
├── requirements.txt       # Dependencies
└── src\
    ├── config.py          # Configuration management
    ├── data\
    │   ├── loaders.py     # Document loading logic
    │   └── processors.py  # Document processing logic
    ├── vector\
    │   └── store.py       # Vector store management
    ├── llm\
    │   └── model.py       # LLM and RAG chain setup
    ├── utils.py           # Utility functions (e.g., chat history)
    └── ui\
        └── interface.py   # Streamlit UI