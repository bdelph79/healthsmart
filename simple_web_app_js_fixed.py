#!/usr/bin/env python3
"""
HealthAngel - Formatted Web Interface
Enhanced version with better formatting for menus and responses
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
    title="HealthAngel",
    description="AI-Powered Healthcare Assistant with Multi-Agent Architecture",
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

def format_response(text: str) -> str:
    """Format the response text for better display"""
    # Convert markdown-style formatting to HTML
    text = text.replace('**', '<strong>').replace('**', '</strong>')
    text = text.replace('*', '<em>').replace('*', '</em>')
    
    # Convert line breaks to HTML
    text = text.replace('\n', '<br>')
    
    # Format bullet points
    text = text.replace('• ', '&bull; ')
    text = text.replace('- ', '&bull; ')
    
    # Format numbered lists
    import re
    text = re.sub(r'(\d+)\.\s+', r'<strong>\1.</strong> ', text)
    
    return text

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with enhanced chat interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HealthAngel - AI Healthcare Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
                height: 80vh;
                display: flex;
                flex-direction: column;
            }
            
            .header {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 25px;
                text-align: center;
                position: relative;
            }
            
            .header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                opacity: 0.1;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }
            
            .chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 25px;
                background: #f8f9fa;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .message {
                max-width: 85%;
                padding: 15px 20px;
                border-radius: 18px;
                position: relative;
                word-wrap: break-word;
                line-height: 1.5;
            }
            
            .user-message {
                background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
                color: white;
                margin-left: auto;
                text-align: right;
                border-bottom-right-radius: 5px;
            }
            
            .assistant-message {
                background: white;
                color: #333;
                margin-right: auto;
                border: 1px solid #e9ecef;
                border-bottom-left-radius: 5px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .assistant-message strong {
                color: #2c3e50;
                font-weight: 600;
            }
            
            .assistant-message em {
                color: #7f8c8d;
                font-style: italic;
            }
            
            .service-menu {
                background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                border: 2px solid #2196F3;
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
            }
            
            .service-menu h3 {
                color: #1976D2;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .service-item {
                background: white;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #4CAF50;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .service-item h4 {
                color: #2c3e50;
                margin-bottom: 8px;
                font-size: 1.1em;
            }
            
            .service-item ul {
                margin: 8px 0;
                padding-left: 20px;
            }
            
            .service-item li {
                margin: 5px 0;
                color: #555;
            }
            
            .input-container {
                padding: 25px;
                background: white;
                border-top: 1px solid #e9ecef;
                display: flex;
                gap: 15px;
                align-items: center;
            }
            
            .input-field {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e9ecef;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: all 0.3s ease;
            }
            
            .input-field:focus {
                border-color: #4CAF50;
                box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
            }
            
            .send-button {
                padding: 15px 30px;
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            }
            
            .send-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
            }
            
            .send-button:active {
                transform: translateY(0);
            }
            
            .loading {
                display: none;
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 20px;
            }
            
            .loading::after {
                content: '';
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #4CAF50;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .error {
                color: #e74c3c;
                background: #ffeaea;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid #e74c3c;
            }
            
            .typing-indicator {
                display: none;
                padding: 15px 20px;
                background: white;
                border-radius: 18px;
                margin-right: auto;
                max-width: 85%;
                border: 1px solid #e9ecef;
            }
            
            .typing-dots {
                display: inline-block;
            }
            
            .typing-dots::after {
                content: '...';
                animation: typing 1.5s infinite;
            }
            
            @keyframes typing {
                0%, 20% { content: '.'; }
                40% { content: '..'; }
                60%, 100% { content: '...'; }
            }
            
            .scroll-to-bottom {
                position: absolute;
                bottom: 80px;
                right: 30px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                cursor: pointer;
                display: none;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            }
            
            .scroll-to-bottom:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 HealthAngel</h1>
                <p>AI-Powered Healthcare Service Navigation</p>
            </div>
            
            <div class="chat-container" id="chatContainer">
                <div class="assistant-message message">
                    <strong>HealthAngel:</strong><br><br>
                    <div class="service-menu">
                        <h3>Welcome! I can help you with these healthcare services:</h3>
                        <div class="service-item">
                            <h4>🩺 Remote Patient Monitoring (RPM)</h4>
                            <ul>
                                <li>Monitor chronic conditions from home</li>
                                <li>Connected devices for health tracking</li>
                                <li>24/7 health monitoring support</li>
                            </ul>
                        </div>
                        <div class="service-item">
                            <h4>💻 Telehealth / Virtual Primary Care</h4>
                            <ul>
                                <li>Virtual doctor visits from home</li>
                                <li>Prescription management and refills</li>
                                <li>Convenient healthcare access</li>
                            </ul>
                        </div>
                        <div class="service-item">
                            <h4>🛡️ Insurance Enrollment</h4>
                            <ul>
                                <li>Help finding health insurance plans</li>
                                <li>Medicare and marketplace assistance</li>
                                <li>Coverage optimization</li>
                            </ul>
                        </div>
                    </div>
                    <br>How can I help you today?
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" class="input-field" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()" class="send-button">Send</button>
            </div>
            
            <div class="loading" id="loading">HealthAngel is thinking<span class="typing-dots"></span></div>
            <button class="scroll-to-bottom" id="scrollBtn" onclick="scrollToBottom()">↓</button>
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
                    // Format the response text
                    const formattedText = formatResponse(text);
                    messageDiv.innerHTML = `<strong>HealthAngel:</strong><br><br>${formattedText}`;
                } else {
                    messageDiv.innerHTML = `<strong>You:</strong><br>${text}`;
                }
                
                chatContainer.appendChild(messageDiv);
                scrollToBottom();
            }
            
            function formatResponse(text) {
                // Convert markdown-style formatting to HTML
                text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
                
                // Convert line breaks to HTML
                text = text.replace(/\n/g, '<br>');
                
                // Format bullet points
                text = text.replace(/• /g, '&bull; ');
                text = text.replace(/- /g, '&bull; ');
                
                // Format numbered lists
                text = text.replace(/(\d+)\.\s+/g, '<strong>$1.</strong> ');
                
                // Format service information
                text = text.replace(/(\*\*.*?Service:\*\*)/g, '<div class="service-menu"><h3>$1</h3>');
                text = text.replace(/(\*\*.*?:\*\*)/g, '<div class="service-item"><h4>$1</h4>');
                
                return text;
            }
            
            function scrollToBottom() {
                const chatContainer = document.getElementById('chatContainer');
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            // Show scroll button when needed
            document.getElementById('chatContainer').addEventListener('scroll', function() {
                const scrollBtn = document.getElementById('scrollBtn');
                const chatContainer = document.getElementById('chatContainer');
                if (chatContainer.scrollTop > 100) {
                    scrollBtn.style.display = 'block';
                } else {
                    scrollBtn.style.display = 'none';
                }
            });
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
        "service": "HealthAngel",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    
    print("🌐 Starting HealthAngel Formatted Web Interface...")
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
