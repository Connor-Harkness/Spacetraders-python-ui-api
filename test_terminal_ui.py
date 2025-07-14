#!/usr/bin/env python3
"""
Test script to verify the terminal UI components are working correctly.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all components can be imported."""
    try:
        from terminal_ui.app import SpaceTradersApp
        print("✅ Terminal UI app import successful")
    except ImportError as e:
        print(f"❌ Terminal UI app import failed: {e}")
        return False
    
    try:
        from automation import AutomationManager, ShipAutomation, ContractAutomation
        print("✅ Automation components import successful")
    except ImportError as e:
        print(f"❌ Automation components import failed: {e}")
        return False
    
    try:
        from utils import calculate_distance, format_credits, validate_ship_for_task
        print("✅ Utility functions import successful")
    except ImportError as e:
        print(f"❌ Utility functions import failed: {e}")
        return False
    
    try:
        from spacetraders_client import SpaceTradersClient
        print("✅ SpaceTraders client import successful")
    except ImportError as e:
        print(f"❌ SpaceTraders client import failed: {e}")
        return False
    
    return True

def test_terminal_ui_creation():
    """Test that the terminal UI can be created."""
    try:
        from terminal_ui.app import SpaceTradersApp
        
        # Test with dummy token
        app = SpaceTradersApp("test_token")
        print("✅ Terminal UI app creation successful")
        return True
    except Exception as e:
        print(f"❌ Terminal UI app creation failed: {e}")
        return False

def test_automation_manager():
    """Test automation manager creation."""
    try:
        from automation import AutomationManager
        from spacetraders_client import SpaceTradersClient
        
        # Test with dummy client
        client = SpaceTradersClient("test_token")
        manager = AutomationManager(client)
        print("✅ Automation manager creation successful")
        return True
    except Exception as e:
        print(f"❌ Automation manager creation failed: {e}")
        return False

def test_utilities():
    """Test utility functions."""
    try:
        from utils import calculate_distance, format_credits
        
        # Test coordinate calculation
        distance = calculate_distance(0, 0, 3, 4)
        assert distance == 5.0
        print("✅ Coordinate calculation working")
        
        # Test credit formatting
        formatted = format_credits(1000000)
        assert "M" in formatted
        print("✅ Credit formatting working")
        
        return True
    except Exception as e:
        print(f"❌ Utility functions test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 SpaceTraders Terminal UI - Component Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Terminal UI Creation", test_terminal_ui_creation),
        ("Automation Manager", test_automation_manager),
        ("Utility Functions", test_utilities)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The terminal UI is ready to use.")
        print("\\nTo run the application:")
        print("1. Set your token: export SPACETRADERS_TOKEN='your_token'")
        print("2. Run: python main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())