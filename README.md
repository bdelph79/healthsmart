# HealthSmart ADK Project

A multi-agent healthcare assistant system built with Google's Application Development Kit (ADK) that intelligently routes patients to appropriate healthcare services based on their needs and eligibility.

## 🏥 Overview

HealthSmart uses AI agents to:
- Conduct conversational health assessments
- Evaluate patient eligibility for services using dynamic CSV-based rules
- Route patients to Remote Patient Monitoring (RPM), Telehealth, or Insurance Enrollment services
- Provide personalized healthcare navigation and enrollment support

## 🏗️ Architecture

### Multi-Agent System
- **Coordinator Agent**: Conducts initial assessment and routes patients
- **RPM Specialist**: Handles Remote Patient Monitoring enrollment and support
- **Telehealth Specialist**: Manages virtual care services and appointments
- **Insurance Specialist**: Assists with insurance enrollment and coverage optimization

### Dynamic Rules Engine
- Loads routing rules from CSV files
- Uses LLM to interpret eligibility criteria
- Provides confidence scores for service recommendations
- Suggests follow-up questions for better assessment

## 📁 Project Structure

```
healthsmart/
├── app/
│   ├── __init__.py
│   ├── smart_health_agent.py    # Main multi-agent system
│   └── rules_engine.py          # Dynamic CSV rules engine
├── data/
│   ├── Marketplace _ Prodiges Health - Inital Use Cases.csv
│   ├── Marketplace _ Prodiges Health - Questions.csv
│   └── Marketplace _ Prodiges Health - RPM Specific.csv
├── config.py                    # Configuration settings
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- **Gemini API Key** (get from https://makersuite.google.com/app/apikey)
- Google Cloud Project (auto-detected, no billing required)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd healthsmart
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your Gemini API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key

4. **Configure your environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

## 🔧 Configuration

The `config.py` file contains all configuration settings:

- **Gemini API Key**: Set in `.env` file (required)
- **Google Cloud Project**: Auto-detected (optional)
- **Location**: Defaults to `us-central1`
- **Model**: Uses `gemini-2.0-flash-exp` by default
- **CSV Paths**: Points to your healthcare rules data

## 📊 Data Sources

The system uses three CSV files for intelligent routing:

1. **Initial Use Cases**: Service eligibility criteria and routing rules
2. **Questions**: Assessment questions with inclusion/exclusion criteria
3. **RPM Specific**: Remote Patient Monitoring enrollment details

## 🤖 Usage Examples

### Basic Patient Assessment
```python
from app.smart_health_agent import HealthcareAssistant

assistant = HealthcareAssistant()

# Patient inquiry
events = await assistant.handle_patient_inquiry(
    user_id="patient_001",
    message="I have diabetes and was recently hospitalized. What services can help me?"
)
```

### Dynamic Rules Evaluation
```python
from app.rules_engine import assess_eligibility_dynamically
import json

patient_data = {
    "age": 67,
    "chronic_conditions": "diabetes, hypertension",
    "recent_hospitalization": True,
    "has_insurance": True
}

result = assess_eligibility_dynamically(json.dumps(patient_data))
print(result)
```

## 🛠️ Development

### Adding New Services
1. Add service type to `ServiceType` enum in `smart_health_agent.py`
2. Create specialist agent for the service
3. Add routing rules to CSV files
4. Update rules engine to handle new service

### Modifying Rules
- Edit the CSV files in the `data/` directory
- Rules are automatically loaded at runtime
- No code changes needed for rule updates

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   gcloud auth application-default login
   ```

2. **CSV File Not Found**
   - Ensure CSV files are in the `data/` directory
   - Check file names match exactly (including spaces)

3. **ADK Import Error**
   - Verify Google ADK is installed: `pip install google-adk`
   - Check your Google Cloud project has ADK enabled

4. **Model Access Issues**
   - Ensure your project has access to Gemini models
   - Check Vertex AI API is enabled

## 📈 Features

- ✅ Multi-agent conversation system
- ✅ Dynamic CSV-based routing rules
- ✅ Patient eligibility assessment
- ✅ Service-specific specialist agents
- ✅ Confidence scoring for recommendations
- ✅ HIPAA-compliant data handling
- ✅ Extensible architecture for new services

## 🔒 Security & Compliance

- All patient data is handled according to HIPAA guidelines
- Secure session management with Google ADK
- No persistent storage of sensitive health information
- Encrypted communication with Google Cloud services

## 📝 License

Copyright 2025 Google LLC - Licensed under Apache License, Version 2.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review Google ADK documentation
- Open an issue in the repository
