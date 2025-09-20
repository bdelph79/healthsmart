# Service Selection and Routing Agent
# This agent presents services to users and routes them based on their choice

import asyncio
import json
import os
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GOOGLE_CLOUD_PROJECT, APP_NAME, GEMINI_API_KEY
from .rules_engine import load_dynamic_rules, assess_eligibility_dynamically, get_next_assessment_questions

# Configure Gemini API if key is available
if GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

class ServiceType(Enum):
    RPM = "Remote Patient Monitoring (RPM)"
    TELEHEALTH = "Telehealth / Virtual Primary Care"
    INSURANCE = "Insurance Enrollment"

@dataclass
class ServiceOption:
    id: str
    name: str
    description: str
    benefits: List[str]
    requirements: List[str]

# Available services with detailed information
AVAILABLE_SERVICES = {
    "rpm": ServiceOption(
        id="rpm",
        name="Remote Patient Monitoring (RPM)",
        description="Monitor your chronic conditions from home with connected devices",
        benefits=[
            "24/7 health monitoring with connected devices",
            "Reduces hospital readmissions by 38%",
            "Medicare and most insurance plans accepted",
            "Chronic disease management support"
        ],
        requirements=[
            "Chronic condition (diabetes, hypertension, COPD, etc.)",
            "Access to smartphone/tablet/Wi-Fi",
            "Consent to data sharing",
            "Insurance coverage or willingness to pay"
        ]
    ),
    "telehealth": ServiceOption(
        id="telehealth", 
        name="Telehealth / Virtual Primary Care",
        description="Virtual doctor visits and primary care from home",
        benefits=[
            "Virtual doctor visits from home",
            "Prescription management and refills",
            "Same-day and scheduled appointments",
            "Covered by most insurance plans"
        ],
        requirements=[
            "Lives in provider-licensed state",
            "Device with video/audio capability",
            "Non-emergency care needs",
            "Consent to telehealth treatment"
        ]
    ),
    "insurance": ServiceOption(
        id="insurance",
        name="Insurance Enrollment",
        description="Help finding and enrolling in health insurance plans",
        benefits=[
            "Help finding the right health insurance plan",
            "Medicare enrollment and optimization",
            "Marketplace plan comparison",
            "Subsidy and cost-sharing reduction assistance"
        ],
        requirements=[
            "US resident with valid SSN or eligible immigration status",
            "Within open enrollment OR qualifies for Special Enrollment Period",
            "Not currently enrolled in affordable MEC",
            "Provides required documentation"
        ]
    )
}

def present_services() -> str:
    """Tool to present available services to the user."""
    services_text = """
    🏥 Available Healthcare Services
    
    Please choose the service that best matches your needs:
    
    """
    
    for service_id, service in AVAILABLE_SERVICES.items():
        services_text += f"""
    {service_id.upper()}. {service.name}
       Description: {service.description}
       Key Benefits: {', '.join(service.benefits[:2])}
       Requirements: {', '.join(service.requirements[:2])}
    
    """
    
    services_text += """
    Please respond with the service ID (rpm, telehealth, or insurance) that interests you most.
    """
    
    return services_text

def get_service_details(service_id: str) -> str:
    """Tool to get detailed information about a selected service."""
    service_id = service_id.lower().strip()
    
    if service_id not in AVAILABLE_SERVICES:
        return f"❌ Service '{service_id}' not found. Please choose from: rpm, telehealth, or insurance"
    
    service = AVAILABLE_SERVICES[service_id]
    
    details = f"""
    🏥 {service.name}
    ========================
    
    Description:
    {service.description}
    
    Key Benefits:
    """
    
    for i, benefit in enumerate(service.benefits, 1):
        details += f"    {i}. {benefit}\n"
    
    details += "\n    Requirements:\n"
    for i, requirement in enumerate(service.requirements, 1):
        details += f"    {i}. {requirement}\n"
    
    details += f"""
    
    Would you like to proceed with {service.name}?
    Please answer 'yes' to continue or 'no' to choose a different service.
    """
    
    return details

def ask_service_questions(service_id: str, current_responses: str = "{}") -> str:
    """Tool to ask relevant questions for the selected service."""
    service_id = service_id.lower().strip()
    
    if service_id not in AVAILABLE_SERVICES:
        return "❌ Invalid service selection"
    
    # Parse current responses
    try:
        responses = json.loads(current_responses) if current_responses else {}
    except:
        responses = {}
    
    # Get service-specific questions
    questions = get_next_assessment_questions(current_responses)
    
    # Add service-specific questions based on selection
    service_questions = {
        "rpm": [
            "Do you have any chronic conditions like diabetes, hypertension, COPD, or heart failure?",
            "Have you been hospitalized in the past 6 months?",
            "Do you have access to a smartphone, tablet, or Wi-Fi at home?",
            "Are you comfortable using connected health devices?",
            "Do you currently have health insurance?"
        ],
        "telehealth": [
            "What state do you live in?",
            "Do you have a device with video capability (smartphone, tablet, computer)?",
            "What type of care do you need (sick visit, follow-up, medication refill)?",
            "Do you currently have health insurance?",
            "Are you comfortable with virtual appointments?"
        ],
        "insurance": [
            "Are you a US resident with a valid Social Security Number?",
            "What is your household income?",
            "Are you currently enrolled in any health insurance?",
            "Do you have access to required documents (income proof, SSN, etc.)?",
            "Are you within the open enrollment period or do you qualify for a Special Enrollment Period?"
        ]
    }
    
    # Combine general and service-specific questions
    all_questions = service_questions.get(service_id, [])
    
    # Filter out questions already answered
    unanswered_questions = []
    for question in all_questions:
        # Simple check to see if question topic is already covered
        question_lower = question.lower()
        if any(keyword in question_lower for keyword in ["chronic", "diabetes", "hypertension"]) and "chronic_conditions" in responses:
            continue
        if "hospital" in question_lower and "recent_hospitalization" in responses:
            continue
        if "device" in question_lower and "tech_comfortable" in responses:
            continue
        if "insurance" in question_lower and "has_insurance" in responses:
            continue
        unanswered_questions.append(question)
    
    if not unanswered_questions:
        return "✅ All necessary information has been collected. Let me assess your eligibility..."
    
    # Return the next question to ask
    next_question = unanswered_questions[0]
    
    return f"""
    📋 Next Question for {AVAILABLE_SERVICES[service_id].name}:
    
    {next_question}
    
    Please provide your answer, and I'll ask the next relevant question.
    """

