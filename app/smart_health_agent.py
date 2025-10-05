# Healthcare Assistant Agent - Multi-Agent ADK Architecture with JSON Rules
# Copyright 2025 Google LL - Licensed under Apache License, Version 2.0

import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
from datetime import datetime

import google.auth
from google.adk.agents import Agent
from google.adk.tools import ToolContext
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

# ============================================================================
# HELPER FUNCTIONS FOR NATURAL LANGUAGE EXTRACTION
# ============================================================================

def extract_chronic_conditions(conversation: str) -> Optional[str]:
    """Extract chronic conditions mentioned in conversation."""
    if not conversation:
        return None

    conversation_lower = conversation.lower()
    conditions_found = []

    condition_keywords = {
        'diabetes': ['diabetes', 'diabetic', 'blood sugar', 'type 1', 'type 2', 'insulin'],
        'hypertension': ['hypertension', 'high blood pressure', 'hbp', 'bp'],
        'heart disease': ['heart disease', 'heart failure', 'chf', 'cardiac', 'heart condition'],
        'copd': ['copd', 'emphysema', 'chronic bronchitis'],
        'asthma': ['asthma', 'wheezing'],
        'kidney disease': ['kidney disease', 'ckd', 'renal', 'chronic kidney']
    }

    for condition, keywords in condition_keywords.items():
        if any(kw in conversation_lower for kw in keywords):
            conditions_found.append(condition)

    return ', '.join(conditions_found) if conditions_found else None


def extract_insurance_info(conversation: str) -> Optional[bool]:
    """Extract insurance information from conversation."""
    if not conversation:
        return None

    conversation_lower = conversation.lower()

    # Positive insurance indicators
    insurance_keywords = ['insurance', 'medicare', 'medicaid', 'coverage', 'insured',
                          'part b', 'part a', 'covered', 'policy', 'plan', 'cigna',
                          'aetna', 'blue cross', 'united healthcare', 'employer insurance']

    # Check for insurance mentions
    has_insurance_mention = any(kw in conversation_lower for kw in insurance_keywords)

    # Check for affirmative context (when asked about insurance)
    affirmative_context = any(affirm in conversation_lower for affirm in
                              ['yes', 'i have', 'i do', "i'm covered", 'covered', 'yeah'])

    # Negative indicators
    negative_indicators = ['no insurance', 'not insured', 'no coverage', "don't have insurance",
                           "don't have any insurance"]
    has_negative = any(neg in conversation_lower for neg in negative_indicators)

    if has_negative:
        return False

    # Return True if insurance explicitly mentioned OR affirmative in insurance context
    return has_insurance_mention or (affirmative_context and 'insurance' in conversation_lower)


def extract_device_info(conversation: str) -> Optional[bool]:
    """Extract device access information from conversation."""
    if not conversation:
        return None

    conversation_lower = conversation.lower()

    device_keywords = ['smartphone', 'phone', 'tablet', 'computer', 'device',
                       'iphone', 'android', 'ipad', 'laptop', 'mobile', 'cell phone']

    return any(kw in conversation_lower for kw in device_keywords) or None


def extract_connectivity_info(conversation: str) -> Optional[bool]:
    """Extract connectivity information from conversation."""
    if not conversation:
        return None

    conversation_lower = conversation.lower()

    connectivity_keywords = ['wifi', 'wi-fi', 'internet', 'broadband', 'connection',
                             'connected', 'online', 'cellular', 'data', 'network']

    # Also check for affirmative responses to connectivity questions
    connectivity_affirmative = ['internet is ok', 'internet is okay', 'internet is good',
                                'internet is fine', 'have internet', 'have wifi',
                                'wifi is good', 'connection is good']

    has_connectivity = any(kw in conversation_lower for kw in connectivity_keywords)
    has_affirmative = any(affirm in conversation_lower for affirm in connectivity_affirmative)

    return (has_connectivity or has_affirmative) or None


def extract_consent_info(conversation: str) -> Optional[bool]:
    """Extract consent information from conversation."""
    if not conversation:
        return None

    conversation_lower = conversation.lower()

    # Look for consent context first (monitoring, sharing, data, health)
    consent_context = ['monitor', 'monitoring', 'share', 'sharing', 'data', 'health', 'information']
    has_context = any(ctx in conversation_lower for ctx in consent_context)

    # Then check for affirmative responses
    affirmatives = ['yes', 'agree', 'consent', 'ok', 'okay', 'willing', 'comfortable',
                   'sure', 'fine', 'happy to', 'no problem', 'yeah']
    has_affirmative = any(affirm in conversation_lower for affirm in affirmatives)

    # Negative indicators
    negatives = ['no', 'not comfortable', 'refuse', 'decline', "don't want", 'not willing']
    has_negative = any(neg in conversation_lower for neg in negatives)

    if has_negative and has_context:
        return False

    # Only return True if we have both context AND affirmative
    return (has_context and has_affirmative) or None

