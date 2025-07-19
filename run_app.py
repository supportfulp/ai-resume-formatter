#!/usr/bin/env python3
"""
Simple script to run the Resume Processing Streamlit app.
This script handles common setup issues and provides helpful error messages.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'streamlit',
        'langchain',
        'google-generativeai',
        'pydantic',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_files():
    """Check if required files exist."""
    required_files = [
        'streamlit_app.py',
        'database.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files are present")
    return True

def setup_environment():
    """Set up environment variables for demo mode."""
    # Set demo mode environment variables
    os.environ['DEMO_MODE'] = 'true'
    
    # Create .env file if it doesn't exist
    if not Path('.env').exists():
        print("📝 Creating .env file for demo mode...")
        with open('.env', 'w') as f:
            f.write("# Demo Mode Configuration\n")
            f.write("DEMO_MODE=true\n")
            f.write("DEBUG=true\n")
            f.write("LOG_LEVEL=INFO\n")
        print("✅ Created .env file")

def main():
    """Main function to run the app."""
    print("🚀 Resume Processing App Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        return 1
    
    # Check files
    if not check_files():
        print("\n❌ Please ensure all required files are present and try again.")
        return 1
    
    # Setup environment
    setup_environment()
    
    print("\n🎯 Starting Streamlit app...")
    print("💡 The app will run in demo mode without database persistence")
    print("🔑 Use username: 'demo', password: 'demo123' to login")
    print("🌐 The app will open in your browser automatically")
    print("⏹️  Press Ctrl+C to stop the app")
    print("-" * 40)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.port', '8501',
            '--server.address', 'localhost'
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"\n❌ Error running app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 