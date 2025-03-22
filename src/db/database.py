# src/db/database.py
import sqlite3
import os
from typing import List, Dict
from src.config import Config
import json

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), '../../chatbot.db')

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    print(f"Initializing SQLite database at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create chat_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        ''')

        # Create processed_docs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_content TEXT NOT NULL,
                metadata TEXT NOT NULL  -- JSON string
            )
        ''')

        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp ON chat_history(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processed_docs_id ON processed_docs(id)')

        conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {str(e)}")
    finally:
        conn.close()

def save_chat_history(history: List[Dict]) -> None:
    """Save chat history to SQLite database."""
    print(f"Saving {len(history)} chat history entries to database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Clear existing entries
        cursor.execute('DELETE FROM chat_history')

        # Insert new entries
        for entry in history:
            cursor.execute('''
                INSERT INTO chat_history (query, answer, timestamp)
                VALUES (?, ?, ?)
            ''', (entry['query'], entry['answer'], entry['timestamp']))

        conn.commit()
        print("Chat history saved to database successfully.")
    except sqlite3.Error as e:
        print(f"Error saving chat history to database: {str(e)}")
    finally:
        conn.close()

def load_chat_history() -> List[Dict]:
    """Load chat history from SQLite database."""
    print(f"Loading chat history from database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT query, answer, timestamp FROM chat_history ORDER BY timestamp ASC')
        rows = cursor.fetchall()

        history = [{"query": row[0], "answer": row[1], "timestamp": row[2]} for row in rows]
        print(f"Loaded {len(history)} chat history entries from database.")
        return history
    except sqlite3.Error as e:
        print(f"Error loading chat history from database: {str(e)}")
        return []
    finally:
        conn.close()

def clear_chat_history() -> None:
    """Clear chat history from SQLite database."""
    print(f"Clearing chat history from database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM chat_history')
        conn.commit()
        print("Chat history cleared from database.")
    except sqlite3.Error as e:
        print(f"Error clearing chat history from database: {str(e)}")
    finally:
        conn.close()

def save_processed_docs(docs: List[Dict]) -> None:
    """Save processed documents to SQLite database."""
    print(f"Saving {len(docs)} processed documents to database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Clear existing entries
        cursor.execute('DELETE FROM processed_docs')

        # Insert new entries
        for doc in docs:
            cursor.execute('''
                INSERT INTO processed_docs (page_content, metadata)
                VALUES (?, ?)
            ''', (doc['page_content'], json.dumps(doc['metadata'])))

        conn.commit()
        print("Processed documents saved to database successfully.")
    except sqlite3.Error as e:
        print(f"Error saving processed documents to database: {str(e)}")
    finally:
        conn.close()

def load_processed_docs() -> List[Dict]:
    """Load processed documents from SQLite database."""
    print(f"Loading processed documents from database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT page_content, metadata FROM processed_docs')
        rows = cursor.fetchall()

        docs = [{"page_content": row[0], "metadata": json.loads(row[1])} for row in rows]
        print(f"Loaded {len(docs)} processed documents from database.")
        return docs
    except sqlite3.Error as e:
        print(f"Error loading processed documents from database: {str(e)}")
        return []
    finally:
        conn.close()
