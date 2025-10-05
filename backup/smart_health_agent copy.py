# Healthcare Assistant Agent - Multi-Agent ADK Architecture
# Copyright 2025 Google LLC - Licensed under Apache License, Version 2.0

import asyncio
import csv
import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path

import google.auth
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import configuration
from config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, GOOGLE_GENAI_USE_VERTEXAI, CSV_PATHS, GEMINI_API_KEY

# Import enhanced rules engine
from app.rules_engine_enhanced import JSONRulesEngine, load_dynamic_rules, assess_eligibility_dynamically, get_next_assessment_questions, assess_service_specific_eligibility

# Set up environment
# os.environ.setdefault("GOOGLE_CLOUD_PROJECT", GOOGLE_CLOUD_PROJECT)
# os.environ.setdefault("GOOGLE_CLOUD_LOCATION", GOOGLE_CLOUD_LOCATION)
# os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", GOOGLE_GENAI_USE_VERTEXAI)

# Configure Gemini API if key is available
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

class ServiceType(Enum):
    RPM = "Remote Patient Monitoring (RPM)"
    TELEHEALTH = "Telehealth / Virtual Primary Care"
    INSURANCE = "Insurance Enrollment"

@dataclass
class RoutingRule:
    program: str
    inclusion_criteria: str
    exclusion_criteria: str
    marketplace_route: str
    fallback: str

@dataclass
class PatientContext:
    user_id: str
    responses: Dict[str, Any]
    qualified_services: List[ServiceType]
    current_conversation_stage: str
    routing_confidence: float

# Service presentation tool
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

# AGENT DEFINITIONS

def load_routing_rules() -> str:
    """Tool to load and return current routing rules as context."""
    return load_dynamic_rules()

def assess_patient_eligibility(patient_responses: str) -> str:
    """Tool to assess patient eligibility for services based on their responses."""
    return assess_eligibility_dynamically(patient_responses)

def get_service_specific_info(service_type: str) -> str:
    """Tool to get detailed information about a specific service."""
    service_info = {
        "RPM": """
        Remote Patient Monitoring (RPM) Service:
        - 24/7 health monitoring with connected devices
        - Chronic disease management support
        - Medicare and most insurance plans accepted
        - Devices include: BP monitors, glucometers, pulse oximeters, smart scales
        - Reduces hospital readmissions by 38%
        """,
        
        "Telehealth": """
        Telehealth / Virtual Primary Care:
        - Virtual doctor visits from home
        - Prescription management and refills
        - Preventive care and wellness checks
        - Same-day and scheduled appointments
        - Covered by most insurance plans
        """,
        
        "Insurance": """
        Insurance Enrollment Assistance:
        - Help finding the right health insurance plan
        - Medicare enrollment and optimization
        - Marketplace plan comparison
        - Subsidy and cost-sharing reduction assistance
        - Year-round enrollment support for eligible life events
        """
    }
    
    return service_info.get(service_type.upper(), "Service information not found.")

def schedule_enrollment(service_type: str, patient_info: str) -> str:
    """Tool to initiate enrollment process for a qualified service."""
    return f"""
    Enrollment initiated for {service_type}!
    
    Next steps:
    1. You'll receive a confirmation email within 2 hours
    2. Our enrollment specialist will call you within 24 hours
    3. Required documents will be sent via secure message
    4. Setup appointment scheduled within 3-5 business days
    
    Reference number: HC{hash(patient_info) % 100000:05d}
    
    Is there anything else I can help you with today?
    """

