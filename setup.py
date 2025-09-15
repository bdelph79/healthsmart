#!/usr/bin/env python3
"""
Setup script for HealthSmart ADK Project
Installs dependencies and verifies configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def check_gcloud_auth():
    """Check if gcloud is authenticated."""
    print("🔐 Checking Google Cloud authentication...")
    try:
        result = subprocess.run("gcloud auth list --filter=status:ACTIVE --format=value(account)", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ Authenticated as: {result.stdout.strip()}")
            return True
        else:
            print("❌ No active Google Cloud authentication found")
            print("   Run: gcloud auth application-default login")
            return False
    except FileNotFoundError:
        print("❌ gcloud CLI not found. Please install Google Cloud SDK")
        return False

def check_project_config():
    """Check Google Cloud project configuration."""
    print("☁️ Checking Google Cloud project...")
    try:
        result = subprocess.run("gcloud config get-value project", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            project = result.stdout.strip()
            print(f"✅ Project: {project}")
            return True
        else:
            print("❌ No project configured")
            print("   Run: gcloud config set project YOUR_PROJECT_ID")
            return False
    except FileNotFoundError:
        print("❌ gcloud CLI not found")
        return False

def check_csv_files():
    """Check if CSV data files exist."""
    print("📊 Checking CSV data files...")
    csv_files = [
        "data/Marketplace _ Prodiges Health - Inital Use Cases.csv",
        "data/Marketplace _ Prodiges Health - Questions.csv", 
        "data/Marketplace _ Prodiges Health - RPM Specific.csv"
    ]
    
    missing_files = []
    for file_path in csv_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing CSV files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All CSV data files found")
    return True

def main():
    """Main setup function."""
    print("🏥 HealthSmart ADK Project Setup")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("CSV Files", check_csv_files),
        ("Dependencies", install_dependencies),
        ("Google Cloud Auth", check_gcloud_auth),
        ("Google Cloud Project", check_project_config),
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Ensure your Google Cloud project has ADK enabled")
        print("2. Run: python3 main.py")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
