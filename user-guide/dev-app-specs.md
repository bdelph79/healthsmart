# HealthSmart ADK - Development Application Specifications

## 📋 Project Overview

**Project Name:** HealthSmart ADK - Healthcare Service Selection and Routing System  
**Technology Stack:** Google ADK (Application Development Kit) + Gemini AI + DB+ Fast api + NextJS

**Architecture:** Multi-Agent Conversational AI System  
**Purpose:** Intelligent healthcare service selection and patient routing  

## 🎯 Functional Requirements

### Core User Flow
1. **Service Presentation** - Agent presents available healthcare services
2. **Service Selection** - User chooses preferred service from list
3. **Dynamic Questioning** - Agent asks service-specific questions
4. **Eligibility Assessment** - System evaluates patient eligibility
5. **Service Routing** - Patient routed to appropriate specialist

### Available Services
- **RPM (Remote Patient Monitoring)** - Chronic condition management
- **Telehealth** - Virtual primary care and consultations
- **Insurance Enrollment** - Health insurance assistance

### Key Features
- ✅ Conversational AI interface
- ✅ Dynamic service selection
- ✅ Intelligent question flow
- ✅ CSV-based rules engine
- ✅ Real-time eligibility assessment
- ✅ Service specialist routing
- ✅ Session management
- ✅ HIPAA-compliant data handling

## 🏗️ Technical Architecture

## 🛠️ Technical Stack

### Core Technologies
- **Python 3.11+** - Primary programming language
- **Google ADK** - Application Development Kit for agent framework
- **Gemini AI** - Google's generative AI model
- **Pandas** - CSV data processing
- **Asyncio** - Asynchronous programming


### API Configuration
- **Primary API:** Gemini API (GEMINI_API_KEY)
- **Model:** gemini-2.0-flash-exp
Supabase 

## 🔧 Implementation Details

#### Service-Specific Questions
- **RPM Questions:** Chronic conditions, hospitalization, technology access
- **Telehealth Questions:** State residency, device capability, care type
- **Insurance Questions:** Legal status, income, enrollment period

### Agent Configuration

#### Service Selector Agent
```python
service_selector_agent = Agent(
    name="ServiceSelector",
    model="gemini-2.0-flash-exp",
    instruction="""You are a healthcare service selector...""",
    tools=[present_services, get_service_details, ask_service_questions, 
           assess_service_eligibility, route_to_service]
)
```

## 🚀 Development Setup

### Prerequisites
- Python 3.11+
- nextjs
- Gemini API Key
- Git repository access
- Google cloud run deployment 

### Installation Steps



# Edit .env file
GEMINI_API_KEY=your-gemini-api-key-here
GOOGLE_CLOUD_PROJECT=healthangel-471700
GOOGLE_CLOUD_LOCATION=us-central1
```

#### 3. API Key Setup
- Get API key from: https://makersuite.google.com/app/apikey
- Add to `.env` file
- No billing required (free tier available)



#### Test Coverage
- ✅ Configuration loading
- ✅ API key validation
- ✅ Service presentation
- ✅ Question flow
- ✅ Eligibility assessment
- ✅ Service routing
- ✅ Agent integration

## 📊 Data Schema

### CSV Data Structure

#### Initial Use Cases (`Marketplace _ Prodiges Health - Inital Use Cases.csv`)
- **Columns:** Program, Inclusion Criteria, Exclusion Criteria, Marketplace Route, Fallback
- **Rows:** 26 service rules
- **Purpose:** Service eligibility rules and routing logic

#### Questions (`Marketplace _ Prodiges Health - Questions.csv`)
- **Columns:** Question, Data Type, Inclusion Criteria, Exclusion Criteria, Marketplace Route, Fallback
- **Rows:** 24 assessment questions
- **Purpose:** Dynamic question generation

#### RPM Specific (`Marketplace _ Prodiges Health - RPM Specific.csv`)
- **Columns:** Greeting, FAQs, Who Qualifies, Enrollment Info
- **Rows:** 47 RPM-specific content
- **Purpose:** RPM service details and enrollment process


## 🔒 Security & Compliance

### Data Protection
- **HIPAA Guidelines** - Patient data handling compliance
- **Session Management** - Secure conversation context
- **API Security** - Key-based authentication
- **No Persistent Storage** - No sensitive data retention

### Environment Security
- **Environment Variables** - Sensitive data in .env file
- **Service Account** - Google Cloud authentication
- **API Rate Limiting** - Built-in quota management

## 🚀 Deployment Considerations

### Production Requirements
- **Python 3.11+** runtime environment
- **Google Cloud Project** with ADK enabled
- **Gemini API access** with sufficient quota
- **CSV data files** in data/ directory
- **Environment variables** properly configured

### Scalability
- **Session Management** - InMemorySessionService (can be upgraded to persistent storage)
- **Rate Limiting** - Built-in API quota management
- **Error Handling** - Comprehensive error handling and fallbacks
- **Monitoring** - Built-in logging and debugging

### Performance
- **Response Time** - < 3 seconds per interaction
- **Memory Usage** - < 100MB typical
- **Concurrent Users** - Limited by API rate limits
- **Data Processing** - CSV data loaded at startup

## 📝 Development Guidelines

### Code Standards
- **Python 3.11+** syntax and features
- **Type hints** for all function parameters and returns
- **Docstrings** for all functions and classes
- **Error handling** for all external API calls
- **Logging** for debugging and monitoring

### Testing Requirements
- **Unit tests** for all tools and functions
- **Integration tests** for agent workflows
- **End-to-end tests** for complete user flows
- **Performance tests** for API rate limits
- **Error handling tests** for edge cases

### Documentation
- **Code comments** explaining complex logic
- **API documentation** for all tools
- **User flow diagrams** for service selection
- **Deployment guides** for production setup

## 🎯 Success Criteria

### Functional Requirements
- ✅ Service presentation working
- ✅ User selection handling
- ✅ Dynamic question flow
- ✅ Eligibility assessment
- ✅ Service routing
- ✅ Multi-service support

### Technical Requirements
- ✅ GEMINI_API_KEY only configuration
- ✅ CSV-based rules engine
- ✅ Agent tool integration
- ✅ Session management
- ✅ Error handling
- ✅ Performance targets met

### Quality Requirements
- ✅ Code quality standards
- ✅ Test coverage > 80%
- ✅ Documentation complete
- ✅ Security compliance
- ✅ Performance benchmarks

## 📞 Support & Resources

### Documentation
- **Google ADK Documentation** - https://cloud.google.com/adk
- **Gemini API Documentation** - https://ai.google.dev/gemini-api
- **Project README** - Comprehensive setup guide
- **Code comments** - Inline documentation

### Development Tools
- **Python 3.11+** - Primary development environment
- **VS Code** - Recommended IDE with Python extensions
- **Git** - Version control
- **Virtual Environment** - Dependency isolation

### Testing Tools
- **pytest** - Unit testing framework
- **asyncio** - Asynchronous testing
- **Mock objects** - API testing without external calls
- **Test data** - Sample patient responses

---
