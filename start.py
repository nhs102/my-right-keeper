#!/usr/bin/env python3
"""
Quick start script for My Rights Keeper application.
This script helps users quickly run the application with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if virtual environment is activated."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import streamlit
        import langchain_core
        import langchain_google_genai
        import langchain_chroma
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Dependencies installed successfully!")
        return True
    else:
        print(f"❌ Failed to install dependencies: {result.stderr}")
        return False

def check_env_file():
    """Check if .env file exists."""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("Please copy .env.example to .env and fill in your API keys:")
        print("  - LAW_API_ID: Get from http://www.law.go.kr/DRF/lawService.do")
        print("  - GOOGLE_API_KEY: Get from https://makersuite.google.com/app/apikey")
        return False
    return True

def run_tests():
    """Run project tests."""
    print("🧪 Running tests...")
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ Some tests failed: {result.stderr}")
        return False

def run_app():
    """Run the Streamlit application."""
    print("🚀 Starting My Rights Keeper...")
    print("📖 The application will open in your default browser.")
    print("🔗 If not, visit: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    # Change to app directory and run streamlit
    app_path = Path('app') / 'web_app.py'
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', str(app_path)])

def main():
    """Main function to orchestrate the startup process."""
    print("⚖️  My Rights Keeper - Korean Labor Law AI Assistant")
    print("=" * 50)
    
    # Check virtual environment
    if not check_environment():
        print("⚠️  Virtual environment not detected.")
        print("Please activate your virtual environment first:")
        print("  Windows: venv\\Scripts\\activate")
        print("  macOS/Linux: source venv/bin/activate")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("📦 Dependencies not found. Installing...")
        if not install_dependencies():
            sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    # Run tests (optional)
    test_choice = input("🧪 Run tests before starting? (y/n) [default: n]: ").strip().lower()
    if test_choice in ['y', 'yes']:
        if not run_tests():
            proceed = input("⚠️  Tests failed. Continue anyway? (y/n) [default: n]: ").strip().lower()
            if proceed not in ['y', 'yes']:
                sys.exit(1)
    
    # Start the application
    try:
        run_app()
    except KeyboardInterrupt:
        print("\n👋 Thank you for using My Rights Keeper!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()