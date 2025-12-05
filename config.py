"""
Configuration settings for the Legal Drafting LLM system
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Configuration
    API_TITLE = "Legal Drafting LLM"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "AI-powered legal document generation system"
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # gemini, llama, mistral
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
    LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "")
    
    # RAG Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "data/embeddings/legal_clauses")
    CLAUSE_DATABASE_PATH = "data/legal_clauses"
    
    # Document Generation
    TEMPLATE_DIR = "templates"
    OUTPUT_DIR = "generated_documents"
    TEMP_DIR = "/tmp/legal_docs"
    
    # API Settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    RATE_LIMIT_PER_MINUTE = 60
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "logs/legal_drafting.log"
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when using Gemini")
        
        # Create necessary directories
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs("logs", exist_ok=True)

# Validate configuration on import
try:
    Config.validate_config()
except ValueError as e:
    print(f"Configuration error: {e}")