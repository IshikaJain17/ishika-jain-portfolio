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
    import requests as http_requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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
- Reduced product costs by 98% through AI automation
- Achieved 96–99% accuracy in production systems
- Scaled AI platforms to 1000+ concurrent sessions
- Improved document extraction accuracy from ~30% to ~98%

**Education & Research:**
- B.Tech in Computer Science & Artificial Intelligence
- GATE Qualified 2025 (CS & DA)
- Research Paper accepted in Journal of Analytical Science and Technology (JAST)

**My Vision & Ambitions:**
- I'm passionate about using AI/ML to solve real-world problems that impact millions
- I believe in building AI that's not just accurate, but accessible and ethical
- My goal is to create innovative automation solutions that transform industries
- I'm excited about the potential of Generative AI to revolutionize how we work and create
- I want to be at the forefront of AI innovation, turning cutting-edge research into production systems
- I thrive on challenges — the harder the problem, the more motivated I am to solve it

**What Makes Me Stand Out:**
- I don't just build models — I deploy production systems with real business impact
- I've consistently achieved 96-99% accuracy while reducing costs by 80-90%
- I bridge the gap between research and production, shipping AI that scales
- I'm a fast learner who stays ahead of the rapidly evolving AI landscape
- I combine technical depth with practical problem-solving mindset
- I'm driven by curiosity and the belief that AI can genuinely make the world better

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
            return self._smart_fallback(query)
        
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
            return self._smart_fallback(query)
    
    def _smart_fallback(self, query: str) -> str:
        """Smart keyword-based fallback when API is unavailable"""
        query_lower = query.lower()
        
        # Greetings
        if any(word in query_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return "Hey! 👋 I'm Ishika Jain, an AI/ML Engineer passionate about building production-grade AI systems. Ask me about my experience, projects, or what drives me!"
        
        # Stand out / Why hire / Unique
        if any(word in query_lower for word in ['stand out', 'unique', 'different', 'why hire', 'why you', 'special']):
            return "What sets me apart? I don't just build models — I ship production systems with real impact. I've achieved 96-99% accuracy while cutting costs by 80-90%. I bridge research and production, and I'm driven by the belief that AI can genuinely solve real-world problems. 🚀"
        
        # Ambition / Vision / Goals
        if any(word in query_lower for word in ['ambition', 'vision', 'goal', 'dream', 'future', 'passionate', 'drive', 'motivat']):
            return "I'm passionate about using AI to solve problems that impact millions. My goal is to be at the forefront of AI innovation — turning cutting-edge research into production systems that transform industries. The harder the problem, the more excited I am to solve it! ✨"
        
        # Experience
        if any(word in query_lower for word in ['experience', 'work', 'job', 'career', 'company', 'years']):
            return "I have 1.5+ years of hands-on experience building production-grade AI systems. Currently an AI/ML Engineer at Edysor Edutech, I've built digital avatars with 96% accuracy and VLM pipelines that improved document extraction from 30% to 98%."
        
        # Skills / Expertise
        if any(word in query_lower for word in ['skill', 'expertise', 'specialize', 'know', 'tech']):
            return "I specialize in Conversational AI, Vision-Language Models, LLM fine-tuning (LoRA/PEFT), RAG systems, and Voice AI. My stack includes Python, PyTorch, LangChain, and I've worked with GPT-4, LLaMA, YOLO, and more."
        
        # Projects
        if any(word in query_lower for word in ['project', 'built', 'created', 'developed', 'production']):
            return "I've deployed real-time AI systems at enterprise scale — digital avatars with 96% accuracy, VLM pipelines with 98% extraction accuracy, and platforms handling 1000+ concurrent sessions. All with significant cost reductions!"
        
        # Contact
        if any(word in query_lower for word in ['contact', 'email', 'reach', 'hire', 'linkedin']):
            return "📧 Email: 17ishikajain@gmail.com\n🔗 LinkedIn: Ishika Jain\n📍 Location: Noida, Delhi NCR\n✅ Open to full-time, freelance, and remote opportunities globally!"
        
        # Education
        if any(word in query_lower for word in ['education', 'degree', 'study', 'college', 'gate', 'qualification']):
            return "I hold a B.Tech in Computer Science & AI, and I'm GATE Qualified 2025 in both CS and Data Science/AI. I also have a research paper published in JAST journal."
        
        # Default
        return "I'm an AI/ML Engineer with 1.5+ years of experience building production AI systems. I'm passionate about solving real-world problems with innovative AI solutions. Ask me about my skills, projects, or what drives me! 🚀"

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

def verify_hcaptcha(token: str) -> bool:
    """Verify hCaptcha token with hCaptcha servers (FREE service)"""
    if not token:
        return True  # Skip verification if no token (for backwards compatibility)
    
    # Get hCaptcha secret key from environment variable
    # Get your FREE keys at: https://www.hcaptcha.com/
    hcaptcha_secret = os.getenv('HCAPTCHA_SECRET_KEY')
    
    if not hcaptcha_secret:
        logger.warning("HCAPTCHA_SECRET_KEY not set. Skipping verification.")
        return True  # Skip if not configured
    
    if not REQUESTS_AVAILABLE:
        logger.warning("requests library not available. Skipping hCaptcha verification.")
        return True
    
    try:
        response = http_requests.post(
            'https://hcaptcha.com/siteverify',
            data={
                'secret': hcaptcha_secret,
                'response': token
            },
            timeout=10
        )
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        logger.error(f"hCaptcha verification error: {e}")
        return True  # Allow on verification error to not block users

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
        
        # Verify hCaptcha token (FREE spam protection)
        hcaptcha_token = data.get('hcaptcha_token')
        if hcaptcha_token and not verify_hcaptcha(hcaptcha_token):
            return jsonify({"error": "Captcha verification failed. Please try again."}), 403
            
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