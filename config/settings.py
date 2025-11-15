"""
Configuration settings for the Speech Translation System
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Azure Speech Services
    azure_speech_key: str
    azure_speech_region: str
    
    # Azure OpenAI
    azure_openai_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_api_version: str = "2023-12-01-preview"
    
    # Azure Translator (Optional)
    azure_translator_key: str = ""
    azure_translator_region: str = ""
    
    # Application Settings
    log_level: str = "INFO"
    max_audio_duration: int = 300
    sample_rate: int = 16000
    audio_chunk_size: int = 1024
    
    # OTT Platform Settings
    ott_stream_url: str = ""
    ott_api_key: str = ""
    
    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Performance Settings
    max_concurrent_translations: int = 10
    translation_timeout: int = 30
    buffer_size: int = 4096
    
    # Supported Languages
    supported_languages: List[str] = [
        "en-US",  # English
        "hi-IN",  # Hindi
        "es-ES",  # Spanish
        "fr-FR",  # French
        "de-DE",  # German
        "it-IT",  # Italian
        "pt-BR",  # Portuguese
        "ja-JP",  # Japanese
        "ko-KR",  # Korean
        "zh-CN",  # Chinese (Simplified)
        "ar-SA",  # Arabic
        "ru-RU",  # Russian
        "tr-TR",  # Turkish
        "nl-NL",  # Dutch
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
