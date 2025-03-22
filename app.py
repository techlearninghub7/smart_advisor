# app.py
import os
import sys
from src.ui.interface import main

if __name__ == "__main__":
    print(f"Running app from {os.getcwd()}")
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    main()