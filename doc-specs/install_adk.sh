#!/bin/bash
# HealthSmart ADK Installation Script

echo "🏥 HealthSmart ADK Project - Installation Script"
echo "================================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install basic requirements
echo "📦 Installing basic requirements..."
pip3 install -r requirements.txt

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK is required but not installed."
    echo "   Please install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ Google Cloud SDK found"

# Authenticate with Google Cloud
echo "🔐 Setting up Google Cloud authentication..."
gcloud auth application-default login

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No Google Cloud project configured."
    echo "   Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Project configured: $PROJECT_ID"

# Install Google ADK (this might fail if not available in your region)
echo "🤖 Installing Google ADK..."
pip3 install google-adk || {
    echo "⚠️  Google ADK installation failed. This might be because:"
    echo "   1. ADK is not available in your region yet"
    echo "   2. You need special access permissions"
    echo "   3. The package name has changed"
    echo ""
    echo "   Please check the Google ADK documentation for the correct installation method."
    echo "   The project structure is ready - you just need to install ADK when available."
}

# Test the project
echo "🧪 Testing project setup..."
python3 test_init.py

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Ensure your Google Cloud project has ADK enabled"
echo "2. If ADK installation failed, install it manually when available"
echo "3. Run: python3 main.py"
