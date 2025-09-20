# Healthcare Assistant Agent - Multi-Agent ADK Architecture with JSON Rules
# Copyright 2025 Google LLC - Licensed under Apache License, Version 2.0

import asyncio
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

# Import configuration - Updated for JSON rules
from config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, GOOGLE_GENAI_USE_VERTEXAI, GEMINI_API_KEY

# Import enhanced JSON rules engine
from app.rules_engine_enhanced import JSONRulesEngine, load_dynamic_rules, assess_eligibility_dynamically, get_next_assessment_questions, assess_service_specific_eligibility

# Set up environment
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

class ServiceType(Enum):
    RPM = "Remote Patient Monitoring (RPM)"
    TELEHEALTH = "Telehealth / Virtual Primary Care"
    INSURANCE = "Insurance Enrollment"
    EMERGENCY = "Emergency Screening"
    PHARMACY = "Pharmacy Savings"
    WELLNESS = "Wellness Programs"

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
    """Present healthcare services to users with enhanced JSON-based information"""
    return """
    🏥 Welcome to HealthSmart Assistant!
    
    I can help you with these healthcare services:
    
    1. 🩺 Remote Patient Monitoring (RPM)
       - Monitor chronic conditions from home
       - Connected devices for health tracking
       - Medicare and insurance coverage available
    
    2. 💻 Telehealth / Virtual Primary Care  
       - Virtual doctor visits from home
       - Prescription management and refills
       - Same-day appointments available
    
    3. 🛡️ Insurance Enrollment
       - Help finding health insurance plans
       - Medicare and marketplace assistance
       - Special enrollment period support
    
    4. 💊 Pharmacy Savings Programs
       - Prescription medication discounts
       - Generic and brand name savings
       - No insurance required
    
    5. 🌟 Wellness Programs
       - Weight management support
       - Diabetes prevention programs
       - Stress management and mental health
    
    ⚠️ Emergency Support: If you're experiencing chest pain, difficulty breathing, 
    stroke symptoms, or other emergencies, please call 911 immediately.
    
    How can I help you today? Please tell me about your health needs.
    """

# ENHANCED TOOL FUNCTIONS WITH JSON RULES

def load_routing_rules() -> str:
    """Tool to load and return current JSON routing rules as context."""
    return load_dynamic_rules()

def assess_patient_eligibility(patient_responses: str) -> str:
    """Tool to assess patient eligibility for services using JSON rules."""
    return assess_eligibility_dynamically(patient_responses)

def check_emergency_symptoms(patient_responses: str) -> str:
    """Tool to check for emergency symptoms requiring immediate attention."""
    try:
        if isinstance(patient_responses, str):
            if patient_responses.startswith('{'):
                responses = json.loads(patient_responses)
            else:
                # Convert conversation text to symptoms check
                responses = {"symptoms": patient_responses, "conversation": patient_responses}
        else:
            responses = patient_responses
    except:
        responses = {"symptoms": patient_responses}  # Fallback for text input
    
    rules_engine = JSONRulesEngine("rules")
    result = rules_engine.evaluate_patient_against_rules(responses, "emergency")
    
    if result.qualified and result.confidence > 0.8:
        return f"""
        🚨 EMERGENCY ALERT 🚨
        {result.reasoning}
        
        IMMEDIATE ACTION REQUIRED:
        Call 911 or go to the nearest emergency room immediately.
        
        Do not delay seeking medical attention.
        Do not continue with other healthcare assessments.
        """
    elif result.qualified and result.confidence > 0.5:
        return f"""
        ⚠️ URGENT CARE NEEDED ⚠️
        {result.reasoning}
        
        Seek medical attention within the next few hours.
        Visit urgent care or emergency room.
        Consider calling your doctor immediately.
        """
    else:
        return f"""
        ✅ No emergency symptoms detected.
        {result.reasoning}
        
        Continue with routine healthcare assessment.
        """

