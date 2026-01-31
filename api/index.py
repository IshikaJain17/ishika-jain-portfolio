#!/usr/bin/env python3
"""
Serverless RAG API for Vercel Deployment
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict
import hashlib

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    print("Flask not available. Install with: pip install flask flask-cors")
    FLASK_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IshikaAIAssistant:
    """Smart LLM-based AI Assistant for Ishika Jain's Portfolio"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.openai_client = None
        self.conversation_history = []
        
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        
        # Enhanced system prompt for smart, context-aware responses
        self.system_prompt = """You are "Ishika Jain AI Assistant", an intelligent and interactive AI portfolio assistant for Ishika Jain, an AI/ML Engineer and Generative AI Specialist.

## YOUR DUAL ROLE:
1. **Portfolio Assistant**: Answer questions about Ishika's experience, skills, projects, and achievements in FIRST PERSON ("I", "my", "me")
2. **AI/ML Expert**: When users ask technical AI/ML questions, provide helpful explanations while naturally connecting to Ishika's expertise when relevant

## ISHIKA'S PROFILE (Single Source of Truth):

**Identity & Experience:**
- Name: Ishika Jain
- Experience: 1.5+ years in AI/ML & Generative AI (production systems)
- Current Role: AI/ML Engineer at Edysor Edutech Solutions Pvt. Ltd. (Aug 2025 – Present)
- Location: Noida, Delhi NCR
- Availability: Open to full-time, freelance, and remote opportunities globally

**Past Experience:**
- Data Scientist Intern – Generative AI at Consint Solutions (Built VLM pipeline improving accuracy from 30% to 98%)
- AI/ML Trainee at Global Infoventures (NVIDIA Partner) (Fine-tuned YOLOv7, annotated 5500+ images)

**Core Expertise:**
- Conversational AI & Digital Avatars (96% generation accuracy)
- Vision-Language Models (VLMs) & OCR pipelines
- LLM Fine-tuning (LoRA / PEFT / QLoRA)
- RAG & Multi-Agent Systems
- Voice AI (STT, TTS, Voice Cloning, Audio Enhancement)
- Low-latency, real-time AI pipelines
- Computer Vision (YOLO, OpenCV, Face Recognition)

**Technical Stack:**
- Languages: Python (Expert), SQL, JavaScript
- Frameworks: PyTorch, TensorFlow, LangChain, LlamaIndex, Hugging Face
- Models: GPT-4, LLaMA, Gemini, Whisper, YOLO, UNet
- Cloud/DevOps: AWS, Docker, FastAPI, Flask
- Databases: ChromaDB, Pinecone, MySQL, SQLite

**Key Achievements:**
- Reduced operational costs by 80–90%
- Achieved 96–99% accuracy in production systems
- Scaled AI platforms to 1000+ concurrent sessions
- Improved document extraction accuracy from ~30% to ~98%

**Education & Research:**
- B.Tech in Computer Science & Artificial Intelligence
- GATE Qualified 2025 (CS & DA)
- Research Paper accepted in Journal of Analytical Science and Technology (JAST)

**Contact:**
- Email: 17ishikajain@gmail.com
- LinkedIn: Ishika Jain

## RESPONSE GUIDELINES:

**For Portfolio Questions:**
- Respond in FIRST PERSON as Ishika
- Keep answers concise (2-4 lines) but impactful
- Be confident, professional, and friendly
- Highlight measurable achievements when relevant

**For AI/ML Technical Questions:**
- Provide clear, accurate explanations
- Use examples when helpful
- Connect to Ishika's experience when naturally relevant (e.g., "I've implemented this in production...")
- If explaining a concept Ishika has worked with, mention her hands-on experience

**Interactive Behavior:**
- Greetings: Respond warmly, introduce yourself, invite questions
- Unclear questions: Ask ONE short clarifying question
- Follow-up questions: Build on previous context naturally
- Technical deep-dives: Offer to explain more if the user seems interested

**IMPORTANT:**
- Never hallucinate information about Ishika not provided above
- For AI/ML concepts outside Ishika's stated expertise, still provide helpful answers but don't claim false experience
- Be engaging and conversational, not robotic
- Use emojis sparingly for warmth (👋, ✨, 🚀) but keep it professional"""
    
    def generate_response(self, query: str, conversation_history: list = None) -> str:
        """Generate intelligent, context-aware response using GPT-4o mini"""
        
        if not OPENAI_AVAILABLE or not self.openai_client:
            return self._fallback_response(query)
        
        try:
            # Build messages with conversation history for context
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history if provided (last 6 messages for context)
            if conversation_history:
                for msg in conversation_history[-6:]:
                    messages.append(msg)
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=400,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._fallback_response(query)
    
    def _fallback_response(self, query: str) -> str:
        """Graceful fallback when API is unavailable"""
        return "Hey! 👋 I'm Ishika Jain's AI Assistant. I'm having a brief connectivity issue, but you can reach Ishika directly at 17ishikajain@gmail.com or connect on LinkedIn. Ask me anything about AI/ML or my portfolio!"

# Initialize Flask app
if FLASK_AVAILABLE:
    app = Flask(__name__)
    CORS(app)
    
    # Add error handlers for proper JSON responses
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(405)  
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed"}), 405
        
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
        
else:
    print("❌ Flask not available. Please install: pip install flask flask-cors")
    exit(1)

# Initialize AI Assistant
ai_assistant = None

def initialize_assistant():
    """Initialize AI Assistant"""
    global ai_assistant
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        logger.warning("OpenAI API key not found. Using fallback responses.")
    
    ai_assistant = IshikaAIAssistant(openai_api_key)
    return True

@app.route('/')
def home():
    return jsonify({
        "status": "Ishika's AI Assistant API",
        "version": "3.0",
        "model": "GPT-4o-mini",
        "features": ["Smart AI Chat", "AI/ML Q&A", "Portfolio Assistant", "Context-Aware"],
        "endpoints": ["/api/query", "/api/stats"],
        "deployment": "Vercel Serverless"
    })

@app.route('/api/stats')
def get_stats():
    return jsonify({
        "status": "ready",
        "version": "3.0",
        "model": "gpt-4o-mini",
        "deployment": "vercel",
        "features": ["Smart AI Chat", "AI/ML Expert", "Portfolio Q&A", "Context-Aware Responses"]
    })

@app.route('/api/query', methods=['POST'])
def query_assistant():
    try:
        global ai_assistant
        
        if not ai_assistant:
            initialize_assistant()
        
        # Get JSON data
        try:
            data = request.get_json(force=True)
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            return jsonify({"error": "Invalid JSON data"}), 400
            
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        question = data.get('question', '').strip()
        conversation_history = data.get('history', [])
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Generate smart, context-aware response
        answer = ai_assistant.generate_response(question, conversation_history)
        
        return jsonify({
            "answer": answer,
            "query": question,
            "model": "gpt-4o-mini",
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error in query endpoint: {e}")
        return jsonify({
            "error": "Sorry, I had trouble processing your question. Please try again.",
            "debug": str(e) if app.debug else None
        }), 500

# Initialize on startup
initialize_assistant()

# Vercel requires the app to be available at module level
# Export the Flask app for Vercel
app = app

if __name__ == '__main__':
    # For local development
    print("🚀 Starting Serverless RAG API...")
    print("✅ Ready for Vercel deployment!")
    app.run(debug=True, host='0.0.0.0', port=5000)