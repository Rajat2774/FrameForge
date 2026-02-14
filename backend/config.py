import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Configuration
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_MODEL")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS Configuration
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # File Paths
    temp_dir: str = Field(default="../runtime/temp", env="TEMP_DIR")
    output_dir: str = Field(default="../runtime/outputs", env="OUTPUT_DIR")
    
    # Rendering Configuration
    manim_quality: str = Field(default="l", env="MANIM_QUALITY")  # l, m, h, k
    manim_format: str = Field(default="mp4", env="MANIM_FORMAT")
    render_timeout: int = Field(default=300, env="RENDER_TIMEOUT")  # seconds
    
    # Code Generation
    llm_temperature: float = Field(default=0.2, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    llm_retry_attempts: int = Field(default=3, env="LLM_RETRY_ATTEMPTS")
    
    # Validation
    strict_validation: bool = Field(default=True, env="STRICT_VALIDATION")
    max_code_length: int = Field(default=10000, env="MAX_CODE_LENGTH")
    
    # Cleanup
    cleanup_enabled: bool = Field(default=True, env="CLEANUP_ENABLED")
    cleanup_max_age_hours: int = Field(default=24, env="CLEANUP_MAX_AGE_HOURS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings():
    """Force reload settings from environment."""
    global _settings
    _settings = None
    return get_settings()