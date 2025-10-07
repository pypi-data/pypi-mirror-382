"""
Configuration Management for OS Forge

Centralized configuration settings and environment variables.
"""

import os
from typing import List


class Config:
    """
    Application configuration settings
    """
    
    # API Configuration
    API_TITLE = "OS Forge"
    API_DESCRIPTION = "Multi-Platform System Hardening Tool with Security Validation"
    API_VERSION = "1.0.0"
    
    # Security Configuration
    API_KEY = os.getenv("OS_FORGE_API_KEY", "dev-key-change-in-production")
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./os_forge.db")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://frontend:3000"
    ]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("POLICY_GUARD_LOG_LEVEL", "INFO")
    
    # Server Configuration
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8000
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS origins from environment or use defaults"""
        env_origins = os.getenv("POLICY_GUARD_CORS_ORIGINS")
        if env_origins:
            return env_origins.split(",")
        return cls.CORS_ORIGINS

