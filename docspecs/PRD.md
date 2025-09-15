# Product Requirements Document (PRD)
## Basic Healthcare Assistant App Implementation Plan

### Executive Summary

This PRD outlines the step-by-step implementation plan to transform the current `smart_health_agent.py` into a fully functional basic healthcare assistant app that presents services (RPM, Telehealth, Insurance) and routes users based on their needs using the coordinator-specialist agent architecture.

### Current State Analysis

#### ✅ **Existing Features in `smart_health_agent.py`**
- Basic agent definitions (Coordinator + 3 Specialists)
- Hardcoded eligibility scoring logic
- Session management with InMemorySessionService
- Basic tool functions (load_routing_rules, assess_patient_eligibility, etc.)
- PatientContext and RoutingRule data structures
- Async conversation handling

#### ❌ **Critical Gaps Identified**

| Feature | Current State | Required State | Priority |
|---------|---------------|----------------|----------|
| **Service Presentation** | ❌ Missing | ✅ Present 3 services clearly | HIGH |
| **CSV Rules Integration** | ❌ Hardcoded | ✅ Dynamic CSV-based rules | HIGH |
| **Agent Handoff** | ❌ No handoff logic | ✅ Route to specialists | HIGH |
| **Question Flow** | ❌ Static questions | ✅ Dynamic assessment | MEDIUM |
| **Service Details** | ❌ Basic info only | ✅ Rich service information | MEDIUM |
| **Multi-Service Support** | ❌ Single service focus | ✅ Handle multiple services | LOW |

### Implementation Plan

## Phase 1: Core Integration (Week 1)

### Step 1.1: Integrate CSV Rules Engine
**Objective**: Replace hardcoded rules with dynamic CSV-based system

**Tasks**:
```python
# 1. Import rules engine
from app.rules_engine import DynamicRulesEngine, load_dynamic_rules, assess_eligibility_dynamically

# 2. Replace HealthcareRulesEngine with DynamicRulesEngine
class HealthcareAssistant:
    def __init__(self):
        self.rules_engine = DynamicRulesEngine(CSV_PATHS)  # Use CSV-based engine
        # ... rest of initialization
```

**Deliverables**:
- [ ] Update imports in `smart_health_agent.py`
- [ ] Replace hardcoded rules with CSV integration
- [ ] Test rules engine loading and processing

### Step 1.2: Add Service Presentation
**Objective**: Present available services to users clearly

**Tasks**:
```python
# Add service presentation tool
def present_available_services() -> str:
    """Present the 3 main services to users"""
    return """
    🏥 Welcome to HealthSmart Assistant!
    
    I can help you with these healthcare services:
    
    1. 🩺 Remote Patient Monitoring (RPM)
       - Monitor chronic conditions from home
       - Connected devices for health tracking
    
    2. 💻 Telehealth / Virtual Primary Care  
       - Virtual doctor visits from home
       - Prescription management and refills
    
    3. 🛡️ Insurance Enrollment
       - Help finding health insurance plans
       - Medicare and marketplace assistance
    
    How can I help you today? Please tell me about your health needs.
    """
```

**Deliverables**:
- [ ] Add service presentation tool
- [ ] Update coordinator agent with service presentation
- [ ] Test service presentation flow

### Step 1.3: Implement Basic Agent Handoff
**Objective**: Route users to appropriate specialist agents

**Tasks**:
```python
# Add handoff logic to HealthcareAssistant
async def route_to_specialist(self, service_type: ServiceType, context: PatientContext):
    """Route user to appropriate specialist agent"""
    specialist = self.specialists.get(service_type)
    if specialist:
        # Create handoff context
        handoff_context = {
            "patient_context": context,
            "service_type": service_type,
            "conversation_stage": "specialist_consultation"
        }
        # Transfer to specialist
        return await self.handle_specialist_consultation(specialist, handoff_context)
```

**Deliverables**:
- [ ] Add handoff logic to HealthcareAssistant class
- [ ] Create specialist consultation handler
- [ ] Test agent handoff flow

