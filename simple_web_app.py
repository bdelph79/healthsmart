#!/usr/bin/env python3
"""
HealthAngel - Simple Web Interface
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

from app.smart_health_agent import root_agent
from app.session_manager import EnhancedSessionManager
from config import config
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Initialize FastAPI app
app = FastAPI(
    title="HealthAngel",
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

# ============================================================================
# GLOBAL STATE (ADK Pattern - Created once at startup, reused for all requests)
# ============================================================================

session_service = None
runner = None
enhanced_session_manager = None

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

@app.on_event("startup")
async def startup_event():
    """Initialize ADK runner and session management (ADK Pattern)"""
    global session_service, runner, enhanced_session_manager

    print("🚀 Initializing HealthAngel...")

    # 1. Create ADK session service
    session_service = InMemorySessionService()

    # 2. Create enhanced session manager (our custom session timeout/cleanup logic)
    enhanced_session_manager = EnhancedSessionManager(
        session_service=session_service,
        session_timeout_minutes=config.session_timeout_minutes
    )
    await enhanced_session_manager.start()

    # 3. Create ADK Runner ONCE (reuse for all requests - ADK pattern)
    runner = Runner(
        agent=root_agent,
        app_name=config.app_name,
        session_service=session_service
    )

    print("🚀 HealthAngel web app started")
    print(f"   Agent: {root_agent.name}")
    print(f"   Model: {root_agent.model}")
    print(f"   Session timeout: {config.session_timeout_minutes} minutes")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global enhanced_session_manager

    if enhanced_session_manager:
        await enhanced_session_manager.stop()

    print("👋 HealthAngel web app stopped")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with chat interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HealthAngel</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #f8f9fa;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }
            
            .app-wrapper {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                overflow: hidden;
                min-height: calc(100vh - 40px);
                display: flex;
                flex-direction: column;
            }
            
            .browser-header {
                background: #f1f3f4;
                height: 40px;
                display: flex;
                align-items: center;
                padding: 0 16px;
                border-bottom: 1px solid #e0e0e0;
            }
            
            .browser-controls {
                display: flex;
                gap: 8px;
                margin-right: 16px;
            }
            
            .browser-btn {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                border: none;
            }
            
            .browser-btn.red { background: #ff5f57; }
            .browser-btn.yellow { background: #ffbd2e; }
            .browser-btn.green { background: #28ca42; }
            
            .url-bar {
                flex: 1;
                background: white;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                color: #666;
            }
            
            .browser-icons {
                display: flex;
                gap: 8px;
            }
            
            .banner {
                background: #20b2aa;
                color: white;
                text-align: center;
                padding: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            
            .app-header {
                background: white;
                padding: 16px 24px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .logo-section {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .hamburger {
                width: 20px;
                height: 16px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                cursor: pointer;
            }
            
            .hamburger span {
                height: 2px;
                background: #333;
                border-radius: 1px;
            }
            
            .logo {
                font-size: 24px;
                font-weight: bold;
            }
            
            .logo .health {
                color: #20b2aa;
            }
            
            .logo .angel {
                color: #008b8b;
            }
            
            .user-info {
                color: #666;
                font-size: 14px;
            }
            
            .header-buttons {
                display: flex;
                gap: 12px;
                align-items: center;
            }
            
            .header-btn {
                width: 40px;
                height: 40px;
                border: 2px solid #20b2aa;
                border-radius: 50%;
                background: transparent;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .header-btn.gray {
                border-color: #ccc;
            }
            
            .header-btn:hover {
                background: #20b2aa;
                color: white;
            }
            
            .header-btn.gray:hover {
                background: #ccc;
            }
            
            .user-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #20b2aa;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
            }
            
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                background: #f8f9fa;
                min-height: 600px;
            }
            
            .chat-container {
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            
            .message {
                margin: 16px 0;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            }
            
            .message.user {
                flex-direction: row-reverse;
            }
            
            .message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 14px;
                flex-shrink: 0;
            }
            
            .assistant-avatar {
                background: #20b2aa;
                color: white;
            }
            
            .user-avatar-small {
                background: #6c757d;
                color: white;
            }
            
            .message-bubble {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                line-height: 1.4;
            }
            
            .message.user .message-bubble {
                background: #20b2aa;
                color: white;
            }
            
            .message-actions {
                margin-top: 12px;
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }
            
            .action-btn {
                padding: 8px 16px;
                border: 2px solid #20b2aa;
                border-radius: 20px;
                background: transparent;
                color: #20b2aa;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .action-btn:hover {
                background: #20b2aa;
                color: white;
            }
            
            .trending-section {
                background: white;
                margin: 16px 0;
                padding: 16px;
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .trending-title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
                color: #333;
                margin-bottom: 12px;
            }
            
            .trending-list {
                list-style: none;
                margin-bottom: 12px;
            }
            
            .trending-list li {
                padding: 4px 0;
                color: #666;
                font-size: 14px;
            }
            
            .trending-actions {
                display: flex;
                gap: 8px;
            }
            
            .trending-btn {
                padding: 6px 12px;
                border: 1px solid #ddd;
                border-radius: 16px;
                background: transparent;
                color: #666;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .trending-btn:hover {
                background: #f0f0f0;
            }
            
            .quick-actions {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin: 16px 0;
            }
            
            .action-section {
                background: white;
                padding: 16px;
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .action-section.yellow {
                background: #fff9e6;
                border-left: 4px solid #ffc107;
            }
            
            .action-section.red {
                background: #ffe6e6;
                border-left: 4px solid #dc3545;
            }
            
            .section-title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
                margin-bottom: 12px;
            }
            
            .section-title .icon {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
            }
            
            .section-title .icon.yellow {
                background: #ffc107;
                color: white;
            }
            
            .section-title .icon.red {
                background: #dc3545;
                color: white;
            }
            
            .section-buttons {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }
            
            .section-btn {
                padding: 8px 12px;
                border: 2px solid #ffc107;
                border-radius: 8px;
                background: transparent;
                color: #ffc107;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .section-btn.red {
                border-color: #dc3545;
                color: #dc3545;
            }
            
            .section-btn:hover {
                background: #ffc107;
                color: white;
            }
            
            .section-btn.red:hover {
                background: #dc3545;
                color: white;
            }
            
            .input-container {
                padding: 16px 24px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .input-field {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 24px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.2s;
            }
            
            .input-field:focus {
                border-color: #20b2aa;
            }
            
            .input-actions {
                display: flex;
                gap: 8px;
                align-items: center;
            }
            
            .input-btn {
                width: 40px;
                height: 40px;
                border: none;
                border-radius: 50%;
                background: #f0f0f0;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .input-btn.send {
                background: #20b2aa;
                color: white;
            }
            
            .input-btn:hover {
                background: #20b2aa;
                color: white;
            }
            
            .loading {
                display: none;
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 16px;
            }
            
            .error {
                color: #dc3545;
                background: #ffe6e6;
                padding: 12px 16px;
                border-radius: 8px;
                margin: 16px 0;
                border-left: 4px solid #dc3545;
            }
            
            .flame-icon {
                color: #ff6b35;
            }

            /* ============================================ */
            /* MOBILE RESPONSIVE STYLES */
            /* ============================================ */

            @media (max-width: 768px) {
                body {
                    padding: 0;
                }

                .app-wrapper {
                    border-radius: 0;
                    min-height: 100vh;
                }

                .browser-header {
                    display: none; /* Hide browser chrome on mobile */
                }

                .banner {
                    font-size: 12px;
                    padding: 6px;
                }

                .app-header {
                    padding: 12px 16px;
                    flex-wrap: wrap;
                }

                .logo-section {
                    gap: 8px;
                    flex: 1;
                }

                .user-info {
                    display: none; /* Hide on mobile, show only on tablet+ */
                }

                .logo {
                    font-size: 20px;
                }

                .header-buttons {
                    gap: 8px;
                }

                .header-btn {
                    width: 36px;
                    height: 36px;
                    font-size: 14px;
                }

                .user-avatar {
                    width: 36px;
                    height: 36px;
                    font-size: 14px;
                }

                .chat-container {
                    padding: 16px;
                }

                .message-bubble {
                    max-width: 85%;
                    font-size: 14px;
                }

                .trending-section {
                    margin: 12px 0;
                    padding: 12px;
                }

                .trending-title {
                    font-size: 14px;
                }

                .trending-list li {
                    font-size: 13px;
                }

                .quick-actions {
                    grid-template-columns: 1fr; /* Stack on mobile */
                    gap: 12px;
                    margin: 12px 0;
                }

                .action-section {
                    padding: 12px;
                }

                .section-buttons {
                    grid-template-columns: 1fr 1fr;
                    gap: 6px;
                }

                .section-btn {
                    font-size: 11px;
                    padding: 6px 8px;
                }

                .input-container {
                    padding: 12px 16px;
                    gap: 8px;
                }

                .input-field {
                    font-size: 14px;
                    padding: 10px 14px;
                }

                .input-btn {
                    width: 36px;
                    height: 36px;
                }

                .input-actions {
                    gap: 6px;
                }

                /* Hide camera button on small mobile */
                .input-actions .input-btn:nth-child(2) {
                    display: none;
                }
            }

            /* Tablet-specific adjustments */
            @media (min-width: 769px) and (max-width: 1024px) {
                .app-wrapper {
                    max-width: 100%;
                    margin: 0;
                    border-radius: 0;
                }

                body {
                    padding: 0;
                }

                .user-info {
                    font-size: 12px;
                    max-width: 250px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }

                .quick-actions {
                    grid-template-columns: 1fr 1fr;
                }

                .chat-container {
                    padding: 20px;
                }
            }

            /* Small mobile devices */
            @media (max-width: 480px) {
                .logo {
                    font-size: 18px;
                }

                .hamburger {
                    width: 18px;
                    height: 14px;
                }

                .header-btn {
                    width: 32px;
                    height: 32px;
                }

                .user-avatar {
                    width: 32px;
                    height: 32px;
                }

                /* Hide voice and support buttons on very small screens */
                .header-btn:nth-child(1),
                .header-btn:nth-child(2) {
                    display: none;
                }

                .message-bubble {
                    max-width: 90%;
                    padding: 10px 14px;
                    font-size: 13px;
                }

                .section-buttons {
                    grid-template-columns: 1fr;
                }

                .trending-actions {
                    flex-direction: column;
                    gap: 6px;
                }

                .trending-btn {
                    width: 100%;
                }

                .action-btn {
                    font-size: 11px;
                    padding: 6px 12px;
                }
            }

            /* Landscape mobile optimization */
            @media (max-width: 768px) and (orientation: landscape) {
                .app-header {
                    padding: 8px 16px;
                }

                .header-btn, .user-avatar {
                    width: 32px;
                    height: 32px;
                }

                .chat-container {
                    padding: 12px;
                }

                .quick-actions {
                    grid-template-columns: 1fr 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="app-wrapper">
            <div class="browser-header">
                <div class="browser-controls">
                    <button class="browser-btn red"></button>
                    <button class="browser-btn yellow"></button>
                    <button class="browser-btn green"></button>
                </div>
                <div class="url-bar">🔒 healthangel.com</div>
                <div class="browser-icons">
                    <span>🛡️</span>
                    <span>➕</span>
                    <span>👤</span>
                </div>
            </div>
            
            <div class="banner">
                Save $1,500+ on Diabetes Medications (UTM)
            </div>
            
            <div class="app-header">
                <div class="logo-section">
                    <div class="hamburger">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <div class="logo">
                        <span class="health">health</span><span class="angel">angel</span>
                    </div>
                    <div class="user-info">Your Focus: Medication Savings • Type 2 Diabetes • Austin, TX</div>
                </div>
                <div class="header-buttons">
                    <button class="header-btn" title="Voice">🎤</button>
                    <button class="header-btn gray" title="Support">🎧</button>
                    <button class="header-btn gray" title="Learn">📚</button>
                    <div class="user-avatar">U</div>
                </div>
            </div>
            
            <div class="main-content">
            <div class="chat-container" id="chatContainer">
                <!-- Chat messages will appear here -->

                <div class="trending-section">
                    <div class="trending-title">
                        <span class="flame-icon">🔥</span>
                        Trending in Your Area
                    </div>
                    <ul class="trending-list">
                        <li>• Insulin prices drop 35% with new state program</li>
                        <li>• 3 new endocrinologists now accepting patients</li>
                        <li>• FDA approves generic diabetes drug</li>
                    </ul>
                    <div class="trending-actions">
                        <button class="trending-btn">Read More</button>
                        <button class="trending-btn">Get Updates</button>
                        <button class="trending-btn">Save Articles</button>
                    </div>
                </div>

                <div class="quick-actions">
                    <div class="action-section yellow">
                        <div class="section-title">
                            <div class="icon yellow">⏰</div>
                            Quick Actions
                        </div>
                        <div class="section-buttons">
                            <button class="section-btn">💊 My Medications</button>
                            <button class="section-btn">📅 Appointments</button>
                            <button class="section-btn">📊 Savings Dashboard</button>
                            <button class="section-btn">👥 Find Providers</button>
                        </div>
                    </div>

                    <div class="action-section red">
                        <div class="section-title">
                            <div class="icon red">🎧</div>
                            Need Immediate Help?
                        </div>
                        <div class="section-buttons">
                            <button class="section-btn red">📞 Call Support</button>
                            <button class="section-btn red">💬 Live Chat</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" class="input-field" placeholder="Ask me anything about your health, medications, or finding care..." onkeypress="handleKeyPress(event)">
                <div class="input-actions">
                    <button class="input-btn" title="Voice">🎤</button>
                    <button class="input-btn" title="Camera">📷</button>
                    <button class="input-btn send" onclick="sendMessage()" title="Send">✈️</button>
                </div>
            </div>
            
            <div class="loading" id="loading">HealthAngel is thinking...</div>
        </div>
        
            <div style="background: #333; color: white; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
                <div>© 2025 HealthAngel. All rights reserved.</div>
                <div style="display: flex; gap: 16px;">
                    <a href="#" style="color: white; text-decoration: none;">Terms & Conditions</a>
                    <a href="#" style="color: white; text-decoration: none;">Privacy Policy</a>
                    <a href="#" style="color: white; text-decoration: none;">Cookies Policy</a>
                </div>
            </div>
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
                messageDiv.className = `message ${sender === 'user' ? 'user' : ''}`;
                
                const avatar = document.createElement('div');
                avatar.className = `message-avatar ${sender === 'user' ? 'user-avatar-small' : 'assistant-avatar'}`;
                avatar.textContent = sender === 'user' ? 'U' : 'P';
                
                const bubble = document.createElement('div');
                bubble.className = 'message-bubble';
                
                if (sender === 'assistant') {
                    bubble.innerHTML = `<strong>HealthAngel:</strong><br>${text}`;
                } else {
                    bubble.textContent = text;
                }
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(bubble);
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            // Add click handlers for action buttons
            document.addEventListener('DOMContentLoaded', function() {
                // Quick action buttons
                const quickActionBtns = document.querySelectorAll('.section-btn');
                quickActionBtns.forEach(btn => {
                    btn.addEventListener('click', function() {
                        const action = this.textContent.trim();
                        addMessage(`I'd like to use: ${action}`, 'user');
                        sendMessage();
                    });
                });
                
                // Action buttons in messages
                const actionBtns = document.querySelectorAll('.action-btn');
                actionBtns.forEach(btn => {
                    btn.addEventListener('click', function() {
                        const action = this.textContent.trim();
                        addMessage(`I'd like to: ${action}`, 'user');
                        sendMessage();
                    });
                });
                
                // Trending buttons
                const trendingBtns = document.querySelectorAll('.trending-btn');
                trendingBtns.forEach(btn => {
                    btn.addEventListener('click', function() {
                        const action = this.textContent.trim();
                        addMessage(`I'd like to: ${action}`, 'user');
                        sendMessage();
                    });
                });
            });
        </script>
    </body>
    </html>
    """

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage, request: Request):
    """Chat endpoint using ADK Runner pattern directly"""
    try:
        print(f"📨 Received message: {chat_message.message}")

        # Capture metadata from request
        metadata = {
            'ip_address': request.client.host if request.client else None,
            'user_agent': request.headers.get('user-agent')
        }

        # Get or create session with full tracking using EnhancedSessionManager
        session, session_id, is_new = await enhanced_session_manager.get_or_create_session(
            user_id=chat_message.user_id,
            session_id=chat_message.session_id
        )

        # Update session metadata
        enhanced_session_manager.update_session_metadata(session_id, metadata)

        # Add FIRST_INTERACTION flag for new sessions
        if is_new:
            full_message = f"FIRST_INTERACTION: {chat_message.message}"
            print("🆕 First interaction - creating new session")
        else:
            full_message = chat_message.message
            print(f"💬 Continuing conversation with session: {session_id}")

        # Create content for ADK
        content = types.Content(
            role="user",
            parts=[types.Part(text=full_message)]
        )

        # Run agent using global runner (ADK pattern - runner reused across requests)
        events = []
        async for event in runner.run_async(
            user_id=chat_message.user_id,
            session_id=session_id,
            new_message=content
        ):
            events.append(event)

        # Extract response text from events
        response_text = ""
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text + " "

        # Clean up response
        response_text = response_text.strip()
        if not response_text:
            response_text = "I'm sorry, I didn't understand that. Could you please rephrase your question?"

        print(f"📝 Using ADK session ID: {session_id}")

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
            features_used=["adk_runner_pattern", "enhanced_session_manager", "tool_context_state", "json_rules"]
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

@app.get("/api/sessions/stats")
async def get_session_stats():
    """Get session statistics for monitoring"""
    try:
        stats = enhanced_session_manager.get_session_stats()
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session stats: {str(e)}")

@app.delete("/api/sessions/{session_id}")
async def end_session(session_id: str):
    """Explicitly end a session"""
    try:
        await enhanced_session_manager.end_session(session_id, reason="api_request")
        return {
            "status": "success",
            "message": f"Session {session_id} ended",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending session: {str(e)}")

if __name__ == "__main__":
    import os
    # Cloud Run sets PORT environment variable to 8080
    port = int(os.environ.get("PORT", 8080))
    
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