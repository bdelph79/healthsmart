# Coordinator-Specialist Agent Interaction Functional Specifications

## Overview

This document defines the detailed functional specifications for how the Coordinator Agent interacts with Specialist Agents and how the Rules Engine is utilized in the multi-agent healthcare system.

## 1. Agent Interaction Architecture

### 1.1 Agent Hierarchy and Responsibilities

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT INTERACTION FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │   Patient       │    │        COORDINATOR AGENT            │ │
│  │   Interface     │◄──►│    (HealthcareCoordinator)          │ │
│  └─────────────────┘    │  • Initial Assessment               │ │
│                         │  • Service Eligibility Evaluation   │ │
│                         │  • Agent Routing Decisions          │ │
│                         │  • Conversation Orchestration       │ │
│                         └─────────────────────────────────────┘ │
│                                      │                          │
│                                      ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              RULES ENGINE INTEGRATION                      │ │
│  │  • DynamicRulesEngine (CSV-based)                         │ │
│  │  • EligibilityResult Generation                           │ │
│  │  • Confidence Scoring                                     │ │
│  │  • Fallback Options                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                      │                          │
│                                      ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              SPECIALIST AGENT ROUTING                      │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│  │  │    RPM      │ │ Telehealth  │ │  Insurance  │          │ │
│  │  │ Specialist  │ │ Specialist  │ │ Specialist  │          │ │
│  │  │             │ │             │ │             │          │ │
│  │  │ • Device    │ │ • Virtual   │ │ • Plan      │          │ │
│  │  │   Setup     │ │   Care      │ │   Selection │          │ │
│  │  │ • Monitoring│ │ • Scheduling│ │ • Enrollment│          │ │
│  │  │ • Compliance│ │ • Prescrip. │ │ • Subsidies │          │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Coordinator Agent Responsibilities

### 2.1 Primary Functions

#### A. Initial Patient Assessment
```python
class CoordinatorAssessment:
    def conduct_initial_assessment(self, patient_message: str) -> AssessmentContext:
        """
        1. Parse patient input for key information
        2. Extract structured data (age, conditions, insurance, etc.)
        3. Generate follow-up questions based on missing data
        4. Create PatientContext object
        """
        
    def extract_patient_data(self, message: str) -> Dict[str, Any]:
        """
        Extract structured data from natural language:
        - Demographics (age, gender, location)
        - Health conditions (chronic diseases, recent hospitalizations)
        - Insurance status and coverage
        - Technology comfort level
        - Care preferences
        """
```

#### B. Service Eligibility Evaluation
```python
class ServiceEligibilityEvaluator:
    def evaluate_all_services(self, context: PatientContext) -> Dict[ServiceType, EligibilityResult]:
        """
        For each service type:
        1. Load relevant CSV rules
        2. Apply inclusion/exclusion criteria
        3. Calculate confidence scores
        4. Generate reasoning and fallback options
        """
        
    def determine_routing_decision(self, eligibility_results: Dict) -> RoutingDecision:
        """
        Based on eligibility results:
        1. Identify highest confidence qualified services
        2. Determine if specialist handoff is needed
        3. Select appropriate specialist agent
        4. Generate handoff context
        """
```

#### C. Agent Routing and Handoff
```python
class AgentRouter:
    def route_to_specialist(self, service_type: ServiceType, context: PatientContext) -> SpecialistHandoff:
        """
        1. Select appropriate specialist agent
        2. Prepare handoff context with:
           - Patient assessment summary
           - Service eligibility details
           - Specific questions/concerns
           - Conversation history
        3. Transfer conversation control
        """
        
    def handle_multi_service_eligibility(self, results: Dict) -> MultiServiceStrategy:
        """
        When patient qualifies for multiple services:
        1. Prioritize services by confidence score
        2. Create service introduction sequence
        3. Coordinate between specialists if needed
        """
```

## 3. Rules Engine Integration

### 3.1 Dynamic Rules Processing

#### A. CSV Rules Loading and Processing
```python
class RulesEngineIntegration:
    def load_service_rules(self, service: ServiceType) -> List[RoutingRule]:
        """
        Load rules from CSV files:
        - initial_use_cases.csv: Service eligibility criteria
        - questions.csv: Assessment question database
        - rpm_specific.csv: RPM-specific requirements
        """
        
    def process_inclusion_criteria(self, criteria: str, responses: Dict) -> float:
        """
        Parse and evaluate inclusion criteria:
        - Age requirements (≥65, <65)
        - Chronic conditions (diabetes, hypertension, etc.)
        - Recent hospitalization status
        - Insurance coverage verification
        - Technology access and consent
        """
        
    def process_exclusion_criteria(self, criteria: str, responses: Dict) -> float:
        """
        Parse and evaluate exclusion criteria:
        - Emergency/urgent care needs
        - Geographic restrictions
        - Coverage limitations
        - Consent refusals
        """
```

