# HealthSmart Agent Design Workflow
**Date:** October 4, 2025  
**File:** `app/smart_health_agent.py`  
**Architecture:** Multi-Agent ADK with JSON Rules Engine

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  HealthcareAssistant                        │
│                    (Main Orchestrator)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ├─ JSON Rules Engine (data/)
                            ├─ Session Service (In-Memory)
                            └─ Active Sessions Store
                            
┌───────────────────────────┴─────────────────────────────────┐
│                                                               │
│                   COORDINATOR AGENT                          │
│              (Single Intelligent Assistant)                  │
│                                                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
         TOOLS (13)              SPECIALIZED AGENTS (5)
```

---

## Conversation Flow

```
1. ENTRY POINT
   └─> handle_patient_inquiry(user_id, message, session_id?)
       │
       ├─ Check for existing session
       ├─ Create new session if needed
       └─ Route to Coordinator Agent

2. COORDINATOR WORKFLOW
   │
   ├─ STEP 0: SAFETY FIRST ⚠️
   │   └─> check_emergency_symptoms()
   │       ├─ HIGH RISK (>80%) → 🚨 Call 911 immediately
   │       ├─ URGENT (>50%) → ⚠️ Urgent care needed
   │       └─ SAFE → Continue assessment
   │
   ├─ STEP 1: FIRST INTERACTION
   │   └─> If "FIRST_INTERACTION:" flag
   │       └─> present_available_services()
   │           ├─ RPM (Remote Patient Monitoring)
   │           ├─ Telehealth (Virtual Care)
   │           ├─ Insurance Enrollment
   │           ├─ Pharmacy Savings
   │           └─ Wellness Programs
   │
   ├─ STEP 2: CONVERSATIONAL ASSESSMENT
   │   └─> get_next_assessment_questions_tool()
   │       ├─ Dynamic question generation from JSON
   │       ├─ ONE question at a time
   │       └─ Prioritized by missing critical data
   │
   ├─ STEP 3: ELIGIBILITY EVALUATION
   │   ├─> assess_service_specific_eligibility_tool()
   │   │   └─ Uses JSON rules engine
   │   │
   │   ├─> Service-Specific Analysis Tools:
   │   │   ├─ analyze_rpm_eligibility()
   │   │   ├─ analyze_insurance_eligibility()
   │   │   ├─ detect_sep_qualification()
   │   │   └─ get_pharmacy_savings_info()
   │   │
   │   └─> Returns:
   │       ├─ Qualified: true/false
   │       ├─ Confidence: 0.0-1.0
   │       ├─ Reasoning: explanation
   │       ├─ Missing criteria
   │       └─ Fallback options
   │
   ├─ STEP 4: SERVICE FOCUS ENGAGEMENT
   │   └─> engage_service_focus(service_type, context, eligibility)
   │       ├─ Generate reference number
   │       ├─ Present service benefits
   │       ├─ Maintain single-agent transparency
   │       └─ NO "routing" or "handoff" language
   │
   └─ STEP 5: ENROLLMENT
       └─> schedule_enrollment(service_type, patient_info)
           ├─ Generate reference number
           ├─ Provide enrollment timeline
           └─ Schedule follow-up steps
```

---

## Data Flow

```
USER INPUT
    ↓
[Session Management]
    ↓
[Coordinator Agent] ←──→ [JSON Rules Engine]
    ↓                         ↓
