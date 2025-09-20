# Complete App Testing Guide

## Overview
This guide shows how to test the entire HealthSmart Assistant app with all Phase 1 and Phase 2 features.

## 🚀 Quick Start Testing

### 1. Run the Main App
```bash
python app/smart_health_agent.py
```

### 2. Run the Phase 2 Test Suite
```bash
python test_phase2_features.py
```

### 3. Run Interactive Testing
```bash
python test_interactive_app.py
```

## 🧪 Comprehensive Testing Options

### Option 1: Interactive Testing
Run the main app and interact with it manually:

```bash
python app/smart_health_agent.py
```

This will:
- Present the 3 healthcare services
- Ask dynamic questions based on your responses
- Assess eligibility for specific services
- Route you to appropriate specialists

### Option 2: Automated Test Suite
Run the comprehensive test suite:

```bash
python test_phase2_features.py
```

This tests:
- Dynamic question flow
- Service-specific assessment
- Missing data identification
- Question priority filtering
- Integrated conversation flow

### Option 3: Service-Specific Testing
Test individual service flows using the interactive app:

```bash
python test_interactive_app.py
# Choose option 2 for manual interactive test
# Then test different service scenarios
```

## 📋 Test Scenarios

### Scenario 1: Complete RPM Journey
1. Start with service presentation
2. Express interest in RPM
3. Answer questions about age, conditions, insurance
4. Get eligibility assessment
5. Route to RPM specialist

### Scenario 2: Telehealth Consultation
1. Start with service presentation
2. Express interest in Telehealth
3. Answer questions about state, tech comfort, care needs
4. Get eligibility assessment
5. Route to Telehealth specialist

### Scenario 3: Insurance Enrollment
1. Start with service presentation
2. Express interest in Insurance
3. Answer questions about income, current coverage, documentation
4. Get eligibility assessment
5. Route to Insurance specialist

### Scenario 4: Multi-Service Eligibility
1. Start with service presentation
2. Provide comprehensive health information
3. Get assessments for all services
4. See which services qualify
5. Choose preferred service

## 🔍 What to Look For

### Phase 1 Features ✅
- Service presentation works correctly
- CSV rules engine loads and processes data
- Basic agent handoff functions
- Dynamic eligibility assessment

### Phase 2 Features ✅
- Questions adapt based on missing data
- Service-specific assessments are accurate
- Question priority filtering prevents overwhelm
- Missing data identification works
- Integrated conversation flow is smooth

## 🐛 Troubleshooting

### Common Issues
1. **API Key Issues**: Make sure GEMINI_API_KEY is set in config.py
2. **CSV Loading Errors**: Check that CSV files exist in data/ directory
3. **Import Errors**: Ensure you're running from the project root directory

### Debug Mode
Add debug prints to see what's happening:

```python
# In app/smart_health_agent.py, add debug prints
print(f"DEBUG: Processing message: {message}")
print(f"DEBUG: Missing data: {missing_data}")
print(f"DEBUG: Next questions: {next_questions}")
```

## 📊 Expected Results

### Successful Test Run Should Show:
1. ✅ All CSV rules loaded successfully
2. ✅ Service presentation with 3 options
3. ✅ Dynamic questions based on responses
4. ✅ Service-specific eligibility assessments
5. ✅ Proper routing to specialists
6. ✅ Smooth conversation flow

### Performance Metrics:
- Question generation: < 100ms
- Eligibility assessment: < 200ms
- Service routing: < 100ms
- Overall response time: < 2 seconds

## 🎯 Success Criteria

The app is working correctly if:
- [ ] Services are presented clearly
- [ ] Questions adapt to user responses
- [ ] Eligibility assessments are accurate
- [ ] Service routing works properly
- [ ] Conversation flow is natural
- [ ] No errors or crashes occur
- [ ] All Phase 1 and Phase 2 features function

## 📝 Test Results Logging

Keep track of test results:

```bash
# Run tests and save output
python test_phase2_features.py > test_results.log 2>&1

# Check for errors
grep -i error test_results.log

# Check for success indicators
grep -i "✅" test_results.log
```

## 🔄 Continuous Testing

Set up automated testing:

```bash
# Create a test runner script
cat > run_all_tests.sh << 'EOF'
#!/bin/bash
echo "Running HealthSmart Assistant Tests..."
echo "======================================"

echo "1. Testing Phase 2 Features..."
python test_phase2_features.py

echo "2. Testing Main App..."
python app/smart_health_agent.py

echo "3. Testing Interactive App..."
python test_interactive_app.py

echo "All tests completed!"
EOF

chmod +x run_all_tests.sh
./run_all_tests.sh
```

This comprehensive testing approach ensures all features work correctly and provides a smooth user experience.
