# HealthSmart ADK - Technical Requirements Summary

## 🎯 Project Overview
**Multi-agent conversational AI system** for healthcare service selection and patient routing using Google ADK + Gemini AI.

## 🏗️ Core Architecture

### System Components
- **Service Selector Agent** - Primary orchestrator with 5 specialized tools
- **Rules Engine** - CSV-based dynamic routing logic (3 CSV files)
- **Configuration System** - Environment management (GEMINI_API_KEY only)
- **Session Management** - InMemorySessionService for conversation context

### Agent Tools (Service Selector)
1. `present_services()` - Show available services
2. `get_service_details(service_id)` - Detailed service info
3. `ask_service_questions(service_id, responses)` - Service-specific questions
4. `assess_service_eligibility(service_id, responses)` - Eligibility evaluation
5. `route_to_service(service_id, responses)` - Route to specialist

## 🛠️ Technical Stack

### Core Technologies
- **Python 3.11+** - Primary language
- **Google ADK 1.14.0** - Agent framework
- **Gemini AI** - Conversational interface (gemini-2.0-flash-exp)
- **Pandas 2.3.2** - CSV data processing
- **Asyncio** - Async programming

### API Configuration
- **Primary API:** Gemini API (GEMINI_API_KEY)
- **Authentication:** API key-based (no OAuth)
- **Rate Limits:** 15 requests/minute (free tier)
- **No billing required** for basic functionality

## 📁 Project Structure
```
healthsmart/
├── app/
│   ├── service_selector_agent.py  # Main agent (5 tools)
│   ├── rules_engine.py            # CSV-based routing logic
│   └── smart_health_agent.py      # Multi-agent system
├── data/                          # 3 CSV files with rules
├── config.py                      # Environment management
├── main.py                        # Entry point
└── requirements.txt               # Dependencies
```

## 🔄 User Flow Implementation

### 1. Service Presentation
- Agent presents 3 services: RPM, Telehealth, Insurance
- Each service has description, benefits, requirements
- User selects preferred service

### 2. Dynamic Questioning
- Service-specific questions based on CSV rules
- Progressive assessment with context awareness
- Real-time eligibility evaluation

### 3. Service Routing
- Eligibility assessment with confidence scoring
- Fallback options for non-qualifying patients
- Route to appropriate specialist

## 📊 Data Requirements

### CSV Data Files (3 files)
- **Initial Use Cases** - 26 service rules and routing logic
- **Questions** - 24 assessment questions with criteria
- **RPM Specific** - 47 RPM service details and enrollment

### Service Data Structure
```python
@dataclass
class ServiceOption:
    id: str
    name: str
    description: str
    benefits: List[str]
    requirements: List[str]
```

## 🔧 Implementation Requirements

### Environment Setup
```bash
# Python 3.11+ virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
GEMINI_API_KEY=your-api-key-here
GOOGLE_CLOUD_PROJECT=healthangel-471700
```

### Code Standards
- **Type hints** for all functions
- **Docstrings** for documentation
- **Error handling** for API calls
- **Async/await** for all agent operations
- **CSV validation** for data integrity

## 🚀 Performance Requirements

### Response Times
- **Service presentation:** < 2 seconds
- **Question generation:** < 3 seconds
- **Eligibility assessment:** < 5 seconds
- **Service routing:** < 3 seconds

### Scalability
- **Memory usage:** < 100MB typical
- **Concurrent users:** Limited by API rate limits
- **Session management:** In-memory (upgradeable)

## 🔒 Security & Compliance

### Data Protection
- **HIPAA guidelines** for patient data
- **No persistent storage** of sensitive data
- **Session-based** conversation context
- **API key security** in environment variables

### Error Handling
- **Rate limit management** (429 errors)
- **API failure fallbacks**
- **Graceful degradation** for non-qualifying patients
- **Comprehensive logging** for debugging

## ✅ Success Criteria

### Functional
- ✅ Service selection flow working
- ✅ Dynamic question generation
- ✅ Eligibility assessment with confidence scores
- ✅ Service routing to specialists
- ✅ Multi-service support (RPM, Telehealth, Insurance)

### Technical
- ✅ GEMINI_API_KEY only configuration
- ✅ CSV-based rules engine
- ✅ Agent tool integration
- ✅ Session management
- ✅ Error handling and fallbacks
- ✅ Performance targets met

### Quality
- ✅ Code quality standards
- ✅ Test coverage > 80%
- ✅ Documentation complete
- ✅ Security compliance
- ✅ Performance benchmarks

## 📋 Deliverables

1. **Working application** with complete service selection flow
2. **Agent tools** implementing all 5 required functions
3. **Rules engine** processing CSV data dynamically
4. **Configuration system** with environment management
5. **Testing suite** with unit and integration tests
6. **Documentation** with setup and usage guides
7. **Error handling** for all edge cases
8. **Performance optimization** meeting response time targets

---

**Project Status:** Ready for Development  
**Timeline:** 2-3 weeks  
**Complexity:** Medium  
**Dependencies:** Google ADK, Gemini API, CSV data files


