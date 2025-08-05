#!/usr/bin/env python3
"""
Startup script for the Resume Processor API server.
This script handles environment setup and starts the FastAPI server.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Checking environment...")
    
    # Check if we're in a conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print(f"✅ Running in conda environment: {conda_env}")
    else:
        print("⚠️  Not running in a conda environment")
    
    # Check for .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Found .env file")
    else:
        print("⚠️  No .env file found - using default settings")
    
    # Check for database connection
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_db = os.getenv('POSTGRES_DB', 'resume_processor')
    print(f"📍 Database: {postgres_db} @ {postgres_host}")

def install_api_dependencies():
    """Install additional dependencies for the API server."""
    print("📦 Installing API server dependencies...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'api_requirements.txt'
        ])
        print("✅ API dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting Resume Processor API server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API documentation will be at: http://localhost:8000/docs")
    print("🔄 Auto-reload is enabled for development")
    print("\n" + "="*60)
    
    try:
        import uvicorn
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[".", "src/"]
        )
    except ImportError:
        print("❌ uvicorn not found. Installing dependencies...")
        if install_api_dependencies():
            import uvicorn
            uvicorn.run(
                "api_server:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                reload_dirs=[".", "src/"]
            )
        else:
            print("❌ Failed to start server")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔧 Resume Processor API Server Startup")
    print("=" * 40)
    
    check_environment()
    print()
    
    # Check if API dependencies are installed
    try:
        import fastapi
        import uvicorn
        print("✅ API dependencies already installed")
    except ImportError:
        if not install_api_dependencies():
            sys.exit(1)
    
    print()
    start_server()