#!/usr/bin/env python3
"""
Demo script for the new service selection and routing flow
Shows the complete user journey without requiring API calls
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.service_selector_agent import AVAILABLE_SERVICES, present_services, get_service_details, ask_service_questions, assess_service_eligibility, route_to_service
import json

def demo_service_presentation():
    """Demo the service presentation."""
    print("🏥 HealthSmart ADK - Service Selection Flow Demo")
    print("=" * 55)
    
    print("\n1. 📋 Presenting Available Services")
    print("-" * 35)
    print("User: Hi, I need help with my healthcare. What services are available?")
    print("\nAssistant Response:")
    print(present_services())

def demo_service_selection():
    """Demo service selection and details."""
    print("\n2. 🎯 Service Selection and Details")
    print("-" * 35)
    
    # Demo RPM selection
    print("User: I'm interested in RPM - I have diabetes and high blood pressure")
    print("\nAssistant Response:")
    print(get_service_details("rpm"))
    
    print("\n" + "="*50)
    
    # Demo Telehealth selection
    print("\nUser: I want to learn about telehealth services")
    print("\nAssistant Response:")
    print(get_service_details("telehealth"))

def demo_question_flow():
    """Demo the question asking flow."""
    print("\n3. ❓ Service-Specific Question Flow")
    print("-" * 35)
    
    # Demo RPM questions
    print("User: Yes, I want to proceed with RPM")
    print("\nAssistant Response:")
    print(ask_service_questions("rpm", "{}"))
    
    print("\n" + "-"*30)
    
    # Demo with some answers
    patient_data = {
        "age": 67,
        "chronic_conditions": "diabetes, hypertension",
        "recent_hospitalization": True,
        "has_insurance": True,
        "tech_comfortable": True
    }
    
    print("User: I have diabetes and hypertension. I was hospitalized 3 months ago. I have insurance and I'm comfortable with technology.")
    print("\nAssistant Response:")
    print(ask_service_questions("rpm", json.dumps(patient_data)))

def demo_eligibility_assessment():
    """Demo eligibility assessment."""
    print("\n4. 🔍 Eligibility Assessment")
    print("-" * 30)
    
    patient_data = {
        "age": 67,
        "chronic_conditions": "diabetes, hypertension",
        "recent_hospitalization": True,
        "has_insurance": True,
        "tech_comfortable": True
    }
    
    print("User: [Provides all required information]")
    print("\nAssistant Response:")
    print(assess_service_eligibility("rpm", json.dumps(patient_data)))

def demo_routing():
    """Demo service routing."""
    print("\n5. 🎯 Service Routing")
    print("-" * 20)
    
    patient_data = {
        "age": 67,
        "chronic_conditions": "diabetes, hypertension",
        "recent_hospitalization": True,
        "has_insurance": True,
        "tech_comfortable": True
    }
    
    print("User: [Completes all questions]")
    print("\nAssistant Response:")
    print(route_to_service("rpm", json.dumps(patient_data)))

def demo_different_services():
    """Demo different service flows."""
    print("\n6. 🔄 Different Service Flows")
    print("-" * 30)
    
    services = ["rpm", "telehealth", "insurance"]
    
    for service_id in services:
        service = AVAILABLE_SERVICES[service_id]
        print(f"\n📋 {service.name} Flow:")
        print("-" * 25)
        
        # Show service details
        print("1. Service Details:")
        details = get_service_details(service_id)
        print(details[:200] + "...")
        
        # Show questions
        print("\n2. Questions Asked:")
        questions = ask_service_questions(service_id, "{}")
        print(questions[:200] + "...")

def main():
    """Main demo function."""
    print("🎬 This demo shows the complete service selection and routing flow")
    print("   without requiring API calls. The actual implementation uses")
    print("   AI agents to provide dynamic, conversational responses.")
    print()
    
    # Run all demos
    demo_service_presentation()
    demo_service_selection()
    demo_question_flow()
    demo_eligibility_assessment()
    demo_routing()
    demo_different_services()
    
    print("\n🎉 Demo Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("  ✅ Service presentation with clear options")
    print("  ✅ Detailed service information and benefits")
    print("  ✅ Service-specific question asking")
    print("  ✅ Eligibility assessment based on responses")
    print("  ✅ Routing to appropriate service specialists")
    print("  ✅ Support for multiple service types")
    print("\n🚀 To test with real AI agents, run:")
    print("   python3 main.py")
    print("   (Note: Requires API key and may have rate limits)")

if __name__ == "__main__":
    main()
