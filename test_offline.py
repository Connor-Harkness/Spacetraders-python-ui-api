#!/usr/bin/env python3
"""
Offline test script for SpaceTraders application.
Tests functionality that doesn't require network access.

This script validates:
- UI components with mock data
- Automation systems structure
- Utility functions
- Error handling
- Component integration
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock
import traceback

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test API key provided in the issue
TEST_API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGlmaWVyIjoiVk9JRF9JTkRfMDEiLCJ2ZXJzaW9uIjoidjIuMy4wIiwicmVzZXRfZGF0ZSI6IjIwMjUtMDctMTMiLCJpYXQiOjE3NTI0OTA2MjMsInN1YiI6ImFnZW50LXRva2VuIn0.ntRp0IL6AUcG-ASZamll5AQBh9C_apXgQUL6OGiS--EjUAGyQqs8XATpPhMG7J-aWPZZG6ywkOT_7C1PaHCxbzLC19-kstLi3rICAMvbeQAMGahMT4WKnL7prVq5g0VKebVwh6H8cQKFxx1kIJ8OV_CTC7XWvek63FZxeA5T0qcDas9wI_GFW2uroSozT7MBnmnDnd1UncQf2rQVM_dhFONdJzgAxrRyaCu_Gf3rW5LWd8xXdeHHUbD6U7ONI8pt5gx_SJkRz4sRM11ANjiyy2p9LQ9paG2uYxPZ6b76sKxd9hdHvPK0TBBpxbcvHBUQE5b7agaBTGP0AZwQdSNIsXXLO29Xu6WGJqxjc6YFGJI-Ln-mQrUNPhJUnLxbh_R2Wfm2mVDSTO49MkK5Y7ZKcp7kF6WKB3Tiium35e2gRT5j9KNPii9TH8Ly49ftkEQXMlGakXLzu16GBIqwyfW-fy-eLeGoCNum7tCWTO5CDYCi0phVcNzlE0xeC37JfCXJEU29Bv6BKb02T3k_1F34nm9Ucj9XMjnib_v7VVI8FGm3n_AqM--cI-Ql-1Sl1eJBJBPN5oZJHmatwfm97dfKnVuJaDsLyBe9tkt7nFbbZc7xVOljRdTU2ITnnDXlFZaQUTaySc-aetwBn4kg2KQoWKkoidquV_4fwATbr4mogkg"

class OfflineTestRunner:
    """Test runner for offline functionality testing."""
    
    def __init__(self):
        self.passed_tests = 0
        self.total_tests = 0
        self.test_results = []
        
    def log_test_result(self, test_name, passed, message=""):
        """Log a test result."""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}")
            if message:
                print(f"   {message}")
        else:
            print(f"❌ {test_name}")
            if message:
                print(f"   {message}")
        
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message
        })
    
    def create_mock_agent(self):
        """Create a mock agent for testing."""
        mock_agent = Mock()
        mock_agent.symbol = "VOID_IND_01"
        mock_agent.headquarters = "X1-ZZ9-A1"
        mock_agent.credits = 150000
        mock_agent.shipCount = 3
        mock_agent.startingFaction = "COSMIC"
        return mock_agent
    
    def create_mock_ship(self):
        """Create a mock ship for testing."""
        mock_ship = Mock()
        mock_ship.symbol = "VOID_IND_01-1"
        
        # Mock registration
        mock_registration = Mock()
        mock_registration.role = "COMMAND"
        mock_ship.registration = mock_registration
        
        # Mock navigation
        mock_nav = Mock()
        mock_nav.status = "DOCKED"
        mock_nav.waypointSymbol = "X1-ZZ9-A1"
        mock_nav.systemSymbol = "X1-ZZ9"
        mock_ship.nav = mock_nav
        
        # Mock fuel
        mock_fuel = Mock()
        mock_fuel.current = 800
        mock_fuel.capacity = 1000
        mock_ship.fuel = mock_fuel
        
        # Mock cargo
        mock_cargo = Mock()
        mock_cargo.units = 30
        mock_cargo.capacity = 100
        mock_cargo.inventory = []
        mock_ship.cargo = mock_cargo
        
        # Mock components
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
    
    def create_mock_contract(self):
        """Create a mock contract for testing."""
        mock_contract = Mock()
        mock_contract.id = "contract-void-001"
        mock_contract.type = "PROCURE"
        mock_contract.accepted = True
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
        mock_delivery.destinationSymbol = "X1-ZZ9-B1"
        mock_delivery.unitsFulfilled = 20
        mock_delivery.unitsRequired = 100
        mock_terms.deliver = [mock_delivery]
        
        mock_terms.deadline = datetime.now(timezone.utc) + timedelta(days=5)
        mock_contract.terms = mock_terms
        
        return mock_contract
    
    def create_mock_system(self):
        """Create a mock system for testing."""
        mock_system = Mock()
        mock_system.symbol = "X1-ZZ9"
        mock_system.type = "NEUTRON_STAR"
        mock_system.sectorSymbol = "X1"
        mock_system.x = 10
        mock_system.y = -5
        mock_system.waypoints = []
        mock_system.factions = []
        return mock_system
    
    async def test_client_initialization(self):
        """Test that the client can be initialized."""
        print("\n🔍 Testing Client Initialization...")
        
        try:
            from spacetraders_client import SpaceTradersClient
            
            # Test client initialization
            client = SpaceTradersClient(TEST_API_KEY)
            
            self.log_test_result(
                "Client Creation",
                client is not None,
                "Client initialized successfully"
            )
            
            self.log_test_result(
                "Token Configuration",
                client.token == TEST_API_KEY,
                "Token properly configured"
            )
            
            self.log_test_result(
                "Base URL Configuration",
                client.base_url == "https://api.spacetraders.io/v2",
                f"Base URL: {client.base_url}"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Client Initialization",
                False,
                f"Client initialization failed: {str(e)}"
            )
            return False
    
    async def test_terminal_ui_components(self):
        """Test terminal UI components with mock data."""
        print("\n🔍 Testing Terminal UI Components...")
        
        try:
            # Test contract widget
            from terminal_ui.widgets.contracts import ContractWidget
            
            contract_widget = ContractWidget()
            mock_contract = self.create_mock_contract()
            
            # Test contract card creation
            contract_card = contract_widget.create_contract_card(mock_contract)
            
            self.log_test_result(
                "Contract Widget",
                contract_card is not None,
                f"Contract card created for {mock_contract.id}"
            )
            
            # Test contract list display
            contracts_display = contract_widget.create_contracts_display([mock_contract])
            
            self.log_test_result(
                "Contract List Display",
                contracts_display is not None,
                "Contract list display created"
            )
            
            # Test ship widget
            from terminal_ui.widgets.ships import ShipWidget
            
            ship_widget = ShipWidget()
            mock_ship = self.create_mock_ship()
            
            # Test ship card creation
            ship_card = ship_widget.create_ship_card(mock_ship)
            
            self.log_test_result(
                "Ship Widget",
                ship_card is not None,
                f"Ship card created for {mock_ship.symbol}"
            )
            
            # Test ship list display
            ships_display = ship_widget.create_ships_display([mock_ship])
            
            self.log_test_result(
                "Ship List Display",
                ships_display is not None,
                "Ship list display created"
            )
            
            # Test dashboard widget
            from terminal_ui.widgets.dashboard import DashboardWidget
            
            dashboard_widget = DashboardWidget()
            mock_agent = self.create_mock_agent()
            
            # Test agent info display
            agent_info = dashboard_widget.create_agent_info(mock_agent)
            
            self.log_test_result(
                "Dashboard Widget",
                agent_info is not None,
                f"Agent info display created for {mock_agent.symbol}"
            )
            
            # Test agent widget
            from terminal_ui.widgets.agent import AgentWidget
            
            agent_widget = AgentWidget()
            agent_display = agent_widget.create_agent_display(mock_agent)
            
            self.log_test_result(
                "Agent Widget",
                agent_display is not None,
                "Agent display created"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Terminal UI Components",
                False,
                f"UI component tests failed: {str(e)}"
            )
            return False
    
    async def test_automation_systems(self):
        """Test automation systems structure."""
        print("\n🔍 Testing Automation Systems...")
        
        try:
            # Test automation manager
            from automation import AutomationManager
            from spacetraders_client import SpaceTradersClient
            
            client = SpaceTradersClient(TEST_API_KEY)
            automation_manager = AutomationManager(client)
            
            self.log_test_result(
                "Automation Manager",
                automation_manager is not None,
                "Automation manager created successfully"
            )
            
            # Test ship automation
            from automation import ShipAutomation
            
            mock_ship = self.create_mock_ship()
            ship_automation = ShipAutomation(client, mock_ship)
            
            self.log_test_result(
                "Ship Automation",
                ship_automation is not None,
                f"Ship automation created for {mock_ship.symbol}"
            )
            
            # Test contract automation
            from automation import ContractAutomation
            
            mock_contract = self.create_mock_contract()
            contract_automation = ContractAutomation(client, mock_contract)
            
            self.log_test_result(
                "Contract Automation",
                contract_automation is not None,
                f"Contract automation created for {mock_contract.id}"
            )
            
            # Test navigation system
            from automation import NavigationSystem
            
            navigation_system = NavigationSystem(client)
            
            self.log_test_result(
                "Navigation System",
                navigation_system is not None,
                "Navigation system created successfully"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Automation Systems",
                False,
                f"Automation tests failed: {str(e)}"
            )
            return False
    
    async def test_utility_functions(self):
        """Test utility functions."""
        print("\n🔍 Testing Utility Functions...")
        
        try:
            # Test coordinate calculations
            from utils import calculate_distance, format_credits, validate_ship_for_task
            
            # Test distance calculation
            distance = calculate_distance(0, 0, 3, 4)
            
            self.log_test_result(
                "Distance Calculation",
                distance == 5.0,
                f"Distance (0,0) to (3,4) = {distance}"
            )
            
            # Test credit formatting
            test_credits = 1500000
            formatted_credits = format_credits(test_credits)
            
            self.log_test_result(
                "Credit Formatting",
                formatted_credits is not None,
                f"Credits: {test_credits:,} → {formatted_credits}"
            )
            
            # Test ship validation
            mock_ship = self.create_mock_ship()
            is_valid = validate_ship_for_task(mock_ship, "MINING")
            
            self.log_test_result(
                "Ship Validation",
                is_valid is not None,
                f"Ship {mock_ship.symbol} valid for mining: {is_valid}"
            )
            
            # Test coordinate utilities
            from utils import find_closest_waypoint, calculate_fuel_cost
            
            # Test waypoint finding
            waypoints = [
                Mock(symbol="X1-ZZ9-A1", x=0, y=0),
                Mock(symbol="X1-ZZ9-B1", x=10, y=0),
                Mock(symbol="X1-ZZ9-C1", x=0, y=10),
            ]
            
            closest = find_closest_waypoint(5, 0, waypoints)
            
            self.log_test_result(
                "Closest Waypoint",
                closest is not None,
                f"Closest waypoint: {closest.symbol}"
            )
            
            # Test fuel calculation
            fuel_cost = calculate_fuel_cost(distance)
            
            self.log_test_result(
                "Fuel Calculation",
                fuel_cost >= 0,
                f"Fuel cost for distance {distance}: {fuel_cost}"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Utility Functions",
                False,
                f"Utility function tests failed: {str(e)}"
            )
            return False
    
    async def test_widget_button_functionality(self):
        """Test widget button functionality."""
        print("\n🔍 Testing Widget Button Functionality...")
        
        try:
            # Test contract widget buttons
            from terminal_ui.widgets.contracts import ContractWidget
            
            contract_widget = ContractWidget()
            
            # Check for button message classes
            button_messages = [
                'ContractAccept',
                'ContractFulfill',
                'ContractAutomate',
                'ContractDetails'
            ]
            
            for msg_class in button_messages:
                has_message = hasattr(contract_widget, msg_class)
                self.log_test_result(
                    f"Contract {msg_class} Message",
                    has_message,
                    f"Message class {'exists' if has_message else 'missing'}"
                )
            
            # Test ship widget buttons
            from terminal_ui.widgets.ships import ShipWidget
            
            ship_widget = ShipWidget()
            
            ship_button_messages = [
                'ShipNavigate',
                'ShipDock',
                'ShipOrbit',
                'ShipRefuel',
                'ShipAutomate'
            ]
            
            for msg_class in ship_button_messages:
                has_message = hasattr(ship_widget, msg_class)
                self.log_test_result(
                    f"Ship {msg_class} Message",
                    has_message,
                    f"Message class {'exists' if has_message else 'missing'}"
                )
            
            # Test button press handlers
            has_contract_handler = hasattr(contract_widget, 'on_button_pressed')
            has_ship_handler = hasattr(ship_widget, 'on_button_pressed')
            
            self.log_test_result(
                "Button Press Handlers",
                has_contract_handler and has_ship_handler,
                "Button press handlers exist"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Widget Button Functionality",
                False,
                f"Button functionality tests failed: {str(e)}"
            )
            return False
    
    async def test_app_integration(self):
        """Test main application integration."""
        print("\n🔍 Testing Application Integration...")
        
        try:
            from terminal_ui.app import SpaceTradersApp
            
            # Test app creation
            app = SpaceTradersApp(TEST_API_KEY)
            
            self.log_test_result(
                "App Creation",
                app is not None,
                "Terminal app created successfully"
            )
            
            # Test app configuration
            self.log_test_result(
                "App Configuration",
                app.token == TEST_API_KEY,
                "Token configured correctly"
            )
            
            # Test app methods
            required_methods = [
                'action_refresh',
                'action_toggle_tab',
                'action_show_dashboard',
                'action_show_ships',
                'action_show_contracts',
                'action_show_agent'
            ]
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(app, method):
                    missing_methods.append(method)
            
            self.log_test_result(
                "App Methods",
                len(missing_methods) == 0,
                f"Missing methods: {missing_methods}" if missing_methods else "All methods exist"
            )
            
            # Test message handlers
            message_handlers = [
                'on_contract_widget_contract_accept',
                'on_contract_widget_contract_fulfill',
                'on_contract_widget_contract_automate',
                'on_ship_widget_ship_navigate',
                'on_ship_widget_ship_dock',
                'on_ship_widget_ship_orbit',
                'on_ship_widget_ship_refuel'
            ]
            
            missing_handlers = []
            for handler in message_handlers:
                if not hasattr(app, handler):
                    missing_handlers.append(handler)
            
            self.log_test_result(
                "Message Handlers",
                len(missing_handlers) == 0,
                f"Missing handlers: {missing_handlers}" if missing_handlers else "All handlers exist"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Application Integration",
                False,
                f"App integration tests failed: {str(e)}"
            )
            return False
    
    async def test_error_handling(self):
        """Test error handling capabilities."""
        print("\n🔍 Testing Error Handling...")
        
        try:
            # Test UI with empty data
            from terminal_ui.widgets.contracts import ContractWidget
            
            contract_widget = ContractWidget()
            
            # Test with empty contract list
            empty_display = contract_widget.create_contracts_display([])
            
            self.log_test_result(
                "Empty Contract Data",
                empty_display is not None,
                "UI handles empty contract data"
            )
            
            # Test with empty ship list
            from terminal_ui.widgets.ships import ShipWidget
            
            ship_widget = ShipWidget()
            empty_ships = ship_widget.create_ships_display([])
            
            self.log_test_result(
                "Empty Ship Data",
                empty_ships is not None,
                "UI handles empty ship data"
            )
            
            # Test invalid client initialization
            from spacetraders_client import SpaceTradersClient
            
            try:
                # Test with empty token
                empty_client = SpaceTradersClient("")
                self.log_test_result(
                    "Empty Token Handling",
                    empty_client.token == "",
                    "Client accepts empty token"
                )
            except Exception:
                self.log_test_result(
                    "Empty Token Handling",
                    False,
                    "Client failed with empty token"
                )
            
            # Test utility function edge cases
            from utils import calculate_distance, format_credits
            
            # Test zero distance
            zero_distance = calculate_distance(0, 0, 0, 0)
            self.log_test_result(
                "Zero Distance",
                zero_distance == 0.0,
                f"Zero distance calculation: {zero_distance}"
            )
            
            # Test zero credits
            zero_credits = format_credits(0)
            self.log_test_result(
                "Zero Credits",
                zero_credits is not None,
                f"Zero credits formatting: {zero_credits}"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Error Handling",
                False,
                f"Error handling tests failed: {str(e)}"
            )
            return False
    
    async def test_model_validation(self):
        """Test model validation and data structures."""
        print("\n🔍 Testing Model Validation...")
        
        try:
            # Test agent model
            from spacetraders_client.models import Agent
            
            agent_data = {
                "symbol": "VOID_IND_01",
                "headquarters": "X1-ZZ9-A1",
                "credits": 150000,
                "startingFaction": "COSMIC",
                "shipCount": 3
            }
            
            agent = Agent(**agent_data)
            
            self.log_test_result(
                "Agent Model",
                agent.symbol == "VOID_IND_01",
                f"Agent: {agent.symbol} with {agent.credits} credits"
            )
            
            # Test contract model
            from spacetraders_client.models import Contract, ContractTerms, ContractPayment
            
            contract_data = {
                "id": "contract-001",
                "factionSymbol": "COSMIC",
                "type": "PROCURE",
                "terms": {
                    "deadline": datetime.now(timezone.utc).isoformat(),
                    "payment": {"onAccepted": 50000, "onFulfilled": 100000},
                    "deliver": []
                },
                "accepted": True,
                "fulfilled": False,
                "expiration": datetime.now(timezone.utc).isoformat(),
                "deadlineToAccept": datetime.now(timezone.utc).isoformat()
            }
            
            # Create contract terms separately
            terms = ContractTerms(
                deadline=datetime.now(timezone.utc),
                payment=ContractPayment(onAccepted=50000, onFulfilled=100000),
                deliver=[]
            )
            
            contract_data["terms"] = terms
            contract_data["expiration"] = datetime.now(timezone.utc)
            contract_data["deadlineToAccept"] = datetime.now(timezone.utc)
            
            contract = Contract(**contract_data)
            
            self.log_test_result(
                "Contract Model",
                contract.id == "contract-001",
                f"Contract: {contract.id} ({contract.type})"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Model Validation",
                False,
                f"Model validation tests failed: {str(e)}"
            )
            return False
    
    async def run_all_tests(self):
        """Run all offline tests."""
        print("🚀 SpaceTraders Application - Offline Functionality Tests")
        print("=" * 70)
        print(f"Test Agent: VOID_IND_01")
        print(f"Started: {datetime.now(timezone.utc).isoformat()}")
        print("\n🔄 Running tests without network connectivity...")
        print()
        
        # Test sequence
        test_sequence = [
            ("Client Initialization", self.test_client_initialization),
            ("Terminal UI Components", self.test_terminal_ui_components),
            ("Automation Systems", self.test_automation_systems),
            ("Utility Functions", self.test_utility_functions),
            ("Widget Button Functionality", self.test_widget_button_functionality),
            ("Application Integration", self.test_app_integration),
            ("Error Handling", self.test_error_handling),
            ("Model Validation", self.test_model_validation),
        ]
        
        # Run tests
        for test_name, test_func in test_sequence:
            print(f"\n{'='*20} {test_name} {'='*20}")
            
            try:
                await test_func()
            except Exception as e:
                self.log_test_result(
                    test_name,
                    False,
                    f"Unexpected error: {str(e)}"
                )
                print(f"Stack trace: {traceback.format_exc()}")
        
        # Final results
        print("\n" + "=" * 70)
        print("📊 OFFLINE TEST RESULTS")
        print("=" * 70)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['name']}")
            if result['message']:
                print(f"   {result['message']}")
        
        # Overall assessment
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL OFFLINE TESTS PASSED!")
            print("The SpaceTraders application components are functioning correctly.")
            print("All UI components, automation systems, and utilities are working.")
            print("\n💡 Network connectivity is required for API operations.")
            print("To test with real API data, ensure network access to api.spacetraders.io")
            return 0
        else:
            failed_tests = self.total_tests - self.passed_tests
            print(f"\n⚠️  {failed_tests} TEST(S) FAILED")
            print("Some functionality may not be working as expected.")
            print("Please review the failed tests above.")
            return 1

async def main():
    """Main entry point for offline tests."""
    # Set the test token in environment
    os.environ['SPACETRADERS_TOKEN'] = TEST_API_KEY
    
    # Create and run test runner
    runner = OfflineTestRunner()
    return await runner.run_all_tests()

if __name__ == "__main__":
    exit(asyncio.run(main()))