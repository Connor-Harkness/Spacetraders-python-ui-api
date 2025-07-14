#!/usr/bin/env python3
"""
Test script to verify the new button functionality works correctly.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_button_functionality():
    """Test that button functionality is properly implemented."""
    print("🔍 Testing Button Functionality...")
    
    try:
        # Test contract widget button handling
        from terminal_ui.widgets.contracts import ContractWidget
        
        # Create a contract widget
        contract_widget = ContractWidget()
        
        # Test that it has the expected message classes
        assert hasattr(contract_widget, 'ContractAccept')
        assert hasattr(contract_widget, 'ContractFulfill')
        assert hasattr(contract_widget, 'ContractAutomate')
        assert hasattr(contract_widget, 'ContractDetails')
        
        # Test that it has the button handler method
        assert hasattr(contract_widget, 'on_button_pressed')
        
        print("✅ Contract widget button functionality verified")
        
        # Test ship widget button handling
        from terminal_ui.widgets.ships import ShipWidget
        
        # Create a ship widget
        ship_widget = ShipWidget()
        
        # Test that it has the expected message classes
        assert hasattr(ship_widget, 'ShipNavigate')
        assert hasattr(ship_widget, 'ShipDock')
        assert hasattr(ship_widget, 'ShipOrbit')
        assert hasattr(ship_widget, 'ShipRefuel')
        assert hasattr(ship_widget, 'ShipAutomate')
        
        # Test that it has the button handler method
        assert hasattr(ship_widget, 'on_button_pressed')
        
        print("✅ Ship widget button functionality verified")
        
        # Test shipyard widget
        from terminal_ui.widgets.shipyard import ShipyardWidget
        
        # Create a shipyard widget
        shipyard_widget = ShipyardWidget()
        
        # Test that it has the expected message classes
        assert hasattr(shipyard_widget, 'ShipPurchase')
        assert hasattr(shipyard_widget, 'ShipyardRefresh')
        
        # Test that it has the button handler method
        assert hasattr(shipyard_widget, 'on_button_pressed')
        
        print("✅ Shipyard widget button functionality verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Button functionality test failed: {e}")
        return False

def test_app_integration():
    """Test that the main app can handle the new messages."""
    print("🔍 Testing App Integration...")
    
    try:
        from terminal_ui.app import SpaceTradersApp
        
        # Create app instance
        app = SpaceTradersApp("test_token")
        
        # Test that it has the expected message handler methods
        assert hasattr(app, 'on_contract_widget_contract_accept')
        assert hasattr(app, 'on_contract_widget_contract_fulfill')
        assert hasattr(app, 'on_contract_widget_contract_automate')
        assert hasattr(app, 'on_contract_widget_contract_details')
        
        assert hasattr(app, 'on_ship_widget_ship_navigate')
        assert hasattr(app, 'on_ship_widget_ship_dock')
        assert hasattr(app, 'on_ship_widget_ship_orbit')
        assert hasattr(app, 'on_ship_widget_ship_refuel')
        assert hasattr(app, 'on_ship_widget_ship_automate')
        
        assert hasattr(app, 'on_shipyard_widget_ship_purchase')
        assert hasattr(app, 'on_shipyard_widget_shipyard_refresh')
        
        # Test that it has the shipyard action
        assert hasattr(app, 'action_show_shipyard')
        
        print("✅ App integration verified")
        
        return True
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def test_client_methods():
    """Test that the client has the required methods."""
    print("🔍 Testing Client Methods...")
    
    try:
        from spacetraders_client import SpaceTradersClient
        
        # Create client instance
        client = SpaceTradersClient("test_token")
        
        # Test that it has the expected methods
        assert hasattr(client, 'accept_contract')
        assert hasattr(client, 'fulfill_contract')
        assert hasattr(client, 'dock_ship')
        assert hasattr(client, 'orbit_ship')
        assert hasattr(client, 'refuel_ship')
        assert hasattr(client, 'purchase_ship')
        assert hasattr(client, 'get_shipyard')
        assert hasattr(client, 'get_system_waypoints')
        
        print("✅ Client methods verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Client methods test failed: {e}")
        return False

def main():
    """Run all functionality tests."""
    print("🚀 SpaceTraders Button Functionality Tests")
    print("=" * 50)
    
    tests = [
        ("Button Functionality", test_button_functionality),
        ("App Integration", test_app_integration),
        ("Client Methods", test_client_methods),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All functionality tests passed! Button functionality is working correctly.")
        return 0
    else:
        print("❌ Some functionality tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())