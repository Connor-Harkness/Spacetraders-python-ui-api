"""
Configuration settings for the SpaceTraders WebUI.
"""

import os
from typing import Optional

class Config:
    """Configuration class for the WebUI application."""
    
    # SpaceTraders API settings
    SPACETRADERS_BASE_URL = "https://api.spacetraders.io/v2"
    SPACETRADERS_TOKEN: Optional[str] = os.getenv("SPACETRADERS_TOKEN")
    
    # Rate limiting settings (SpaceTraders allows 2 requests per second)
    RATE_LIMIT_REQUESTS = 2
    RATE_LIMIT_WINDOW = 1.0  # seconds
    
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    PORT = int(os.getenv("PORT", "5000"))
    HOST = os.getenv("HOST", "127.0.0.1")
    
    # UI settings
    APP_NAME = "SpaceTraders WebUI"
    REFRESH_INTERVAL = 30  # seconds
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration settings."""
        # Re-read the environment variable in case it was set after import
        cls.SPACETRADERS_TOKEN = os.getenv("SPACETRADERS_TOKEN")
        if not cls.SPACETRADERS_TOKEN:
            raise ValueError(
                "SPACETRADERS_TOKEN environment variable is required. "
                "Please set it to your SpaceTraders API token."
            )