import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Google and Pinecone API settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    
    # Pinecone and Embedding Configuration
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'schedule')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'models/embedding-001')
    JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', './test.json')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret_key')
    ENV = os.getenv('FLASK_ENV', 'production')
