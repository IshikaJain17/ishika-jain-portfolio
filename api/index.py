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
    from flask import Flask, request, jsonify, Response
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
        self.init_error = None
        
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                # Strip any whitespace from API key
                clean_key = openai_api_key.strip()
                self.openai_client = OpenAI(api_key=clean_key)
                # Test the client with a simple call
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.init_error = str(e)
                self.openai_client = None
        
        # Enhanced system prompt for smart, context-aware responses
        self.system_prompt = """You are "Ishika Jain AI Assistant", an intelligent and interactive AI portfolio assistant for Ishika Jain, an AI/ML Engineer and Generative AI Specialist.

## YOUR DUAL ROLE:
1. Portfolio Assistant: Answer questions about Ishika's experience, skills, projects, and achievements in FIRST PERSON ("I", "my", "me")
2. AI/ML Expert: When users ask technical AI/ML questions, provide helpful explanations while naturally connecting to Ishika's expertise when relevant

## RESPONSE FORMAT:
- Use structured point-based lists with bullet points (•)
- Keep answers concise and aligned
- NO unnecessary markdown bold (**) or asterisks
- Use clear line breaks between sections
- Order information logically: main points first

## ISHIKA'S PROFILE (Single Source of Truth):

Identity & Experience:
- Name: Ishika Jain
- Experience: 1.5+ years in AI/ML & Generative AI (production systems)
- Current Role: AI/ML Engineer at Edysor Edutech Solutions Pvt. Ltd. (Aug 2025 – Present)
- Location: Noida, Delhi NCR
- Availability: Open to full-time, freelance, and remote opportunities globally

Past Experience:
- Data Scientist Intern – Generative AI at Consint Solutions (Built VLM pipeline improving accuracy from 30% to 98%)
- AI/ML Trainee at Global Infoventures (NVIDIA Partner) (Fine-tuned YOLOv7, annotated 5500+ images)

Core Expertise:
- Conversational AI & Digital Avatars (96% generation accuracy)
- Vision-Language Models (VLMs) & OCR pipelines
- LLM Fine-tuning (LoRA / PEFT / QLoRA)
- RAG & Multi-Agent Systems
- Voice AI (STT, TTS, Voice Cloning, Audio Enhancement)
- Low-latency, real-time AI pipelines
- Computer Vision (YOLO, OpenCV, Face Recognition)

Technical Stack:
- Languages: Python (Expert), SQL, JavaScript
- Frameworks: PyTorch, TensorFlow, LangChain, LlamaIndex, Hugging Face
- Models: GPT-4, LLaMA, Gemini, Whisper, YOLO, UNet
- Cloud/DevOps: AWS, Docker, FastAPI, Flask
- Databases: ChromaDB, Pinecone, MySQL, SQLite

Key Achievements:
- Reduced operational costs by 80–90%
- Reduced product costs by 98% through AI automation
- Achieved 96–99% accuracy in production systems
- Scaled AI platforms to 1000+ concurrent sessions
- Improved document extraction accuracy from ~30% to ~98%

Education & Research:
- B.Tech in Computer Science & Artificial Intelligence
- GATE Qualified 2025 (CS & DA)
- Research Paper accepted in Journal of Analytical Science and Technology (JAST)

Vision & Ambitions:
- Passionate about using AI/ML to solve real-world problems impacting millions
- Believe in building AI that's accessible and ethical
- Goal: Create innovative automation solutions transforming industries
- Want to be at forefront of AI innovation
- Thrive on challenges and cutting-edge problem-solving

What Makes Me Stand Out:
- Deploy production systems with real business impact
- Consistently achieved 96-99% accuracy with 80-90% cost reduction
- Bridge research and production effectively
- Fast learner staying ahead of AI landscape
- Combine technical depth with practical problem-solving
- Driven by belief that AI can improve the world

Contact:
- Email: 17ishikajain@gmail.com
- LinkedIn: https://www.linkedin.com/in/ishika-jain-987635238/

## RESPONSE GUIDELINES:

For Portfolio Questions:
- Respond in FIRST PERSON as Ishika
- Use point format with bullet points
- Keep answers concise but impactful
- Highlight measurable achievements
- NO unnecessary bold or special formatting

For AI/ML Technical Questions:
- Provide clear, accurate explanations in structured format
- Use bullet points for multiple concepts
- Connect to Ishika's hands-on experience when relevant
- Format as point lists for clarity

Interactive Behavior:
- Greetings: Respond warmly with point-based intro
- Unclear questions: Ask ONE short clarifying question
- Follow-up questions: Build context naturally
- Technical deep-dives: Offer more detail in point format

IMPORTANT:
- Never hallucinate information about Ishika not provided above
- Always use point/list format for clarity
- Remove all unnecessary bold (**) and special formatting
- Be engaging and professional
- Keep output aligned and organized"""
    
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
    
    def generate_response_stream(self, query: str, conversation_history: list = None):
        """Generate streaming response using GPT-4o mini"""
        
        if not OPENAI_AVAILABLE or not self.openai_client:
            # Yield fallback as a single chunk
            yield self._smart_fallback(query)
            return
        
        try:
            # Build messages with conversation history for context
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history if provided (last 6 messages for context)
            if conversation_history:
                for msg in conversation_history[-6:]:
                    messages.append(msg)
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            # Create streaming response
            stream = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=400,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming API error: {e}")
            yield self._smart_fallback(query)
    
    def _smart_fallback(self, query: str) -> str:
        """Smart keyword-based fallback when API is unavailable"""
        query_lower = query.lower()
        
        # Greetings
        if any(word in query_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return "Hey! I'm Ishika Jain, an AI/ML Engineer passionate about building production-grade AI systems.\n\nFeel free to ask me about:\n• My experience and background\n• My projects and achievements\n• AI/ML expertise and technical skills\n• Career opportunities"
        
        # Stand out / Why hire / Unique
        if any(word in query_lower for word in ['stand out', 'unique', 'different', 'why hire', 'why you', 'special']):
            return "What sets me apart:\n\n• Build production systems with real impact\n• Achieved 96-99% accuracy in production deployments\n• Reduced costs by 80-90% through AI automation\n• Bridge research and production effectively\n• Driven by solving real-world problems\n• Fast learner staying ahead of AI trends"
        
        # Ambition / Vision / Goals
        if any(word in query_lower for word in ['ambition', 'vision', 'goal', 'dream', 'future', 'passionate', 'drive', 'motivat']):
            return "My vision and ambitions:\n\n• Use AI to solve problems impacting millions\n• Be at the forefront of AI innovation\n• Turn cutting-edge research into production systems\n• Transform industries through automation\n• Create ethical and accessible AI solutions\n• Thrive on solving hard, challenging problems"
        
        # Experience
        if any(word in query_lower for word in ['experience', 'work', 'job', 'career', 'company', 'years']):
            return "My professional background:\n\n• Current: AI/ML Engineer at Edysor Edutech Solutions (Aug 2025 - Present)\n• 1.5+ years hands-on experience in production AI systems\n• Data Scientist Intern (Generative AI) at Consint Solutions\n• AI/ML Trainee at Global Infoventures (NVIDIA Partner)\n• Location: Noida, Delhi NCR\n• Open to full-time, freelance, and remote opportunities"
        
        # Skills / Expertise
        if any(word in query_lower for word in ['skill', 'expertise', 'specialize', 'know', 'tech']):
            return "My core expertise:\n\n• Conversational AI and Digital Avatars\n• Vision-Language Models and OCR pipelines\n• LLM Fine-tuning (LoRA, PEFT, QLoRA)\n• RAG and Multi-Agent Systems\n• Voice AI (STT, TTS, Voice Cloning)\n• Computer Vision (YOLO, OpenCV, Face Recognition)\n\nTech Stack: Python, PyTorch, TensorFlow, LangChain, LlamaIndex, Hugging Face, AWS, Docker"
        
        # Projects
        if any(word in query_lower for word in ['project', 'built', 'created', 'developed', 'production']):
            return "Key projects and achievements:\n\n• Digital avatars with 96% generation accuracy\n• VLM pipeline improving extraction from 30% to 98%\n• Real-time AI systems at enterprise scale\n• Platforms handling 1000+ concurrent sessions\n• Cost reduction of 80-90% through automation\n• Scaled AI solutions with measurable business impact"
        
        # Contact
        if any(word in query_lower for word in ['contact', 'email', 'reach', 'hire', 'linkedin']):
            return "Get in touch:\n\n• Email: 17ishikajain@gmail.com\n• LinkedIn: https://www.linkedin.com/in/ishika-jain-987635238/\n• Location: Noida, Delhi NCR\n• Availability: Full-time, freelance, remote (global)"
        
        # Education
        if any(word in query_lower for word in ['education', 'degree', 'study', 'college', 'gate', 'qualification']):
            return "Educational background:\n\n• B.Tech in Computer Science & Artificial Intelligence\n• GATE Qualified 2025 (CS & Data Science/AI)\n• Research paper published in Journal of Analytical Science and Technology (JAST)\n• Continuous learner with focus on latest AI/ML advances"
        
        # Default
        return "I'm an AI/ML Engineer with 1.5+ years of experience building production AI systems.\n\nYou can ask me about:\n• My experience and projects\n• AI/ML technical expertise\n• Skills and achievements\n• Career opportunities and vision"

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
    global ai_assistant
    has_client = ai_assistant and ai_assistant.openai_client is not None
    return jsonify({
        "status": "ready",
        "version": "3.0",
        "model": "gpt-4o-mini",
        "deployment": "vercel",
        "ai_enabled": has_client,
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

@app.route('/api/query/stream', methods=['POST'])
def query_assistant_stream():
    """Streaming endpoint for real-time LLM responses"""
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
        
        def generate():
            """Generator for Server-Sent Events"""
            try:
                for chunk in ai_assistant.generate_response_stream(question, conversation_history):
                    # Send each chunk as an SSE event
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                # Send completion signal
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"Error in streaming endpoint: {e}")
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