"""
Production configuration for KrishiSetu API
"""
import os
from typing import List

class Settings:
    # API Configuration
    API_TITLE = "KrishiSetu API"
    API_DESCRIPTION = "Crop Disease and Pest Detection API"
    API_VERSION = "1.0.0"
    
    # Security
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # File Upload Limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = 10  # requests per minute
    RATE_LIMIT_WINDOW = 60    # seconds
    
    # Model Paths
    MODEL_DIR = "model"
    PEST_MODEL_PATH = os.path.join(MODEL_DIR, "pest_model_b0.pth")
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "app.log"
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "models/gemini-1.5-flash"
    GEMINI_RETRY_ATTEMPTS = 3
    GEMINI_RETRY_DELAY = 15  # seconds

# Production-specific settings
class ProductionSettings(Settings):
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ALLOWED_ORIGINS = []  # Must be configured for production
    
    # Enhanced security for production
    RATE_LIMIT_REQUESTS = 5  # More restrictive
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB for production

# Get settings based on environment
def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProductionSettings()
    return Settings()

settings = get_settings()