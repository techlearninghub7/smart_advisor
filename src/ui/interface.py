# src/ui/interface.py
import streamlit as st
import time
import os
from dotenv import load_dotenv
from src.data.loaders import load_documents
from src.data.processors import process_documents
from src.vector.store import initialize_vector_store, update_vector_store
from src.llm.model import setup_llm_and_retriever, process_with_standalone_llm, create_rag_chain
from src.llm.chat_history_processor import prepare_chat_history_for_llm
from src.db.database import init_db, save_chat_history, load_chat_history, clear_chat_history, save_processed_docs, load_processed_docs
from src.config import Config
from google.api_core import exceptions


def setup_ui():
    # Load .env explicitly for Streamlit
    load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
    print("Loading .env file...")

    # Initialize SQLite database
    init_db()

     # Include Bootstrap CDN and custom CSS
    st.markdown("""
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
        .logo-container { text-align: center; margin-bottom: 20px; }
        .logo-img { max-width: 100px; height: auto; }
        .main-title { font-size: 28px; font-weight: bold; color: #2c3e50; text-align: center; margin-bottom: 20px; }
        .chat-container { background-color: #f8f9fa; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .chat-message { background-color: #ffffff; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .chat-message strong { color: #2c3e50; }
        .sidebar .sidebar-content { background-color: #f8f9fa; padding: 15px; border-right: 1px solid #dee2e6; }
        .history-item { background-color: #ffffff; padding: 10px; border-radius: 5px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        .history-item p { margin: 0; }
        </style>
    """, unsafe_allow_html=True)

    # Add company logo
    logo_path = os.path.join(os.path.dirname(__file__), '../../static/logo.jpg')
    if os.path.exists(logo_path):
        print(f"Loading logo from {logo_path}")
        ##st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(logo_path, width=100, caption="")
        ##st.markdown('<div class="main-title">Chatbot powered by TIAA</div>', unsafe_allow_html=True)
    else:
        print(f"Logo not found at {logo_path}. Using placeholder.")
        st.markdown("""
            <div class="logo-container">
                <img src="https://via.placeholder.com/150x50.png?text=Company+Logo" class="logo-img" alt="Company Logo">
            </div>
        """, unsafe_allow_html=True)

    # Main title
    ##st.markdown('<div class="main-title">Chatbot powered by TIAA</div>', unsafe_allow_html=True)

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = load_chat_history()
        print(f"Initialized chat history with {len(st.session_state.chat_history)} entries.")
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = initialize_vector_store()
        print(f"Initial vectorstore setup: {st.session_state.vectorstore is not None}")

    # Body
    st.markdown('<div class="body-container">', unsafe_allow_html=True)
    # Sidebar for uploads and history
    with st.sidebar:
        st.markdown('<h4 class="mb-3">Document Management</h4>', unsafe_allow_html=True)
        with st.expander("Upload Files & URLs", expanded=True):
            pdf_files = st.file_uploader("PDFs", type="pdf", accept_multiple_files=True, key="pdf_upload")
            docx_files = st.file_uploader("DOCX", type="docx", accept_multiple_files=True, key="docx_upload")
            csv_files = st.file_uploader("CSVs", type="csv", accept_multiple_files=True, key="csv_upload")
            url_input = st.text_area("Enter URLs (one per line)", height=100, key="url_input")
            additional_urls = [url.strip() for url in url_input.split("\n") if url.strip()]
            print(f"Uploaded files: PDFs={len(pdf_files or [])}, DOCX={len(docx_files or [])}, CSV={len(csv_files or [])}, URLs={len(additional_urls)}")

        if pdf_files or docx_files or csv_files or additional_urls:
            with st.spinner("Processing documents..."):
                documents = load_documents(pdf_files, docx_files, csv_files, additional_urls)
                print(f"Loaded documents count: {len(documents)}")
                if not documents:
                    st.error("No documents were successfully loaded. Please check the files or URLs.")
                else:
                    processed_docs = process_documents(documents)
                    print(f"Processed documents count: {len(processed_docs)}")
                    if not processed_docs:
                        st.error("Document processing failed. Please check the file formats.")
                    else:
                        if st.session_state.vectorstore is None:
                            st.session_state.vectorstore = initialize_vector_store(processed_docs)
                            print(f"Vectorstore after init with docs: {st.session_state.vectorstore is not None}")
                        if st.session_state.vectorstore is not None:
                            update_vector_store(st.session_state.vectorstore, processed_docs)
                            all_docs = st.session_state.vectorstore._collection.get(include=["documents", "metadatas"])
                            doc_dicts = [{"page_content": doc, "metadata": meta} for doc, meta in zip(all_docs["documents"], all_docs["metadatas"])]
                            save_processed_docs(doc_dicts)  # Save to SQLite instead of JSON
                            print(f"Saved {len(doc_dicts)} documents to database")
                            st.success("Documents processed and saved.")
                        else:
                            st.error("Vector store initialization failed. Please check the API key or try again.")

        st.markdown('<h4 class="mt-4 mb-3">Chat History</h4>', unsafe_allow_html=True)
        if st.session_state.chat_history:
            for entry in st.session_state.chat_history:
                st.markdown(f"""
                    <div class="history-item">
                        <p><strong>Q:</strong> {entry['query']}</p>
                        <p><strong>A:</strong> {entry['answer']}</p>
                        <p><small><strong>Time:</strong> {time.ctime(entry['timestamp'])}</small></p>
                    </div>
                """, unsafe_allow_html=True)
                print(f"Displayed chat history entry: Q={entry['query'][:20]}...")
        else:
            st.info("No chat history yet.")
            print("No chat history to display.")

        if st.button("Clear Chat History", key="clear_history", help="Delete all chat history"):
            clear_chat_history()
            st.session_state.chat_history = []
            st.success("Chat history cleared.")
            print("Chat history cleared.")

    # Main chat area
    st.markdown('<h4 >Chat with the Virtual Assistant!</h4>', unsafe_allow_html=True)
    with st.container():
        ##st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        query = st.chat_input("Please ask a question:", key="chat_input")
        print(f"User input: {query}")

        if query:
            if st.session_state.vectorstore is None:
                st.error("Cannot process query: Vector store is not initialized. Please upload documents first.")
                print("Vector store is None, skipping query processing.")
            else:
                with st.spinner("Generating response..."):
                    # Load and prepare chat history
                    chat_history = load_chat_history()
                    chat_history_str = prepare_chat_history_for_llm(chat_history)
                    print(f"Chat history string length: {len(chat_history_str)}")
                    st.session_state.chat_history = chat_history  # Sync with session state
                    standalone_llm, final_llm, retriever = setup_llm_and_retriever(st.session_state.vectorstore)
                    
                    try:
                        # Step 1: Refine query with standalone LLM (as per diagram)
                        refined_query = process_with_standalone_llm(standalone_llm, query, chat_history_str)
                        
                        # Step 2: Retrieve enhanced text and generate response (as per diagram)
                        rag_chain = create_rag_chain(final_llm, retriever, chat_history_str)
                        response = rag_chain.invoke({"input": refined_query, "chat_history": chat_history_str})
                        answer = response["answer"]
                        print(f"Generated answer: {answer[:50]}...")
                    except exceptions.ResourceExhausted as e:
                        st.error(f"API quota exceeded: {str(e)}. Please check your Google API quota or wait before retrying.")
                        print(f"ResourceExhausted error: {str(e)}")
                        return
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}. Please try again.")
                        print(f"Unexpected error: {str(e)}")
                        return

                    # Update and save chat history
                    st.session_state.chat_history.append({"query": query, "answer": answer, "timestamp": time.time()})
                    save_chat_history(st.session_state.chat_history)
                    st.success("Chat history saved.")
                    print(f"Appended chat history, total entries: {len(st.session_state.chat_history)}")

                    st.markdown(f'<div class="chat-message"><strong>Response:</strong><br>{answer}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)               
                    
        st.markdown('</div>', unsafe_allow_html=True)
    
def main():
    print("Starting application...")
    Config.validate_api_key()
    setup_ui()
    print("Application setup completed.")

if __name__ == "__main__":
    main()