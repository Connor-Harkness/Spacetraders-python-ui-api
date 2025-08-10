#!/usr/bin/env python3
"""
SpaceTraders WebUI - Standalone Web Application

A standalone web interface for the SpaceTraders API.
"""

import os
import sys
from pathlib import Path

# Add the webui directory to the Python path
webui_dir = Path(__file__).parent
sys.path.insert(0, str(webui_dir))

def main():
    """Main entry point for the WebUI application."""
    from config import Config
    from app import app, initialize_client
    
    # Load environment variables from .env file if it exists
    from dotenv import load_dotenv
    load_dotenv()
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        print("Please set your SpaceTraders API token:")
        print("  export SPACETRADERS_TOKEN='your_token_here'")
        print()
        print("Or create a .env file in the webui directory with:")
        print("  SPACETRADERS_TOKEN=your_token_here")
        print()
        print("If you don't have a token, register at: https://spacetraders.io/")
        return 1
    
    # Initialize the API client
    initialize_client()
    
    # Print startup information
    print("🚀 SpaceTraders WebUI")
    print("=" * 50)
    print(f"Starting web server on http://{Config.HOST}:{Config.PORT}")
    print(f"Rate limiting: {Config.RATE_LIMIT_REQUESTS} requests per {Config.RATE_LIMIT_WINDOW} seconds")
    print(f"Auto-refresh interval: {Config.REFRESH_INTERVAL} seconds")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Run the Flask application
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True  # Enable threading for better concurrent request handling
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())