def analyze_conversation_for_rpm_eligibility(conversation_text: str) -> str:
    """Use LLM to analyze conversation and assess RPM eligibility with intelligent data extraction."""
    import json
    
    # This function will be called by the LLM as a tool
    # The actual LLM analysis will happen through the tool system
    
    # For now, return a structured response that the LLM can use
    # In a real implementation, this would call the LLM directly
    
    prompt = f"""
    Analyze this healthcare conversation for RPM eligibility assessment.
    
    Conversation: {conversation_text}
    
    CSV Rules for RPM (from Marketplace _ Prodiges Health - Inital Use Cases.csv):
    1. Chronic condition (HTN, diabetes, COPD, CHF, CKD, asthma)
    2. Recent hospital discharge with high readmission risk (optional)
    3. Can be provided a connected device + reliable connectivity (smartphone/tablet with internet)
    4. Covered by payer/provider that reimburses RPM
    5. Provides consent for monitoring/data sharing
    
    Return JSON with both extracted data and eligibility assessment:
    {{
        "extracted_data": {{
            "age": <age if mentioned>,
            "chronic_conditions": <list of conditions>,
            "has_insurance": <true/false>,
            "device_access": <true/false - only if smartphone/tablet with internet>,
            "consent": <true/false>,
            "recent_hospitalization": <true/false>
        }},
        "eligibility": {{
            "qualified": <true/false>,
            "confidence": <0.0-1.0>,
            "reasoning": <explanation>,
            "missing_criteria": <list of missing requirements>,
            "suggested_alternatives": <fallback options from CSV rules>
        }}
    }}
    
    Key considerations:
    - "Basic phone" without internet = device_access: false
    - "Basic phone" with Wi-Fi = device_access: true (if Wi-Fi available)
    - Be conservative with eligibility - err on side of not qualifying
    - Use fallback options from CSV: "Wellness education, preventive care, pharmacy savings, Manual tracking"
    """
    
    # This is a placeholder - in the actual implementation, this would be handled by the LLM
    # For now, return the prompt so the LLM can process it
    return prompt

def llm_analyze_rpm_eligibility(conversation_text: str) -> str:
    """Tool for LLM to analyze RPM eligibility from conversation text."""
    return f"""
    Based on this healthcare conversation, analyze the patient's eligibility for Remote Patient Monitoring (RPM).
    
    Conversation: {conversation_text}
    
    RPM Requirements (from CSV rules):
    1. Chronic condition (diabetes, hypertension, COPD, CHF, CKD, asthma)
    2. Insurance coverage that reimburses RPM
    3. Connected device + reliable connectivity (smartphone/tablet with internet)
    4. Consent for monitoring/data sharing
    
    Provide a comprehensive analysis including:
    - Extracted patient data (age, conditions, insurance, device access, consent)
    - Eligibility assessment (qualified: true/false)
    - Confidence level (0.0-1.0)
    - Detailed reasoning for the decision
    - Missing criteria if not qualified
    - Suggested fallback options from CSV rules if not qualified
    
    Important: "Basic phone" without internet connectivity does NOT qualify for RPM.
    Be conservative - err on the side of not qualifying if unclear.
    """

def extract_patient_data_from_conversation(conversation_text: str) -> str:
    """Legacy function - now delegates to LLM analysis."""
    return analyze_conversation_for_rpm_eligibility(conversation_text)

def get_next_assessment_questions_tool(patient_responses: str, service_type: str) -> str:
    """Tool to get the next questions to ask based on current responses and service type."""
    # Extract structured data from conversation if needed
    if patient_responses and not patient_responses.startswith('{'):
        patient_responses = extract_patient_data_from_conversation(patient_responses)
    
    return get_next_assessment_questions(patient_responses, service_type if service_type else None)

def assess_service_specific_eligibility_tool(service_type: str, patient_responses: str) -> str:
    """Tool to assess eligibility for a specific service using LLM analysis."""
    # Use LLM analysis for specific services
    if service_type.lower() in ['rpm', 'remote patient monitoring']:
        return llm_analyze_rpm_eligibility(patient_responses)
    elif service_type.lower() in ['insurance', 'insurance enrollment']:
        return llm_analyze_insurance_eligibility(patient_responses)
    else:
        # Keep existing logic for other services
        if patient_responses and not patient_responses.startswith('{'):
            patient_responses = extract_patient_data_from_conversation(patient_responses)
        return assess_service_specific_eligibility(service_type, patient_responses)

