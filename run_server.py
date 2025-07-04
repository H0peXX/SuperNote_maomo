#!/usr/bin/env python3
"""
Simple server startup script for Maomo
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start both backend and frontend"""
    print("🚀 Starting Maomo Collaborative Note-Taking Platform")
    print("=" * 60)
    
    # Set Python path to include the project root
    project_root = Path(__file__).parent.absolute()
    os.environ['PYTHONPATH'] = str(project_root)
    
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path: {os.environ.get('PYTHONPATH')}")
    
    try:
        print("\n📍 Starting Backend Server...")
        print("📖 API Documentation will be available at: http://localhost:8000/docs")
        
        # Start the backend using subprocess
        backend_dir = project_root / "backend"
        
        # Change to backend directory and start uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print(f"📂 Working directory: {backend_dir}")
        print("\n" + "=" * 60)
        print("🔥 Backend is starting...")
        print("⚠️  Press Ctrl+C to stop")
        print("=" * 60)
        
        # Start the server
        subprocess.run(cmd, cwd=backend_dir, env=os.environ)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
