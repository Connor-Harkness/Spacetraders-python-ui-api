#!/usr/bin/env python3
"""
Test script for the SpaceTraders WebUI

This script tests the basic functionality of the webui without requiring
an actual SpaceTraders API token.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add webui to path
webui_dir = Path(__file__).parent
sys.path.insert(0, str(webui_dir))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from config import Config
        print("✓ Config imported")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from rate_limiter import RateLimiter
        print("✓ RateLimiter imported")
    except Exception as e:
        print(f"✗ RateLimiter import failed: {e}")
        return False
    
    try:
        from api_client import SpaceTradersAPIClient
        print("✓ SpaceTradersAPIClient imported")
    except Exception as e:
        print(f"✗ SpaceTradersAPIClient import failed: {e}")
        return False
    
    try:
        from app import app
        print("✓ Flask app imported")
    except Exception as e:
        print(f"✗ Flask app import failed: {e}")
        return False
    
    return True

def test_rate_limiter():
    """Test the rate limiter functionality."""
    print("\\nTesting rate limiter...")
    
    try:
        from rate_limiter import RateLimiter
        import time
        
        # Create a rate limiter that allows 2 requests per second
        limiter = RateLimiter(max_requests=2, time_window=1.0)
        
        # Test that we can make 2 requests quickly
        start_time = time.time()
        
        async def test_requests():
            await limiter.acquire()
            await limiter.acquire()
            elapsed = time.time() - start_time
            
            # Should be fast for the first 2 requests
            if elapsed < 0.1:
                print("✓ First 2 requests processed quickly")
                return True
            else:
                print(f"✗ First 2 requests took too long: {elapsed:.2f}s")
                return False
        
        # Run the async test
        result = asyncio.run(test_requests())
        return result
        
    except Exception as e:
        print(f"✗ Rate limiter test failed: {e}")
        return False

def test_app_creation():
    """Test Flask app creation."""
    print("\\nTesting Flask app creation...")
    
    try:
        from app import create_app
        
        # Set a dummy token to avoid validation error
        os.environ['SPACETRADERS_TOKEN'] = 'test-token'
        
        app = create_app()
        
        if app is not None:
            print("✓ Flask app created successfully")
            return True
        else:
            print("✗ Flask app creation returned None")
            return False
            
    except Exception as e:
        print(f"✗ Flask app creation failed: {e}")
        return False

def test_config_validation():
    """Test configuration validation."""
    print("\\nTesting configuration validation...")
    
    try:
        from config import Config
        
        # Test with no token (should fail)
        original_token = os.environ.get('SPACETRADERS_TOKEN')
        if 'SPACETRADERS_TOKEN' in os.environ:
            del os.environ['SPACETRADERS_TOKEN']
        
        try:
            Config.validate()
            print("✗ Config validation should have failed without token")
            return False
        except ValueError:
            print("✓ Config validation correctly rejects missing token")
        
        # Test with token (should pass)
        os.environ['SPACETRADERS_TOKEN'] = 'test-token'
        try:
            Config.validate()
            print("✓ Config validation passes with token")
        except Exception as e:
            print(f"✗ Config validation failed with token: {e}")
            return False
        
        # Restore original token
        if original_token:
            os.environ['SPACETRADERS_TOKEN'] = original_token
        elif 'SPACETRADERS_TOKEN' in os.environ:
            del os.environ['SPACETRADERS_TOKEN']
        
        return True
        
    except Exception as e:
        print(f"✗ Config validation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 SpaceTraders WebUI Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_rate_limiter,
        test_config_validation,
        test_app_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WebUI is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())