def get_service_specific_info(service_type: str) -> str:
    """Tool to get detailed information about a specific service using JSON rules."""
    
    # Load service information from JSON rules
    rules_engine = JSONRulesEngine("rules")
    service_key = rules_engine._normalize_service_name(service_type)
    
    if service_key in rules_engine.rules:
        rule = rules_engine.rules[service_key]
        
        # Extract service information from JSON rule
        service_name = rule.get("service", service_type)
        description = rule.get("description", "")
        
        info = f"""
        {service_name}:
        {description}
        
        """
        
        # Add requirements if available
        if "requirements" in rule:
            info += "Requirements:\n"
            for req_name, req_config in rule["requirements"].items():
                if req_config.get("required"):
                    question = req_config.get("question", req_name)
                    info += f"• {question}\n"
        
        # Add benefits/features if available
        if "program_components" in rule:
            info += "\nProgram Components:\n"
            for component in rule["program_components"]:
                info += f"• {component}\n"
        
        return info
    
    # Fallback to static information if JSON rule not found
    service_info = {
        "RPM": """
        Remote Patient Monitoring (RPM) Service:
        - 24/7 health monitoring with connected devices
        - Chronic disease management support
        - Medicare and most insurance plans accepted
        - Devices include: BP monitors, glucometers, pulse oximeters, smart scales
        - Reduces hospital readmissions by 38%
        """,
        
        "TELEHEALTH": """
        Telehealth / Virtual Primary Care:
        - Virtual doctor visits from home
        - Prescription management and refills
        - Preventive care and wellness checks
        - Same-day and scheduled appointments
        - Covered by most insurance plans
        """,
        
        "INSURANCE": """
        Insurance Enrollment Assistance:
        - Help finding the right health insurance plan
        - Medicare enrollment and optimization
        - Marketplace plan comparison
        - Subsidy and cost-sharing reduction assistance
        - Year-round enrollment support for eligible life events
        """,
        
        "PHARMACY": """
        Pharmacy Savings Programs:
        - Up to 80% off prescription medications
        - No insurance required
        - Accepted at 60,000+ pharmacies nationwide
        - Covers generic and brand medications
        - Free discount card and mobile app
        """,
        
        "WELLNESS": """
        Wellness Programs:
        - Weight management and nutrition counseling
        - Diabetes prevention programs
        - Smoking cessation support
        - Stress management and mental health
        - Chronic disease self-management
        """
    }
    
    return service_info.get(service_type.upper(), "Service information not found.")

def schedule_enrollment(service_type: str, patient_info: str) -> str:
    """Tool to initiate enrollment process for a qualified service."""
    
    # Generate reference number
    ref_number = f"HC{hash(patient_info) % 100000:05d}"
    
    # Get service-specific enrollment timeline from JSON rules
    rules_engine = JSONRulesEngine("rules")
    service_key = rules_engine._normalize_service_name(service_type)
    
    timeline = "3-5 business days"  # Default
    if service_key in rules_engine.rules:
        rule = rules_engine.rules[service_key]
        if "enrollment_timeline" in rule:
            timeline_data = rule["enrollment_timeline"]
            if isinstance(timeline_data, dict):
                timeline = timeline_data.get("eligibility_confirmation", timeline)
            else:
                timeline = str(timeline_data)
    
    return f"""
    ✅ Enrollment initiated for {service_type}!
    
    Reference Number: {ref_number}
    
    Next steps:
    1. You'll receive a confirmation email within 2 hours
    2. Our enrollment specialist will call you within 24 hours
    3. Required documents will be sent via secure message
    4. Setup appointment scheduled within {timeline}
    
    Important: Please keep your reference number for tracking.
    
    Is there anything else I can help you with today?
    """

def get_next_assessment_questions_tool(patient_responses: str, service_type: Optional[str] = None) -> str:
    """Tool to get the next questions using JSON assessment database."""
    return get_next_assessment_questions(patient_responses, service_type)