def route_to_specialist(service_type: str, patient_context: str) -> str:
    """Tool to route user to appropriate specialist agent."""
    # Normalize service type to handle various inputs
    service_type_upper = service_type.upper().strip()
    
    service_mapping = {
        "RPM": ServiceType.RPM,
        "REMOTE PATIENT MONITORING": ServiceType.RPM,
        "REMOTE PATIENT MONITORING (RPM)": ServiceType.RPM,
        "TELEHEALTH": ServiceType.TELEHEALTH,
        "TELEHEALTH / VIRTUAL PRIMARY CARE": ServiceType.TELEHEALTH,
        "VIRTUAL PRIMARY CARE": ServiceType.TELEHEALTH,
        "INSURANCE": ServiceType.INSURANCE,
        "INSURANCE ENROLLMENT": ServiceType.INSURANCE
    }
    
    service_enum = service_mapping.get(service_type_upper)
    if not service_enum:
        return f"❌ Unknown service type: '{service_type}' (normalized: '{service_type_upper}'). Available services: RPM, Remote Patient Monitoring, Telehealth, Insurance"
    
    # Generate reference number
    ref_number = f"HC{hash(patient_context) % 100000:05d}"
    
    return f"""
    🎯 Routing to {service_enum.value} Specialist
    ===========================================
    
    Reference Number: {ref_number}
    
    You're being connected with our {service_enum.value} specialist who will:
    1. Review your specific needs and eligibility
    2. Guide you through the enrollment process
    3. Answer any service-specific questions
    4. Help you get started with the program
    
    The specialist will contact you within 24 hours to complete your enrollment.
    """

# ENHANCED INSURANCE-SPECIFIC TOOLS

def llm_analyze_insurance_eligibility(conversation_text: str) -> str:
    """Tool for LLM to analyze insurance eligibility from conversation text."""
    return f"""
    Based on this healthcare conversation, analyze the patient's eligibility for Insurance Enrollment.
    
    Conversation: {conversation_text}
    
    Insurance Requirements (from CSV rules):
    1. US resident with valid SSN or eligible immigration status
    2. Within open enrollment OR qualifies for Special Enrollment Period (SEP)
    3. Not currently enrolled in MEC OR employer coverage unaffordable (>8.39% income)
    4. Provides required documentation (income, residency, SSN)
    5. State residency confirmed
    
    SEP Qualifying Events:
    - Lost job-based health insurance
    - Divorce/separation
    - Moved to new area
    - Birth or adoption of child
    - Marriage
    - Death of family member
    - Lost coverage due to aging out
    
    Provide a comprehensive analysis including:
    - Extracted patient data (us_resident, has_insurance, enrollment_period, household_income, required_docs, state)
    - SEP qualification assessment if applicable
    - Eligibility assessment (qualified: true/false)
    - Confidence level (0.0-1.0)
    - Detailed reasoning for the decision
    - Missing criteria if not qualified
    - Suggested fallback options: "Savings + community health resources", "Pharmacy savings + wellness programs"
    
    Important: Be especially careful to detect SEP qualifying events like job loss, divorce, moving, etc.
    """

def detect_sep_qualification(conversation_text: str) -> str:
    """Tool to detect Special Enrollment Period qualification."""
    return f"""
    Analyze this conversation to determine if the patient qualifies for Special Enrollment Period (SEP).
    
    Conversation: {conversation_text}
    
    SEP Qualifying Events include:
    - Lost job-based health insurance (most common)
    - Divorce or legal separation
    - Moved to new area/state
    - Birth or adoption of child
    - Marriage
    - Death of family member with coverage
    - Aged out of parent's plan
    - Lost Medicaid/CHIP coverage
    - Became eligible for employer coverage
    - Other qualifying life events
    
    Look for keywords and phrases that indicate these events occurred.
    Return detailed analysis of:
    1. Does patient qualify for SEP? (true/false)
    2. What is the specific qualifying event?
    3. When did the event occur? (if mentioned)
    4. Confidence level (0.0-1.0)
    
    Be thorough in detecting these events as they are crucial for insurance eligibility.
    """