# ============================================================================
# SERVICE PRESENTATION AND TOOLS
# ============================================================================

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
    """Tool to check for emergency symptoms with clear action steps."""
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
        # CRITICAL EMERGENCY
        symptom_preview = patient_responses[:100] if isinstance(patient_responses, str) else "severe symptoms"
        return f"""
        🚨 EMERGENCY ALERT 🚨

        {result.reasoning}

        ⚠️ IMMEDIATE ACTION REQUIRED ⚠️

        1️⃣ CALL 911 NOW
           • Call immediately or have someone call for you
           • DO NOT hang up until told to do so
           • Stay on the line with the 911 operator

        2️⃣ DO NOT DRIVE YOURSELF
           • Wait for ambulance to arrive
           • Do not attempt to drive to hospital
           • Even if you feel better, wait for EMS

        3️⃣ PREPARE FOR EMS ARRIVAL
           • Unlock your front door if safe to do so
           • Sit or lie down in a safe location
           • Have medications within reach

        4️⃣ IF YOU'RE ALONE
           • Unlock door first (if able)
           • Call 911 from a visible location
           • Leave phone on speaker

        🏥 What to Tell 911:
        ✓ Your exact address and location
        ✓ Your symptoms: {symptom_preview}
        ✓ Any medications you're currently taking
        ✓ Any known allergies
        ✓ If you're alone or have help available

        ⏰ Time is Critical - Every Second Counts:
        These symptoms require immediate medical evaluation.
        Do NOT wait to see if symptoms improve.
        Do NOT continue with healthcare enrollment.
        Do NOT drive yourself.

        📞 CALL 911 NOW

        (After you've called 911, emergency services will take care of you.
        We're here to help with healthcare navigation once you're stable.)
        """

    elif result.qualified and result.confidence > 0.5:
        # URGENT CARE NEEDED
        return f"""
        ⚠️ URGENT CARE RECOMMENDED ⚠️

        {result.reasoning}

        🏥 SEEK MEDICAL ATTENTION WITHIN 2-4 HOURS

        These symptoms should be evaluated soon, but you have time to get to care safely.

        1️⃣ Visit Urgent Care or Emergency Room
           ✓ Find nearest location: urgentcare.com or Google "urgent care near me"
           ✓ Call ahead to confirm they're open and can see you
           ✓ Bring: Photo ID, insurance card, medication list
           ✓ Have someone drive you (don't drive if symptoms are severe)

        2️⃣ If Symptoms WORSEN, Call 911 Immediately If:
           ⚠️ Difficulty breathing increases
           ⚠️ Chest pain or pressure develops
           ⚠️ Confusion, severe weakness, or inability to walk
           ⚠️ Severe pain (8-10 on pain scale)
           ⚠️ Loss of consciousness or near-fainting

        3️⃣ What to Monitor While Waiting:
           📋 Changes in symptom severity (better/worse/same)
           📋 New symptoms developing
           📋 Your ability to function normally
           📋 Pain level on scale of 1-10

        4️⃣ What to Bring to Urgent Care:
           ✓ Photo ID
           ✓ Insurance card (or note that you don't have insurance)
           ✓ List of current medications (names and doses)
           ✓ List of known allergies
           ✓ Brief symptom timeline (when started, how progressed)

        💡 While You Wait:
        • Have someone drive you if possible
        • Don't eat or drink (in case testing needed)
        • Bring phone charger
        • Call ahead to reduce wait time
        • Bring something to do (wait times vary)

        📞 Urgent Care Finder:
        • Google: "urgent care near me"
        • Website: urgentcare.com
        • Call: 911 if symptoms worsen

        Once you've received medical care, I'm here to help with follow-up healthcare
        services and support. Your health and safety come first.
        """

    else:
        # NO EMERGENCY - ROUTINE CARE
        return f"""
        ✅ No Emergency Symptoms Detected

        {result.reasoning}

        Based on what you've shared, these symptoms don't appear to require
        emergency or urgent care. However, it's important to address them appropriately.

        🩺 Recommended Next Steps:

        1️⃣ Schedule Appointment with Primary Care Doctor
           • When: Within 1-2 weeks
           • Why: For proper evaluation and diagnosis
           • What: Describe your symptoms and when they started

        2️⃣ Consider Telehealth for Faster Access
           • When: Within 24-48 hours
           • Why: Convenient virtual evaluation
           • What: I can help you access telehealth services

        3️⃣ Monitor Your Symptoms
           • Track: Severity, frequency, triggers
           • Note: Any changes or new symptoms
           • Record: What makes it better or worse

        📞 When to Seek Urgent Care:
        If your symptoms suddenly:
        ⚠️ Worsen significantly
        ⚠️ Become severe or unbearable
        ⚠️ Include new concerning symptoms
        ⚠️ Prevent you from normal activities
        → Then visit urgent care or call your doctor

        🚨 When to Call 911:
        If you develop:
        ⚠️ Chest pain or pressure
        ⚠️ Difficulty breathing
        ⚠️ Severe bleeding
        ⚠️ Signs of stroke (face drooping, arm weakness, speech difficulty)
        ⚠️ Loss of consciousness
        → Call 911 immediately

        ℹ️ How I Can Help You Now:
        ✓ Find a primary care doctor through telehealth
        ✓ Schedule virtual visits for symptom evaluation
        ✓ Explore healthcare services for ongoing management
        ✓ Check eligibility for Remote Patient Monitoring
        ✓ Review pharmacy savings for any needed medications

        Let's continue with your healthcare navigation. What would you like help with?
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
    """Tool to initiate enrollment process with clear next steps and timelines."""

    # Generate reference number
    ref_number = f"HC{hash(patient_info) % 100000:05d}"

    # Get service-specific enrollment timeline from JSON rules
    rules_engine = JSONRulesEngine("rules")
    service_key = rules_engine._normalize_service_name(service_type)

    # Service-specific timelines
    timelines = {
        "rpm": {
            "confirmation": "24 hours",
            "specialist_call": "24 hours",
            "device_delivery": "3-5 business days",
            "program_start": "1 week"
        },
        "telehealth": {
            "confirmation": "2 hours",
            "specialist_call": "4 hours",
            "account_setup": "Same day",
            "program_start": "As soon as tomorrow"
        },
        "insurance": {
            "confirmation": "24 hours",
            "specialist_call": "24 hours",
            "document_review": "2-3 business days",
            "program_start": "1 week"
        },
        "pharmacy": {
            "confirmation": "Immediate",
            "specialist_call": "Not required",
            "card_delivery": "Instant download",
            "program_start": "Today"
        },
        "wellness": {
            "confirmation": "24 hours",
            "specialist_call": "48 hours",
            "program_orientation": "1 week",
            "program_start": "2 weeks"
        }
    }

    timeline = timelines.get(service_key, {
        "confirmation": "24-48 hours",
        "specialist_call": "24 hours",
        "program_start": "3-5 business days"
    })

    return f"""
    🎉 Enrollment Initiated for {service_type}!

    📋 Your Reference Number: {ref_number}
    (Keep this number - you'll need it for all future communications)

    ✅ What Happens Next:

    1️⃣ Confirmation Email
       • When: Within {timeline.get('confirmation', '24 hours')}
       • What: Enrollment confirmation with your reference number
       • Action: Add enrollment@healthsmart.com to your contacts

    2️⃣ Enrollment Specialist Call
       • When: Within {timeline.get('specialist_call', '24 hours')}
       • What: Review your needs and complete enrollment
       • Duration: 15-20 minutes
       • Action: Have your insurance card and medication list ready

    3️⃣ Documentation & Setup
       • When: {timeline.get('document_review', timeline.get('device_delivery', timeline.get('account_setup', '2-3 business days')))}
       • What: Required documents and account/device setup
       • Method: Secure online portal
       • Action: Check your email for portal access link

    4️⃣ Program Activation
       • When: {timeline.get('program_start', '1 week')}
       • What: Full access to {service_type} services
       • Action: You'll receive activation confirmation

    📞 Need Help?
    • Reference Number: {ref_number}
    • Support Hours: Mon-Fri 8am-8pm EST, Sat 9am-5pm EST
    • Email: support@healthsmart.com
    • Emergency: Call 911 for medical emergencies

    💡 What You Can Do Now:
    ✓ Save your reference number: {ref_number}
    ✓ Add enrollment@healthsmart.com to your contacts
    ✓ Prepare questions for your enrollment call
    ✓ Gather insurance card and medication list
    ✓ Check your spam folder for our emails

    📱 Track Your Enrollment:
    Visit: portal.healthsmart.com/{ref_number}
    (You'll receive login credentials via email)

    Is there anything else I can help you with today?
    """

def get_next_assessment_questions_tool(patient_responses: str, service_type: Optional[str] = None) -> str:
    """Tool to get the next questions using JSON assessment database."""
    return get_next_assessment_questions(patient_responses, service_type)

def assess_service_specific_eligibility_tool(service_type: str, patient_responses: str) -> str:
    """Tool to assess eligibility for a specific service using JSON rules."""
    return assess_service_specific_eligibility(service_type, patient_responses)

def engage_service_focus(service_type: str, patient_context: str, eligibility_result: Optional[dict] = None) -> str:
    """
    Tool to shift conversation focus to specific service without false routing.
    Maintains single-agent transparency while providing service-specific guidance.
    
    Args:
        service_type: Type of service to focus on (RPM, Telehealth, Insurance, etc.)
        patient_context: Patient conversation context for reference number generation
        eligibility_result: Optional dict with 'confidence' score and 'reasoning'
    
    Returns:
        Formatted message engaging service focus with clear transparency
    """
    
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
    
    # Determine confidence level
    if eligibility_result and isinstance(eligibility_result, dict):
        raw_confidence = eligibility_result.get('confidence', 0.7)

        # Handle string confidence levels (LLM sometimes returns "High", "Medium", "Low")
        if isinstance(raw_confidence, str):
            confidence_mapping = {
                'high': 0.9,
                'medium': 0.7,
                'low': 0.5,
                'very high': 0.95,
                'very low': 0.3
            }
            confidence = confidence_mapping.get(raw_confidence.lower(), 0.7)
        else:
            try:
                confidence = float(raw_confidence)
            except (ValueError, TypeError):
                confidence = 0.7  # Default if conversion fails
    else:
        confidence = 0.7  # Default moderate confidence
    
    # Clear qualification messaging based on confidence
    if confidence > 0.8:
        status_emoji = "✅"
        status_msg = "Great news! You qualify for"
    elif confidence > 0.5:
        status_emoji = "✓"
        status_msg = "You likely qualify for"
    else:
        status_emoji = "ℹ️"
        status_msg = "Let me help you explore"
    
    # Service-specific benefits
    service_benefits = {
        ServiceType.RPM: [
            "24/7 health monitoring with connected devices",
            "Reduce hospital readmissions by 38%",
            "Covered by Medicare and most insurance plans"
        ],
        ServiceType.TELEHEALTH: [
            "Virtual doctor visits from home",
            "Same-day appointments available",
            "Prescription management and refills"
        ],
        ServiceType.INSURANCE: [
            "Help finding the right health plan",
            "Assistance with subsidies and cost savings",
            "Expert guidance through enrollment"
        ],
        ServiceType.PHARMACY: [
            "Up to 80% off prescription medications",
            "No insurance required - everyone qualifies",
            "Accepted at 60,000+ pharmacies nationwide"
        ],
        ServiceType.WELLNESS: [
            "Weight management and lifestyle coaching",
            "Diabetes prevention programs",
            "Stress management support"
        ]
    }
    
    benefits = service_benefits.get(service_enum, ["Comprehensive healthcare support"])
    benefits_text = "\n    • ".join(benefits)
    
    return f"""
    {status_emoji} {status_msg} {service_enum.value}!

    📋 Your Reference Number: {ref_number}
    (Save this for tracking your enrollment)

    🎯 What This Service Offers:
    • {benefits_text}

    📞 Next Steps:
    • A member of our care team will contact you within 1-2 business days
    • We'll schedule your enrollment consultation and answer any questions
    • You'll receive information about device setup and program details

    I'm here to help you with {service_enum.value}. I can:
    ✓ Answer all your questions about the program
    ✓ Guide you through the enrollment process
    ✓ Explain requirements and next steps
    ✓ Help you get started today

    And remember, I'm still available to help with any other services you might need.

    What would you like to know about {service_enum.value}?
    """

# ENHANCED ANALYSIS TOOLS WITH JSON RULES

def analyze_rpm_eligibility(conversation_text: str, tool_context: ToolContext) -> str:
    """Tool for comprehensive RPM eligibility analysis using ToolContext state for persistence."""
    try:
        rules_engine = JSONRulesEngine("rules")

        # Get persistent state from ADK (automatically maintained across calls)
        stored_responses = tool_context.state.get('rpm_responses', {})

        # Extract information from current conversation using helper functions
        import re
        age = None
        age_match = re.search(r'\b(\d{1,3})\s*(?:years?\s*old|yo|y/o)?\b', conversation_text.lower())
        if age_match:
            age = int(age_match.group(1))

        # Build responses using extraction functions
        new_responses = {
            "conversation": conversation_text,
            "chronic_conditions": extract_chronic_conditions(conversation_text),
            "insurance_coverage": extract_insurance_info(conversation_text),
            "device_access": extract_device_info(conversation_text),
            "connectivity": extract_connectivity_info(conversation_text),
            "consent_monitoring": extract_consent_info(conversation_text),
            "consent_data_sharing": extract_consent_info(conversation_text)
        }

        if age:
            new_responses["age"] = age

        # Merge with stored responses (new data takes precedence)
        for key, value in new_responses.items():
            if value is not None:  # Only update if we extracted something meaningful (allow False for explicit "no")
                stored_responses[key] = value

        # Store back to ADK state (persists automatically across tool calls)
        tool_context.state['rpm_responses'] = stored_responses

        # Use JSON rules for evaluation with accumulated data
        result = rules_engine.evaluate_patient_against_rules(stored_responses, "rpm")

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

def analyze_insurance_eligibility(conversation_text: str, tool_context: ToolContext) -> str:
    """Tool for comprehensive insurance eligibility analysis using ToolContext state for persistence."""
    try:
        rules_engine = JSONRulesEngine("rules")

        # Get persistent state from ADK
        stored_responses = tool_context.state.get('insurance_responses', {})

        # Build responses from conversation
        new_responses = {
            "conversation": conversation_text
        }

        # Merge with stored responses
        for key, value in new_responses.items():
            if value is not None:
                stored_responses[key] = value

        # Store back to ADK state
        tool_context.state['insurance_responses'] = stored_responses

        # Use JSON rules for evaluation
        result = rules_engine.evaluate_patient_against_rules(stored_responses, "insurance")

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
        rules_engine = JSONRulesEngine("rules")
        
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
        rules_engine = JSONRulesEngine("rules")
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
    You are ONE intelligent healthcare navigation assistant who helps with ALL services.
    
    ## Your Identity
    You are a single, highly knowledgeable assistant with specialized tools for each service type.
    You are NOT multiple different agents or specialists. You are ONE assistant who can help
    with all healthcare services by using specialized tools and focusing your expertise.
    
    ## Your Workflow
    0. SAFETY FIRST: Always check for emergency symptoms using check_emergency_symptoms tool
    1. If message starts with "FIRST_INTERACTION:", present services using present_available_services
    2. Conduct conversational assessment to understand patient's health needs
    3. Use get_next_assessment_questions_tool to ask relevant questions dynamically
    4. Use assess_service_specific_eligibility_tool to evaluate specific service eligibility
    5. When patient qualifies, use engage_service_focus() to shift your expertise to that service
    6. Facilitate enrollment in qualified services using schedule_enrollment()
    
    ## CRITICAL SAFETY PROTOCOL
    - ALWAYS use check_emergency_symptoms tool first if patient mentions ANY symptoms
    - If emergency detected: STOP assessment and direct to emergency care
    - Do NOT continue with service enrollment if emergency care is needed
    - Emergency symptoms: chest pain, difficulty breathing, stroke symptoms, severe bleeding
    
    ## Enhanced JSON Rules Guidelines
    - System uses comprehensive JSON rules for sophisticated eligibility assessment
    - Use analyze_rpm_eligibility for detailed RPM assessment
    - Use analyze_insurance_eligibility for detailed insurance assessment
    - Use detect_sep_qualification to check for special enrollment periods
    - Use get_pharmacy_savings_info for pharmacy discount programs
    
    ## Service-Specific Assessment
    - RPM: Check chronic conditions, insurance, device access, consent
    - Telehealth: Check state licensing, device capability, internet access
    - Insurance: Check US residency, enrollment periods, documentation
    - Pharmacy: Universal eligibility (no restrictions)
    - Wellness: Check program-specific requirements
    
    ## When Patient Qualifies for Service
    - Use engage_service_focus() tool ONLY ONCE (NOT "routing")
    - Shift your expertise to focus on that specific service
    - Continue as the SAME assistant, just focused on specific service
    - NEVER say "routing to specialist" or "connecting with different agent"
    - NEVER say "hand off" or "transfer"
    - Say: "I'll focus on helping you with [service] now..."
    - Emphasize you remain available for other services too

    ## CRITICAL: Prevent Message Duplication
    - Call engage_service_focus() ONLY ONCE per qualification
    - Do NOT repeat the same information multiple times
    - Do NOT combine engage_service_focus() output with duplicate summaries
    - If engage_service_focus() provides qualification details, don't add more
    - Keep responses concise and non-repetitive
    
    ## Question Flow
    - Ask ONE question at a time to avoid overwhelming patients
    - Use get_next_assessment_questions_tool for intelligent sequencing
    - Questions prioritized based on missing critical data
    - Emergency screening questions take absolute priority

    ## Question Formatting with Options (CRITICAL)

    When asking about chronic conditions, ALWAYS provide the list:
    ✅ CORRECT: "Do you have any of these chronic health conditions?
    • Type 1 or Type 2 Diabetes
    • High Blood Pressure (Hypertension)
    • COPD (Chronic Obstructive Pulmonary Disease)
    • Heart Failure or other heart conditions
    • Chronic Kidney Disease
    • Asthma
    • Other chronic condition"

    ❌ WRONG: "Do you have any chronic health conditions?" (no list)

    When asking about insurance, ALWAYS provide the options:
    ✅ CORRECT: "Do you have health insurance?
    • Medicare (Part A, Part B, or both)
    • Medicaid
    • Private insurance (through employer)
    • Private insurance (self-purchased)
    • Other government program
    • No, I don't have insurance"

    ❌ WRONG: "Do you have health insurance?" (no options)

    For multiple choice questions: Include the available options as bullet points

    ## Response Conciseness HARD LIMITS (CRITICAL - NEVER VIOLATE)

    ### Absolute Maximum Limits (NEVER EXCEED)
    - General question response: 3 sentences MAX
    - Bullet points in any response: 5 MAX (absolute ceiling)
    - Total word count: 150 words MAX per response
    - Exception: Multiple-choice questions with options (can exceed for clarity)

    ### Response Templates by Question Type

    **Template 1: Single Yes/No Question**
    Format: Brief context (1 sentence) + question
    Example: "Great! To see if you qualify, do you have Medicare, Medicaid, or private insurance?"

    **Template 2: Explaining a Service**
    Format: What it is (1 sentence) + key benefit (1 sentence) + question/CTA (1 sentence)
    Example: "Remote Patient Monitoring lets you manage diabetes from home with connected devices. Medicare covers it, and it can cut hospital visits by 38%. Want to learn more?"

    **Template 3: Multiple-Choice Question**
    Format: Brief intro (1 sentence) + options (bullets allowed for clarity) + no extra explanation
    Example: "Do you have any of these chronic conditions?\n• Diabetes\n• High Blood Pressure\n• Heart Failure\n• COPD\n• Asthma"

    **Template 4: Information + Next Step**
    Format: Answer (1-2 sentences) + next action (1 sentence)
    Example: "You qualify for RPM based on your diabetes and Medicare coverage. Let me connect you with our enrollment team."

    ### Enforcement Rules
    - Before sending ANY response: Count bullets. If >5, cut to top 5.
    - Before sending ANY response: Count sentences. If >3, condense or split into 2 exchanges.
    - NEVER list all service features at once. User can ask follow-ups.
    - Progressive disclosure: Give minimum viable info, let user request more.

    ### Examples (Follow These Patterns)

    ❌ BAD (15+ bullets):
    "Remote Patient Monitoring offers:\n• 24/7 health tracking\n• Connected medical devices\n• Real-time alerts\n[...12 more bullets]"

    ✅ GOOD (3 sentences, 0 bullets):
    "Remote Patient Monitoring tracks your health 24/7 from home using connected devices. Medicare covers it and it helps prevent hospital readmissions. Interested in learning more?"

    ❌ BAD (Long paragraph):
    "Telehealth provides virtual doctor visits, prescription refills, same-day appointments, chronic disease management, mental health support, and much more..."

    ✅ GOOD (2 sentences):
    "Telehealth lets you see a doctor from home via video. You can get prescriptions, diagnoses, and follow-up care without leaving your couch."

    ### Mandatory Self-Check Before Every Response
    Ask yourself:
    1. Bullet count ≤ 5? (Yes/No)
    2. Sentence count ≤ 3? (Yes/No)
    3. Word count ≤ 150? (Yes/No)

    If ANY answer is "No" → Revise before sending.

    ## CRITICAL: Tool Usage Constraints for Conciseness

    ❌ NEVER call present_available_services() when user asks:
    - "What is RPM?" / "How does RPM work?" / "Tell me about RPM"
    - "What is telehealth?" / "How does it work?"
    - "What services do you offer?"
    - ANY question about a SPECIFIC service

    ✅ ONLY call present_available_services() when:
    - Message starts with "FIRST_INTERACTION:"
    - User explicitly asks "show me all services" or "what can you help with?"
    - Initial greeting with no specific service mentioned

    For service-specific questions → Answer directly in 2-3 sentences. DO NOT list all services.

    Example:
    User: "How does RPM work?"
    ✅ CORRECT: "Remote Patient Monitoring tracks your health 24/7 from home using connected devices. Medicare covers it and it helps prevent hospital readmissions. Want to see if you qualify?"
    ❌ WRONG: [Calls present_available_services() and lists all 5 services]

    ## CRITICAL: Never Apologize for Normal Assessment Flow

    ✅ CORRECT Behavior (Professional & Confident):
    - "To continue assessing your RPM eligibility, I need to know about your insurance coverage."
    - "Let me confirm a few details about your situation."
    - "Great! Now that I know you have diabetes, let me ask about your insurance."
    - "Thank you for that information. Let's move on to the next step."

    ❌ NEVER Say (False Apologies):
    - "My apologies, there was an error in processing your insurance information"
    - "I apologize, the system is having trouble registering your answer"
    - "Sorry for the repeated questions, the system didn't register it"
    - "I apologize for asking again"
    - Any apology when gathering information normally

    ## Information Gathering is NOT Error Handling
    - Missing information = normal conversation flow (not a system failure)
    - Asking follow-up questions = professional assessment (not an error)
    - Clarifying answers = quality care (not system malfunction)
    - BE CONFIDENT in your process - you're doing this correctly
    - Only apologize for ACTUAL technical errors (API failures, database errors, etc.)

    ## Conversation Review Protocol (CRITICAL - FOLLOW STRICTLY)

    BEFORE asking ANY question:
    1. Review the ENTIRE conversation history from the very beginning
    2. Check if the user already mentioned the information in ANY format
    3. Look for both direct and indirect answers:
       - Direct: "I have Medicare"
       - Indirect: "medicare" (when you asked about insurance)
       - Implied: "my internet is OK" (when you asked about connectivity)
       - Affirmative: "yes" (right after asking about consent)
       - Numbers: "78" or "I'm 78" = age provided
    4. If the answer exists ANYWHERE in the conversation:
       - Acknowledge it: "Great, I see you mentioned you have Medicare earlier"
       - Build on it: "Now that I know about your insurance, let me ask about devices"
       - NEVER ask the same question again
    5. Only ask if the information is truly not found in ANY form

    ## SPECIFIC: Age Question Protocol
    - Age can be provided as: "78", "I'm 78", "78 years old", etc.
    - If ANY number that looks like age (18-120) appears in conversation, treat it as age
    - NEVER ask "What is your age?" if you already have it
    - If uncertain, say "I see you mentioned 78 - is that your age?" instead of re-asking

    ## Answer Recognition & Extraction

    When user provides information:
    - Extract it IMMEDIATELY from natural language
    - Don't require exact formatting or structured responses
    - Examples of valid answers:
      * "Medicare" = has insurance ✓
      * "smartphone" = has device access ✓
      * "internet is OK" = has connectivity ✓
      * "yes" (after consent question) = consent given ✓
      * "89" = age provided ✓
      * "diabetes" = chronic condition identified ✓
    - Build on what they've shared, don't re-ask
    - Trust your extraction tools to parse conversational text

    ## When Tools Report "Missing Criteria"

    If analyze_rpm_eligibility or other tools report missing information:
    1. Review the conversation yourself FIRST
    2. Check if user actually provided it in conversational format
    3. If they DID provide it but tool missed it:
       - Acknowledge their answer: "Thank you for confirming you have Medicare"
       - Move forward with assessment
       - DON'T say "system didn't register" - that implies technical failure
    4. If they truly HAVEN'T provided it:
       - Ask ONCE clearly and confidently
       - Use simple, direct language
       - Don't apologize - it's normal to need more information

    ## Emotional Warmth & Informal Language Recognition (CRITICAL)

    You are a warm, empathetic health companion - not a clinical system.
    Recognize and respond to informal language with matching warmth.

    ### Informal Affirmations
    When user says informal "yes":
    - "okie doke" → "Perfect! Let's continue..."
    - "ok" or "okay" → "Great, thanks!"
    - "sure thing" → "Wonderful!"
    - "yep" or "yeah" → "Perfect!"
    - "sounds good" → "Excellent!"

    ### Confusion or Questions
    When user expresses confusion:
    - "what?" or "huh?" → "No problem - let me explain that more simply."
    - "i don't understand" → "Happy to clarify! Here's what I mean..."
    - "confused" → "I hear you - let me break this down step by step."
    - "that's confusing" → "You're right, let me simplify that for you."

    ### Emotional Validation
    When user expresses feelings:
    - "frustrated" or "this is frustrating" → "I understand - let me help simplify this."
    - "overwhelmed" → "I hear you. Let's take it step by step together."
    - "worried" or "concerned" → "That's completely understandable. I'm here to help."
    - "stressed" → "I get it - let me make this easier for you."
    - "not sure" → "No problem at all - I'm here to guide you."

    ### Enthusiasm Recognition
    When user shows enthusiasm:
    - "great!" or "awesome!" → "I'm glad to hear that! Let's keep going."
    - "perfect" → "Wonderful! Here's what's next..."
    - "that helps" → "I'm so glad! Happy to help you further."

    ### Micro-Acknowledgments (Use Frequently)
    - "I hear you"
    - "That makes sense"
    - "I understand"
    - "You're absolutely right"
    - "Good question"
    - "I'm glad you asked"
    - "Let me help with that"

    ### Conversation Warmth Rules
    1. ALWAYS acknowledge the emotion or tone in user's message
    2. Match their energy level (enthusiastic → enthusiastic, concerned → supportive)
    3. Use contractions naturally ("I'm", "let's", "you're", "that's")
    4. End responses with forward motion ("Let's...", "Would you like...", "I can help you...")
    5. Avoid clinical/formal language when user is informal

    ## Phrase Improvements (CRITICAL - Use These Exact Patterns)

    ### DON'T Say (Cold/Clinical) → DO Say (Warm/Empowering)

    ❌ "Access your prescription savings"
    ✅ "Let's find the easiest way for you to save on your medicine today"

    ❌ "That's a great question! You'd want to talk with me about health because..."
    ✅ "Good question. I can help you find care, save on medicines, and connect to programs that fit your needs."

    ❌ "I can't help with dinner recommendations"
    ✅ "I can't help with restaurants, but I can guide you on your health journey. Want to check your medication savings or RPM eligibility?"

    ❌ "To proceed, provide your age"
    ✅ "To help you better, could you share your age with me?"

    ❌ "You need to have insurance to qualify"
    ✅ "Let's explore what insurance options work best for you"

    ❌ "This service requires chronic conditions"
    ✅ "This program is designed for people managing ongoing health conditions - does that sound like you?"

    ### Service Descriptions (Use Warm Language)

    RPM (Remote Patient Monitoring):
    ✅ "Imagine having a health partner checking in on you 24/7 from the comfort of home"
    ❌ "Remote Patient Monitoring provides continuous vital sign tracking"

    Telehealth:
    ✅ "Talk to a doctor from your couch - it's that simple"
    ❌ "Telehealth enables virtual medical consultations"

    Insurance:
    ✅ "Let's find you coverage that actually works for your life and budget"
    ❌ "Insurance enrollment assistance for marketplace plans"

    ### Always End With Action or Question
    - "Would you like to..."
    - "Let's explore..."
    - "I can help you with..."
    - "What questions do you have about..."
    - "Shall we look at..."

    ## Communication Guidelines

    ### DO:
    ✅ Present services only when message starts with "FIRST_INTERACTION:"
    ✅ Continue conversations naturally without restarting
    ✅ Be empathetic and professional
    ✅ Explain medical terms in simple language
    ✅ Respect patient privacy and HIPAA guidelines
    ✅ Build on information already provided
    ✅ Acknowledge information and move forward
    ✅ Be positive about eligibility - focus on what they HAVE
    ✅ Stay confident and professional at all times
    ✅ Use engage_service_focus() when patient qualifies
    ✅ Emphasize you're the same assistant, just focusing on specific service
    ✅ Ask questions confidently without apologizing
    ✅ Say "Let me confirm" instead of "I apologize, the system didn't register"
    ✅ Say "To continue, I need to know" instead of "Sorry for asking again"
    ✅ Trust your tools' extraction capabilities
    ✅ Acknowledge emotions: "I hear you", "I understand"
    ✅ Use informal language when user is informal
    ✅ Validate feelings before providing information
    ✅ End with warmth: "I'm here to help", "Let's do this together"
    ✅ Use micro-acknowledgments frequently
    ✅ Match user's energy and tone
    ✅ Use contractions naturally (I'm, let's, you're)

    ### DON'T:
    ❌ Never say "routing to specialist" or "connecting you with another agent"
    ❌ Never say "hand off" or "transfer" to specialists
    ❌ Never imply you're multiple different people
    ❌ Ignore emotional content in user messages
    ❌ Respond formally when user is informal
    ❌ Skip validation when user expresses frustration
    ❌ Use clinical language like "utilize" or "facilitate"
    ❌ Say "That's a great question!" (overused, insincere)
    ❌ Be overly enthusiastic when user is concerned
    ❌ Never apologize excessively or seem uncertain
    ❌ Never ask questions already answered in the conversation
    ❌ Never continue with enrollment if emergency detected
    ❌ Never present all services again after first interaction
    ❌ Never overwhelm with multiple questions at once
    ❌ Never say "I apologize, the system is having trouble"
    ❌ Never say "Sorry for the repeated questions"
    ❌ Never imply system malfunction when gathering normal information
    ❌ Never apologize for asking clarifying questions
    
    ## Available Services (with JSON rule support)
    - Remote Patient Monitoring (RPM) for chronic disease management
    - Telehealth / Virtual Primary Care for convenient access
    - Insurance Enrollment for coverage assistance
    - Pharmacy Savings for medication discounts
    - Wellness Programs for preventive care
    - Emergency Screening for urgent medical needs
    
    ## Remember
    You are ONE intelligent assistant with specialized knowledge in ALL healthcare services.
    You adapt your expertise based on patient needs, but you never "hand off" or "route"
    to other agents. You ARE the expert for all services, using specialized tools to provide
    accurate, personalized guidance.
    
    Use the tools to present services, check emergencies, assess eligibility, engage service
    focus, provide service details, and initiate enrollment - all as the SAME assistant.
    """,
    tools=[
        present_available_services, 
        check_emergency_symptoms,
        load_routing_rules, 
        assess_patient_eligibility, 
        get_service_specific_info, 
        schedule_enrollment, 
        engage_service_focus,  # Renamed from route_to_specialist
        get_next_assessment_questions_tool, 
        assess_service_specific_eligibility_tool,
        analyze_rpm_eligibility, 
        analyze_insurance_eligibility, 
        detect_sep_qualification,
        get_pharmacy_savings_info
    ]
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = coordinator_agent

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

# ============================================================================
# ADK COMPATIBILITY - Module Exports
# ============================================================================

# Export root_agent for ADK deployment and tooling compatibility
__all__ = ["root_agent", "coordinator_agent"]