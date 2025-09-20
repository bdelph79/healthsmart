# Testing the Full HealthSmart ADK Application

This guide shows you how to test the complete HealthSmart ADK application with all its features.

## 🚀 Quick Start Testing

### 1. **Basic Full App Test**
```bash
source venv/bin/activate
python3 main.py
```
**What it does:**
- Initializes the complete multi-agent system
- Runs a sample patient interaction
- Tests all ADK agents and tools
- Shows real AI responses

**Expected output:** ✅ Full conversation with AI agents

### 2. **Interactive Testing**
```bash
source venv/bin/activate
python3 test_interactive.py
```
**Features:**
- Test different patient scenarios
- Create custom patient data
- Explore CSV data
- Real-time eligibility assessment

### 3. **Comprehensive Test Suite**
```bash
source venv/bin/activate
python3 test_comprehensive.py
```
**Tests everything:**
- All components
- Performance metrics
- Multiple patient scenarios
- ADK integration

## 🧪 Detailed Testing Approaches

### Test 1: Full Application with Sample Patient
```bash
python3 main.py
```
**Sample interaction:**
- Patient: "I have diabetes and high blood pressure. I was recently in the hospital."
- System: Routes to appropriate services
- Agents: Provide personalized recommendations

### Test 2: Custom Patient Scenarios
```bash
python3 test_interactive.py
```
**Choose from:**
1. Elderly with Multiple Conditions
2. Young Adult - No Conditions  
3. Middle-aged with Diabetes
4. Custom Patient (interactive input)

### Test 3: Rules Engine Testing
```bash
python3 -c "
from app.rules_engine import assess_eligibility_dynamically
import json

# Test different patient types
patients = [
    {
        'name': 'Elderly with chronic conditions',
        'data': {
            'age': 75,
            'chronic_conditions': 'diabetes, hypertension, heart failure',
            'recent_hospitalization': True,
            'has_insurance': True,
            'tech_comfortable': True
        }
    },
    {
        'name': 'Young adult with no conditions',
        'data': {
            'age': 25,
            'chronic_conditions': '',
            'recent_hospitalization': False,
            'has_insurance': False,
            'tech_comfortable': True
        }
    }
]

for patient in patients:
    print(f'\\nTesting: {patient[\"name\"]}')
    result = assess_eligibility_dynamically(json.dumps(patient['data']))
    print(result)
"
```

### Test 4: Agent-Specific Testing
```bash
python3 -c "
from app.smart_health_agent import HealthcareAssistant
import asyncio

async def test_agents():
    assistant = HealthcareAssistant()
    
    # Test different patient inquiries
    inquiries = [
        'I need help with my diabetes management',
        'I want to enroll in health insurance',
        'Can I get virtual care appointments?',
        'I was recently hospitalized and need monitoring'
    ]
    
    for inquiry in inquiries:
        print(f'\\nPatient: {inquiry}')
        events = await assistant.handle_patient_inquiry(
            user_id='test_patient',
            message=inquiry
        )
        
        print('Assistant Response:')
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(f'  {part.text}')

asyncio.run(test_agents())
"
```

## 🔍 What Each Test Validates

### Full App Test (`main.py`)
- ✅ Multi-agent system initialization
- ✅ ADK agent creation and configuration
- ✅ Tool integration (rules engine, CSV data)
- ✅ Real AI conversation flow
- ✅ Patient routing and recommendations
- ✅ Error handling and edge cases

### Interactive Test (`test_interactive.py`)
- ✅ Patient scenario testing
- ✅ Custom data input
- ✅ Real-time eligibility assessment
- ✅ CSV data exploration
- ✅ Rules engine functionality

### Comprehensive Test (`test_comprehensive.py`)
- ✅ All component integration
- ✅ Performance metrics
- ✅ Multiple patient types
- ✅ ADK imports and configuration
- ✅ Error handling

## 📊 Expected Test Results

### Successful Full App Test
```
🏥 HealthSmart ADK - Healthcare Assistant
==================================================
Project: data-management-365112
App: healthcare_assistant
==================================================
✅ Healthcare Assistant initialized successfully

📋 Example Patient Interaction:
------------------------------
🤖 Assistant Response:
   [AI-generated response with service recommendations]

✅ ADK Project initialized and running successfully!
```

### Successful Interactive Test
```
🧪 HealthSmart ADK - Interactive Testing
=============================================

Test Options:
1. Test Patient Scenarios
2. Test Rules Engine Functions  
3. Explore CSV Data
4. Run All Tests
5. Exit

Select an option (1-5): 1

Available test scenarios:
  1. Elderly with Multiple Conditions
  2. Young Adult - No Conditions
  3. Middle-aged with Diabetes
  4. Custom Patient (interactive)

Select a scenario (1-4): 1
```

## 🚨 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **"API key not found" errors**
   ```bash
   # Check .env file
   cat .env
   
   # Or set environment variable
   export GEMINI_API_KEY=your-key-here
   ```

3. **"CSV file not found" errors**
   ```bash
   # Check data directory
   ls -la data/
   
   # Verify file names match exactly
   ```

4. **"Billing disabled" errors**
   - This is expected if using Vertex AI
   - Use Gemini API instead (no billing required)

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH=.
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
exec(open('main.py').read())
"
```

## 🎯 Testing Checklist

Before considering your app ready:

- [ ] `python3 main.py` runs successfully
- [ ] AI agents respond appropriately
- [ ] Patient routing works correctly
- [ ] Rules engine processes data
- [ ] CSV data loads properly
- [ ] Error handling works
- [ ] Performance is acceptable
- [ ] All test suites pass

## 🚀 Advanced Testing

### Load Testing
```bash
# Test with multiple patients
for i in {1..5}; do
  echo "Test $i:"
  python3 main.py
  sleep 2
done
```

### Performance Testing
```bash
# Time the application startup
time python3 main.py

# Monitor memory usage
python3 -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

### Integration Testing
```bash
# Test all components together
python3 test_comprehensive.py && \
python3 test_gemini_api.py && \
python3 main.py
```

## 📝 Test Results Interpretation

- **✅ All tests pass**: App is fully functional
- **⚠️ Warnings**: Usually safe to ignore (e.g., billing warnings)
- **❌ Errors**: Need to be fixed before deployment
- **🔄 Loading**: Normal startup process

Your HealthSmart ADK application is ready for production use! 🎉
