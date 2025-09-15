# Gemini API Integration Guide

This guide explains how to use the Gemini API with your HealthSmart ADK project instead of Vertex AI.

## 🚀 Benefits of Using Gemini API

- ✅ **No billing required** - Free tier available
- ✅ **Faster setup** - No Google Cloud project configuration needed
- ✅ **Direct API access** - Works immediately
- ✅ **Same functionality** - Full ADK support

## 🔑 Setup Instructions

### 1. Get Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Configure Environment Variables

**Option A: Using .env file (Recommended)**
```bash
# Copy the example file
cp env.example .env

# Edit .env file and add your API key
GEMINI_API_KEY=your-actual-api-key-here
```

**Option B: Using environment variables**
```bash
export GEMINI_API_KEY=your-actual-api-key-here
```

### 3. Test the Configuration

```bash
source venv/bin/activate
python3 test_gemini_api.py
```

## 📋 Configuration Details

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key (REQUIRED) | None |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | Auto-detected |
| `GOOGLE_CLOUD_LOCATION` | Google Cloud region | us-central1 |

### Configuration

The application **only uses GEMINI_API_KEY** for all AI operations:
- Automatically sets `GOOGLE_GENAI_USE_VERTEXAI=False`
- Uses Gemini API exclusively
- No billing required
- Works with free tier

## 🧪 Testing

### Test Gemini API Configuration
```bash
python3 test_gemini_api.py
```

### Test Full Application
```bash
python3 main.py
```

### Test Comprehensive Suite
```bash
python3 test_comprehensive.py
```

## 🔧 Usage Examples

### Basic Usage
```python
from config import GEMINI_API_KEY
import google.generativeai as genai

# Configure API
genai.configure(api_key=GEMINI_API_KEY)

# Create model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Generate content
response = model.generate_content("Hello, world!")
print(response.text)
```

### ADK Agent Usage
```python
from google.adk.agents import Agent

# Create agent (automatically uses Gemini API)
agent = Agent(
    name="MyAgent",
    model="gemini-2.0-flash-exp",
    instruction="You are a helpful assistant."
)
```

## 🚨 Troubleshooting

### Common Issues

1. **"No module named 'google.generativeai'"**
   ```bash
   pip install google-generativeai
   ```

2. **"GEMINI_API_KEY not found"**
   - Check your .env file exists
   - Verify the API key is set correctly
   - Run: `python3 test_gemini_api.py`

3. **"API key invalid"**
   - Verify the API key is correct
   - Check if the key has expired
   - Generate a new key from Google AI Studio

4. **"Quota exceeded"**
   - Check your API usage limits
   - Wait for quota reset
   - Consider upgrading your plan

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 API Limits

### Free Tier Limits
- 15 requests per minute
- 1 million tokens per day
- Rate limits apply

### Paid Tier
- Higher rate limits
- More tokens per day
- Priority support

## 🔄 Switching Between APIs

### Use Gemini API (Default with key)
```bash
# Set in .env file
GEMINI_API_KEY=your-key-here
```

### Use Vertex AI (Requires billing)
```bash
# Remove or comment out GEMINI_API_KEY
# GOOGLE_GENAI_USE_VERTEXAI=True
```

## 📝 Example .env File

```env
# HealthSmart ADK Project Environment Variables

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Gemini API Configuration (Recommended)
GEMINI_API_KEY=your-gemini-api-key-here

# Alternative: Use Vertex AI (requires billing)
# GOOGLE_GENAI_USE_VERTEXAI=True
```

## 🎯 Best Practices

1. **Keep API keys secure** - Never commit them to version control
2. **Use .env files** - For local development
3. **Monitor usage** - Check your API quotas regularly
4. **Test thoroughly** - Use the test scripts provided
5. **Handle errors** - Implement proper error handling

## 🚀 Quick Start

1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Copy `env.example` to `.env`
3. Add your API key to `.env`
4. Run `python3 test_gemini_api.py`
5. Run `python3 main.py`

That's it! Your HealthSmart ADK project is now using the Gemini API. 🎉
