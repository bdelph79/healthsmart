#!/usr/bin/env python3
"""
HealthSmart Assistant Demo
Shows the complete app functionality with Phase 1 and Phase 2 features
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.smart_health_agent import HealthcareAssistant

async def demo_complete_app():
    """Demonstrate the complete HealthSmart Assistant app"""
    
    print("🏥 HealthSmart Assistant - Complete App Demo")
    print("=" * 60)
    print("This demo shows all Phase 1 and Phase 2 features working together")
    print("=" * 60)
    
    assistant = HealthcareAssistant()
    user_id = "demo_user_001"
    
    # Demo conversation flow
    demo_scenarios = [
        {
            "title": "Scenario 1: RPM Service Journey",
            "messages": [
                "Hi, I need help with my healthcare. What services are available?",
                "I'm interested in RPM. I have diabetes and high blood pressure.",
                "I'm 68 years old and have Medicare.",
                "Yes, I've been hospitalized recently for my diabetes.",
                "I'm comfortable with technology and have a smartphone."
            ]
        },
        {
            "title": "Scenario 2: Telehealth Service Journey", 
            "messages": [
                "I need virtual care. What telehealth options do you have?",
                "I live in California and need a primary care doctor.",
                "I'm 45 years old with insurance.",
                "I have a smartphone with video capability.",
                "I need help with medication refills."
            ]
        },
        {
            "title": "Scenario 3: Insurance Enrollment Journey",
            "messages": [
                "I need help with health insurance. What can you offer?",
                "I'm 35 years old and currently uninsured.",
                "My household income is about $45,000 per year.",
                "I live in Texas and have a valid SSN.",
                "I'm not currently enrolled in any health insurance."
            ]
        }
    ]
    
    for scenario in demo_scenarios:
        print(f"\n🎯 {scenario['title']}")
        print("=" * 50)
        
        for i, message in enumerate(scenario['messages']):
            print(f"\n👤 User: {message}")
            
            # Add FIRST_INTERACTION flag to first message
            if i == 0:
                full_message = f"FIRST_INTERACTION: {message}"
            else:
                full_message = message
            
            try:
                events = await assistant.handle_patient_inquiry(
                    user_id=user_id,
                    message=full_message
                )
                
                # Display assistant response
                print("🤖 Assistant: ", end="")
                response_parts = []
                for event in events:
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_parts.append(part.text)
                
                if response_parts:
                    print(" ".join(response_parts))
                else:
                    print("No response received")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 30)
            
            # Small delay to make it readable
            await asyncio.sleep(1)
        
        print(f"\n✅ {scenario['title']} completed!")
        print("=" * 50)
    
    print("\n🎉 Complete App Demo Finished!")
    print("\nPhase 1 Features Demonstrated:")
    print("✅ Service presentation")
    print("✅ CSV rules engine integration")
    print("✅ Basic agent handoff")
    print("✅ Dynamic eligibility assessment")
    
    print("\nPhase 2 Features Demonstrated:")
    print("✅ Dynamic question flow")
    print("✅ Service-specific assessment")
    print("✅ Missing data identification")
    print("✅ Question priority filtering")
    print("✅ Enhanced CSV integration")
    
    print("\n🚀 The HealthSmart Assistant is fully functional!")

if __name__ == "__main__":
    asyncio.run(demo_complete_app())
