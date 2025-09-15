#!/bin/bash
# HealthSmart ADK Project - Virtual Environment Activation Script

echo "🏥 HealthSmart ADK Project"
echo "=========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if ADK is installed
python3 -c "import google.adk" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Google ADK is installed"
else
    echo "❌ Google ADK not found. Installing..."
    pip install google-adk
fi

# Check Google Cloud authentication
echo "☁️ Checking Google Cloud authentication..."
gcloud auth list --filter=status:ACTIVE --format=value(account) > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Google Cloud authenticated"
    PROJECT=$(gcloud config get-value project 2>/dev/null)
    echo "   Project: $PROJECT"
else
    echo "❌ Google Cloud not authenticated. Run: gcloud auth application-default login"
fi

echo ""
echo "🎉 Environment ready! You can now run:"
echo "   python3 main.py"
echo ""
echo "💡 To deactivate the virtual environment later, run: deactivate"
