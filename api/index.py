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

class SimpleRAGSystem:
    """Simplified RAG system for serverless deployment"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.openai_client = None
        
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        
        # System prompt for Ishika Jain AI Assistant
        self.system_prompt = """You are "Ishika Jain AI Assistant", the official AI portfolio assistant of Ishika Jain, an AI/ML Engineer and Generative AI Specialist.

Your role is to answer questions exactly as Ishika would, in first person, representing her professional experience, skills, and achievements.

Core Rules:
- Always respond in FIRST PERSON ("I", "my", "me")
- Keep answers very short, clear, and impactful (2-4 lines max)
- Tone: confident, professional, friendly
- Optimize responses for recruiters, founders, and technical interviewers
- Avoid unnecessary jargon unless the user asks for deep technical details
- Never hallucinate or assume information not explicitly provided
- If something is unknown or not mentioned, respond politely and briefly

About Me (Single Source of Truth):
- Name: Ishika Jain
- Experience: 1.5+ years in AI/ML & Generative AI (production systems)
- Current Role: AI/ML Engineer at Edysor Edutech Solutions Pvt. Ltd. (Aug 2025 – Present)

Past Experience:
- Data Scientist Intern – Generative AI at Consint Solutions
- AI/ML Trainee at Global Infoventures (NVIDIA Partner)

Core Expertise:
- Conversational AI & Digital Avatars
- Vision-Language Models (VLMs)
- LLM Fine-tuning (LoRA / PEFT)
- RAG & Multi-Agent Systems
- Voice AI (STT, TTS, Voice Cloning, Audio Enhancement)
- Low-latency, real-time AI pipelines

Key Achievements:
- Reduced operational costs by 80–90%
- Achieved 96–99% accuracy in production systems
- Scaled AI platforms to 1000+ concurrent sessions
- Improved document extraction accuracy from ~30% to ~98%

Education:
- B.Tech in Computer Science & Artificial Intelligence
- GATE Qualified 2025 (CS & DA)

Research:
- Paper accepted in Journal of Analytical Science and Technology (JAST)

Location: Noida, Delhi NCR
Availability: Open to full-time, freelance, and remote opportunities globally

Contact Details:
- Email: 17ishikajain@gmail.com
- LinkedIn: Ishika Jain

Conversation Behavior:
- If the user greets (hi/hello), respond warmly and invite them to ask about my work
- If asked about experience, skills, or projects, answer concisely and confidently
- If asked for contact details, share Email and LinkedIn
- If a question is unclear, ask one short clarifying question"""
    
    def simple_search(self, query: str) -> str:
        """Simple keyword-based search for serverless deployment"""
        query_lower = query.lower()
        
        # Greeting queries
        if any(word in query_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return "Hey! 👋 I'm Ishika Jain, an AI/ML Engineer specializing in Generative AI. Feel free to ask me about my experience, skills, or projects!"
        
        # Education queries
        if any(word in query_lower for word in ['education', 'degree', 'study', 'college', 'university', 'qualification']):
            return "I hold a B.Tech in Computer Science & Artificial Intelligence. I'm also GATE Qualified 2025 in both CS and Data Science/AI."
        
        # Programming/Skills queries
        if any(word in query_lower for word in ['programming', 'languages', 'skills', 'technical', 'python', 'code', 'specialize', 'expertise']):
            return "I specialize in Conversational AI & Digital Avatars, Vision-Language Models, LLM Fine-tuning (LoRA/PEFT), RAG & Multi-Agent Systems, and Voice AI. I build low-latency, real-time AI pipelines."
        
        # Experience queries
        if any(word in query_lower for word in ['experience', 'work', 'job', 'career', 'company', 'years']):
            return "I have 1.5+ years of hands-on experience building production-grade AI and Generative AI systems. Currently, I'm an AI/ML Engineer at Edysor Edutech Solutions."
        
        # Projects queries
        if any(word in query_lower for word in ['projects', 'built', 'created', 'developed', 'production']):
            return "Yes, I've deployed real-time AI systems at enterprise scale. I've built digital avatars with 96% accuracy, VLM pipelines improving accuracy from ~30% to ~98%, and scaled platforms to 1000+ concurrent sessions."
        
        # Contact queries
        if any(word in query_lower for word in ['contact', 'email', 'reach', 'hire', 'available', 'linkedin']):
            return "📧 Email: 17ishikajain@gmail.com\n🔗 LinkedIn: Ishika Jain\n📍 Location: Noida, Delhi NCR\n✅ I'm open to full-time, freelance, and remote opportunities globally!"
        
        # Achievements queries
        if any(word in query_lower for word in ['achievement', 'award', 'recognition', 'gate', 'paper', 'research']):
            return "I'm GATE Qualified 2025 (CS & DA), have a research paper accepted in JAST journal, reduced operational costs by 80-90%, and achieved 96-99% accuracy in production systems."
        
        # Default response
        return "I'm an AI/ML Engineer with 1.5+ years of experience in production-grade Generative AI systems. Ask me about my skills, experience, projects, or achievements!"
    
    def generate_response(self, query: str) -> str:
        """Generate response using OpenAI GPT-4o mini or fallback"""
        try:
            if OPENAI_AVAILABLE and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": self.system_prompt
                        },
                        {
                            "role": "user", 
                            "content": query
                        }
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
        
        # Fallback to simple search
        return self.simple_search(query)

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

# Initialize RAG system
rag_system = None

def initialize_rag():
    """Initialize RAG system"""
    global rag_system
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        logger.warning("OpenAI API key not found. Using fallback responses.")
    
    rag_system = SimpleRAGSystem(openai_api_key)
    return True

@app.route('/')
def home():
    return jsonify({
        "status": "Ishika's AI Assistant API",
        "version": "2.0",
        "endpoints": ["/api/query", "/api/stats"],
        "deployment": "Vercel Serverless"
    })

@app.route('/api/stats')
def get_stats():
    return jsonify({
        "status": "ready",
        "version": "serverless",
        "deployment": "vercel",
        "features": ["AI Assistant", "Resume Q&A", "Contact Info"]
    })

@app.route('/api/query', methods=['POST'])
def query_rag():
    try:
        global rag_system
        
        if not rag_system:
            initialize_rag()
        
        # Get JSON data
        try:
            data = request.get_json(force=True)
        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            return jsonify({"error": "Invalid JSON data"}), 400
            
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Generate response
        answer = rag_system.generate_response(question)
        
        return jsonify({
            "answer": answer,
            "query": question,
            "method": "serverless_rag",
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Error in query endpoint: {e}")
        return jsonify({
            "error": "Sorry, I had trouble processing your question. Please try again.",
            "debug": str(e) if app.debug else None
        }), 500

# Initialize on startup
initialize_rag()

# Vercel requires the app to be available at module level
# Export the Flask app for Vercel
app = app

if __name__ == '__main__':
    # For local development
    print("🚀 Starting Serverless RAG API...")
    print("✅ Ready for Vercel deployment!")
    app.run(debug=True, host='0.0.0.0', port=5000)