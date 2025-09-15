#!/usr/bin/env python3
"""
Interactive HealthSmart Assistant Runner
Run this to test the full healthcare assistant with real conversations
"""

import asyncio
import sys
from app.smart_health_agent import HealthcareAssistant

async def interactive_session():
    """Run an interactive session with the healthcare assistant"""
    
    print("🏥 HealthSmart Assistant - Interactive Session")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'bye' to end the session")
    print("=" * 60)
    
    # Initialize assistant
    assistant = HealthcareAssistant()
    print("✅ Assistant initialized successfully!")
    print()
    
    # Get user ID
    user_id = input("Enter your user ID (or press Enter for 'test_user'): ").strip()
    if not user_id:
        user_id = "test_user"
    
    print(f"\n👋 Hello! I'm your HealthSmart Assistant. How can I help you today?")
    print("(I'll start by showing you our available services)")
    print()
    
    # Create a single session for the entire conversation
    session = await assistant.session_service.create_session(
        app_name="healthcare_assistant", 
        user_id=user_id
    )
    session_id = session.id
    print(f"📱 Session created: {session_id}")
    
    message_count = 0
    
    while True:
        try:
            # Get user input
            user_message = input(f"\nYou: ").strip()
            
            # Check for exit commands
            if user_message.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Thank you for using HealthSmart Assistant! Have a great day!")
                break
            
            if not user_message:
                print("Please enter a message or type 'quit' to exit.")
                continue
            
            message_count += 1
            print(f"\n🤖 Assistant (Message #{message_count}):")
            print("-" * 40)
            
            # Process the message with the same session
            # Add context for first message
            if message_count == 1:
                full_message = f"FIRST_INTERACTION: {user_message}"
            else:
                full_message = user_message
                
            events = await assistant.handle_patient_inquiry(
                user_id=user_id,
                message=full_message,
                session_id=session_id
            )
            
            # Display assistant response
            response_text = ""
            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
            
            if response_text:
                print(response_text)
            else:
                print("I'm processing your request...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

def run_demo_scenarios():
    """Run predefined demo scenarios"""
    
    print("🏥 HealthSmart Assistant - Demo Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "New Patient - Service Inquiry",
            "message": "Hi, I need help with my healthcare. What services are available?"
        },
        {
            "name": "Chronic Condition Patient",
            "message": "I have diabetes and high blood pressure. I was recently in the hospital. What services might help me manage my health better?"
        },
        {
            "name": "Insurance Help Needed",
            "message": "I don't have health insurance and need help finding a plan. What can you do for me?"
        },
        {
            "name": "Telehealth Interest",
            "message": "I need to see a doctor but can't get to the office. Do you have virtual visits?"
        }
    ]
    
    assistant = HealthcareAssistant()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Demo Scenario {i}: {scenario['name']}")
        print("-" * 50)
        print(f"User: {scenario['message']}")
        print("\nAssistant:")
        
        try:
            events = asyncio.run(assistant.handle_patient_inquiry(
                user_id=f"demo_user_{i}",
                message=scenario['message']
            ))
            
            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(part.text)
                            
        except Exception as e:
            print(f"❌ Error in scenario {i}: {e}")
        
        print("\n" + "=" * 60)
        input("Press Enter to continue to next scenario...")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Interactive Session (chat with the assistant)")
    print("2. Demo Scenarios (run predefined test cases)")
    print("3. Quick Test (single message)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(interactive_session())
    elif choice == "2":
        run_demo_scenarios()
    elif choice == "3":
        # Quick test
        assistant = HealthcareAssistant()
        message = input("Enter your message: ")
        print("\n🤖 Assistant Response:")
        print("-" * 40)
        
        events = asyncio.run(assistant.handle_patient_inquiry(
            user_id="quick_test",
            message=message
        ))
        
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(part.text)
    else:
        print("Invalid choice. Running quick test...")
        asyncio.run(interactive_session())
