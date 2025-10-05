# 🏥 HealthSmart Assistant - Apprentice Development Assignment

**Assignment Type:** Full-Stack Healthcare AI Application  
**Technology Stack:** Google ADK + Gemini AI + FastAPI + JSON Rules Engine  
**Difficulty Level:** Intermediate to Advanced  
**Estimated Time:** 2-3 weeks  
**Deadline:** [To be specified by hiring manager]

---

## 📋 Assignment Overview

You are tasked with building a **HealthSmart Assistant** - an AI-powered healthcare service navigation and patient routing system. This is a sophisticated multi-agent conversational AI application that helps patients find and enroll in appropriate healthcare services through intelligent assessment, emergency screening, and dynamic routing.

### 🎯 What You'll Build

A complete healthcare navigation platform that:
- **Screens** for emergency symptoms requiring immediate attention
- **Presents** available healthcare services to patients  
- **Conducts** dynamic, conversational assessments using JSON-based rules
- **Evaluates** eligibility using sophisticated business logic
- **Routes** patients to appropriate specialist agents
- **Facilitates** enrollment in qualified services

---

## 🏗️ Technical Requirements

### Core Technology Stack (MANDATORY)

**Primary Framework:** Google Agent Development Kit (ADK)  
**AI Model:** Google Gemini AI (gemini-2.0-flash-exp or gemini-2.5-flash)  
**Backend:** FastAPI (Python 3.11+)  
**Data Format:** JSON-based rules engine  
**Session Management:** InMemorySessionService (upgradeable to persistent storage)

### Required Dependencies

```python
# Core ADK and AI
google-adk
google-cloud-aiplatform  
google-genai
google-generativeai

# Web Framework
fastapi
uvicorn

# Data Processing
pandas
python-dotenv

# Async Support
asyncio
```

### Architecture Requirements

**Multi-Agent System Design:**
- **Coordinator Agent**: Main orchestrator with emergency screening
- **Specialist Agents**: Service-specific agents for detailed consultation
- **JSON Rules Engine**: Advanced eligibility assessment with confidence scoring
- **Emergency Screening**: Immediate triage for critical medical situations
- **Web Interface**: Modern chat-based user interface

---

## 🎯 Functional Requirements

### 1. Emergency Screening System (CRITICAL)

**Must Implement:**
- Automatic emergency symptom detection
- Critical condition triage (chest pain, stroke, breathing issues)
- Immediate 911 referral for life-threatening situations
- Urgent care routing for non-emergency but urgent conditions

**JSON Rules Structure:**
```json
{
  "critical_emergency_symptoms": {
    "cardiovascular": {
      "symptoms": ["chest pain", "severe chest pain", "heart attack symptoms"],
      "action": "call_911_immediately",
      "message": "Call 911 immediately. These may be signs of a heart attack."
    }
  }
}
```

### 2. Healthcare Service Presentation

**Available Services:**
- 🩺 **Remote Patient Monitoring (RPM)** - Chronic condition management
- 💻 **Telehealth / Virtual Primary Care** - Virtual doctor visits
- 🛡️ **Insurance Enrollment** - Health insurance assistance
- 💊 **Pharmacy Savings Programs** - Prescription discounts
- 🌟 **Wellness Programs** - Weight management, diabetes prevention
- 🚨 **Emergency Screening** - Immediate triage

### 3. Dynamic Assessment System

**Question Categories:**
- **Demographics**: Age, gender, state of residence
- **Health Status**: Chronic conditions, emergency symptoms, medications
- **Insurance Coverage**: Current insurance status and satisfaction
- **Technology Access**: Device availability, internet connectivity
- **Financial Situation**: Income, medication costs
- **Care Preferences**: Communication preferences, health goals

**Assessment Flow Logic:**
- Ask one question at a time to avoid overwhelming patients
- Prioritize questions based on service interest
- Skip questions already answered
- Follow up on positive responses with targeted questions

### 4. Eligibility Assessment Engine

**Service-Specific Requirements:**

**RPM (Remote Patient Monitoring):**
- Age 18+ required
- Chronic conditions (diabetes, hypertension, COPD, heart failure, etc.)
- Insurance coverage for medical devices
- Device access (smartphone, tablet, computer)
- Reliable internet connectivity
- Consent for data sharing

