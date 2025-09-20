#!/usr/bin/env python3
"""
HealthSmart Assistant - Simple Web Interface
Simplified version for testing
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
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
    allow_origins=["*"],
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

# Store conversation history
conversation_history: Dict[str, List[Dict]] = {}

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
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
            }
            .chat-container {
                height: 400px;
                overflow-y: auto;
                padding: 20px;
                background: #f9f9f9;
            }
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 5px;
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
                border-top: 1px solid #ddd;
                display: flex;
                gap: 10px;
            }
            .input-field {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            .send-button {
                padding: 10px 20px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .send-button:hover {
                background: #0056b3;
            }
            .loading {
                display: none;
                text-align: center;
                color: #666;
                font-style: italic;
            }
            .error {
                color: red;
                background: #ffe6e6;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
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
                    🩺 <strong>Remote Patient Monitoring (RPM)</strong><br>
                    💻 <strong>Telehealth / Virtual Primary Care</strong><br>
                    🛡️ <strong>Insurance Enrollment</strong><br><br>
                    How can I help you today?
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
                    console.log('Sending message:', message);
                    
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
                    
                    console.log('Response status:', response.status);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('Response data:', data);
                    
                    // Add assistant response to chat
                    addMessage(data.response, 'assistant');
                    
                    // Update session ID if provided
                    if (data.session_id) {
                        sessionId = data.session_id;
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Sorry, there was an error: ' + error.message, 'assistant');
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
    try:
        print(f"📨 Received message: {chat_message.message}")
        
        # For new conversations, don't pass session_id to let ADK create it
        # For existing conversations, use the session_id from the request
        if not chat_message.session_id or chat_message.session_id not in conversation_history:
            session_id = None
            full_message = f"FIRST_INTERACTION: {chat_message.message}"
            print("🆕 First interaction - letting ADK create session")
        else:
            session_id = chat_message.session_id
            full_message = chat_message.message
            print(f"💬 Continuing conversation with session: {session_id}")
        
        # Get response from healthcare assistant
        events, adk_session_id = await assistant.handle_patient_inquiry(
            user_id=chat_message.user_id,
            message=full_message,
            session_id=session_id
        )
        
        # Extract response text
        response_text = ""
        
        for event in events:
            # Extract response text
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text + " "
        
        # Clean up response
        response_text = response_text.strip()
        if not response_text:
            response_text = "I'm sorry, I didn't understand that. Could you please rephrase your question?"
        
        # Use the ADK session ID
        final_session_id = adk_session_id
        print(f"📝 Using ADK session ID: {final_session_id}")
        
        # Store conversation history
        if final_session_id not in conversation_history:
            conversation_history[final_session_id] = []
        
        conversation_history[final_session_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": chat_message.message,
            "assistant_response": response_text
        })
        
        return ChatResponse(
            response=response_text,
            session_id=final_session_id,
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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    print("🌐 Starting HealthAngel Cloud Run Service...")
    print("=" * 50)
    print(f"📍 Web Interface: http://localhost:{port}")
    print(f"📋 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/api/health")
    print("=" * 50)
    
    uvicorn.run(
        "simple_web_app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
