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
        
        # Store resume data in memory (for serverless)
        self.resume_data = """
        Ishika Jain is an AI/ML Engineer and Generative AI Specialist with 1.5+ years of hands-on industry experience developing production-ready AI solutions. 

        Educational Background:
        - Bachelor of Technology (B.Tech) in Computer Science and Engineering
        - Specialized in Artificial Intelligence and Machine Learning
        - GATE Qualified 2025 in Computer Science & Data Science/AI
        - Strong academic foundation in algorithms, data structures, mathematics, and statistics

        Professional Experience:
        - AI/ML Engineer at Edysor Edutech Solutions Pvt. Ltd. (Aug 2025 – Present): Created custom AI avatar using advanced open-source models with 96% generation accuracy, reducing costs by 80%. Built context-aware messaging AI bot with modern frameworks, reducing manual query handling by 95%. Scaled AI systems to 1000+ concurrent sessions.

        - Data Scientist Intern (Generative AI) at Consint Solutions Pvt. Ltd. (Apr 2025 – Jul 2025): Built end-to-end VLM pipeline for passport entity extraction, improving accuracy from 30.45% to 98.06%.

        - AI-ML Trainee at Global Infoventures Pvt. Ltd. (NVIDIA Partnership) (Dec 2023 – Jun 2024): Annotated 5500+ images using Roboflow and applied augmentation techniques. Fine-tuned YOLOv7 for multiple projects achieving 95% accuracy.

        Core Expertise:
        - Conversational AI & Digital Avatars
        - Vision-Language Models (VLMs)
        - LLM Fine-tuning (LoRA/PEFT)
        - RAG & Multi-Agent Systems
        - Voice AI (STT, TTS, Voice Cloning, Audio Enhancement)
        - Low-latency, real-time AI pipelines

        Technical Skills and Programming Languages:
        - Programming Languages: Python (Expert), SQL (Advanced), JavaScript (Intermediate)  
        - AI/ML Frameworks: PyTorch, TensorFlow, OpenCV, YOLOv7/YOLOv8, scikit-learn
        - Computer Vision: Face Recognition, Object Detection, Image Processing, OpenCV
        - NLP & LLM: OpenAI, Gemini, LLaMA, RAG Pipelines, Vector Embeddings, Transformers
        - Cloud & DevOps: AWS, Docker, Flask, FastAPI, Git
        - Databases: MySQL, ChromaDB, SQLite
        - Web Technologies: HTML, CSS, JavaScript, React basics

        Major Projects:
        - Smart Glasses for Visually Impaired: Real-time object detection and audio feedback system
        - VLM-RAG OCR System: Document processing pipeline with 98% accuracy improvement
        - Digital Human AI Avatar: UNet architecture with HuBERT features for realistic avatars
        - Face Recognition Attendance System: OpenCV-based automated attendance tracking
        - PPE Detection System: YOLOv7 for workplace safety compliance monitoring
        - Movie Recommendation System: ML-based content filtering and recommendations
        - Fatigue Detection System: Computer vision for driver safety monitoring

        Key Achievements and Recognition:
        - Reduced operational costs by up to 80–90%
        - Achieved 96–99% model accuracy in production
        - Scaled AI systems to 1000+ concurrent sessions
        - Improved document extraction accuracy from ~30% to ~98%
        - GATE Qualified 2025 (Computer Science & Data Science/AI) 
        - Research Paper accepted in Journal of Analytical Science and Technology (JAST)
        - 1st Runner-Up in Ideathon 1.0 & 2.0 competitions
        - Google Cloud Arcade AI & GenAI skill badges 2025
        - NVIDIA AI Summit Mumbai 2024 attendee

        Contact Information: 
        Email: 17ishikajain@gmail.com
        LinkedIn: ishika-jain-987635238  
        Location: Noida, Delhi NCR, India
        Availability: Open for full-time, freelance, and remote opportunities globally
        """
    
    def simple_search(self, query: str) -> str:
        """Simple keyword-based search for serverless deployment"""
        query_lower = query.lower()
        
        # Greeting queries
        if any(word in query_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return "Hey there! 👋 I'm Ishika. Great to have you here! Feel free to ask me anything about my experience, projects, or skills."
        
        # Education queries
        if any(word in query_lower for word in ['education', 'degree', 'study', 'college', 'university', 'qualification']):
            return "I hold a B.Tech in Computer Science & AI, and I'm GATE Qualified 2025 in both CS and Data Science/AI."
        
        # Programming/Skills queries
        if any(word in query_lower for word in ['programming', 'languages', 'skills', 'technical', 'python', 'code']):
            return "I'm proficient in Python (Expert), SQL (Advanced), and JavaScript. I work extensively with PyTorch, TensorFlow, OpenCV, and various LLM frameworks."
        
        # Experience queries
        if any(word in query_lower for word in ['experience', 'work', 'job', 'career', 'company', 'years']):
            return "I have 1.5+ years of hands-on experience building production-grade AI systems. Currently, I'm an AI/ML Engineer at Edysor Edutech, previously worked at Consint Solutions and Global Infoventures (NVIDIA Partner)."
        
        # Projects queries
        if any(word in query_lower for word in ['projects', 'built', 'created', 'developed']):
            return "I've built several production systems including AI Avatars with 96% accuracy, VLM-RAG OCR (98% accuracy), Smart Glasses for visually impaired, and real-time detection systems."
        
        # Contact queries
        if any(word in query_lower for word in ['contact', 'email', 'reach', 'hire', 'available', 'linkedin']):
            return "📧 Email: 17ishikajain@gmail.com\n🔗 LinkedIn: ishika-jain-987635238\n📍 Location: Noida, Delhi NCR\n✅ I'm open to full-time, freelance, and remote opportunities globally!"
        
        # Achievements queries
        if any(word in query_lower for word in ['achievement', 'award', 'recognition', 'gate', 'paper', 'research']):
            return "I'm GATE Qualified 2025, have a research paper published in JAST journal, and achieved 96-99% accuracy in production AI systems while reducing costs by 80-90%."
        
        # Specialization queries
        if any(word in query_lower for word in ['specialize', 'expertise', 'focus', 'best at']):
            return "I specialize in Conversational AI Avatars, Vision-Language Models, LLM Fine-tuning, RAG systems, and low-latency real-time AI pipelines."
        
        # Default response
        return "I'm an AI/ML Engineer with 1.5+ years of experience in production-grade Generative AI systems. I specialize in conversational AI, VLMs, and scalable GenAI pipelines. Ask me about my experience, skills, or projects!"
    
    def generate_response(self, query: str) -> str:
        """Generate response using OpenAI or fallback"""
        try:
            if OPENAI_AVAILABLE and self.openai_client:
                system_prompt = """You are "Ishika Jain", an AI/ML Engineer and Generative AI Specialist with 1.5+ years of hands-on industry experience.

Your role is to act as my personal portfolio assistant and answer questions exactly as if *I* am responding.

RULES:
- Always respond in FIRST PERSON ("I", "my", "me")
- Keep answers VERY SHORT, clear, and easy to understand (2–4 lines max)
- Be confident, professional, and friendly
- No unnecessary technical jargon unless the user asks for deep details
- Never hallucinate information beyond what is provided
- If something is not explicitly mentioned, say it politely and briefly
- Optimize answers for recruiters, founders, and technical interviewers

ABOUT ME (SOURCE OF TRUTH):
- Name: Ishika Jain
- Experience: 1.5+ years in AI/ML & Generative AI (production systems)
- Current Role: AI/ML Engineer at Edysor Edutech Solutions Pvt. Ltd. (Aug 2025 – Present)
- Past Experience:
  • Data Scientist Intern – Generative AI at Consint Solutions
  • AI/ML Trainee at Global Infoventures (NVIDIA Partner)
- Core Expertise:
  • Conversational AI & Digital Avatars
  • Vision-Language Models (VLMs)
  • LLM Fine-tuning (LoRA/PEFT)
  • RAG & Multi-Agent Systems
  • Voice AI (STT, TTS, Voice Cloning, Audio Enhancement)
  • Low-latency, real-time AI pipelines
- Key Achievements:
  • Reduced operational costs by up to 80–90%
  • Achieved 96–99% model accuracy in production
  • Scaled AI systems to 1000+ concurrent sessions
  • Improved document extraction accuracy from ~30% to ~98%
- Education:
  • B.Tech in Computer Science & Artificial Intelligence
  • GATE Qualified 2025 (CS & DA)
- Research:
  • Paper accepted in Journal of Analytical Science and Technology (JAST)
- Location: Noida, Delhi NCR
- Availability: Open to full-time, freelance, and remote opportunities globally

ANSWERING STYLE EXAMPLES:
Q: "How much experience do you have?"
A: "I have 1.5+ years of hands-on experience building production-grade AI and Generative AI systems."

Q: "What do you specialize in?"
A: "I specialize in conversational AI avatars, vision-language models, and scalable GenAI pipelines."

Q: "Have you worked on real production systems?"
A: "Yes, I've deployed multiple real-time AI systems used at enterprise scale with high accuracy and low latency."

If the user greets (hi/hello), respond warmly and invite them to ask about my work.
If the user asks for contact details, share email (17ishikajain@gmail.com) and LinkedIn (ishika-jain-987635238).
If the question is unclear, ask a short clarifying question."""

                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": system_prompt
                        },
                        {
                            "role": "user", 
                            "content": f"Reference Data:\n{self.resume_data}\n\nUser Question: {query}"
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