**Telehealth:**
- State of residence (licensing requirements)
- Device access and internet connectivity
- Technology comfort level
- Insurance status (optional)

**Insurance Enrollment:**
- Current insurance status
- State of residence
- Household income
- Special enrollment period eligibility

### 5. Multi-Agent Routing System

**Agent Architecture:**
- **Coordinator Agent**: Emergency screening, service presentation, initial assessment
- **RPM Specialist**: Detailed RPM consultation and enrollment
- **Telehealth Specialist**: Virtual care services and appointments
- **Insurance Specialist**: Insurance plan selection and enrollment
- **Pharmacy Specialist**: Prescription savings and medication assistance
- **Wellness Specialist**: Lifestyle programs and preventive care

**Routing Logic:**
- Confidence scoring for service recommendations
- Fallback options when primary service unavailable
- Seamless handoffs between agents with context preservation
- Service-specific tools for each specialist

---

## 📊 Data Structure Requirements

### JSON Rules Engine

You must implement a comprehensive JSON-based rules system with these files:

**1. Service Eligibility Rules:**
- `rpm_eligibility.json` - RPM requirements and criteria
- `telehealth_eligibility.json` - Virtual care eligibility
- `insurance_enrollment.json` - Insurance enrollment requirements
- `pharmacy_savings.json` - Prescription discount programs
- `wellness_programs.json` - Wellness program requirements

**2. Assessment System:**
- `assessment_questions.json` - Dynamic question generation
- `emergency_screening.json` - Critical symptom detection

**3. Enhanced Features:**
- Confidence scoring for all assessments
- Decision trails for complete audit
- Fallback options when services unavailable
- Dynamic question sequencing based on missing data

### Sample JSON Structure

```json
{
  "rule_id": "rpm_chronic_conditions_v2_1",
  "service": "Remote Patient Monitoring",
  "version": "2.1.0",
  "requirements": {
    "age": {
      "required": true,
      "min_value": 18,
      "question": "What is your age?",
      "validation": "Must be 18 or older for adult RPM programs"
    },
    "chronic_conditions": {
      "required": true,
      "type": "contains_any",
      "values": ["diabetes", "hypertension", "copd", "heart failure"],
      "question": "Do you have any chronic health conditions?",
      "clinical_rationale": "RPM most effective for ongoing chronic disease management"
    }
  },
  "exclusion_criteria": {
    "emergency_symptoms": {
      "type": "contains_any",
      "values": ["chest pain", "difficulty breathing", "stroke symptoms"],
      "action": "immediate_emergency_referral",
      "message": "Please seek immediate medical attention or call 911"
    }
  }
}
```

---

## 🖥️ User Interface Requirements

### Web Application Features

**Development Version (web_app.py):**
- Modern chat interface at `http://localhost:8000`
- Real-time conversation with AI agents
- Emergency screening integration
- Service selection and assessment flows
- Session management and conversation history
- API documentation at `/docs`

**Production Version (simple_web_app.py):**
- Cloud Run deployment ready
- HealthAngel-branded interface
- Same backend functionality
- Optimized for production deployment

### API Endpoints Required

**Core Endpoints:**
- `GET /` - Main chat interface
- `POST /api/chat` - Send message to AI assistant
- `GET /api/health` - Health check endpoint
- `GET /api/features` - Available features
- `GET /api/conversations/{session_id}` - Conversation history

**Admin Endpoints:**
- `GET /admin/monitoring` - System monitoring dashboard
- `GET /admin/metrics` - Performance metrics
- `POST /admin/update-rules` - Update JSON rules

---

## 🔧 Implementation Guidelines

### Project Structure

```
healthsmart/
├── app/
│   ├── __init__.py
│   ├── smart_health_agent.py      # Main multi-agent system
│   └── rules_engine_enhanced.py   # JSON rules engine
├── data/
│   ├── rules/                     # JSON rules files
│   │   ├── rpm_eligibility.json
│   │   ├── telehealth_eligibility.json
│   │   ├── insurance_enrollment.json
│   │   ├── pharmacy_savings.json
│   │   ├── wellness_programs.json
│   │   ├── assessment_questions.json
│   │   └── emergency_screening.json
│   └── [legacy CSV files]         # Backup data
├── web_app.py                     # Development web interface
├── simple_web_app.py             # Production web interface
├── main.py                       # Command-line demo
├── config.py                     # Configuration management
├── requirements.txt              # Python dependencies
└── README.md                     # Documentation
```

