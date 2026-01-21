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
        Ishika Jain is an AI/ML Engineer and Generative AI Specialist with 1+ years of experience developing production-ready AI solutions. 

        Educational Background:
        - Bachelor of Technology (B.Tech) in Computer Science and Engineering
        - Specialized in Artificial Intelligence and Machine Learning
        - GATE Qualified 2025 in Computer Science & Data Science/AI
        - Strong academic foundation in algorithms, data structures, mathematics, and statistics

        Professional Experience:
        - AI/ML Engineer at Edysor Edutech Solutions Pvt. Ltd. (Aug 2025 – Present): Created custom AI avatar using advanced open-source models with 96% generation accuracy, reducing costs by 80%. Built context-aware messaging AI bot with modern frameworks, reducing manual query handling by 95%.

        - Data Scientist Intern at Consint Solutions Pvt. Ltd. (Apr 2025 – Jul 2025): Built end-to-end VLM pipeline for passport entity extraction, improving accuracy from 30.45% to 98.06%.

        - AI-ML Trainee at Global Infoventures Pvt. Ltd. (NVIDIA Partnership) (Dec 2023 – Jun 2024): Annotated 5500+ images using Roboflow and applied augmentation techniques. Fine-tuned YOLOv7 for multiple projects achieving 95% accuracy.

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
        - GATE Qualified 2025 (Computer Science & Data Science/AI) 
        - Research Paper accepted in Journal of Analytical Science and Technology (JAST)
        - 1st Runner-Up in Ideathon 1.0 & 2.0 competitions
        - Google Cloud Arcade AI & GenAI skill badges 2025
        - NVIDIA AI Summit Mumbai 2024 attendee
        - Multiple successful AI/ML project deployments

        Contact Information: 
        Email: 17ishikajain@gmail.com
        LinkedIn: ishika-jain-987635238  
        Location: Noida, Delhi NCR, India
        Availability: Open for full-time opportunities and freelance projects globally
        """
    
    def simple_search(self, query: str) -> str:
        """Simple keyword-based search for serverless deployment"""
        query_lower = query.lower()
        
        # Education queries
        if any(word in query_lower for word in ['education', 'degree', 'study', 'college', 'university', 'qualification']):
            return "Ishika holds a Bachelor of Technology (B.Tech) in Computer Science and Engineering with specialization in AI/ML. She's GATE Qualified 2025 in Computer Science & Data Science/AI."
        
        # Programming/Skills queries
        if any(word in query_lower for word in ['programming', 'languages', 'skills', 'technical', 'python', 'code']):
            return "Ishika's technical skills include:\n• Programming: Python (Expert), SQL, JavaScript\n• AI/ML: PyTorch, TensorFlow, OpenCV, YOLOv7/8\n• Cloud: AWS, Docker, Flask, FastAPI\n• Databases: MySQL, ChromaDB"
        
        # Experience queries
        if any(word in query_lower for word in ['experience', 'work', 'job', 'career', 'company']):
            return "Ishika has 1+ years of AI/ML experience:\n• Current: AI/ML Engineer at Edysor Edutech (96% accuracy AI avatars)\n• Previous: Data Scientist at Consint Solutions (98% OCR accuracy)\n• Trainee: AI-ML at Global Infoventures (NVIDIA Partnership)"
        
        # Projects queries
        if any(word in query_lower for word in ['projects', 'built', 'created', 'developed']):
            return "Key projects:\n• Smart Glasses for Visually Impaired\n• VLM-RAG OCR System (98% accuracy)\n• Digital Human AI Avatar\n• Face Recognition Attendance System\n• PPE Detection System"
        
        # Contact queries
        if any(word in query_lower for word in ['contact', 'email', 'reach', 'hire', 'available']):
            return "📧 Email: 17ishikajain@gmail.com\n🔗 LinkedIn: ishika-jain-987635238\n📍 Location: Noida, Delhi NCR\n✅ Available for full-time & freelance opportunities globally"
        
        # Achievements queries
        if any(word in query_lower for word in ['achievement', 'award', 'recognition', 'gate', 'paper']):
            return "🏆 Achievements:\n• GATE Qualified 2025 (CS & Data Science/AI)\n• Research Paper in JAST Journal\n• 1st Runner-Up in Ideathon competitions\n• Google Cloud AI badges\n• NVIDIA AI Summit attendee"
        
        # Default response
        return "Ishika is an AI/ML Engineer with 1+ years experience in production-ready AI solutions, specialized in conversational AI avatars and vision-language models. Ask about her education, skills, experience, or projects!"
    
    def generate_response(self, query: str) -> str:
        """Generate response using OpenAI or fallback"""
        try:
            if OPENAI_AVAILABLE and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are Ishika's AI assistant. Give SHORT, CLEAR answers about her background. Use bullet points when listing multiple items. Keep responses under 3-4 sentences. Be conversational and friendly."
                        },
                        {
                            "role": "user", 
                            "content": f"About Ishika:\n{self.resume_data}\n\nQ: {query}\n\nProvide a concise, friendly answer:"
                        }
                    ],
                    max_tokens=150,
                    temperature=0.2
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