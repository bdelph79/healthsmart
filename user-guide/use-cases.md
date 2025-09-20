# HealthSmart Assistant - Use Cases & Test Scenarios

## 📋 Overview

This document provides comprehensive end-to-end test scenarios for the HealthSmart Assistant application. Each scenario includes the exact messages users should type to test all three healthcare services: Remote Patient Monitoring (RPM), Telehealth, and Insurance Enrollment.

## 🎯 Test Environment Setup

### Prerequisites
- Web app running on `http://localhost:8000`
- Virtual environment activated
- All dependencies installed
- CSV data files loaded

### Starting the Application
```bash
cd /Users/bdelph/Documents/Startup-projects/healthsmart
source venv/bin/activate
python web_app.py
```

## 🩺 Use Case 1: Remote Patient Monitoring (RPM) - Qualified Patient

### Scenario
**Patient Profile**: 65-year-old with diabetes, recent hospitalization, Medicare insurance, comfortable with technology

### Test Messages (Copy & Paste Each Message)

```
1. hello
```

**Expected Response**: Welcome message with 3 services presented

```
2. I'm interested in RPM
```

**Expected Response**: Asks about chronic conditions or age

```
3. I have diabetes and I'm 65 years old
```

**Expected Response**: Asks about recent hospitalization or insurance

```
4. Yes, I was in the hospital 2 months ago
```

**Expected Response**: Asks about insurance coverage

```
5. I have Medicare
```

**Expected Response**: Asks about device access or technology comfort

```
6. Yes, I have a smartphone and Wi-Fi at home
```

**Expected Response**: Asks about data sharing consent

```
7. I'm comfortable sharing my health data
```

**Expected Response**: Confirms eligibility and offers to connect with RPM specialist

```
8. Yes, please connect me
```

**Expected Response**: Routes to RPM specialist with reference number

---

## 🩺 Use Case 2: Remote Patient Monitoring (RPM) - Partially Qualified

### Scenario
**Patient Profile**: 45-year-old with hypertension, no recent hospitalization, private insurance, needs device access

### Test Messages

```
1. Hi, I need help with my health
```

**Expected Response**: Welcome message with 3 services

```
2. I want to learn about remote monitoring
```

**Expected Response**: Asks about chronic conditions

```
3. I have high blood pressure
```

**Expected Response**: Asks about age

```
4. I'm 45 years old
```

**Expected Response**: Asks about insurance coverage (not year of birth)

```
5. I have private insurance through my job
```

**Expected Response**: Asks about device access (not hospitalization)

```
6. I don't have a smartphone, just a basic phone
```

**Expected Response**: Suggests fallback options or alternative services

---

## 💻 Use Case 3: Telehealth - Qualified Patient

### Scenario
**Patient Profile**: 30-year-old in California, needs virtual care, has video-capable device, private insurance

### Test Messages

```
1. I need to see a doctor virtually
```

**Expected Response**: Presents services, asks about location

```
2. I live in California
```

**Expected Response**: Asks about device capability

```
3. I have a laptop with camera
```

**Expected Response**: Asks about type of care needed

```
4. I need a sick visit for a cold
```

**Expected Response**: Asks about insurance

```
5. I have Blue Cross insurance
```

**Expected Response**: Asks about comfort with virtual appointments

```
6. Yes, I'm comfortable with video calls
```

**Expected Response**: Confirms eligibility and offers telehealth specialist

```
7. Yes, connect me please
```

**Expected Response**: Routes to Telehealth specialist

---

## 💻 Use Case 4: Telehealth - State Restriction

### Scenario
**Patient Profile**: Patient in non-licensed state, needs care

### Test Messages

```
1. I need a virtual doctor visit
```

**Expected Response**: Presents services

```
2. I live in Alaska
```

**Expected Response**: Explains state restrictions, suggests alternatives

```
3. What are my options?
```

**Expected Response**: Provides fallback options or in-person care locator

---

## 🛡️ Use Case 5: Insurance Enrollment - Qualified Patient

### Scenario
**Patient Profile**: 28-year-old US resident, no current insurance, within open enrollment, has required documents

### Test Messages

```
1. I need help with health insurance
```

**Expected Response**: Presents services, asks about residency status

```
2. I'm a US citizen with a Social Security Number
```

**Expected Response**: Asks about current insurance status

```
3. I don't have insurance right now
```

**Expected Response**: Asks about enrollment period

```
4. Yes, I'm within the open enrollment period
```

**Expected Response**: Asks about household income

```
5. My household income is $35,000 per year
```

**Expected Response**: Asks about required documents

```
6. Yes, I have my tax returns and SSN card
```

**Expected Response**: Confirms eligibility and offers insurance specialist

```
7. Yes, help me enroll
```

**Expected Response**: Routes to Insurance specialist

---

## 🛡️ Use Case 6: Insurance Enrollment - Special Enrollment Period

### Scenario
**Patient Profile**: Recently lost job, needs insurance, qualifies for SEP

### Test Messages

```
1. I lost my job and need health insurance
```

**Expected Response**: Presents services

```
2. I'm a US resident
```