### Key Implementation Requirements

**1. Error Handling & Stability:**
- Comprehensive error logging with correlation IDs
- Circuit breaker pattern for API calls
- Retry logic with exponential backoff
- Graceful fallbacks for API failures

**2. Session Management:**
- Persistent conversation context
- User session tracking with unique IDs
- HIPAA-compliant data handling
- Rate limiting for API protection

**3. Assessment Flow:**
- One question at a time presentation
- Question deduplication logic
- Progress indicators for users
- Service-specific question prioritization

**4. Security & Compliance:**
- HIPAA guidelines compliance
- Data encryption for sensitive information
- No persistent storage of health data
- Secure API key management

---

## 🧪 Testing Requirements

### Test Coverage Required

**Unit Tests:**
- Configuration loading and validation
- API key authentication
- JSON rules engine functionality
- Service eligibility assessment
- Emergency screening logic

**Integration Tests:**
- Multi-agent communication
- Service routing logic
- Web interface functionality
- Session management

**End-to-End Tests:**
- Complete user journey from service selection to enrollment
- Emergency screening scenarios
- All service assessment flows
- Error handling and recovery

### Test Files to Create

```python
# Testing/test_gemini_api.py - API connectivity tests
# Testing/test_service_flow.py - Service routing tests  
# Testing/test_interactive_app.py - User interaction tests
# Testing/test_phase2_features.py - Advanced feature tests
```

---

## 📈 Performance Requirements

### Response Time Targets
- **Emergency Screening**: < 1 second for critical symptom detection
- **General Responses**: < 3 seconds per interaction
- **Assessment Completion**: < 30 seconds for full assessment
- **Service Routing**: < 2 seconds for eligibility evaluation

### Scalability Requirements
- Support 100+ concurrent users
- Memory usage < 100MB typical
- Session management for 1000+ active sessions
- API rate limiting and quota management

---

## 🚀 Deployment Requirements

### Development Environment
- Python 3.11+ runtime
- Virtual environment setup
- Google Cloud Project with ADK enabled
- Gemini API key configuration
- Local development server

### Production Deployment
- Docker containerization
- Google Cloud Run deployment
- Environment variable configuration
- Health monitoring and logging
- Auto-scaling capabilities

### Environment Configuration

```bash
# Required environment variables
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
```

---

## 📋 Deliverables Checklist

### Phase 1: Core System (Week 1)
- [ ] Google ADK project setup and configuration
- [ ] Basic multi-agent architecture implementation
- [ ] JSON rules engine with all required files
- [ ] Emergency screening system
- [ ] Basic web interface (FastAPI)

### Phase 2: Assessment System (Week 2)
- [ ] Dynamic question generation system
- [ ] Service-specific eligibility assessment
- [ ] Multi-agent routing and handoffs
- [ ] Session management and context retention
- [ ] Error handling and stability improvements

### Phase 3: User Experience (Week 3)
- [ ] Complete web interface with chat functionality
- [ ] Service presentation and selection flows
- [ ] Assessment progress tracking
- [ ] Production-ready deployment configuration
- [ ] Comprehensive testing suite

### Final Deliverables
- [ ] Complete source code repository
- [ ] Comprehensive README with setup instructions
- [ ] API documentation
- [ ] Test suite with 90%+ coverage
- [ ] Deployment guide for production
- [ ] Demo video showing all features

---

## 🎯 Success Criteria

### Technical Success Metrics
- **System Uptime**: 99%+ during testing
- **Response Time**: < 3 seconds average
- **Error Rate**: < 5% of interactions
- **Assessment Completion**: 90%+ completion rate

### Functional Success Metrics
- **Emergency Detection**: 100% accuracy for critical symptoms
- **Service Selection**: 100% accurate service identification
- **Eligibility Assessment**: 95%+ accuracy for service recommendations
- **User Experience**: Smooth, intuitive conversation flow

### Code Quality Metrics
- **Test Coverage**: 90%+ code coverage
- **Documentation**: Complete API and code documentation
- **Error Handling**: Comprehensive error handling throughout
- **Security**: HIPAA compliance and secure data handling

---

## 🚨 Critical Success Factors

