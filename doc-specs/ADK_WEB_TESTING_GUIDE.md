# ADK Web Testing Guide

## 🌐 **Testing HealthSmart Assistant with ADK Web**

### **Quick Start**

**1. Start the Web Interface:**
```bash
python start_web.py
```

**2. Open in Browser:**
- **Main Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### **🎯 What You Can Test**

#### **1. Interactive Chat Interface**
- Real-time conversation with the healthcare assistant
- Service presentation and selection
- Dynamic question flow (1 question at a time)
- Service-specific assessments
- Eligibility evaluation

#### **2. API Endpoints**
- `/chat` - Send messages to the assistant
- `/api/health` - Check system health
- `/api/features` - View available features
- `/api/conversations/{session_id}` - Get conversation history

### **🧪 Testing Scenarios**

#### **Scenario 1: RPM Service Journey**
1. Open http://localhost:8000
2. Type: "Hi, I need help with my healthcare. What services are available?"
3. Type: "I'm interested in RPM. I have diabetes and high blood pressure."
4. Type: "I'm 68 years old and have Medicare."
5. Type: "Yes, I've been hospitalized recently for my diabetes."
6. Type: "I'm comfortable with technology and have a smartphone."

**Expected Results:**
- ✅ Services presented clearly
- ✅ Dynamic questions (1 at a time)
- ✅ Service-specific assessment
- ✅ Eligibility evaluation
- ✅ Specialist routing

#### **Scenario 2: Telehealth Service Journey**
1. Type: "I need virtual care. What telehealth options do you have?"
2. Type: "I live in California and need a primary care doctor."
3. Type: "I have a smartphone with video capability."
4. Type: "I need help with medication refills."

#### **Scenario 3: Insurance Enrollment Journey**
1. Type: "I need help with health insurance. What can you offer?"
2. Type: "My household income is about $45,000 per year."
3. Type: "I'm currently uninsured."
4. Type: "I live in Texas and have a valid SSN."

### **🔧 API Testing**

#### **Using curl:**
```bash
# Send a chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, I need help with my healthcare", "user_id": "test_user"}'

# Check health
curl "http://localhost:8000/api/health"

# Get features
curl "http://localhost:8000/api/features"
```

#### **Using Python:**
```python
import requests

# Send message
response = requests.post("http://localhost:8000/chat", json={
    "message": "I need help with RPM",
    "user_id": "test_user"
})
print(response.json())

# Check health
health = requests.get("http://localhost:8000/api/health")
print(health.json())
```

### **📊 Features Demonstrated**

#### **Phase 1 Features:**
- ✅ **Service Presentation** - 3 healthcare services clearly displayed
- ✅ **CSV Rules Integration** - Dynamic rule loading and processing
- ✅ **Dynamic Eligibility Assessment** - Uses CSV rules for evaluation
- ✅ **Basic Agent Handoff** - Routes users to appropriate specialists

#### **Phase 2 Features:**
- ✅ **Dynamic Question Flow** - Asks 1 question at a time based on missing data
- ✅ **Service-Specific Assessment** - Tailored evaluation for each service
- ✅ **Missing Data Identification** - Smart gap detection system
- ✅ **Question Priority Filtering** - Prevents user overwhelm
- ✅ **Enhanced CSV Integration** - Intelligent rule processing

### **🎨 Web Interface Features**

#### **User Interface:**
- **Modern Design** - Clean, professional healthcare interface
- **Real-time Chat** - Instant responses from the assistant
- **Session Management** - Maintains conversation context
- **Responsive Design** - Works on desktop and mobile
- **Loading Indicators** - Shows when assistant is thinking

#### **Technical Features:**
- **FastAPI Backend** - High-performance async web framework
- **RESTful API** - Standard HTTP endpoints
- **Session Storage** - In-memory conversation history
- **Error Handling** - Graceful error management
- **Health Monitoring** - System health checks

### **🔍 Debugging & Troubleshooting**

#### **Common Issues:**

**1. Port Already in Use:**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

**2. Module Import Errors:**
```bash
# Ensure you're in the project root
cd /Users/bdelph/Documents/Startup-projects/healthsmart
python start_web.py
```

**3. API Key Issues:**
- Check that GEMINI_API_KEY is set in config.py
- Verify API key is valid and has quota remaining

**4. CSV Loading Errors:**
- Ensure CSV files exist in data/ directory
- Check file permissions

#### **Debug Mode:**
```bash
# Run with debug logging
PYTHONPATH=/Users/bdelph/Documents/Startup-projects/healthsmart python web_app.py
```

### **📈 Performance Testing**

#### **Load Testing:**
```bash
# Install Apache Bench
brew install httpd

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/api/health
```

#### **Response Time Testing:**
- **Chat Response**: < 2 seconds
- **Health Check**: < 100ms
- **API Endpoints**: < 500ms

### **🚀 Production Deployment**

#### **For Production:**
1. **Use Gunicorn** instead of Uvicorn
2. **Add Database** for conversation storage
3. **Implement Authentication** for user management
4. **Add Logging** for monitoring
5. **Use HTTPS** for security

#### **Docker Deployment:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "web_app.py"]
```

### **📋 Testing Checklist**

- [ ] Web interface loads correctly
- [ ] Chat functionality works
- [ ] Service presentation displays properly
- [ ] Dynamic questions work (1 at a time)
- [ ] Service-specific assessments function
- [ ] API endpoints respond correctly
- [ ] Error handling works gracefully
- [ ] Session management maintains context
- [ ] Mobile responsiveness works
- [ ] Performance meets requirements

### **🎉 Success Criteria**

The ADK Web testing is successful if:
- ✅ Web interface loads without errors
- ✅ Chat conversations flow naturally
- ✅ All Phase 1 and Phase 2 features work
- ✅ API endpoints respond correctly
- ✅ Error handling is graceful
- ✅ Performance is acceptable
- ✅ User experience is smooth and intuitive

## 🚀 **Ready to Test!**

Run `python start_web.py` and open http://localhost:8000 to start testing the HealthSmart Assistant with ADK Web!
