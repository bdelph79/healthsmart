# Healthcare Assistant Agent - Multi-Agent ADK Architecture
# Copyright 2025 Google LLC - Licensed under Apache License, Version 2.0

import asyncio
import csv
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

import google.auth
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import configuration
from config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, GOOGLE_GENAI_USE_VERTEXAI, CSV_PATHS, GEMINI_API_KEY

# Import rules engine
from app.rules_engine import DynamicRulesEngine, load_dynamic_rules, assess_eligibility_dynamically

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

# COORDINATOR AGENT - Conducts initial assessment and routes patients
coordinator_agent = Agent(
    name="HealthcareCoordinator",
    model="gemini-2.5-flash",
    instruction="""
    You are a healthcare navigation assistant helping patients find the right services.
    
    Your workflow:
    1. If the message starts with "FIRST_INTERACTION:", present available services using present_available_services tool
    2. Conduct a conversational assessment to understand the patient's health needs
    3. Ask relevant questions to determine service eligibility  
    4. Use the routing rules to evaluate which services they qualify for
    5. Provide personalized recommendations with clear explanations
    6. Route qualified patients to appropriate specialist agents
    7. Facilitate enrollment in qualified services
    
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
    
    Available services:
    - Remote Patient Monitoring (RPM) for chronic disease management
    - Telehealth for convenient primary care access  
    - Insurance Enrollment for coverage assistance
    
    Use the tools to present services, load current routing rules, assess eligibility, get service details, route to specialists, and initiate enrollment.
    """,
    tools=[present_available_services, load_routing_rules, assess_patient_eligibility, get_service_specific_info, schedule_enrollment, route_to_specialist]
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
        self.rules_engine = DynamicRulesEngine(CSV_PATHS)
        
    async def handle_patient_inquiry(self, user_id: str, message: str, session_id: str = None):
        """Main entry point for patient interactions."""
        
        if not session_id:
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
        
        content = types.Content(role="user", parts=[types.Part(text=message)])
        
        events = []
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=session_id, 
            new_message=content
        ):
            events.append(event)
            
        return events
    
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
    
    print("🏥 HealthSmart Assistant - Phase 1 Implementation")
    print("=" * 50)
    
    # Patient inquiry
    events = await assistant.handle_patient_inquiry(
        user_id="patient_001",
        message="Hi, I need help with my healthcare. What services are available?"
    )
    
    # Process and display response
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    print(f"Assistant: {part.text}")
    
    print("\n" + "=" * 50)
    print("Phase 1 Features Implemented:")
    print("✅ CSV Rules Engine Integration")
    print("✅ Service Presentation")
    print("✅ Basic Agent Handoff")
    print("✅ Dynamic Eligibility Assessment")

if __name__ == "__main__":
    asyncio.run(main())