### 1. Emergency Safety (NON-NEGOTIABLE)
- Emergency screening must work flawlessly
- Critical symptoms must trigger immediate 911 referral
- No false negatives for life-threatening conditions
- Clear, urgent messaging for emergency situations

### 2. Service Accuracy (HIGH PRIORITY)
- 100% accurate service identification
- Proper eligibility assessment for each service
- Correct routing to specialist agents
- Fallback options when services unavailable

### 3. User Experience (HIGH PRIORITY)
- Intuitive, conversational interface
- One question at a time to avoid overwhelming
- Clear progress indicators
- Responsive, fast interactions

### 4. Technical Excellence (MEDIUM PRIORITY)
- Clean, maintainable code
- Comprehensive error handling
- Proper logging and monitoring
- Scalable architecture

---

## 📚 Resources and Documentation

### Google ADK Documentation
- [Google ADK Official Docs](https://cloud.google.com/adk)
- [Agent Development Guide](https://cloud.google.com/adk/docs/agents)
- [Session Management](https://cloud.google.com/adk/docs/sessions)

### Gemini AI Documentation
- [Gemini API Documentation](https://ai.google.dev/gemini-api)
- [Model Configuration](https://ai.google.dev/gemini-api/docs/model-configuration)
- [Safety and Security](https://ai.google.dev/gemini-api/docs/safety-settings)

### FastAPI Documentation
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [WebSocket Support](https://fastapi.tiangolo.com/advanced/websockets/)
- [Deployment Guide](https://fastapi.tiangolo.com/deployment/)

### Healthcare Compliance
- [HIPAA Guidelines](https://www.hhs.gov/hipaa/for-professionals/index.html)
- [Healthcare Data Security](https://www.hhs.gov/hipaa/for-professionals/security/index.html)

---

## 🎯 Evaluation Criteria

### Technical Implementation (40%)
- Code quality and architecture
- ADK integration and agent implementation
- JSON rules engine functionality
- Error handling and stability

### Feature Completeness (30%)
- Emergency screening system
- Service assessment flows
- Multi-agent routing
- Web interface functionality

### User Experience (20%)
- Intuitive conversation flow
- Clear service presentation
- Responsive interface
- Error messaging and recovery

### Testing and Documentation (10%)
- Test coverage and quality
- Code documentation
- Setup and deployment guides
- API documentation

---

## 💡 Bonus Points

### Advanced Features (Optional)
- Voice interface integration
- Multi-language support
- Advanced analytics dashboard
- Mobile-responsive design
- Real-time monitoring and alerts

### Innovation (Optional)
- Creative UI/UX improvements
- Advanced AI features
- Performance optimizations
- Security enhancements
- Integration capabilities

---

## 🚀 Getting Started

### Step 1: Environment Setup
```bash
# Clone the repository (if provided)
git clone [repository-url]
cd healthsmart

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Google Cloud Setup
```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable adk.googleapis.com
```

### Step 3: API Key Configuration
```bash
# Get Gemini API key from https://makersuite.google.com/app/apikey
# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env
echo "GOOGLE_CLOUD_PROJECT=your_project_id" >> .env
```

### Step 4: Start Development
```bash
# Run development server
python web_app.py

# Open browser to http://localhost:8000
```

---

## 📞 Support and Questions

### Technical Questions
- Review the provided codebase and documentation
- Check Google ADK and Gemini AI documentation
- Test with the provided sample data and rules

### Assignment Clarifications
- Contact the hiring manager for requirements clarification
- Use the provided test cases as reference
- Follow the success criteria and evaluation metrics

### Emergency Support
- For critical technical issues, document the problem
- Provide detailed error logs and reproduction steps
- Focus on core functionality first, then enhancements

---

## 🎯 Final Notes

This assignment tests your ability to:
- Build complex AI applications with Google ADK
- Implement sophisticated business logic with JSON rules
- Create user-friendly healthcare interfaces
- Handle sensitive data with proper security
- Design scalable, maintainable architectures

**Remember:** This is a healthcare application dealing with sensitive patient data. Security, accuracy, and user safety are paramount. Focus on building a robust, reliable system that patients can trust with their health information.

**Good luck!** 🏥✨

---

*Assignment created by HealthSmart Development Team*  
*Last updated: January 2025*  
*Version: 1.0*