#### B. Confidence Scoring Algorithm
```python
class ConfidenceScoring:
    def calculate_service_confidence(self, service: ServiceType, context: PatientContext) -> float:
        """
        Weighted scoring system:
        - Inclusion criteria matches: +0.6 per match
        - Exclusion criteria violations: -0.4 per violation
        - Data completeness bonus: +0.1-0.2
        - Final score: 0.0-1.0 (threshold: 0.5 for qualification)
        """
        
    def generate_eligibility_reasoning(self, score: float, matches: List) -> str:
        """
        Generate human-readable explanation:
        - List qualifying criteria met
        - Explain confidence level
        - Suggest clarifying questions if needed
        """
```

### 3.2 Assessment Question Generation

#### A. Dynamic Question Selection
```python
class QuestionGenerator:
    def generate_next_questions(self, context: PatientContext) -> List[AssessmentQuestion]:
        """
        Based on current context and missing data:
        1. Identify critical missing information
        2. Select questions from CSV database
        3. Prioritize by service eligibility impact
        4. Limit to 2-3 questions to avoid overwhelming
        """
        
    def prioritize_questions(self, questions: List[AssessmentQuestion]) -> List[AssessmentQuestion]:
        """
        Priority order:
        1. Demographics (age, location)
        2. Health conditions and history
        3. Insurance and coverage
        4. Technology access and preferences
        5. Care goals and preferences
        """
```

## 4. Specialist Agent Interaction Patterns

### 4.1 Handoff Protocol

#### A. Coordinator to Specialist Handoff
```python
class SpecialistHandoff:
    def prepare_handoff_context(self, service: ServiceType, context: PatientContext) -> HandoffContext:
        """
        Handoff package includes:
        1. Patient assessment summary
        2. Service eligibility confirmation
        3. Specific patient concerns/questions
        4. Conversation history and context
        5. Recommended next steps
        """
        
    def execute_handoff(self, specialist: Agent, handoff_context: HandoffContext) -> None:
        """
        1. Transfer conversation control to specialist
        2. Provide specialist with context
        3. Update session state
        4. Monitor specialist performance
        """
```

#### B. Specialist Agent Capabilities

##### RPM Specialist Agent
```python
class RPMSpecialistCapabilities:
    def handle_device_setup(self, patient_info: Dict) -> DeviceSetupPlan:
        """
        - Assess device needs (BP monitor, glucometer, etc.)
        - Check insurance coverage for devices
        - Create setup timeline and instructions
        - Schedule device delivery/installation
        """
        
    def manage_monitoring_protocol(self, conditions: List[str]) -> MonitoringProtocol:
        """
        - Define monitoring frequency
        - Set up alert thresholds
        - Create compliance tracking
        - Schedule provider check-ins
        """
```

##### Telehealth Specialist Agent
```python
class TelehealthSpecialistCapabilities:
    def schedule_virtual_visit(self, patient_info: Dict) -> VisitSchedule:
        """
        - Check provider availability
        - Verify insurance coverage
        - Schedule appropriate appointment type
        - Send preparation instructions
        """
        
    def manage_prescription_requests(self, request: str) -> PrescriptionPlan:
        """
        - Process refill requests
        - Check medication interactions
        - Coordinate with pharmacy
        - Schedule follow-up if needed
        """
```

##### Insurance Specialist Agent
```python
class InsuranceSpecialistCapabilities:
    def assess_insurance_options(self, patient_info: Dict) -> InsuranceOptions:
        """
        - Check marketplace eligibility
        - Calculate subsidy amounts
        - Compare plan options
        - Identify cost-saving opportunities
        """
        
    def facilitate_enrollment(self, selected_plan: str) -> EnrollmentProcess:
        """
        - Guide through enrollment steps
        - Collect required documentation
        - Submit application
        - Track enrollment status
        """
```

### 4.2 Multi-Service Coordination

#### A. Parallel Service Management
```python
class MultiServiceCoordinator:
    def coordinate_services(self, qualified_services: List[ServiceType]) -> ServicePlan:
        """
        When patient qualifies for multiple services:
        1. Create service introduction sequence
        2. Coordinate between specialists
        3. Avoid conflicting recommendations
        4. Ensure seamless patient experience
        """
        
    def manage_service_priorities(self, services: List[ServiceType]) -> List[ServiceType]:
        """
        Priority order:
        1. Insurance (if uninsured) - foundational
        2. RPM (if chronic conditions) - clinical priority
        3. Telehealth - convenience and access
        """
```

