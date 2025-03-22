# src/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR")
    ##DOCS_FILE = os.getenv("DOCS_FILE")
    ##CHAT_HISTORY_FILE = os.getenv("CHAT_HISTORY_FILE")
    print(GOOGLE_API_KEY,VECTORSTORE_DIR)
    @classmethod
    def validate_api_key(cls):
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in .env file. Please set it in D:/AI Projects/tiaa_wma_chabot/.env")
        print(f"Validated GOOGLE_API_KEY: {cls.GOOGLE_API_KEY[:5]}... (partial for security)")