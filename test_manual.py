#!/usr/bin/env python3
"""
Manual test script to verify the UI components display correctly.
"""

import sys
import os
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_mock_contract():
    """Create a mock contract for testing."""
    mock_contract = Mock()
    mock_contract.id = "test-contract-123"
    mock_contract.type = "PROCURE"
    mock_contract.accepted = False
    mock_contract.fulfilled = False
    mock_contract.factionSymbol = "COSMIC"
    
    # Mock terms
    mock_terms = Mock()
    mock_payment = Mock()
    mock_payment.onAccepted = 50000
    mock_payment.onFulfilled = 100000
    mock_terms.payment = mock_payment
    
    mock_delivery = Mock()
    mock_delivery.tradeSymbol = "IRON_ORE"
    mock_delivery.destinationSymbol = "X1-TEST-A1"
    mock_delivery.unitsFulfilled = 0
    mock_delivery.unitsRequired = 100
    mock_terms.deliver = [mock_delivery]
    
    from datetime import datetime, timezone, timedelta
    mock_terms.deadline = datetime.now(timezone.utc) + timedelta(days=7)
    
    mock_contract.terms = mock_terms
    return mock_contract

def create_mock_ship():
    """Create a mock ship for testing."""
    mock_ship = Mock()
    mock_ship.symbol = "TEST-SHIP-1"
    
    # Mock registration
    mock_registration = Mock()
    mock_registration.role = "COMMAND"
    mock_ship.registration = mock_registration
    
    # Mock navigation
    mock_nav = Mock()
    mock_nav.status = "DOCKED"
    mock_nav.waypointSymbol = "X1-TEST-A1"
    mock_nav.systemSymbol = "X1-TEST"
    mock_ship.nav = mock_nav
    
    # Mock fuel
    mock_fuel = Mock()
    mock_fuel.current = 800
    mock_fuel.capacity = 1000
    mock_ship.fuel = mock_fuel
    
    # Mock cargo
    mock_cargo = Mock()
    mock_cargo.units = 50
    mock_cargo.capacity = 100
    mock_ship.cargo = mock_cargo
    
    # Mock frame, engine, reactor
    mock_frame = Mock()
    mock_frame.name = "Frame Mount I"
    mock_ship.frame = mock_frame
    
    mock_engine = Mock()
    mock_engine.name = "Engine Impulse Drive I"
    mock_ship.engine = mock_engine
    
    mock_reactor = Mock()
    mock_reactor.name = "Reactor Solar I"
    mock_ship.reactor = mock_reactor
    
    return mock_ship

def create_mock_shipyard():
    """Create a mock shipyard for testing."""
    mock_shipyard = Mock()
    mock_shipyard.symbol = "X1-TEST-A1"
    mock_shipyard.modificationsFee = 5000
    
    # Mock ship types
    mock_ship_type = Mock()
    mock_ship_type.value = "SHIP_PROBE"
    mock_shipyard.shipTypes = [mock_ship_type]
    
    # Mock available ships
    mock_ship = Mock()
    mock_ship.type = mock_ship_type
    mock_ship.name = "Probe"
    mock_ship.description = "A small exploration vessel"
    mock_ship.purchasePrice = 75000
    mock_ship.supply = Mock()
    mock_ship.supply.value = "ABUNDANT"
    
    mock_ship.frame = Mock()
    mock_ship.frame.name = "Frame Probe"
    mock_ship.reactor = Mock()
    mock_ship.reactor.name = "Reactor Solar I"
    mock_ship.engine = Mock()
    mock_ship.engine.name = "Engine Impulse Drive I"
    mock_ship.modules = []
    mock_ship.mounts = []
    mock_ship.crew = Mock()
    
    mock_shipyard.ships = [mock_ship]
    mock_shipyard.transactions = []
    
    return mock_shipyard

def create_mock_system():
    """Create a mock system for testing."""
    mock_system = Mock()
    mock_system.symbol = "X1-TEST"
    mock_system.type = "NEUTRON_STAR"
    mock_system.sectorSymbol = "X1"
    mock_system.x = 0
    mock_system.y = 0
    mock_system.waypoints = []
    mock_system.factions = []
    return mock_system

async def test_contract_widget():
    """Test the contract widget with mock data."""
    print("🔍 Testing Contract Widget...")
    
    try:
        from terminal_ui.widgets.contracts import ContractWidget
        
        # Create widget
        widget = ContractWidget()
        
        # Create mock contract
        mock_contract = create_mock_contract()
        
        # Test the card creation
        card = widget.create_contract_card(mock_contract)
        
        print("✅ Contract widget can create cards successfully")
        
        # Test with accepted contract
        mock_contract.accepted = True
        card = widget.create_contract_card(mock_contract)
        
        print("✅ Contract widget handles accepted contracts")
        
        return True
        
    except Exception as e:
        print(f"❌ Contract widget test failed: {e}")
        return False

async def test_ship_widget():
    """Test the ship widget with mock data."""
    print("🔍 Testing Ship Widget...")
    
    try:
        from terminal_ui.widgets.ships import ShipWidget
        
        # Create widget
        widget = ShipWidget()
        
        # Create mock ship
        mock_ship = create_mock_ship()
        
        # Test the card creation
        card = widget.create_ship_card(mock_ship)
        
        print("✅ Ship widget can create cards successfully")
        
        # Test with different ship statuses
        mock_ship.nav.status = "IN_TRANSIT"
        card = widget.create_ship_card(mock_ship)
        
        print("✅ Ship widget handles different ship statuses")
        
        return True
        
    except Exception as e:
        print(f"❌ Ship widget test failed: {e}")
        return False

async def test_shipyard_widget():
    """Test the shipyard widget with mock data."""
    print("🔍 Testing Shipyard Widget...")
    
    try:
        from terminal_ui.widgets.shipyard import ShipyardWidget
        
        # Create widget
        widget = ShipyardWidget()
        
        # Create mock data
        mock_system = create_mock_system()
        mock_shipyard = create_mock_shipyard()
        
        # Test the card creation
        card = widget.create_shipyard_card("X1-TEST-A1", mock_shipyard)
        
        print("✅ Shipyard widget can create cards successfully")
        
        # Test system selector
        selector = widget.create_system_selector()
        
        print("✅ Shipyard widget can create system selector")
        
        return True
        
    except Exception as e:
        print(f"❌ Shipyard widget test failed: {e}")
        return False

async def test_widgets():
    """Test all widget functionality."""
    print("🚀 SpaceTraders Widget Manual Tests")
    print("=" * 50)
    
    tests = [
        ("Contract Widget", test_contract_widget),
        ("Ship Widget", test_ship_widget),
        ("Shipyard Widget", test_shipyard_widget),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if await test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All widget tests passed! UI components are working correctly.")
        return 0
    else:
        print("❌ Some widget tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(test_widgets()))