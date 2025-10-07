from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # AI Models
    TEXT_MODEL_NAME: str = "Qwen/Qwen2-7B-Instruct"
    TEXT_MODEL_DEVICE: str = "cpu"
    IMAGE_MODEL_NAME: str = "stabilityai/stable-diffusion-xl-base-1.0"
    IMAGE_MODEL_DEVICE: str = "cpu"
    
    # External APIs
    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    
    # Story Configuration
    MAX_STORY_LENGTH: int = 10000
    MAX_CONTEXT_LENGTH: int = 4000
    DEFAULT_GENRE: str = "fantasy"
    
    # File Storage
    STORIES_PATH: str = "./data/stories"
    IMAGES_PATH: str = "./data/images"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"

settings = Settings()