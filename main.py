#!/usr/bin/env python3
"""
HealthSmart ADK Project - Healthcare Assistant with Multi-Agent Architecture
Initializes and runs the healthcare assistant system.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.service_selector_agent import ServiceSelector
from config import GOOGLE_CLOUD_PROJECT, APP_NAME

async def main():
    """Main entry point for the HealthSmart ADK application."""
    print("🏥 HealthSmart ADK - Healthcare Assistant")
    print("=" * 50)
    print(f"Project: {GOOGLE_CLOUD_PROJECT}")
    print(f"App: {APP_NAME}")
    print("=" * 50)
    
    try:
        # Initialize the service selector
        selector = ServiceSelector()
        print("✅ Service Selector initialized successfully")
        
        # Example service selection interaction
        print("\n📋 Example Service Selection Flow:")
        print("-" * 40)
        
        events = await selector.handle_service_selection(
            user_id="demo_patient_001",
            message="Hi, I need help with my healthcare. What services are available?"
        )
        
        # Display the response
        print("\n🤖 Assistant Response:")
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(f"   {part.text}")
        
        print("\n✅ ADK Project initialized and running successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing ADK project: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you're authenticated with Google Cloud: gcloud auth application-default login")
        print("2. Verify your project has the necessary APIs enabled")
        print("3. Check that the CSV data files are in the correct location")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