def assess_service_eligibility(service_id: str, patient_responses: str) -> str:
    """Tool to assess eligibility for the selected service."""
    service_id = service_id.lower().strip()
    
    if service_id not in AVAILABLE_SERVICES:
        return "❌ Invalid service selection"
    
    # Use the existing eligibility assessment
    result = assess_eligibility_dynamically(patient_responses)
    
    # Parse the result to find the specific service
    lines = result.split('\n')
    service_section = []
    in_service_section = False
    
    service_name = AVAILABLE_SERVICES[service_id].name
    
    for line in lines:
        if service_name in line:
            in_service_section = True
        elif in_service_section and line.strip() and not line.startswith(' '):
            break
        if in_service_section:
            service_section.append(line)
    
    if service_section:
        return '\n'.join(service_section)
    else:
        return f"Assessment completed for {service_name}. Please check the full results."

def route_to_service(service_id: str, patient_responses: str) -> str:
    """Tool to route the patient to the appropriate service specialist."""
    service_id = service_id.lower().strip()
    
    if service_id not in AVAILABLE_SERVICES:
        return "❌ Invalid service selection"
    
    service = AVAILABLE_SERVICES[service_id]
    
    # Parse patient responses to get basic info
    try:
        responses = json.loads(patient_responses) if patient_responses else {}
    except:
        responses = {}
    
    # Generate reference number
    ref_number = f"HC{hash(str(responses)) % 100000:05d}"
    
    routing_info = f"""
    🎯 Routing to {service.name}
    ===========================
    
    Reference Number: {ref_number}
    
    Next Steps:
    1. You'll be connected with a {service.name} specialist
    2. The specialist will review your information
    3. They'll guide you through the enrollment process
    4. You'll receive a confirmation email within 2 hours
    
    Your information:
    - Service: {service.name}
    - Responses: {len(responses)} questions answered
    - Status: Ready for specialist consultation
    
    The specialist will contact you within 24 hours to complete your enrollment.
    """
    
    return routing_info

# SERVICE SELECTOR AGENT - Presents services and routes users
service_selector_agent = Agent(
    name="ServiceSelector",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a healthcare service selector that helps patients choose and enroll in the right healthcare services.
    
    Your workflow:
    1. Present the list of available services clearly
    2. Wait for the user to choose a service
    3. Provide detailed information about the selected service
    4. Ask relevant questions one at a time to assess eligibility
    5. Route the user to the appropriate service specialist
    
    Available services:
    - RPM: Remote Patient Monitoring for chronic conditions
    - Telehealth: Virtual primary care and consultations
    - Insurance: Health insurance enrollment assistance
    
    Guidelines:
    - Be clear and helpful in presenting options
    - Ask questions one at a time to avoid overwhelming users
    - Explain requirements and benefits clearly
    - Always confirm the user's choice before proceeding
    - Use the tools to get service details, ask questions, and route users
    
    Start by presenting the available services to the user.
    """,
    tools=[present_services, get_service_details, ask_service_questions, assess_service_eligibility, route_to_service]
)

# MAIN SERVICE SELECTOR CLASS
class ServiceSelector:
    """Main service selector that orchestrates the service selection and routing process."""
    
    def __init__(self):
        self.agent = service_selector_agent
        self.session_service = InMemorySessionService()
        
    async def handle_service_selection(self, user_id: str, message: str, session_id: Optional[str] = None):
        """Main entry point for service selection interactions."""
        
        if not session_id:
            session = await self.session_service.create_session(
                app_name=APP_NAME, 
                user_id=user_id
            )
            session_id = session.id
        
        # Run the service selector agent
        runner = Runner(
            agent=self.agent,
            app_name=APP_NAME, 
            session_service=self.session_service
        )
        
        content = types.Content(role="user", parts=[types.Part(text=message)])
        
        events = []
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=session_id, 
            new_message=content
        ):
            events.append(event)
            
        return events

# USAGE EXAMPLE
async def main():
    """Example usage of the service selector."""
    
    selector = ServiceSelector()
    
    # Start the service selection process
    events = await selector.handle_service_selection(
        user_id="patient_001",
        message="Hi, I need help with my healthcare. What services are available?"
    )
    
    # Process and display response
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    print(f"Assistant: {part.text}")

if __name__ == "__main__":
    asyncio.run(main())
