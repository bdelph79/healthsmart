# HealthSmart ADK Project - Testing Guide

This guide explains how to test the HealthSmart ADK project at different levels.

## 🧪 Testing Approaches

### 1. **Basic Initialization Test**
```bash
source venv/bin/activate
python3 test_init.py
```
**What it tests:**
- Python dependencies
- Configuration loading
- CSV file access
- Rules engine initialization
- Agent structure

**Expected output:** 5/5 tests passed ✅

### 2. **Comprehensive Test Suite**
```bash
source venv/bin/activate
python3 test_comprehensive.py
```
**What it tests:**
- All basic functionality
- Rules engine with multiple patient scenarios
- Performance testing
- ADK imports
- Full system initialization

**Expected output:** 8/8 tests passed ✅

### 3. **Interactive Testing**
```bash
source venv/bin/activate
python3 test_interactive.py
```
**What it provides:**
- Interactive patient scenario testing
- Custom patient data input
- CSV data exploration
- Rules engine function testing

**Features:**
- Pre-built patient scenarios
- Custom patient creation
- Real-time eligibility assessment
- CSV data browsing

### 4. **Full System Test (Requires Billing)**
```bash
source venv/bin/activate
python3 main.py
```
**What it tests:**
- Complete multi-agent system
- Real ADK agent interactions
- End-to-end patient flow

**Requirements:** Billing enabled on Google Cloud project

## 🔧 Individual Component Tests

### Test Rules Engine Only
```python
from app.rules_engine import assess_eligibility_dynamically
import json

# Test patient data
patient = {
    "age": 67,
    "chronic_conditions": "diabetes, hypertension",
    "recent_hospitalization": True,
    "has_insurance": True
}

# Run assessment
result = assess_eligibility_dynamically(json.dumps(patient))
print(result)
```

### Test CSV Data Loading
```python
from config import CSV_PATHS
import pandas as pd

# Load and inspect data
for name, path in CSV_PATHS.items():
    df = pd.read_csv(path)
    print(f"{name}: {len(df)} rows, {len(df.columns)} columns")
    print(df.head())
```

### Test Agent Structure
```python
from app.smart_health_agent import HealthcareAssistant, ServiceType

# Check service types
print([s.value for s in ServiceType])

# Initialize assistant (without running)
assistant = HealthcareAssistant()
print("✅ Assistant initialized")
```

## 📊 Test Scenarios

### Scenario 1: Elderly with Multiple Conditions
```json
{
    "age": 75,
    "chronic_conditions": "diabetes, hypertension, heart failure",
    "recent_hospitalization": True,
    "has_insurance": True,
    "tech_comfortable": True
}
```
**Expected:** High RPM eligibility, moderate telehealth eligibility

### Scenario 2: Young Adult - No Conditions
```json
{
    "age": 25,
    "chronic_conditions": "",
    "recent_hospitalization": False,
    "has_insurance": False,
    "tech_comfortable": True
}
```
**Expected:** High insurance eligibility, low clinical service eligibility

### Scenario 3: Middle-aged with Diabetes
```json
{
    "age": 45,
    "chronic_conditions": "diabetes",
    "recent_hospitalization": False,
    "has_insurance": True,
    "tech_comfortable": False
}
```
**Expected:** Moderate RPM eligibility, high telehealth eligibility

## 🚨 Troubleshooting Tests

### Common Issues and Solutions

1. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

2. **CSV File Not Found**
   ```bash
   # Check file paths
   ls -la data/
   
   # Verify file names match exactly
   ```

3. **Google Cloud Authentication**
   ```bash
   # Re-authenticate
   gcloud auth application-default login
   
   # Check project
   gcloud config get-value project
   ```

4. **Billing Not Enabled**
   ```
   Error: BILLING_DISABLED
   Solution: Enable billing on Google Cloud project
   ```

## 📈 Performance Testing

### Load Testing
```python
import time
from app.rules_engine import assess_eligibility_dynamically
import json

# Test with multiple patients
patients = [
    {"age": 65, "chronic_conditions": "diabetes"},
    {"age": 30, "chronic_conditions": ""},
    {"age": 55, "chronic_conditions": "hypertension"}
]

start_time = time.time()
for patient in patients:
    assess_eligibility_dynamically(json.dumps(patient))
end_time = time.time()

print(f"Processed {len(patients)} patients in {end_time - start_time:.2f} seconds")
```

### Memory Testing
```python
import psutil
import os

# Check memory usage
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {memory_mb:.2f} MB")
```

## ✅ Test Checklist

Before deploying or sharing your project:

- [ ] All basic tests pass (5/5)
- [ ] Comprehensive tests pass (8/8)
- [ ] Interactive tests work
- [ ] CSV data loads correctly
- [ ] Rules engine processes patients
- [ ] Agent structure is valid
- [ ] ADK imports work
- [ ] Performance is acceptable
- [ ] Error handling works
- [ ] Documentation is complete

## 🎯 Quick Test Commands

```bash
# Quick health check
python3 test_init.py

# Full test suite
python3 test_comprehensive.py

# Interactive testing
python3 test_interactive.py

# Full system (requires billing)
python3 main.py
```

## 📝 Test Results Interpretation

- **✅ All tests passed**: Project is fully functional
- **⚠️ Billing warning**: Expected, enable billing for full functionality
- **❌ Import errors**: Check virtual environment and dependencies
- **❌ CSV errors**: Check file paths and data format
- **❌ Agent errors**: Check ADK installation and configuration
