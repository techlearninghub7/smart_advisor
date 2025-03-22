# src/llm/chat_history_processor.py
from typing import List, Dict
from src.db.database import save_chat_history, load_chat_history, clear_chat_history

def prepare_chat_history_for_llm(history: List[Dict]) -> str:
    """Prepare chat history for LLM input by formatting it into a string."""
    print(f"Preparing {len(history)} chat history entries for LLM...")
    if not history:
        return "No previous chat history available."
    formatted_history = "\n".join([f"Q: {entry['query']}\nA: {entry['answer']}" for entry in history[-10:]])  # Limit to last 10 entries
    print(f"Formatted chat history length: {len(formatted_history)} characters")
    return formatted_history

# The following functions are now handled by src/db/database.py
# - load_chat_history()
# - save_chat_history()
# - clear_chat_history()