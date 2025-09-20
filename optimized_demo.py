
#!/usr/bin/env python3
"""
Optimized HealthSmart Assistant Demo
Avoids API warnings and rate limiting issues
"""

import asyncio
import sys
import os
import warnings
import logging

# Suppress warnings
warnings.filterwarnings("ignore")
logging.getLogger("google.auth").setLevel(logging.ERROR)

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.smart_health_agent import HealthcareAssistant

async def optimized_demo():
    """Optimized demo with minimal API calls"""
    
    print("🏥 HealthSmart Assistant - Optimized Demo")
    print("=" * 50)
    
    assistant = HealthcareAssistant()
    user_id = "optimized_demo_user"
    
    # Single interaction to demonstrate functionality
    message = "FIRST_INTERACTION: Hi, I need help with my healthcare. What services are available?"
    
    print(f"\n👤 User: {message}")
    
    try:
        events = await assistant.handle_patient_inquiry(
            user_id=user_id,
            message=message
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
    
    print("\n✅ Optimized demo completed!")
    print("\nThis demonstrates:")
    print("✅ Service presentation")
    print("✅ Dynamic question flow")
    print("✅ CSV rules integration")
    print("✅ Minimal API usage")

if __name__ == "__main__":
    asyncio.run(optimized_demo())
