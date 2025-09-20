# 🏥 HealthSmart Assistant

**AI-Powered Healthcare Service Navigation & Patient Routing System**

A multi-agent conversational AI system built with Google's Agent Development Kit (ADK) that helps patients find and enroll in appropriate healthcare services through intelligent assessment and dynamic routing.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-green.svg)](https://cloud.google.com/adk)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev/gemini-api)
[![FastAPI](https://img.shields.io/badge/FastAPI-Web%20API-red.svg)](https://fastapi.tiangolo.com/)

## 🎯 Overview

HealthSmart Assistant is an intelligent healthcare navigation system that:

- **Presents** available healthcare services to patients
- **Conducts** dynamic, conversational assessments
- **Evaluates** eligibility using CSV-based business rules
- **Routes** patients to appropriate specialist agents
- **Facilitates** enrollment in qualified services

### Available Services

- 🩺 **Remote Patient Monitoring (RPM)** - Chronic condition management with connected devices
- 💻 **Telehealth / Virtual Primary Care** - Virtual doctor visits and consultations
- 🛡️ **Insurance Enrollment** - Health insurance plan selection and enrollment assistance

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Coordinator    │────│  Rules Engine    │────│  CSV Data       │
│  Agent          │    │  (Dynamic)       │    │  (Business      │
│                 │    │                  │    │   Rules)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ├─── RPM Specialist Agent
         ├─── Telehealth Specialist Agent
         └─── Insurance Specialist Agent
```

### Key Components

- **Coordinator Agent**: Main orchestrator that conducts assessments and routes patients
- **Specialist Agents**: Service-specific agents for detailed consultation
- **Dynamic Rules Engine**: CSV-driven eligibility assessment and question generation
- **Web Interface**: FastAPI-based chat interface for user interaction

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd healthsmart
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp env.example .env
```

Edit `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

5. **Run the application**
```bash
python web_app.py
```

6. **Open in browser**
```
http://localhost:8000
```

## 🖥️ Usage

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Start chatting with the HealthSmart Assistant
3. Choose from available healthcare services
4. Answer assessment questions
5. Get routed to appropriate specialists

### API Endpoints

- **Web Interface**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`
- **Features**: `http://localhost:8000/api/features`

### Command Line Usage

```bash
# Activate virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run main healthcare assistant
python main.py

# Run smart health agent directly
python app/smart_health_agent.py

# Run service selector
python app/service_selector_agent.py

# Run demo applications
python optimized_demo.py
python demo_app.py
```

**Note:** Always activate the virtual environment before running any Python scripts to ensure all dependencies are available.

## 📊 Data Structure

The system uses three CSV files for business logic:

### 1. Initial Use Cases (`data/Marketplace _ Prodiges Health - Inital Use Cases.csv`)
- **Purpose**: Service eligibility rules and routing logic
- **Columns**: Program, Inclusion Criteria, Exclusion Criteria, Marketplace Route, Fallback
- **Rows**: 26 service rules

### 2. Questions Database (`data/Marketplace _ Prodiges Health - Questions.csv`)
- **Purpose**: Dynamic question generation for patient assessment
- **Columns**: Question, Data Type, Inclusion Criteria, Exclusion Criteria, Marketplace Route, Fallback
- **Rows**: 24 assessment questions

### 3. RPM Specific (`data/Marketplace _ Prodiges Health - RPM Specific.csv`)
- **Purpose**: RPM service details and enrollment information
- **Columns**: Greeting, FAQs, Who Qualifies, Enrollment Info
- **Rows**: 47 RPM-specific content items

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | No | Auto-detected |
| `GOOGLE_CLOUD_LOCATION` | Google Cloud region | No | us-central1 |
| `GOOGLE_GENAI_USE_VERTEXAI` | Use Vertex AI instead of Gemini API | No | True |

### Model Configuration

- **Primary Model**: `gemini-2.0-flash-exp`
- **Fallback Model**: `gemini-2.5-flash`
- **API Provider**: Google Gemini API (with Vertex AI fallback)

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest Testing/

# Run specific test files
python Testing/test_gemini_api.py
python Testing/test_service_flow.py
python Testing/test_interactive_app.py

# Run with coverage
python -m pytest Testing/ --cov=app
```

### Test Coverage

- ✅ Configuration loading
- ✅ API key validation
- ✅ Service presentation
- ✅ Dynamic question flow
- ✅ Eligibility assessment
- ✅ Service routing
- ✅ Agent integration

## 🏗️ Development

### Project Structure

```
healthsmart/
├── app/                          # Core application modules
│   ├── smart_health_agent.py    # Main multi-agent system
│   ├── service_selector_agent.py # Service selection agent
│   └── rules_engine.py          # Dynamic rules engine
├── data/                        # CSV data files
│   ├── Marketplace _ Prodiges Health - Inital Use Cases.csv
│   ├── Marketplace _ Prodiges Health - Questions.csv
│   └── Marketplace _ Prodiges Health - RPM Specific.csv
├── Testing/                     # Test suite
├── web_app.py                   # FastAPI web interface
├── main.py                      # Main entry point
├── config.py                    # Configuration management
└── requirements.txt             # Python dependencies
```

### Key Features

#### Dynamic Question Flow
- Asks questions based on missing critical data
- One question at a time to avoid overwhelming patients
- Service-specific question prioritization

#### CSV-Driven Rules Engine
- No hardcoded business logic
- AI interprets complex eligibility criteria
- Easy to update rules without code changes

#### Multi-Agent Architecture
- Coordinator agent for initial assessment
- Specialist agents for detailed consultation
- Seamless handoffs between agents

#### Session Management
- Conversation context preservation
- User session tracking
- HIPAA-compliant data handling

## 🔒 Security & Compliance

### Data Protection
- **HIPAA Guidelines**: Patient data handling compliance
- **Session Management**: Secure conversation context
- **API Security**: Key-based authentication
- **No Persistent Storage**: No sensitive data retention

### Environment Security
- **Environment Variables**: Sensitive data in .env file
- **Service Account**: Google Cloud authentication
- **API Rate Limiting**: Built-in quota management

## 🚀 Deployment

### Production Requirements
- Python 3.11+ runtime environment
- Google Cloud Project with ADK enabled
- Gemini API access with sufficient quota
- CSV data files in data/ directory
- Environment variables properly configured

### Docker Deployment

```bash
# Build Docker image
docker build -t healthsmart-assistant .

# Run container
docker run -p 8000:8000 --env-file .env healthsmart-assistant
```

### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy healthsmart-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📈 Performance

### Benchmarks
- **Response Time**: < 3 seconds per interaction
- **Memory Usage**: < 100MB typical
- **Concurrent Users**: Limited by API rate limits
- **Data Processing**: CSV data loaded at startup

### Scalability
- **Session Management**: InMemorySessionService (upgradeable to persistent storage)
- **Rate Limiting**: Built-in API quota management
- **Error Handling**: Comprehensive error handling and fallbacks
- **Monitoring**: Built-in logging and debugging

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards

- **Python 3.11+** syntax and features
- **Type hints** for all function parameters and returns
- **Docstrings** for all functions and classes
- **Error handling** for all external API calls
- **Logging** for debugging and monitoring

## 📞 Support

### Documentation
- **Google ADK Documentation**: https://cloud.google.com/adk
- **Gemini API Documentation**: https://ai.google.dev/gemini-api
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

### Troubleshooting

**Common Issues:**

1. **ModuleNotFoundError: No module named 'config'**
   ```bash
   # This is fixed in the code, but if you still see it:
   # Make sure you're running from the project root directory
   cd /Users/bdelph/Documents/Startup-projects/healthsmart
   
   # And activate the virtual environment
   source venv/bin/activate
   ```

2. **Authentication Error**
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Missing CSV Files**
   - Ensure all CSV files are in the `data/` directory
   - Check file names match exactly (including spaces)

4. **API Key Issues**
   - Verify GEMINI_API_KEY is set in .env file
   - Check API key is valid at https://makersuite.google.com/app/apikey

5. **Import Errors**
   ```bash
   # Make sure you're in the project root
   cd /Users/bdelph/Documents/Startup-projects/healthsmart
   
   # Install in development mode
   pip install -e .
   ```

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Review the [API Documentation](http://localhost:8000/docs)
- Run the test suite to verify setup

## 📄 License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google ADK** for the agent development framework
- **Gemini AI** for the conversational AI capabilities
- **FastAPI** for the web interface framework
- **Pandas** for CSV data processing

---

**HealthSmart Assistant** - Making healthcare navigation intelligent and accessible. 🏥✨
