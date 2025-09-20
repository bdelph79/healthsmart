# Multi-Agent Architecture Overview

## System Architecture Analysis

### **Multi-Agent Architecture Overview**

The smart health agent follows a **coordinator-specialist pattern** with the following key components:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HEALTHCARE ASSISTANT SYSTEM                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   Patient       │    │        HealthcareAssistant          │ │
│  │   Interface     │◄──►│         (Orchestrator)              │ │
│  └─────────────────┘    └─────────────────────────────────────┘ │
│                                      │                          │
│                                      ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              COORDINATOR AGENT                              │ │
│  │         (HealthcareCoordinator)                            │ │
│  │  • Initial assessment & routing                            │ │
│  │  • Conversational interface                                │ │
│  │  • Service eligibility evaluation                          │ │
│  │  • Patient context management                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                      │                          │
│                                      ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              SPECIALIST AGENTS                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│  │  │    RPM      │ │ Telehealth  │ │  Insurance  │          │ │
│  │  │ Specialist  │ │ Specialist  │ │ Specialist  │          │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                      │                          │
│                                      ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              RULES ENGINE & TOOLS                          │ │
│  │  • HealthcareRulesEngine                                   │ │
│  │  • Service eligibility scoring                             │ │
│  │  • CSV data integration (planned)                          │ │
│  │  • Tool functions:                                         │ │
│  │    - load_routing_rules()                                  │ │
│  │    - assess_patient_eligibility()                          │ │
│  │    - get_service_specific_info()                           │ │
│  │    - schedule_enrollment()                                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                      │                          │
│                                      ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              EXTERNAL SERVICES                             │ │
│  │  • Google Gemini 2.5 Flash (LLM)                          │ │
│  │  • Google ADK (Agent Development Kit)                     │ │
│  │  • InMemorySessionService                                  │ │
│  │  • CSV Data Sources                                        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### **Key Design Patterns & Components**

#### **1. Multi-Agent Architecture**
- **Coordinator Agent**: Central orchestrator that handles initial patient interactions
- **Specialist Agents**: Domain-specific agents for RPM, Telehealth, and Insurance
- **Agent Routing**: Dynamic routing based on patient needs and service eligibility

#### **2. Data Models**
```python
@dataclass
class PatientContext:
    user_id: str
    responses: Dict[str, Any]
    qualified_services: List[ServiceType]
    current_conversation_stage: str
    routing_confidence: float

@dataclass  
class RoutingRule:
    program: str
    inclusion_criteria: str
    exclusion_criteria: str
    marketplace_route: str
    fallback: str
```

#### **3. Rules Engine**
- **HealthcareRulesEngine**: Centralized business logic for service eligibility
- **Scoring System**: Weighted scoring for each service type (RPM, Telehealth, Insurance)
- **CSV Integration**: Planned integration with external data sources

#### **4. Service Types**
```python
class ServiceType(Enum):
    RPM = "Remote Patient Monitoring (RPM)"
    TELEHEALTH = "Telehealth / Virtual Primary Care" 
    INSURANCE = "Insurance Enrollment"
```

### **Architecture Strengths**

1. **Modular Design**: Clear separation of concerns between coordinator and specialists
2. **Extensible**: Easy to add new service types and specialist agents
3. **Tool-Based**: Each agent has access to shared tools for consistent functionality
4. **Session Management**: Built-in session handling for conversation continuity
5. **Async Support**: Full async/await pattern for scalability

### **Architecture Weaknesses**

1. **Limited Routing Logic**: Currently only uses coordinator agent, specialists aren't actively used
2. **Hardcoded Rules**: Eligibility scoring is hardcoded rather than data-driven
3. **No Agent Handoff**: No mechanism to transfer conversations to specialist agents
4. **CSV Integration Incomplete**: `load_rules_from_csv()` is empty
5. **Context Parsing**: Patient response parsing is placeholder implementation

### **Data Flow**

```
Patient Input → HealthcareAssistant → Coordinator Agent → Rules Engine → 
Service Eligibility → Tool Functions → Response Generation → Patient Output
```

### **Tool Functions**

1. **load_routing_rules()**: Returns current routing rules as context
2. **assess_patient_eligibility()**: Evaluates service eligibility with confidence scores
3. **get_service_specific_info()**: Provides detailed service information
4. **schedule_enrollment()**: Initiates enrollment process with reference numbers

### **Technology Stack**

- **Google ADK**: Agent Development Kit for multi-agent orchestration
- **Gemini 2.5 Flash**: Large Language Model for natural language processing
- **Python Async**: Asynchronous programming for concurrent operations
- **Dataclasses**: Type-safe data structures
- **Enum**: Type-safe service type definitions

### **Implementation Status**

The architecture is well-designed for a healthcare navigation system but needs implementation of the specialist agent routing and CSV data integration to reach its full potential.

### **Next Steps for Full Implementation**

1. **Implement Agent Handoff**: Add logic to transfer conversations to specialist agents based on service eligibility
2. **Complete CSV Integration**: Implement `load_rules_from_csv()` to load dynamic routing rules
3. **Enhanced Context Parsing**: Improve patient response parsing for better context understanding
4. **Specialist Agent Activation**: Add routing logic to activate specialist agents when needed
5. **Data Persistence**: Add database integration for patient context and conversation history
