#!/usr/bin/env python3
"""
Startup script for Maomo Backend
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import pymongo
        import motor
        import google.generativeai
        import streamlit
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment variables"""
    required_vars = [
        "GEMINI_API_KEY",
        "SECRET_KEY",
        "MONGODB_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.template")
        return False
    
    print("✅ Environment variables are set")
    return True

def start_backend():
    """Start the FastAPI backend"""
    if not check_requirements():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    print("🚀 Starting Maomo Backend...")
    print("📍 Backend will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload is enabled")
    print("\n" + "="*50)
    
    # Start uvicorn from the project root directory
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_backend()
