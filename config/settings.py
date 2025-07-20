"""Configuration settings for the resume formatting application."""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Google Gemini Configuration
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_temperature: float = 0.1
    gemini_max_tokens: int = 4000
    
    # Application Configuration
    app_name: str = "Resume Formatter LLM"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # File Processing
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_formats: list = [".pdf", ".docx", ".doc"]
    output_dir: str = "output"
    
    # Processing Options
    default_template_style: str = "professional"
    enable_content_enhancement: bool = True
    enable_ats_optimization: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 