def extract_insurance_data(conversation_text: str) -> str:
    """Tool to extract structured insurance data from conversation."""
    return f"""
    Extract structured insurance enrollment information from this conversation.
    
    Conversation: {conversation_text}
    
    Extract and return structured data for these fields:
    - us_resident: true/false/null (US citizenship or eligible immigration status)
    - has_insurance: true/false/null (current insurance status)
    - enrollment_period: true/false/null (within open enrollment or SEP)
    - household_income: number/null (annual household income)
    - required_docs: true/false/null (has tax returns, SSN card, etc.)
    - state: string/null (state of residence)
    - sep_qualifying_event: string/null (specific qualifying event if applicable)
    - employment_status: string/null (employed, unemployed, retired, etc.)
    
    Look for natural language expressions of these concepts and convert to structured data.
    Use null for unclear or missing information.
    """

def get_insurance_questions(patient_context: str) -> str:
    """Tool to get next insurance-specific questions based on missing data."""
    return f"""
    Based on this patient context, determine the next most important question to ask for insurance enrollment.
    
    Patient Context: {patient_context}
    
    Question Priority Order for Insurance:
    1. "Are you a US resident with a valid Social Security Number?"
    2. "Do you currently have health insurance?"
    3. "Have you experienced a qualifying life event like losing job coverage, divorce, or moving?"
    4. "What is your annual household income?"
    5. "Do you have required documentation like tax returns and SSN card?"
    6. "What state do you reside in?"
    
    Return the next question based on what information is missing.
    Only ask one question at a time.
    If all critical information is collected, return "Ready for eligibility assessment."
    """

