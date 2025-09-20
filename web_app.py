#!/usr/bin/env python3
"""
HealthSmart Assistant - Web Interface for ADK Testing
FastAPI-based web application for testing the healthcare assistant
"""

import asyncio
import json
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from app.smart_health_agent import HealthcareAssistant
from config import GOOGLE_CLOUD_PROJECT, APP_NAME

# Initialize FastAPI app
app = FastAPI(
    title="HealthSmart Assistant",
    description="Healthcare Assistant with Multi-Agent Architecture",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the healthcare assistant
assistant = HealthcareAssistant()

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str
    user_id: str = "web_user"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    features_used: List[str]

# Store conversation history (in production, use a proper database)
conversation_history: Dict[str, List[Dict]] = {}

# Simple rate limiting - track last request time
last_request_time = 0
MIN_REQUEST_INTERVAL = 6  # 6 seconds between requests (10 requests per minute = 6 seconds)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with chat interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HealthSmart Assistant</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
            }
            .chat-container {
                height: 500px;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            .message {
                margin: 15px 0;
                padding: 15px;
                border-radius: 10px;
                max-width: 80%;
            }
            .user-message {
                background: #007bff;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .assistant-message {
                background: #e9ecef;
                color: #333;
                margin-right: auto;
            }
            .input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #dee2e6;
                display: flex;
                gap: 10px;
            }
            .input-field {
                flex: 1;
                padding: 12px;
                border: 2px solid #dee2e6;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            .input-field:focus {
                border-color: #007bff;
            }
            .send-button {
                padding: 12px 25px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }
            .send-button:hover {
                background: #0056b3;
            }
            .features {
                background: #e3f2fd;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #2196F3;
            }
            .loading {
                display: none;
                text-align: center;
                color: #666;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 HealthSmart Assistant</h1>
                <p>AI-Powered Healthcare Service Navigation</p>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="assistant-message message">
                    <strong>HealthSmart Assistant:</strong><br>
                    Welcome! I can help you with these healthcare services:<br><br>
                    🩺 <strong>Remote Patient Monitoring (RPM)</strong> - Monitor chronic conditions from home<br>
                    💻 <strong>Telehealth / Virtual Primary Care</strong> - Virtual doctor visits<br>
                    🛡️ <strong>Insurance Enrollment</strong> - Help finding health insurance plans<br><br>
                    How can I help you today? Please tell me about your health needs.
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" class="input-field" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()" class="send-button">Send</button>
            </div>
            
            <div class="loading" id="loading">Assistant is thinking...</div>
        </div>

        <script>
            let sessionId = 'session_' + Date.now();
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message to chat
                addMessage(message, 'user');
                input.value = '';
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            user_id: 'web_user',
                            session_id: sessionId
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Add assistant response to chat
                    addMessage(data.response, 'assistant');
                    
                    // Update session ID if provided
                    if (data.session_id) {
                        sessionId = data.session_id;
                    }
                    
                } catch (error) {
                    addMessage('Sorry, there was an error processing your request.', 'assistant');
                    console.error('Error:', error);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }
            
            function addMessage(text, sender) {
                const chatContainer = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                
                if (sender === 'assistant') {
                    messageDiv.innerHTML = `<strong>HealthSmart Assistant:</strong><br>${text}`;
                } else {
                    messageDiv.innerHTML = `<strong>You:</strong><br>${text}`;
                }
                
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Chat endpoint for the healthcare assistant"""
    global last_request_time
    
    try:
        # Rate limiting check
        current_time = time.time()
        time_since_last_request = current_time - last_request_time
        
        if time_since_last_request < MIN_REQUEST_INTERVAL:
            wait_time = MIN_REQUEST_INTERVAL - time_since_last_request
            print(f"⏳ Rate limiting: waiting {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)
        
        last_request_time = time.time()
        
        print(f"📨 Received message: {chat_message.message}")
        print(f"👤 User ID: {chat_message.user_id}")
        print(f"🆔 Session ID: {chat_message.session_id}")
        
        # Add FIRST_INTERACTION flag if it's the first message
        if not chat_message.session_id or chat_message.session_id not in conversation_history:
            full_message = f"FIRST_INTERACTION: {chat_message.message}"
            print("🆕 First interaction detected")
        else:
            full_message = chat_message.message
            print("💬 Continuing conversation")
        
        # Get response from healthcare assistant
        print("🤖 Calling healthcare assistant...")
        result = await assistant.handle_patient_inquiry(
            user_id=chat_message.user_id,
            message=full_message,
            session_id=chat_message.session_id
        )
        
        # Handle the tuple returned by handle_patient_inquiry
        events, session_id = result
        print(f"✅ Received {len(events)} events from assistant")
        
        # Extract response text
        response_text = ""
        for event in events:
            if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text + " "
            elif hasattr(event, 'text'):
                response_text += event.text + " "
        
        # Clean up response
        response_text = response_text.strip()
        if not response_text:
            response_text = "I'm sorry, I didn't understand that. Could you please rephrase your question?"
        
        print(f"💬 Response: {response_text[:100]}...")
        
        # Store conversation history
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        conversation_history[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": chat_message.message,
            "assistant_response": response_text
        })
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            features_used=["dynamic_questions", "service_assessment", "csv_rules"]
        )
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HealthSmart Assistant",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/features")
async def get_features():
    """Get available features"""
    return {
        "features": [
            "Service Presentation",
            "Dynamic Question Flow (1 question at a time)",
            "Service-Specific Assessment",
            "Missing Data Identification",
            "Question Priority Filtering",
            "CSV Rules Integration",
            "Integrated Conversation Flow"
        ],
        "services": [
            "Remote Patient Monitoring (RPM)",
            "Telehealth / Virtual Primary Care",
            "Insurance Enrollment"
        ]
    }

@app.get("/api/conversations/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in conversation_history:
        return {"conversations": []}
    
    return {"conversations": conversation_history[session_id]}

@app.delete("/api/conversations/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversation_history:
        del conversation_history[session_id]
        return {"message": "Conversation history cleared"}
    
    return {"message": "Session not found"}

if __name__ == "__main__":
    print("🌐 Starting HealthSmart Assistant Web Interface...")
    print("=" * 50)
    print("📍 Web Interface: http://localhost:8000")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/health")
    print("=" * 50)
    
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )