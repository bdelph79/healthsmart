#!/usr/bin/env python3
"""
Start HealthSmart Assistant Web Interface
"""

import subprocess
import sys
import os
from pathlib import Path

def start_web_interface():
    """Start the web interface"""
    
    print("🌐 HealthSmart Assistant - Web Interface")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("web_app.py"):
        print("❌ Error: web_app.py not found. Please run from the project root directory.")
        return 1
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected. Consider activating it first.")
        print("   Run: source venv/bin/activate")
    
    print("🚀 Starting web server...")
    print("📍 Web Interface: http://localhost:8000")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/health")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the web server
        subprocess.run([
            sys.executable, "web_app.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting web server: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = start_web_interface()
    sys.exit(exit_code)