## 5. Conversation Flow Specifications

### 5.1 Assessment Phase Flow

```
Patient Input → Coordinator Assessment → Rules Engine Evaluation → 
Service Eligibility → Specialist Routing → Service-Specific Interaction
```

#### Detailed Flow Steps:

1. **Initial Contact**
   - Patient sends message
   - Coordinator greets and explains process
   - Begins structured assessment

2. **Data Collection**
   - Ask demographic questions
   - Gather health history
   - Assess insurance status
   - Evaluate technology access

3. **Rules Processing**
   - Apply CSV-based rules
   - Calculate eligibility scores
   - Generate confidence levels
   - Identify fallback options

4. **Routing Decision**
   - Determine if specialist needed
   - Select appropriate specialist
   - Prepare handoff context
   - Transfer conversation control

5. **Service Delivery**
   - Specialist handles service-specific needs
   - Provides detailed information
   - Facilitates enrollment
   - Schedules follow-up

### 5.2 Error Handling and Fallbacks

#### A. Low Confidence Scenarios
```python
class LowConfidenceHandler:
    def handle_uncertain_eligibility(self, results: Dict) -> Response:
        """
        When confidence < 0.5:
        1. Ask clarifying questions
        2. Suggest fallback services
        3. Offer general health resources
        4. Schedule follow-up assessment
        """
```

#### B. No Service Eligibility
```python
class NoEligibilityHandler:
    def handle_no_qualification(self, context: PatientContext) -> Response:
        """
        When no services qualify:
        1. Explain why services don't apply
        2. Offer alternative resources
        3. Provide general health education
        4. Suggest re-assessment in future
        """
```

## 6. Implementation Requirements

### 6.1 Technical Implementation

#### A. Agent Communication Protocol
```python
class AgentCommunication:
    def send_handoff_message(self, from_agent: str, to_agent: str, context: Dict) -> None:
        """
        Structured handoff message format:
        {
            "handoff_type": "service_specialist",
            "source_agent": "coordinator",
            "target_agent": "rpm_specialist",
            "patient_context": {...},
            "eligibility_results": {...},
            "conversation_history": [...],
            "next_steps": [...]
        }
        """
```

#### B. Session State Management
```python
class SessionStateManager:
    def update_conversation_state(self, session_id: str, state: ConversationState) -> None:
        """
        Track conversation state:
        - Current agent handling conversation
        - Assessment progress
        - Service eligibility status
        - Handoff history
        """
```

### 6.2 Data Flow Requirements

#### A. Patient Data Processing
```python
class PatientDataProcessor:
    def parse_natural_language(self, message: str) -> StructuredData:
        """
        Extract structured data from patient messages:
        - Use NLP to identify key information
        - Map to standardized data fields
        - Validate data completeness
        - Flag missing critical information
        """
```

#### B. Rules Engine Integration
```python
class RulesEngineConnector:
    def evaluate_patient_eligibility(self, patient_data: Dict) -> EligibilityResults:
        """
        Connect to DynamicRulesEngine:
        1. Load relevant CSV rules
        2. Apply criteria matching
        3. Calculate confidence scores
        4. Generate reasoning and fallbacks
        """
```

## 7. Quality Assurance and Monitoring

### 7.1 Performance Metrics

#### A. Agent Performance Tracking
- Response accuracy and relevance
- Handoff success rate
- Patient satisfaction scores
- Service enrollment completion rate

#### B. Rules Engine Effectiveness
- Eligibility prediction accuracy
- False positive/negative rates
- Confidence score calibration
- Fallback option utilization

### 7.2 Continuous Improvement

#### A. Rules Engine Updates
- Regular CSV data updates
- Rule effectiveness analysis
- Confidence threshold optimization
- New service integration

#### B. Agent Training
- Conversation quality monitoring
- Specialist knowledge updates
- Handoff protocol improvements
- Patient feedback integration

## 8. Security and Compliance

### 8.1 HIPAA Compliance
- Secure data transmission between agents
- Patient data encryption
- Access logging and audit trails
- Consent management

### 8.2 Data Privacy
- Minimal data sharing between agents
- Patient data anonymization where possible
- Secure session management
- Data retention policies

This functional specification provides the detailed framework for implementing the coordinator-specialist agent interaction system with comprehensive rules engine integration.