[Tool Selection]        [data/*.json files]
    ↓                    - emergency_screening.json
[Tool Execution]         - rpm_eligibility.json
    ↓                    - telehealth_eligibility.json
[Response Generation]    - insurance_enrollment.json
    ↓                    - pharmacy_savings.json
[Event Stream]           - wellness_programs.json
    ↓                    - assessment_questions.json
USER OUTPUT
```

---

## Tool Categories

### 1. Service Presentation (1 tool)
- `present_available_services()` - Initial greeting with service overview

### 2. Safety Tools (1 tool)
- `check_emergency_symptoms()` - Emergency triage and safety screening

### 3. Assessment Tools (3 tools)
- `get_next_assessment_questions_tool()` - Dynamic Q&A generation
- `assess_patient_eligibility()` - General eligibility assessment
- `assess_service_specific_eligibility_tool()` - Service-specific eligibility

### 4. Service Analysis Tools (4 tools)
- `analyze_rpm_eligibility()` - Deep RPM eligibility analysis
- `analyze_insurance_eligibility()` - Insurance enrollment analysis
- `detect_sep_qualification()` - Special enrollment period detection
- `get_pharmacy_savings_info()` - Pharmacy savings program information

### 5. Service Management Tools (4 tools)
- `load_routing_rules()` - Load JSON rules context
- `get_service_specific_info()` - Detailed service information
- `engage_service_focus()` - Focus assistant on specific service (NO routing)
- `schedule_enrollment()` - Initiate enrollment process

**Total: 13 Tools**

---

## Key Design Principles

### 1. Single-Agent Architecture
- ONE coordinator appears as all specialists
- Uses `engage_service_focus()` instead of routing
- No "handoff" or "transfer" language
- Maintains transparency about being same assistant
- User never knows multiple agents exist in background

### 2. JSON Rules-Based System
- All eligibility logic stored in JSON files (`data/`)
- Dynamic question generation from JSON database
- Sophisticated scoring with confidence levels
- Audit trail and reasoning for every decision
- Easy to update rules without code changes

### 3. Safety-First Protocol
- Emergency screening is ALWAYS first priority
- Stops enrollment if emergency detected
- Clear escalation paths:
  - **Critical (>80% confidence)** → 🚨 Call 911 immediately
  - **Urgent (>50% confidence)** → ⚠️ Urgent care within hours
  - **Routine** → ✅ Continue normal assessment

### 4. Session Continuity
- Maintains conversation context across messages
- Reuses sessions when session_id provided
- Tracks active sessions in memory
- Builds on previous information (never re-asks)
- Natural conversation flow without restarts

### 5. One Question at a Time
- Avoids overwhelming patients
- Intelligent question sequencing
- Prioritizes missing critical data
- Natural conversational rhythm
- Emergency questions take absolute priority

---

## Service Types (Enum)

```python
ServiceType.RPM          # Remote Patient Monitoring
ServiceType.TELEHEALTH   # Telehealth / Virtual Primary Care
ServiceType.INSURANCE    # Insurance Enrollment
ServiceType.PHARMACY     # Pharmacy Savings
ServiceType.WELLNESS     # Wellness Programs
```

---

## Specialized Agents (Background Support)

Though not directly exposed to users, these provide domain expertise to the coordinator:

### 1. RPM Specialist Agent
- Chronic disease monitoring expertise
- Device setup and technology requirements
- Medicare reimbursement guidance
- Clinical monitoring protocols
- 38% hospital readmission reduction focus

### 2. Telehealth Specialist Agent
- Virtual care options and capabilities
- State licensing requirements
- Technology platform guidance
- Prescription management
- Emergency procedures for virtual care

### 3. Insurance Specialist Agent
- Marketplace plan comparison
- Medicare enrollment guidance
- Special Enrollment Period (SEP) detection
- Subsidy eligibility assessment
- Required documentation guidance

### 4. Pharmacy Specialist Agent
- Prescription discount programs
- Generic vs brand medication savings
- Medicare Part D gap coverage
- Universal eligibility (no restrictions)
- Up to 80% medication savings

### 5. Wellness Specialist Agent
- Weight management programs
- Diabetes prevention (DPP)
- Smoking cessation support
- Stress management
- Preventive care coordination

**Critical Design Note:** The coordinator agent presents as having all this expertise itself, NOT as routing to these specialists. Users interact with one intelligent assistant throughout.

---

## HealthcareAssistant Class Methods

### Core Methods

#### `handle_patient_inquiry(user_id, message, session_id?)`
Main entry point for patient interactions
- **Input:** User ID, message text, optional session ID
- **Output:** Event stream, session ID
- **Function:** Routes to coordinator, manages sessions

#### `handle_conversation(user_id, messages)`
Process full conversation with multiple messages
- **Input:** User ID, list of messages
- **Output:** All events from conversation
- **Function:** Maintains session across multiple exchanges

#### `emergency_triage(user_id, symptoms)`
Immediate safety assessment
- **Input:** User ID, symptom description
- **Output:** Emergency level, action, message, reasoning
- **Levels:** critical, urgent, routine
- **Function:** JSON rules-based emergency screening

#### `get_service_eligibility_summary(patient_responses)`
Comprehensive eligibility across all services
- **Input:** Patient response dictionary
- **Output:** Eligibility summary for all services
- **Function:** Evaluates against all JSON rules simultaneously

---

## JSON Rules Engine Integration

### Rules Directory Structure
```
data/
├── emergency_screening.json      # Emergency symptom detection
├── rpm_eligibility.json          # RPM qualification rules
├── telehealth_eligibility.json   # Telehealth state licensing
├── insurance_enrollment.json     # Insurance & SEP rules
├── pharmacy_savings.json         # Pharmacy program rules
├── wellness_programs.json        # Wellness program rules
└── assessment_questions.json     # Dynamic question database
```

### Rule Evaluation Output
Every rule evaluation returns:
- `qualified`: Boolean eligibility status
- `confidence`: Float 0.0-1.0 confidence score
- `reasoning`: Human-readable explanation
- `missing_criteria`: List of unmet requirements
- `next_questions`: Suggested follow-up questions
- `fallback_options`: Alternative services if not qualified

---

## Communication Guidelines

### DO ✅
- Present services only on "FIRST_INTERACTION:" flag
- Continue conversations naturally without restarting
- Be empathetic and professional
- Explain medical terms in simple language
- Respect patient privacy and HIPAA guidelines
- Build on information already provided
- Acknowledge information and move forward
- Be positive about eligibility - focus on what they HAVE
- Stay confident and professional
- Use `engage_service_focus()` when patient qualifies
- Emphasize being the same assistant, just focusing on specific service

### DON'T ❌
- Never say "routing to specialist" or "connecting you with another agent"
- Never say "hand off" or "transfer" to specialists
- Never imply being multiple different people
- Never apologize excessively or seem uncertain
- Never ask questions already answered
- Never continue with enrollment if emergency detected
- Never present all services again after first interaction
- Never overwhelm with multiple questions at once

---

## Example User Journey

### Journey: 65-year-old with diabetes seeking RPM

```
1. USER: "Hi, I need help with my healthcare"
   AGENT: [Uses present_available_services()]
   → Shows 5 service categories

2. USER: "I have diabetes and want to monitor my blood sugar"
   AGENT: [Uses check_emergency_symptoms()]
   → No emergency detected
   AGENT: [Uses get_next_assessment_questions_tool()]
   → Asks about insurance coverage

3. USER: "Yes, I have Medicare"
   AGENT: [Uses analyze_rpm_eligibility()]
   → Extracts: age (Medicare-eligible), chronic condition (diabetes), insurance (yes)
   → Confidence: 0.85 (High)

4. AGENT: [Uses engage_service_focus("RPM", context)]
   → "Great news! You qualify for Remote Patient Monitoring!"
   → Provides reference number HC12345
   → Explains benefits and next steps
   → Emphasizes SAME assistant helping with RPM now

5. USER: "How does this work?"
   AGENT: [Uses get_service_specific_info("RPM")]
   → Explains devices, monitoring, Medicare coverage
   → Answers questions as RPM-focused assistant

6. USER: "I want to enroll"
   AGENT: [Uses schedule_enrollment("RPM", patient_info)]
   → Initiates enrollment
   → Provides timeline and next steps
   → Asks about other services
```

---

## Technical Implementation Details

### Dependencies
- **Google ADK**: Agent framework and runners
- **Gemini 2.0 Flash Exp**: LLM model for all agents
- **JSON Rules Engine**: Custom eligibility evaluation
- **In-Memory Sessions**: Session state management

### Session Management
- Sessions persist across messages
- Session ID tracks conversation continuity
- Active sessions stored in memory dictionary
- Session contains full conversation history

### Tool Execution Flow
1. User message received
2. Coordinator agent analyzes intent
3. Agent selects appropriate tool(s)
4. Tools execute with JSON rules engine
5. Results returned to agent
6. Agent generates natural language response
7. Response streamed back to user

### Error Handling
- Graceful fallbacks for missing JSON rules
- Error messages wrapped in tool responses
- Confidence scoring accounts for missing data
- Alternative service suggestions when primary fails

---

## Future Enhancement Opportunities

Based on `prd-enhancements-20251004.md`:

1. **Comprehensive Context Tracking**
   - Enhanced session state management
   - Multi-turn conversation memory
   - Previous service attempt tracking

2. **Database Integration**
   - PostgreSQL for persistent sessions
   - User profile storage
   - Enrollment tracking and follow-up

3. **Voice Interface**
   - Web Speech API integration
   - Real-time speech-to-text
   - Natural voice interactions

4. **Next.js Web Application**
   - Modern React-based UI
   - Real-time chat interface
   - Mobile-responsive design

---

## File References

### Primary Files
- `app/smart_health_agent.py` (1011 lines) - Main agent implementation
- `app/rules_engine_enhanced.py` (698 lines) - JSON rules evaluation engine
- `config.py` - Configuration and environment setup

### JSON Rules Files
- `data/emergency_screening.json` (206 lines)
- `data/rpm_eligibility.json` (183 lines)
- `data/telehealth_eligibility.json` (180 lines)
- `data/insurance_enrollment.json` (204 lines)
- `data/pharmacy_savings.json` (192 lines)
- `data/wellness_programs.json` (258 lines)
- `data/assessment_questions.json` (332 lines)

### Web Interface
- `simple_web_app.py` (902 lines) - Flask-based web interface

---

## Summary

The HealthSmart Agent is a sophisticated multi-agent system that **appears as a single intelligent assistant** to users. It leverages:

- **JSON-based rules** for flexible, auditable eligibility decisions
- **Safety-first protocol** with immediate emergency detection
- **Natural conversation flow** with dynamic question generation
- **Session continuity** for coherent multi-turn dialogues
- **Service focus engagement** without false "routing" to specialists
- **13 specialized tools** covering assessment, analysis, and enrollment
- **5 background specialist agents** providing domain expertise

The system prioritizes user experience through transparency, empathy, and intelligent guidance while maintaining clinical accuracy and safety protocols.



