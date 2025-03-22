# src/llm/model.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.config import Config

def setup_llm_and_retriever(vectorstore):
    """Set up LLM and retriever."""
    if vectorstore is None:
        raise ValueError("Vector store is None. Cannot setup LLM and retriever.")
    print("Setting up LLM and retriever...")
    
    standalone_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=4096,
        timeout=None,
        google_api_key=Config.GOOGLE_API_KEY
    )
    print("Standalone LLM initialized.")

    final_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=4096,
        timeout=None,
        google_api_key=Config.GOOGLE_API_KEY
    )
    print("Final LLM initialized.")

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
    print("Retriever set up with k=10 similarity search.")
    print("Retriever and LLMs set up, ready to use with chat history.")
    return standalone_llm, final_llm, retriever

def process_with_standalone_llm(llm, query, chat_history):
    """Process the query and chat history with a standalone LLM."""
    print(f"Processing query '{query[:20]}...' with chat history of length: {len(chat_history)}")
    standalone_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that refines user queries using chat history. "
                   "Given the chat history and new question, rephrase or enrich the question "
                   "to improve retrieval accuracy. Keep the output summarize and concise for the wealth management advisor and subject matter expert"),
        ("human", "Chat History:\n{chat_history}\n\nNew Question:\n{input}")
    ])
    chain = standalone_prompt | llm
    response = chain.invoke({"input": query, "chat_history": chat_history or "No previous chat history"})
    print(f"Refined query: {response.content}")
    return response.content

def create_rag_chain(llm, retriever, chat_history):
    """Create RAG chain with prompt for final LLM."""
    print(f"Creating RAG chain with chat history length: {len(chat_history)}")
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context and previous chat history to answer the question. "
        "If you don't know the answer, say that you don't know. Provide detailed answers when appropriate."
        "\n\n"
        "Previous Chat History:\n{chat_history}\n\n"
        "Retrieved Context:\n{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    print("RAG chain created with chat history integrated.")
    return rag_chain