## Phase 2: Enhanced Assessment (Week 2)

### Step 2.1: Dynamic Question Flow
**Objective**: Implement intelligent question asking based on user responses

**Tasks**:
```python
# Enhance question generation
def get_next_assessment_questions(self, context: PatientContext) -> List[str]:
    """Generate next questions based on current context and missing data"""
    # Use CSV-based question generation
    questions = self.rules_engine.generate_assessment_questions()
    
    # Filter based on missing information
    missing_data = self.identify_missing_critical_data(context)
    relevant_questions = self.filter_questions_by_priority(questions, missing_data)
    
    return relevant_questions[:2]  # Limit to 2 questions
```

**Deliverables**:
- [ ] Implement dynamic question generation
- [ ] Add missing data identification logic
- [ ] Test question flow with different user scenarios

### Step 2.2: Service-Specific Assessment
**Objective**: Tailor questions based on user's service interest

**Tasks**:
```python
# Add service-specific assessment
def assess_service_specific_eligibility(self, service_type: ServiceType, context: PatientContext) -> EligibilityResult:
    """Assess eligibility for specific service using CSV rules"""
    return self.rules_engine.evaluate_patient_against_rules(
        context.responses, 
        service_type.value
    )
```

**Deliverables**:
- [ ] Add service-specific eligibility assessment
- [ ] Integrate with CSV rules engine
- [ ] Test eligibility scoring accuracy

## Phase 3: User Experience (Week 3)

### Step 3.1: Rich Service Information
**Objective**: Provide detailed service information to users

**Tasks**:
```python
# Enhance service information
def get_detailed_service_info(self, service_type: ServiceType) -> str:
    """Get comprehensive service information"""
    service_info = {
        ServiceType.RPM: {
            "description": "Monitor chronic conditions with connected devices",
            "benefits": ["24/7 monitoring", "Reduces readmissions by 38%", "Insurance covered"],
            "requirements": ["Chronic condition", "Device access", "Consent"],
            "devices": ["BP monitor", "Glucometer", "Pulse oximeter", "Smart scale"]
        },
        # ... other services
    }
    return self.format_service_info(service_info[service_type])
```

**Deliverables**:
- [ ] Create detailed service information database
- [ ] Add service information formatting
- [ ] Test service information presentation

### Step 3.2: Multi-Service Support
**Objective**: Handle users who qualify for multiple services

**Tasks**:
```python
# Add multi-service coordination
def handle_multi_service_eligibility(self, eligibility_results: Dict) -> MultiServicePlan:
    """Coordinate when user qualifies for multiple services"""
    qualified_services = [s for s, result in eligibility_results.items() if result.qualified]
    
    if len(qualified_services) > 1:
        return self.create_service_priority_plan(qualified_services)
    else:
        return self.route_to_single_service(qualified_services[0])
```

**Deliverables**:
- [ ] Implement multi-service coordination logic
- [ ] Create service priority system
- [ ] Test multi-service scenarios

## Phase 4: Integration & Testing (Week 4)

### Step 4.1: Complete Integration
**Objective**: Integrate all components into unified system

**Tasks**:
```python
# Update main HealthcareAssistant class
class HealthcareAssistant:
    def __init__(self):
        self.coordinator = coordinator_agent
        self.specialists = {...}
        self.rules_engine = DynamicRulesEngine(CSV_PATHS)  # CSV-based
        self.session_service = InMemorySessionService()
        
    async def handle_patient_inquiry(self, user_id: str, message: str, session_id: str = None):
        """Enhanced main entry point with full workflow"""
        # 1. Present services if first interaction
        # 2. Conduct assessment
        # 3. Evaluate eligibility
        # 4. Route to specialist if needed
        # 5. Handle service delivery
```

**Deliverables**:
- [ ] Complete HealthcareAssistant integration
- [ ] Update all agent instructions
- [ ] Test end-to-end workflow

### Step 4.2: Error Handling & Fallbacks
**Objective**: Handle edge cases and errors gracefully

