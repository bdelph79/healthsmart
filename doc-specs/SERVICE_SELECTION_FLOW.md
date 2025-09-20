# Service Selection and Routing Flow

This document describes the new service selection and routing flow implemented in the HealthSmart ADK project.

## 🎯 Overview

The new flow implements a user-guided service selection process where:

1. **Agent presents a list of supported services**
2. **User chooses from the list**
3. **LLM agent asks suitable questions based on the choice**
4. **Routes user to the right service specialist**

## 🏗️ Architecture

### Service Selector Agent
- **Primary Agent**: `ServiceSelector` - Orchestrates the entire flow
- **Tools**: 5 specialized tools for different aspects of the flow
- **Session Management**: Maintains conversation context

### Available Services
1. **RPM** - Remote Patient Monitoring for chronic conditions
2. **Telehealth** - Virtual primary care and consultations  
3. **Insurance** - Health insurance enrollment assistance

## 🔄 Complete User Flow

### Step 1: Service Presentation
```
User: "Hi, I need help with my healthcare. What services are available?"

Assistant: 
🏥 Available Healthcare Services

Please choose the service that best matches your needs:

RPM. Remote Patient Monitoring (RPM)
   Description: Monitor your chronic conditions from home with connected devices
   Key Benefits: 24/7 health monitoring with connected devices, Reduces hospital readmissions by 38%
   Requirements: Chronic condition (diabetes, hypertension, COPD, etc.), Access to smartphone/tablet/Wi-Fi

TELEHEALTH. Telehealth / Virtual Primary Care
   Description: Virtual doctor visits and primary care from home
   Key Benefits: Virtual doctor visits from home, Prescription management and refills
   Requirements: Lives in provider-licensed state, Device with video/audio capability

INSURANCE. Insurance Enrollment
   Description: Help finding and enrolling in health insurance plans
   Key Benefits: Help finding the right health insurance plan, Medicare enrollment and optimization
   Requirements: US resident with valid SSN or eligible immigration status, Within open enrollment OR qualifies for Special Enrollment Period

Please respond with the service ID (rpm, telehealth, or insurance) that interests you most.
```

### Step 2: Service Selection & Details
```
User: "I'm interested in RPM - I have diabetes and high blood pressure"

Assistant:
🏥 Remote Patient Monitoring (RPM)
========================

Description:
Monitor your chronic conditions from home with connected devices

Key Benefits:
1. 24/7 health monitoring with connected devices
2. Reduces hospital readmissions by 38%
3. Medicare and most insurance plans accepted
4. Chronic disease management support

Requirements:
1. Chronic condition (diabetes, hypertension, COPD, etc.)
2. Access to smartphone/tablet/Wi-Fi
3. Consent to data sharing
4. Insurance coverage or willingness to pay

Would you like to proceed with Remote Patient Monitoring (RPM)?
Please answer 'yes' to continue or 'no' to choose a different service.
```

### Step 3: Service-Specific Questions
```
User: "Yes, I want to proceed with RPM"

Assistant:
📋 Next Question for Remote Patient Monitoring (RPM):

Do you have any chronic conditions like diabetes, hypertension, COPD, or heart failure?

Please provide your answer, and I'll ask the next relevant question.
```

### Step 4: Continued Questioning
```
User: "I have diabetes and hypertension. I was hospitalized 3 months ago. I have insurance and I'm comfortable with technology."

Assistant:
📋 Next Question for Remote Patient Monitoring (RPM):

Do you have access to a smartphone, tablet, or Wi-Fi at home?

Please provide your answer, and I'll ask the next relevant question.
```

### Step 5: Eligibility Assessment
```
User: [Provides all required information]

Assistant:
[Performs eligibility assessment using rules engine]
[Shows qualification status and confidence scores]
```

### Step 6: Service Routing
```
User: [Completes all questions]

Assistant:
🎯 Routing to Remote Patient Monitoring (RPM)
===========================

Reference Number: HC36735

Next Steps:
1. You'll be connected with a Remote Patient Monitoring (RPM) specialist
2. The specialist will review your information
3. They'll guide you through the enrollment process
4. You'll receive a confirmation email within 2 hours

Your information:
- Service: Remote Patient Monitoring (RPM)
- Responses: 5 questions answered
- Status: Ready for specialist consultation

The specialist will contact you within 24 hours to complete your enrollment.
```

## 🛠️ Implementation Details

### Tools Available to the Agent

1. **`present_services()`** - Shows available services with descriptions
2. **`get_service_details(service_id)`** - Provides detailed service information
3. **`ask_service_questions(service_id, responses)`** - Asks service-specific questions
4. **`assess_service_eligibility(service_id, responses)`** - Evaluates eligibility
5. **`route_to_service(service_id, responses)`** - Routes to service specialist

### Service-Specific Questions

#### RPM Questions
- Do you have any chronic conditions like diabetes, hypertension, COPD, or heart failure?
- Have you been hospitalized in the past 6 months?
- Do you have access to a smartphone, tablet, or Wi-Fi at home?
- Are you comfortable using connected health devices?
- Do you currently have health insurance?

#### Telehealth Questions
- What state do you live in?
- Do you have a device with video capability (smartphone, tablet, computer)?
- What type of care do you need (sick visit, follow-up, medication refill)?
- Do you currently have health insurance?
- Are you comfortable with virtual appointments?

#### Insurance Questions
- Are you a US resident with a valid Social Security Number?
- What is your household income?
- Are you currently enrolled in any health insurance?
- Do you have access to required documents (income proof, SSN, etc.)?
- Are you within the open enrollment period or do you qualify for a Special Enrollment Period?

## 🧪 Testing

### Demo Script (No API Required)
```bash
python3 demo_service_flow.py
```
Shows the complete flow without requiring API calls.

### Full Test (With AI Agents)
```bash
python3 main.py
```
Runs the complete system with AI agents (requires API key).

### Interactive Testing
```bash
python3 test_service_flow.py
```
Tests different service selection scenarios.

## 📊 Benefits of New Flow

1. **User-Guided**: Users choose their preferred service
2. **Focused Questions**: Only relevant questions are asked
3. **Clear Information**: Detailed service descriptions and benefits
4. **Efficient Routing**: Direct routing to appropriate specialists
5. **Better UX**: More intuitive and less overwhelming
6. **Scalable**: Easy to add new services

## 🔧 Configuration

### Adding New Services
1. Add service to `AVAILABLE_SERVICES` in `service_selector_agent.py`
2. Define service-specific questions
3. Update routing logic if needed

### Modifying Questions
Edit the `service_questions` dictionary in `ask_service_questions()` function.

### Customizing Service Details
Update the `ServiceOption` dataclass and `AVAILABLE_SERVICES` dictionary.

## 🚀 Usage

### Basic Usage
```python
from app.service_selector_agent import ServiceSelector

selector = ServiceSelector()
events = await selector.handle_service_selection(
    user_id="patient_001",
    message="Hi, I need help with my healthcare. What services are available?"
)
```

### Integration with Existing System
The service selector can be integrated with the existing multi-agent system or used standalone.

## 📝 Next Steps

1. **Test with real users** to validate the flow
2. **Add more services** as needed
3. **Refine questions** based on user feedback
4. **Integrate with backend systems** for actual routing
5. **Add analytics** to track service selection patterns

The new service selection flow provides a much more user-friendly and efficient way to guide patients to the right healthcare services! 🎉
