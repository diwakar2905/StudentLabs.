#!/usr/bin/env python
"""
Run the StudentLabs FastAPI server
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 Starting StudentLabs API...")
    print("📍 Server running at http://0.0.0.0:8000")
    print("📚 API Docs at http://localhost:8000/docs")
    print("⏸  Press CTRL+C to quit\n")
    
    # Run uvicorn as a subprocess with proper module import
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])