def assess_service_specific_eligibility_tool(service_type: str, patient_responses: str) -> str:
    """Tool to assess eligibility for a specific service using JSON rules."""
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
        "INSURANCE ENROLLMENT": ServiceType.INSURANCE,
        "PHARMACY": ServiceType.PHARMACY,
        "PHARMACY SAVINGS": ServiceType.PHARMACY,
        "WELLNESS": ServiceType.WELLNESS,
        "WELLNESS PROGRAMS": ServiceType.WELLNESS
    }
    
    service_enum = service_mapping.get(service_type_upper)
    if not service_enum:
        available_services = ", ".join(service_mapping.keys())
        return f"❌ Unknown service type: '{service_type}'. Available services: {available_services}"
    
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
    
    Please save your reference number: {ref_number}
    """

# ENHANCED ANALYSIS TOOLS WITH JSON RULES

def analyze_rpm_eligibility(conversation_text: str) -> str:
    """Tool for comprehensive RPM eligibility analysis using JSON rules with context awareness."""
    try:
        rules_engine = JSONRulesEngine("data")
        
        # Extract key information from conversation context
        conversation_lower = conversation_text.lower()
        
        # Check for chronic conditions mentioned
        chronic_conditions = []
        if any(term in conversation_lower for term in ['diabetes', 'diabetic', 'blood sugar']):
            chronic_conditions.append('diabetes')
        if any(term in conversation_lower for term in ['hypertension', 'high blood pressure', 'bp']):
            chronic_conditions.append('hypertension')
        if any(term in conversation_lower for term in ['heart disease', 'cardiac', 'heart condition']):
            chronic_conditions.append('heart disease')
        if any(term in conversation_lower for term in ['copd', 'asthma', 'respiratory']):
            chronic_conditions.append('respiratory conditions')
        
        # Check for insurance mentioned
        has_insurance = any(term in conversation_lower for term in ['insurance', 'medicare', 'medicaid', 'coverage'])
        
        # Check for device access mentioned
        has_devices = any(term in conversation_lower for term in ['smartphone', 'phone', 'tablet', 'wifi', 'wi-fi', 'internet'])
        
        # Check for data sharing consent mentioned
        consents_to_sharing = any(term in conversation_lower for term in ['yes', 'willing', 'agree', 'consent', 'share'])
        
        # Create structured responses based on conversation context
        responses = {
            "conversation": conversation_text,
            "chronic_conditions": chronic_conditions,
            "has_insurance": has_insurance,
            "has_devices": has_devices,
            "consents_to_sharing": consents_to_sharing
        }
        
        # Use JSON rules for evaluation
        result = rules_engine.evaluate_patient_against_rules(responses, "rpm")
        
        status = "✅ QUALIFIED" if result.qualified else "❌ NOT QUALIFIED"
        confidence_pct = f"{result.confidence:.0%}"
        
        response = f"""
        🩺 RPM Eligibility Analysis:
        Status: {status} (Confidence: {confidence_pct})
        Reasoning: {result.reasoning}
        """
        
        if result.missing_criteria:
            response += f"\nMissing Criteria: {', '.join(result.missing_criteria)}"
        
        if result.next_questions:
            response += f"\nNext Questions: {'; '.join(result.next_questions)}"
        
        if result.fallback_options:
            response += f"\nAlternative Options: {', '.join(result.fallback_options)}"
        
        return response
        
    except Exception as e:
        return f"❌ Error analyzing RPM eligibility: {str(e)}"

def analyze_insurance_eligibility(conversation_text: str) -> str:
    """Tool for comprehensive insurance eligibility analysis using JSON rules."""
    try:
        rules_engine = JSONRulesEngine("data")
        
        # Convert conversation to structured data for analysis
        responses = {"conversation": conversation_text}
        
        # Use JSON rules for evaluation
        result = rules_engine.evaluate_patient_against_rules(responses, "insurance")
        
        status = "✅ QUALIFIED" if result.qualified else "❌ NOT QUALIFIED"
        confidence_pct = f"{result.confidence:.0%}"
        
        response = f"""
        🛡️ Insurance Enrollment Analysis:
        Status: {status} (Confidence: {confidence_pct})
        Reasoning: {result.reasoning}
        """
        
        if result.missing_criteria:
            response += f"\nMissing Information: {', '.join(result.missing_criteria)}"
        
        if result.next_questions:
            response += f"\nNext Questions: {'; '.join(result.next_questions)}"
        
        if result.fallback_options:
            response += f"\nAlternative Resources: {', '.join(result.fallback_options)}"
        
        return response
        
    except Exception as e:
        return f"❌ Error analyzing insurance eligibility: {str(e)}"

def detect_sep_qualification(conversation_text: str) -> str:
    """Tool to detect Special Enrollment Period qualification using JSON rules."""
    try:
        rules_engine = JSONRulesEngine("data")
        
        if "insurance" in rules_engine.rules:
            enrollment_periods = rules_engine.rules["insurance"].get("enrollment_periods", {})
            qualifying_events = enrollment_periods.get("special_enrollment", {}).get("qualifying_events", [])
            
            conversation_lower = conversation_text.lower()
            detected_events = []
            
            for event in qualifying_events:
                if any(keyword in conversation_lower for keyword in event.lower().split()):
                    detected_events.append(event)
            
            if detected_events:
                return f"""
                ✅ Special Enrollment Period (SEP) Qualification Detected
                
                Qualifying Events Found:
                {chr(10).join(f'• {event}' for event in detected_events)}
                
                This means you can enroll in health insurance outside the normal open enrollment period.
                Enrollment window: 60 days from qualifying event.
                """
            else:
                return """
                ❌ No Special Enrollment Period qualifying events detected.
                
                You may still qualify for:
                • Open enrollment (November 1 - January 15)
                • Medicaid (year-round enrollment)
                • Employer insurance (during employer open enrollment)
                """
        
        return "Unable to check SEP qualification - insurance rules not loaded."
        
    except Exception as e:
        return f"❌ Error checking SEP qualification: {str(e)}"

def get_pharmacy_savings_info(patient_responses: str) -> str:
    """Tool to provide pharmacy savings information using JSON rules."""
    try:
        rules_engine = JSONRulesEngine("data")
        result = rules_engine.evaluate_patient_against_rules(
            {"responses": patient_responses}, 
            "pharmacy"
        )
        
        return f"""
        💊 Pharmacy Savings Program:
        Eligibility: ✅ Everyone qualifies (no restrictions)
        
        Savings Available:
        • Up to 80% off prescription medications
        • Generic medications: 30-80% savings
        • Brand medications: 10-50% savings
        
        How it works:
        • Free discount card (immediate download)
        • Accepted at 60,000+ pharmacies
        • Cannot combine with insurance
        • Covers entire household including pets
        
        Special Programs:
        • Medicare Part D gap coverage
        • Chronic disease medication packages
        • Mail-order savings for 90-day supplies
        
        Get started: Download the free app or print discount card immediately.
        """
        
    except Exception as e:
        return f"❌ Error getting pharmacy savings info: {str(e)}"

# COORDINATOR AGENT - Enhanced with JSON rules and emergency screening
coordinator_agent = Agent(
    name="HealthcareCoordinator",
    model="gemini-2.5-flash",
    instruction="""
    You are a healthcare navigation assistant helping patients find the right services using advanced JSON-based rules.
    
    Your workflow:
    0. SAFETY FIRST: Always check for emergency symptoms using check_emergency_symptoms tool before proceeding
    1. If the message starts with "FIRST_INTERACTION:", present available services using present_available_services tool
    2. Conduct a conversational assessment to understand the patient's health needs
    3. Use get_next_assessment_questions_tool to ask relevant questions dynamically
    4. Use assess_service_specific_eligibility_tool to evaluate specific service eligibility
    5. Provide personalized recommendations with clear explanations
    6. Route qualified patients to appropriate specialist agents
    7. Facilitate enrollment in qualified services
    
    CRITICAL SAFETY PROTOCOL:
    - ALWAYS use check_emergency_symptoms tool first if patient mentions ANY symptoms
    - If emergency symptoms detected, STOP assessment and direct to emergency care
    - Do NOT continue with service enrollment if emergency care is needed
    - Emergency symptoms include: chest pain, difficulty breathing, stroke symptoms, severe bleeding, etc.
    
    Enhanced JSON Rules Guidelines:
    - The system now uses comprehensive JSON rules instead of CSV files
    - JSON rules provide more sophisticated eligibility assessment
    - Emergency screening is automatically built into the system
    - Use analyze_rpm_eligibility for detailed RPM assessment
    - Use analyze_insurance_eligibility for detailed insurance assessment
    - Use detect_sep_qualification to check for special enrollment periods
    - Use get_pharmacy_savings_info for pharmacy discount programs
    
    Service-Specific Assessment:
    - RPM: Check chronic conditions, insurance, device access, consent
    - Telehealth: Check state licensing, device capability, internet access
    - Insurance: Check US residency, enrollment periods, documentation
    - Pharmacy: Universal eligibility (no restrictions)
    - Wellness: Check program-specific requirements
    
    Question Flow:
    - Ask one question at a time to avoid overwhelming patients
    - Use get_next_assessment_questions_tool for intelligent question sequencing
    - Questions are prioritized based on missing critical data
    - Emergency screening questions take absolute priority
    
    Important guidelines:
    - Only present services when message starts with "FIRST_INTERACTION:"
    - Continue conversations naturally without restarting
    - Be empathetic and professional
    - Explain medical terms in simple language
    - Always respect patient privacy and HIPAA guidelines
    - If unsure about eligibility, err on the side of connecting them with services
    - Use route_to_specialist tool to hand off to appropriate specialists
    - Maintain conversation context and flow
    - Build on previous responses in the conversation
    - Don't ask the same question twice
    - Be positive about eligibility - focus on what they HAVE
    
    Available services (with JSON rule support):
    - Remote Patient Monitoring (RPM) for chronic disease management
    - Telehealth for convenient primary care access  
    - Insurance Enrollment for coverage assistance
    - Pharmacy Savings for medication discounts
    - Wellness Programs for preventive care
    - Emergency Screening for urgent medical needs
    
    Use the tools to present services, check emergencies, assess eligibility, get service details, route to specialists, and initiate enrollment.
    """,
    tools=[
        present_available_services, 
        check_emergency_symptoms,
        load_routing_rules, 
        assess_patient_eligibility, 
        get_service_specific_info, 
        schedule_enrollment, 
        route_to_specialist, 
        get_next_assessment_questions_tool, 
        assess_service_specific_eligibility_tool,
        analyze_rpm_eligibility, 
        analyze_insurance_eligibility, 
        detect_sep_qualification,
        get_pharmacy_savings_info
    ]
)

# SPECIALIZED AGENTS FOR EACH SERVICE - Enhanced for JSON rules

rpm_specialist_agent = Agent(
    name="RPMSpecialist", 
    model="gemini-2.5-flash",
    instruction="""
    You are a Remote Patient Monitoring specialist using advanced JSON-based eligibility rules.
    
    Help patients understand:
    - RPM services and chronic disease management benefits
    - Device setup and technology requirements
    - Insurance coverage and Medicare reimbursement
    - Enrollment process and timeline
    - Clinical monitoring protocols
    
    Focus on:
    - How RPM improves health outcomes for chronic conditions
    - 38% reduction in hospital readmissions
    - 24/7 monitoring and early intervention
    - Connected devices (BP monitors, glucose meters, scales, pulse oximeters)
    - Care team coordination and data sharing
    
    Use JSON rules for accurate eligibility assessment and device recommendations.
    """,
    tools=[get_service_specific_info, schedule_enrollment, analyze_rpm_eligibility]
)

telehealth_specialist_agent = Agent(
    name="TelehealthSpecialist",
    model="gemini-2.5-flash", 
    instruction="""
    You are a Telehealth specialist using JSON-based state licensing and eligibility rules.
    
    Help patients understand:
    - Virtual care options and appointment types
    - State licensing requirements and restrictions
    - Technology requirements and platform setup
    - Insurance coverage and self-pay options
    - What conditions can/cannot be treated virtually
    
    Focus on:
    - Convenience and accessibility benefits
    - Same-day urgent care availability
    - Prescription management capabilities
    - When in-person care is required
    - Safety protocols and emergency procedures
    """,
    tools=[get_service_specific_info, schedule_enrollment]
)

insurance_specialist_agent = Agent(
    name="InsuranceSpecialist",
    model="gemini-2.5-flash",
    instruction="""
    You are an Insurance enrollment specialist using comprehensive JSON-based eligibility rules.
    
    Help patients understand:
    - Marketplace plan options and metal tiers
    - Medicare enrollment and supplement plans
    - Special Enrollment Period qualification
    - Subsidy eligibility and cost-sharing reductions
    - Required documentation and enrollment process
    
    Focus on:
    - Cost savings and coverage optimization
    - Plan comparison and decision support
    - Enrollment deadlines and timelines
    - Post-enrollment support and plan usage
    - Appeals and special circumstances
    
    Pay special attention to detecting qualifying life events for SEP.
    """,
    tools=[get_service_specific_info, schedule_enrollment, analyze_insurance_eligibility, detect_sep_qualification]
)

pharmacy_specialist_agent = Agent(
    name="PharmacySpecialist",
    model="gemini-2.5-flash",
    instruction="""
    You are a Pharmacy Savings specialist helping patients save money on medications.
    
    Help patients understand:
    - Prescription discount programs and savings cards
    - Generic vs brand medication options
    - Pharmacy network and acceptance
    - Special programs for chronic conditions
    - Medicare Part D gap coverage
    
    Focus on:
    - Immediate savings (up to 80% off medications)
    - Universal eligibility (no income or insurance restrictions)
    - Free discount cards and mobile apps
    - Medication therapy management
    - Adherence support and refill synchronization
    """,
    tools=[get_service_specific_info, schedule_enrollment, get_pharmacy_savings_info]
)

wellness_specialist_agent = Agent(
    name="WellnessSpecialist",
    model="gemini-2.5-flash",
    instruction="""
    You are a Wellness Programs specialist helping patients with preventive care and lifestyle management.
    
    Help patients understand:
    - Available wellness programs (weight management, diabetes prevention, smoking cessation)
    - Program components and duration
    - Insurance coverage and cost information
    - Eligibility requirements and enrollment process
    - Success rates and outcome tracking
    
    Focus on:
    - Preventive care and early intervention
    - Lifestyle behavior change support
    - Group and individual program options
    - Long-term health improvement goals
    - Integration with other healthcare services
    """,
    tools=[get_service_specific_info, schedule_enrollment]
)

# MAIN HEALTHCARE ASSISTANT CLASS - Enhanced for JSON rules
class HealthcareAssistant:
    """Main healthcare assistant that orchestrates the multi-agent system with JSON rules."""
    
    def __init__(self, rules_dir: str = "data"):
        self.coordinator = coordinator_agent
        self.specialists = {
            ServiceType.RPM: rpm_specialist_agent,
            ServiceType.TELEHEALTH: telehealth_specialist_agent, 
            ServiceType.INSURANCE: insurance_specialist_agent,
            ServiceType.PHARMACY: pharmacy_specialist_agent,
            ServiceType.WELLNESS: wellness_specialist_agent
        }
        self.session_service = InMemorySessionService()
        # Use JSON rules engine instead of CSV
        self.rules_engine = JSONRulesEngine(rules_dir)
        # Store active sessions to maintain context
        self.active_sessions = {}
        
    async def handle_patient_inquiry(self, user_id: str, message: str, session_id: Optional[str] = None):
        """Main entry point for patient interactions with JSON rules support."""
        
        # Use existing session if provided, otherwise create new one
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            print(f"🔄 Using existing session: {session_id}")
        else:
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
        """Handle a full conversation with session continuity and JSON rules."""
        session = await self.session_service.create_session(
            app_name="healthcare_assistant", 
            user_id=user_id
        )
        session_id = session.id
        
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
    
    async def emergency_triage(self, user_id: str, symptoms: str):
        """Emergency triage using JSON rules for immediate safety assessment."""
        
        # Use emergency screening rules
        result = self.rules_engine.evaluate_patient_against_rules(
            {"symptoms": symptoms}, 
            "emergency"
        )
        
        if result.qualified and result.confidence > 0.8:
            return {
                "emergency_level": "critical",
                "action": "call_911_immediately",
                "message": "Call 911 immediately. These symptoms require emergency medical attention.",
                "reasoning": result.reasoning
            }
        elif result.qualified and result.confidence > 0.5:
            return {
                "emergency_level": "urgent",
                "action": "urgent_care_same_day",
                "message": "Seek urgent medical care within the next few hours.",
                "reasoning": result.reasoning
            }
        else:
            return {
                "emergency_level": "routine",
                "action": "continue_assessment",
                "message": "No emergency symptoms detected. Continue with healthcare assessment.",
                "reasoning": result.reasoning
            }
    
    def get_service_eligibility_summary(self, patient_responses: Dict) -> Dict:
        """Get eligibility summary for all services using JSON rules."""
        
        services = ["rpm", "telehealth", "insurance", "pharmacy", "wellness"]
        eligibility_summary = {}
        
        for service in services:
            try:
                result = self.rules_engine.evaluate_patient_against_rules(patient_responses, service)
                eligibility_summary[service] = {
                    "qualified": result.qualified,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "missing_criteria": result.missing_criteria,
                    "fallback_options": result.fallback_options
                }
            except Exception as e:
                eligibility_summary[service] = {
                    "qualified": False,
                    "confidence": 0.0,
                    "reasoning": f"Error evaluating {service}: {str(e)}",
                    "missing_criteria": ["evaluation_error"],
                    "fallback_options": []
                }
        
        return eligibility_summary

# USAGE EXAMPLE
async def main():
    """Example usage of the enhanced healthcare assistant with JSON rules."""
    
    assistant = HealthcareAssistant("rules")
    
    print("🏥 HealthSmart Assistant - JSON Rules Implementation")
    print("=" * 60)
    
    # Test emergency triage
    emergency_result = await assistant.emergency_triage(
        user_id="test_001",
        symptoms="I have chest pain and difficulty breathing"
    )
    print(f"Emergency Triage Result: {emergency_result}")
    print()
    
    # Test patient inquiry
    events, session_id = await assistant.handle_patient_inquiry(
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
    
    print("\n" + "=" * 60)
    print("JSON Rules Features Implemented:")
    print("✅ Emergency symptom screening with JSON rules")
    print("✅ Sophisticated eligibility assessment")
    print("✅ Dynamic question generation from JSON database")
    print("✅ Service-specific analysis tools")
    print("✅ Enhanced fallback and alternative options")
    print("✅ Decision trail tracking and audit support")
    print("✅ Confidence scoring and reasoning")

if __name__ == "__main__":
    asyncio.run(main())