**Expected Response**: Asks about current insurance

```
3. I just lost my job-based insurance
```

**Expected Response**: Asks about qualifying life event

```
4. Yes, losing job coverage qualifies me
```

**Expected Response**: Asks about income and documents

```
5. My income is $40,000 and I have my documents
```

**Expected Response**: Confirms SEP eligibility and offers specialist

---

## 🚫 Use Case 7: Multiple Service Interest

### Scenario
**Patient Profile**: Patient interested in multiple services

### Test Messages

```
1. I need help with both RPM and telehealth
```

**Expected Response**: Asks which service to focus on first

```
2. Let's start with RPM
```

**Expected Response**: Proceeds with RPM assessment

```
3. I have diabetes and I'm 60
```

**Expected Response**: Continues RPM assessment

```
4. Actually, I want to switch to telehealth
```

**Expected Response**: Switches to telehealth assessment

---

## 🔄 Use Case 8: Conversation Continuity Test

### Scenario
**Patient Profile**: Test session management and context retention

### Test Messages

```
1. Hello, I'm interested in healthcare services
```

**Expected Response**: Presents services

```
2. I have diabetes
```

**Expected Response**: Asks about age (should remember diabetes)

```
3. I'm 70 years old
```

**Expected Response**: Asks about insurance (should remember age and diabetes)

```
4. I have Medicare
```

**Expected Response**: Asks about device access (should remember all previous info)

---

## 🧪 Use Case 9: Edge Cases & Error Handling

### Scenario
**Patient Profile**: Test various edge cases

### Test Messages

```
1. I don't know what I need
```

**Expected Response**: Asks clarifying questions about health needs

```
2. I'm not sure about my insurance
```

**Expected Response**: Asks specific questions to determine insurance status

```
3. Can you help me with something else?
```

**Expected Response**: Offers other services or general assistance

```
4. I'm not comfortable with this
```

**Expected Response**: Respects privacy, offers alternatives

---

## 📊 Use Case 10: Complete RPM Journey

### Scenario
**Patient Profile**: Full RPM enrollment process

### Test Messages

```
1. I need help managing my diabetes
```

**Expected Response**: Presents services, focuses on RPM

```
2. Yes, I'm interested in RPM
```

**Expected Response**: Asks about chronic conditions

```
3. I have type 2 diabetes and high blood pressure
```

**Expected Response**: Asks about age

```
4. I'm 58 years old
```

**Expected Response**: Asks about recent hospitalization

```
5. I was hospitalized 3 months ago for diabetes complications
```

**Expected Response**: Asks about insurance

```
6. I have Medicare Part A and B
```

**Expected Response**: Asks about device access

```
7. I have an iPhone and home Wi-Fi
```

**Expected Response**: Asks about data sharing consent

```
8. Yes, I'm comfortable with remote monitoring
```

**Expected Response**: Confirms full eligibility

```
9. Yes, please enroll me
```

**Expected Response**: Initiates enrollment process with reference number

```
10. What happens next?
```

**Expected Response**: Explains next steps and timeline

---

## 🎯 Testing Checklist

### For Each Use Case, Verify:

- [ ] **Service Presentation**: Correctly presents 3 services initially
- [ ] **Dynamic Questions**: Asks relevant questions based on responses
- [ ] **Context Retention**: Remembers previous answers
- [ ] **Eligibility Assessment**: Correctly evaluates qualification
- [ ] **Specialist Routing**: Routes to appropriate specialist when qualified
- [ ] **Fallback Options**: Offers alternatives when not qualified
- [ ] **Reference Numbers**: Generates unique reference numbers
- [ ] **Professional Tone**: Maintains empathetic, professional communication
- [ ] **HIPAA Compliance**: Respects privacy and data handling
- [ ] **Error Handling**: Gracefully handles unexpected responses

### Performance Metrics:

- [ ] **Response Time**: < 3 seconds per interaction
- [ ] **Session Continuity**: Maintains context across multiple messages
- [ ] **Question Flow**: Asks 1 question at a time
- [ ] **Logical Progression**: Questions build on previous answers
- [ ] **No Repetition**: Doesn't ask the same question twice

## 🔧 Troubleshooting

### Common Issues:

1. **Session Reset**: If conversation context is lost, refresh the page
2. **Slow Responses**: Check if virtual environment is activated
3. **Error Messages**: Check terminal for detailed error logs
4. **Missing Data**: Ensure CSV files are in the data/ directory

### Debug Commands:

```bash
# Check if app is running
curl http://localhost:8000/api/health

# Check features
curl http://localhost:8000/api/features

# View logs
tail -f /path/to/logfile
```

## 📝 Notes

- **Copy & Paste**: Use the exact messages provided for consistent testing
- **Wait for Response**: Allow time for AI processing between messages
- **Clear Browser**: Refresh browser between different use cases
- **Test All Paths**: Try both qualified and non-qualified scenarios
- **Document Issues**: Note any unexpected responses or errors

---

**Happy Testing! 🚀**

These use cases cover all major scenarios and edge cases for comprehensive testing of the HealthSmart Assistant application.