# COORDINATOR AGENT - Conducts initial assessment and routes patients
coordinator_agent = Agent(
    name="HealthcareCoordinator",
    model="gemini-2.5-flash",
    instruction="""
    You are a healthcare navigation assistant helping patients find the right services.
    
    Your workflow:
    1. If the message starts with "FIRST_INTERACTION:", present available services using present_available_services tool
    2. Conduct a conversational assessment to understand the patient's health needs
    3. Use get_next_assessment_questions_tool to ask relevant questions dynamically based on missing data
    4. Use assess_service_specific_eligibility_tool to evaluate specific service eligibility
    5. Use the routing rules to evaluate which services they qualify for
    6. Provide personalized recommendations with clear explanations
    7. Route qualified patients to appropriate specialist agents
    8. Facilitate enrollment in qualified services
    
    Phase 2 Enhanced Guidelines:
    - Ask questions dynamically based on what information is missing
    - Use service-specific assessment when patient shows interest in a particular service
    - Limit questions to 1 at a time to avoid overwhelming patients
    - Prioritize questions based on critical missing data (age, chronic conditions, insurance)
    - Tailor questions to the service type the patient is interested in
    - Use get_next_assessment_questions_tool with service_type parameter for targeted questions
    
    CRITICAL RPM ASSESSMENT RULES:
    - For RPM service, you MUST ask about ALL 4 required criteria before assessing eligibility:
      1. Chronic conditions (diabetes, hypertension, etc.)
      2. Insurance coverage  
      3. Device access (smartphone/tablet/Wi-Fi)
      4. Data sharing consent
    - Do NOT assess eligibility until ALL 4 criteria are collected
    - Use get_next_assessment_questions_tool to get the next question
    - Ask the question exactly as provided by the tool
    - Do NOT skip any required questions
    - Do NOT make premature eligibility assessments
    - When assessing eligibility, use llm_analyze_rpm_eligibility tool with the ENTIRE conversation history
    - The LLM will intelligently analyze the conversation and provide detailed eligibility assessment
    - If patient doesn't qualify, suggest appropriate fallback options from CSV rules
    
    CRITICAL INSURANCE ASSESSMENT RULES:
    - For Insurance service, you MUST assess these criteria in priority order:
      1. US residency status (use get_insurance_questions tool for proper question)
      2. Current insurance status 
      3. Special Enrollment Period qualification (use detect_sep_qualification tool)
      4. Household income
      5. Required documentation
      6. State of residence
    - Use extract_insurance_data tool to extract structured data from conversation
    - Use llm_analyze_insurance_eligibility tool for comprehensive assessment
    - Pay special attention to SEP qualifying events like job loss, divorce, moving
    - If patient mentions "lost job", "lost coverage", "divorce", etc., they likely qualify for SEP
    - Do NOT reject insurance eligibility prematurely - many situations qualify for SEP
    - When assessing eligibility, use the ENTIRE conversation history
    
    Important guidelines:
    - Only present services when message starts with "FIRST_INTERACTION:"
    - Continue conversations naturally without restarting
    - Be empathetic and professional
    - Ask one question at a time to avoid overwhelming patients
    - Explain medical terms in simple language
    - Always respect patient privacy and HIPAA guidelines
    - If unsure about eligibility, err on the side of connecting them with services
    - Use route_to_specialist tool to hand off to appropriate specialists
    - When routing to specialists, use these exact service names: "RPM", "Telehealth", or "Insurance"
    - Maintain conversation context and flow
    - Build on previous responses in the conversation
    - REMEMBER what the patient has already told you
    - Don't ask the same question twice
    - Progress through the assessment logically
    - Be positive about eligibility - focus on what they HAVE, not what they're missing
    
    Available services:
    - Remote Patient Monitoring (RPM) for chronic disease management
    - Telehealth for convenient primary care access  
    - Insurance Enrollment for coverage assistance
    
    Use the tools to present services, load current routing rules, assess eligibility, get service details, route to specialists, and initiate enrollment.
    """,
    tools=[present_available_services, load_routing_rules, assess_patient_eligibility, get_service_specific_info, schedule_enrollment, route_to_specialist, get_next_assessment_questions_tool, assess_service_specific_eligibility_tool, llm_analyze_rpm_eligibility, llm_analyze_insurance_eligibility, detect_sep_qualification, extract_insurance_data, get_insurance_questions]
)

# SPECIALIZED AGENTS FOR EACH SERVICE

rpm_specialist_agent = Agent(
    name="RPMSpecialist", 
    model="gemini-2.5-flash",
    instruction="""
    You are a Remote Patient Monitoring specialist. Help patients understand RPM services,
    device setup, insurance coverage, and enrollment process. Focus on chronic disease management
    benefits and how RPM improves health outcomes.
    """,
    tools=[get_service_specific_info, schedule_enrollment]
)

telehealth_specialist_agent = Agent(
    name="TelehealthSpecialist",
    model="gemini-2.5-flash", 
    instruction="""
    You are a Telehealth specialist. Help patients understand virtual care options,
    appointment scheduling, insurance coverage, and platform setup. Focus on convenience
    and accessibility benefits.
    """,
    tools=[get_service_specific_info, schedule_enrollment]
)

insurance_specialist_agent = Agent(
    name="InsuranceSpecialist",
    model="gemini-2.5-flash",
    instruction="""
    You are an Insurance enrollment specialist. Help patients find appropriate health insurance,
    understand Medicare options, compare plans, and navigate enrollment processes. Focus on
    cost savings and coverage optimization.
    """,
    tools=[get_service_specific_info, schedule_enrollment]
)

