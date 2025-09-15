# Google Cloud Configuration for HealthSmart ADK Project
import os
from google.auth import default
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get default credentials and project
credentials, project_id = default()

# Configuration settings
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", project_id)
GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_GENAI_USE_VERTEXAI = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True")

# Gemini API Key support
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    # If Gemini API key is provided, use it instead of Vertex AI
    GOOGLE_GENAI_USE_VERTEXAI = "False"
    # Set the API key for google-generativeai
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    # Also set for google-genai compatibility
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# CSV Data paths
CSV_PATHS = {
    'initial_use_cases': 'data/Marketplace _ Prodiges Health - Inital Use Cases.csv',
    'questions': 'data/Marketplace _ Prodiges Health - Questions.csv', 
    'rpm_specific': 'data/Marketplace _ Prodiges Health - RPM Specific.csv'
}

# Agent configuration
DEFAULT_MODEL = "gemini-2.0-flash-exp"
APP_NAME = "healthcare_assistant"

# Service types
SERVICE_TYPES = {
    "RPM": "Remote Patient Monitoring (RPM)",
    "TELEHEALTH": "Telehealth / Virtual Primary Care", 
    "INSURANCE": "Insurance Enrollment"
}

print(f"🔧 HealthSmart ADK Configuration Loaded:")
print(f"   Project: {GOOGLE_CLOUD_PROJECT}")
print(f"   Location: {GOOGLE_CLOUD_LOCATION}")
print(f"   Using Vertex AI: {GOOGLE_GENAI_USE_VERTEXAI}")