**Tasks**:
```python
# Add comprehensive error handling
class ErrorHandler:
    def handle_low_confidence_eligibility(self, results: Dict) -> str:
        """Handle when confidence < 0.5"""
        
    def handle_no_service_eligibility(self, context: PatientContext) -> str:
        """Handle when no services qualify"""
        
    def handle_agent_handoff_failure(self, error: Exception) -> str:
        """Handle handoff failures"""
```

**Deliverables**:
- [ ] Implement error handling for all scenarios
- [ ] Add fallback responses
- [ ] Test error scenarios

## Phase 5: Basic App Completion (Week 5)

### Step 5.1: User Interface Integration
**Objective**: Create simple interface for testing

**Tasks**:
```python
# Add simple CLI interface
async def run_basic_app():
    """Simple CLI interface for testing"""
    assistant = HealthcareAssistant()
    
    print("🏥 HealthSmart Assistant - Basic App")
    print("=" * 40)
    
    user_id = input("Enter your user ID: ")
    
    while True:
        message = input("\nYou: ")
        if message.lower() in ['quit', 'exit', 'bye']:
            break
            
        events = await assistant.handle_patient_inquiry(user_id, message)
        
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(f"Assistant: {part.text}")
```

**Deliverables**:
- [ ] Create basic CLI interface
- [ ] Add user interaction loop
- [ ] Test complete user journey

### Step 5.2: Documentation & Testing
**Objective**: Document and test the basic app

**Tasks**:
- [ ] Create user guide
- [ ] Add comprehensive test cases
- [ ] Document API endpoints
- [ ] Create deployment guide

**Deliverables**:
- [ ] Complete documentation
- [ ] Test suite with 10+ scenarios
- [ ] Deployment instructions

## Success Criteria

### Functional Requirements
- [ ] User can see all 3 services clearly presented
- [ ] User can describe their health needs
- [ ] System asks relevant questions dynamically
- [ ] System evaluates eligibility using CSV rules
- [ ] System routes to appropriate specialist
- [ ] Specialist provides service-specific help
- [ ] System handles multiple service eligibility
- [ ] System provides fallbacks for no eligibility

### Technical Requirements
- [ ] CSV rules engine fully integrated
- [ ] Agent handoff working correctly
- [ ] Session management functional
- [ ] Error handling comprehensive
- [ ] Basic CLI interface working
- [ ] All tests passing

### User Experience Requirements
- [ ] Clear service presentation
- [ ] Natural conversation flow
- [ ] Helpful error messages
- [ ] Smooth agent transitions
- [ ] Complete service information

## Risk Mitigation

### Technical Risks
- **CSV Integration Complexity**: Start with simple CSV loading, iterate
- **Agent Handoff Issues**: Implement basic handoff first, enhance later
- **Session State Management**: Use simple in-memory storage initially

### User Experience Risks
- **Overwhelming Questions**: Limit to 2 questions at a time
- **Confusing Service Options**: Use clear, simple descriptions
- **Poor Error Handling**: Implement comprehensive fallbacks

## Timeline Summary

| Week | Phase | Key Deliverables |
|------|-------|------------------|
| 1 | Core Integration | CSV rules, service presentation, basic handoff |
| 2 | Enhanced Assessment | Dynamic questions, service-specific assessment |
| 3 | User Experience | Rich service info, multi-service support |
| 4 | Integration & Testing | Complete integration, error handling |
| 5 | Basic App Completion | CLI interface, documentation, testing |

## Next Steps

1. **Immediate**: Start with Step 1.1 (CSV Rules Integration)
2. **Week 1**: Complete Phase 1 (Core Integration)
3. **Week 2**: Complete Phase 2 (Enhanced Assessment)
4. **Week 3**: Complete Phase 3 (User Experience)
5. **Week 4**: Complete Phase 4 (Integration & Testing)
6. **Week 5**: Complete Phase 5 (Basic App Completion)

This plan provides a clear, step-by-step approach to transform the current `smart_health_agent.py` into a fully functional basic healthcare assistant app that meets all the requirements specified in the Coordinator-Specialist-Agent-Interaction-Specs.md.