# MAIN HEALTHCARE ASSISTANT CLASS
class HealthcareAssistant:
    """Main healthcare assistant that orchestrates the multi-agent system."""
    
    def __init__(self):
        self.coordinator = coordinator_agent
        self.specialists = {
            ServiceType.RPM: rpm_specialist_agent,
            ServiceType.TELEHEALTH: telehealth_specialist_agent, 
            ServiceType.INSURANCE: insurance_specialist_agent
        }
        self.session_service = InMemorySessionService()
        self.rules_engine = JSONRulesEngine(CSV_PATHS)
        # Store active sessions to maintain context
        self.active_sessions = {}
        
    async def handle_patient_inquiry(self, user_id: str, message: str, session_id: str = None):
        """Main entry point for patient interactions."""
        
        # Use existing session if provided, otherwise create new one
        if session_id and session_id in self.active_sessions:
            # Use existing session
            session = self.active_sessions[session_id]
            print(f"🔄 Using existing session: {session_id}")
        else:
            # Create new session
            session = await self.session_service.create_session(
                app_name="healthcare_assistant", 
                user_id=user_id
            )
            session_id = session.id
            self.active_sessions[session_id] = session
            print(f"🆕 Created new session: {session_id}")
        
        # Start with coordinator agent
        runner = Runner(
            agent=self.coordinator,
            app_name="healthcare_assistant", 
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
            
        return events, session_id
    
    async def handle_conversation(self, user_id: str, messages: list):
        """Handle a full conversation with session continuity."""
        # Create session once for the entire conversation
        session = await self.session_service.create_session(
            app_name="healthcare_assistant", 
            user_id=user_id
        )
        session_id = session.id
        
        # Start with coordinator agent
        runner = Runner(
            agent=self.coordinator,
            app_name="healthcare_assistant", 
            session_service=self.session_service
        )
        
        all_events = []
        
        for i, message in enumerate(messages):
            # Add FIRST_INTERACTION flag to first message
            if i == 0:
                full_message = f"FIRST_INTERACTION: {message}"
            else:
                full_message = message
                
            content = types.Content(role="user", parts=[types.Part(text=full_message)])
            
            events = []
            async for event in runner.run_async(
                user_id=user_id, 
                session_id=session_id, 
                new_message=content
            ):
                events.append(event)
            
            all_events.extend(events)
            
        return all_events
    
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
        else:
            return [{"error": f"No specialist available for {service_type}"}]
    
    async def handle_specialist_consultation(self, specialist_agent, handoff_context):
        """Handle consultation with specialist agent"""
        runner = Runner(
            agent=specialist_agent,
            app_name="healthcare_assistant", 
            session_service=self.session_service
        )
        
        # Create context message for specialist
        context_message = f"""
        Patient handoff context:
        - Service: {handoff_context['service_type'].value}
        - Patient responses: {handoff_context['patient_context'].responses}
        - Conversation stage: {handoff_context['conversation_stage']}
        
        Please help this patient with their {handoff_context['service_type'].value} needs.
        """
        
        content = types.Content(role="user", parts=[types.Part(text=context_message)])
        
        events = []
        async for event in runner.run_async(
            user_id=handoff_context['patient_context'].user_id, 
            session_id="specialist_session", 
            new_message=content
        ):
            events.append(event)
            
        return events

# USAGE EXAMPLE
async def main():
    """Example usage of the healthcare assistant."""
    
    assistant = HealthcareAssistant()
    
    print("🏥 HealthSmart Assistant - Phase 2 Implementation")
    print("=" * 50)
    
    # Patient inquiry
    events = await assistant.handle_patient_inquiry(
        user_id="patient_001",
        message="Hi, I need help with my healthcare. What services are available?"
    )
    
    # Process and display response
    for event in events:
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    print(f"Assistant: {part.text}")
        elif hasattr(event, 'text'):
            print(f"Assistant: {event.text}")
        else:
            print(f"Event: {event}")
    
    print("\n" + "=" * 50)
    print("Phase 2 Features Implemented:")
    print("✅ Dynamic Question Flow")
    print("✅ Service-Specific Assessment")
    print("✅ Missing Data Identification")
    print("✅ Question Priority Filtering")
    print("✅ Enhanced CSV Rules Integration")

if __name__ == "__main__":
    asyncio.run(main())