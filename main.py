#!/usr/bin/env python3
"""
SpaceTraders Terminal UI - Main Entry Point

A comprehensive terminal user interface for managing your SpaceTraders account,
including fleet management, contract automation, and resource management.

Usage:
    python main.py

Prerequisites:
    - Set SPACETRADERS_TOKEN environment variable with your API token
    - Install dependencies: pip install -r requirements.txt

Features:
    - Interactive dashboard with account overview
    - Ship fleet management with automation
    - Contract management and automation
    - Smart navigation (orbit/dock requirements)
    - Resource management and auto-refuel
    - Coordinate-based pathfinding
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from terminal_ui.app import main

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("SPACETRADERS_TOKEN"):
        print("❌ Error: SPACETRADERS_TOKEN environment variable not set")
        print()
        print("Please set your SpaceTraders API token:")
        print("  export SPACETRADERS_TOKEN='your_token_here'")
        print()
        print("If you don't have a token, you can register a new agent at:")
        print("  https://spacetraders.io/")
        print()
        print("Or use the example.py script to register programmatically.")
        sys.exit(1)
    
    # Print welcome message
    print("🚀 SpaceTraders Terminal UI")
    print("=" * 50)
    print("Starting the terminal user interface...")
    print("Press 'q' to quit at any time")
    print()
    
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)