# src/llm/chat_history_processor.py
from typing import List, Dict
import json
import os
from src.config import Config

def load_chat_history() -> List[Dict]:
    """Load chat history from file."""
    print(f"Loading chat history from {Config.CHAT_HISTORY_FILE}...")
    if os.path.exists(Config.CHAT_HISTORY_FILE):
        try:
            with open(Config.CHAT_HISTORY_FILE, "r") as f:
                history = json.load(f)
                print(f"Loaded {len(history)} chat history entries.")
                return history
        except json.JSONDecodeError as e:
            print(f"Error decoding chat history file: {str(e)}. Returning empty list.")
            return []
    print("No chat history file found. Returning empty list.")
    return []

def prepare_chat_history_for_llm(history: List[Dict]) -> str:
    """Prepare chat history for LLM input by formatting it into a string."""
    print(f"Preparing {len(history)} chat history entries for LLM...")
    if not history:
        return "No previous chat history available."
    formatted_history = "\n".join([f"Q: {entry['query']}\nA: {entry['answer']}" for entry in history[-10:]])  # Limit to last 10 entries
    print(f"Formatted chat history length: {len(formatted_history)} characters")
    return formatted_history

def save_chat_history(history: List[Dict]) -> None:
    """Save chat history to file."""
    print(f"Saving {len(history)} chat history entries...")
    try:
        with open(Config.CHAT_HISTORY_FILE, "w") as f:
            json.dump(history, f)
        print(f"Chat history saved to {Config.CHAT_HISTORY_FILE}")
    except Exception as e:
        print(f"Error saving chat history: {str(e)}")

def clear_chat_history() -> None:
    """Clear chat history and delete file."""
    print(f"Clearing chat history from {Config.CHAT_HISTORY_FILE}...")
    if os.path.exists(Config.CHAT_HISTORY_FILE):
        try:
            os.remove(Config.CHAT_HISTORY_FILE)
            print("Chat history file deleted.")
        except Exception as e:
            print(f"Error deleting chat history file: {str(e)}")
    else:
        print("No chat history file to clear.")