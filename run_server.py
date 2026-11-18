"""
System Server Launcher Script for Urban Road Encroachment Detection System.
Automatically sets PYTHONPATH and launches Uvicorn server on http://127.0.0.1:8000.
"""

import os
import sys
import uvicorn

# Ensure project root directory is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.chdir(PROJECT_ROOT)

if __name__ == "__main__":
    print("=" * 70)
    print("URBAN ROAD ENCROACHMENT DETECTION SYSTEM -- SERVER LAUNCHER")
    print("=" * 70)
    print(f"Project Root: {PROJECT_ROOT}")
    print("Dashboard URL: http://127.0.0.1:8000/frontend/index.html")
    print("=" * 70)
    
    uvicorn.run("src.backend.app:app", host="127.0.0.1", port=8000, reload=True)
