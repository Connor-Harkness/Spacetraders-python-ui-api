#!/usr/bin/env python3
"""
Comprehensive integration test script for SpaceTraders application.
Tests all functionality using the provided API key.

This script validates:
- API client authentication and basic operations
- Terminal UI components with real data
- Automation systems functionality
- Error handling and edge cases
- End-to-end user workflows
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone
import traceback

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test API key provided in the issue
TEST_API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGlmaWVyIjoiVk9JRF9JTkRfMDEiLCJ2ZXJzaW9uIjoidjIuMy4wIiwicmVzZXRfZGF0ZSI6IjIwMjUtMDctMTMiLCJpYXQiOjE3NTI0OTA2MjMsInN1YiI6ImFnZW50LXRva2VuIn0.ntRp0IL6AUcG-ASZamll5AQBh9C_apXgQUL6OGiS--EjUAGyQqs8XATpPhMG7J-aWPZZG6ywkOT_7C1PaHCxbzLC19-kstLi3rICAMvbeQAMGahMT4WKnL7prVq5g0VKebVwh6H8cQKFxx1kIJ8OV_CTC7XWvek63FZxeA5T0qcDas9wI_GFW2uroSozT7MBnmnDnd1UncQf2rQVM_dhFONdJzgAxrRyaCu_Gf3rW5LWd8xXdeHHUbD6U7ONI8pt5gx_SJkRz4sRM11ANjiyy2p9LQ9paG2uYxPZ6b76sKxd9hdHvPK0TBBpxbcvHBUQE5b7agaBTGP0AZwQdSNIsXXLO29Xu6WGJqxjc6YFGJI-Ln-mQrUNPhJUnLxbh_R2Wfm2mVDSTO49MkK5Y7ZKcp7kF6WKB3Tiium35e2gRT5j9KNPii9TH8Ly49ftkEQXMlGakXLzu16GBIqwyfW-fy-eLeGoCNum7tCWTO5CDYCi0phVcNzlE0xeC37JfCXJEU29Bv6BKb02T3k_1F34nm9Ucj9XMjnib_v7VVI8FGm3n_AqM--cI-Ql-1Sl1eJBJBPN5oZJHmatwfm97dfKnVuJaDsLyBe9tkt7nFbbZc7xVOljRdTU2ITnnDXlFZaQUTaySc-aetwBn4kg2KQoWKkoidquV_4fwATbr4mogkg"

class IntegrationTestRunner:
    """Main test runner for comprehensive integration testing."""
    
    def __init__(self):
        self.passed_tests = 0
        self.total_tests = 0
        self.client = None
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
    
    async def test_client_authentication(self):
        """Test API client authentication."""
        print("\n🔍 Testing API Client Authentication...")
        
        try:
            from spacetraders_client import SpaceTradersClient
            
            # Initialize client with test token
            self.client = SpaceTradersClient(TEST_API_KEY)
            
            # Test authentication by getting agent info
            agent = await self.client.get_my_agent()
            
            self.log_test_result(
                "Client Authentication",
                agent is not None,
                f"Agent: {agent.symbol} ({agent.headquarters})"
            )
            
            # Test basic client properties
            self.log_test_result(
                "Client Configuration",
                self.client.token == TEST_API_KEY,
                f"Token configured correctly"
            )
            
            return agent is not None
            
        except Exception as e:
            self.log_test_result(
                "Client Authentication",
                False,
                f"Authentication failed: {str(e)}"
            )
            return False
    
    async def test_agent_operations(self):
        """Test agent-related operations."""
        print("\n🔍 Testing Agent Operations...")
        
        try:
            if not self.client:
                self.log_test_result("Agent Operations", False, "No client available")
                return False
            
            # Get agent info
            agent = await self.client.get_my_agent()
            
            self.log_test_result(
                "Get Agent Info",
                agent is not None,
                f"Credits: {agent.credits:,}, Ships: {agent.shipCount}, HQ: {agent.headquarters}"
            )
            
            return agent is not None
            
        except Exception as e:
            self.log_test_result(
                "Agent Operations",
                False,
                f"Agent operations failed: {str(e)}"
            )
            return False
    
    async def test_ship_operations(self):
        """Test ship-related operations."""
        print("\n🔍 Testing Ship Operations...")
        
        try:
            if not self.client:
                self.log_test_result("Ship Operations", False, "No client available")
                return False
            
            # Get ships
            ships_response = await self.client.get_ships()
            ships = ships_response['data']
            
            self.log_test_result(
                "Get Ships",
                len(ships) > 0,
                f"Found {len(ships)} ships"
            )
            
            if ships:
                # Test ship details
                ship = ships[0]
                
                self.log_test_result(
                    "Ship Details",
                    ship.symbol is not None,
                    f"Ship: {ship.symbol} ({ship.registration.role}) at {ship.nav.waypointSymbol}"
                )
                
                # Test ship status
                self.log_test_result(
                    "Ship Status",
                    ship.nav.status in ["DOCKED", "IN_ORBIT", "IN_TRANSIT"],
                    f"Status: {ship.nav.status}"
                )
                
                # Test fuel and cargo
                self.log_test_result(
                    "Ship Resources",
                    ship.fuel.current >= 0 and ship.cargo.units >= 0,
                    f"Fuel: {ship.fuel.current}/{ship.fuel.capacity}, Cargo: {ship.cargo.units}/{ship.cargo.capacity}"
                )
            
            return len(ships) > 0
            
        except Exception as e:
            self.log_test_result(
                "Ship Operations",
                False,
                f"Ship operations failed: {str(e)}"
            )
            return False
    
    async def test_contract_operations(self):
        """Test contract-related operations."""
        print("\n🔍 Testing Contract Operations...")
        
        try:
            if not self.client:
                self.log_test_result("Contract Operations", False, "No client available")
                return False
            
            # Get contracts
            contracts_response = await self.client.get_contracts()
            contracts = contracts_response['data']
            
            self.log_test_result(
                "Get Contracts",
                contracts is not None,
                f"Found {len(contracts)} contracts"
            )
            
            if contracts:
                # Test contract details
                contract = contracts[0]
                
                self.log_test_result(
                    "Contract Details",
                    contract.id is not None,
                    f"Contract: {contract.id} ({contract.type}) - {'Accepted' if contract.accepted else 'Available'}"
                )
                
                # Test contract terms
                if contract.terms:
                    payment_info = f"Payment: {contract.terms.payment.onAccepted:,} + {contract.terms.payment.onFulfilled:,}"
                    
                    self.log_test_result(
                        "Contract Terms",
                        contract.terms.payment is not None,
                        payment_info
                    )
                    
                    if contract.terms.deliver:
                        delivery_info = f"Delivery: {len(contract.terms.deliver)} items"
                        
                        self.log_test_result(
                            "Contract Deliveries",
                            len(contract.terms.deliver) > 0,
                            delivery_info
                        )
            
            return contracts is not None
            
        except Exception as e:
            self.log_test_result(
                "Contract Operations",
                False,
                f"Contract operations failed: {str(e)}"
            )
            return False
    
    async def test_system_operations(self):
        """Test system and waypoint operations."""
        print("\n🔍 Testing System Operations...")
        
        try:
            if not self.client:
                self.log_test_result("System Operations", False, "No client available")
                return False
            
            # Get agent to find their system
            agent = await self.client.get_my_agent()
            system_symbol = agent.headquarters.split('-')[0] + '-' + agent.headquarters.split('-')[1]
            
            # Get system info
            system = await self.client.get_system(system_symbol)
            
            self.log_test_result(
                "Get System Info",
                system is not None,
                f"System: {system.symbol} ({system.type}) at ({system.x}, {system.y})"
            )
            
            # Get waypoints
            waypoints = await self.client.get_system_waypoints(system_symbol)
            
            self.log_test_result(
                "Get Waypoints",
                len(waypoints) > 0,
                f"Found {len(waypoints)} waypoints"
            )
            
            if waypoints:
                # Test waypoint details
                waypoint = waypoints[0]
                
                self.log_test_result(
                    "Waypoint Details",
                    waypoint.symbol is not None,
                    f"Waypoint: {waypoint.symbol} ({waypoint.type}) at ({waypoint.x}, {waypoint.y})"
                )
            
            return system is not None and len(waypoints) > 0
            
        except Exception as e:
            self.log_test_result(
                "System Operations",
                False,
                f"System operations failed: {str(e)}"
            )
            return False
    
    async def test_market_operations(self):
        """Test market-related operations."""
        print("\n🔍 Testing Market Operations...")
        
        try:
            if not self.client:
                self.log_test_result("Market Operations", False, "No client available")
                return False
            
            # Get agent to find their system
            agent = await self.client.get_my_agent()
            system_symbol = agent.headquarters.split('-')[0] + '-' + agent.headquarters.split('-')[1]
            
            # Get waypoints to find markets
            waypoints = await self.client.get_system_waypoints(system_symbol)
            
            # Find a market waypoint
            market_waypoint = None
            for waypoint in waypoints:
                if hasattr(waypoint, 'traits') and waypoint.traits:
                    for trait in waypoint.traits:
                        if trait.symbol == "MARKETPLACE":
                            market_waypoint = waypoint
                            break
                    if market_waypoint:
                        break
            
            if market_waypoint:
                # Get market info
                market = await self.client.get_market(market_waypoint.symbol)
                
                self.log_test_result(
                    "Get Market Info",
                    market is not None,
                    f"Market: {market_waypoint.symbol} with {len(market.tradeGoods)} goods"
                )
                
                if market.tradeGoods:
                    # Test market goods
                    good = market.tradeGoods[0]
                    
                    self.log_test_result(
                        "Market Goods",
                        good.symbol is not None,
                        f"Good: {good.symbol} - Buy: {good.purchasePrice}, Sell: {good.sellPrice}"
                    )
            else:
                self.log_test_result(
                    "Market Operations",
                    False,
                    "No marketplace found in system"
                )
                return False
            
            return market_waypoint is not None
            
        except Exception as e:
            self.log_test_result(
                "Market Operations",
                False,
                f"Market operations failed: {str(e)}"
            )
            return False
    
    async def test_terminal_ui_components(self):
        """Test terminal UI components with real data."""
        print("\n🔍 Testing Terminal UI Components...")
        
        try:
            if not self.client:
                self.log_test_result("Terminal UI Components", False, "No client available")
                return False
            
            # Test contract widget
            from terminal_ui.widgets.contracts import ContractWidget
            
            contracts_response = await self.client.get_contracts()
            contracts = contracts_response['data']
            contract_widget = ContractWidget()
            
            if contracts:
                contract_card = contract_widget.create_contract_card(contracts[0])
                
                self.log_test_result(
                    "Contract Widget",
                    contract_card is not None,
                    "Contract card created successfully"
                )
            
            # Test ship widget
            from terminal_ui.widgets.ships import ShipWidget
            
            ships_response = await self.client.get_ships()
            ships = ships_response['data']
            ship_widget = ShipWidget()
            
            if ships:
                ship_card = ship_widget.create_ship_card(ships[0])
                
                self.log_test_result(
                    "Ship Widget",
                    ship_card is not None,
                    "Ship card created successfully"
                )
            
            # Test dashboard widget
            from terminal_ui.widgets.dashboard import DashboardWidget
            
            dashboard_widget = DashboardWidget()
            
            # Test agent info display
            agent = await self.client.get_my_agent()
            agent_info = dashboard_widget.create_agent_info(agent)
            
            self.log_test_result(
                "Dashboard Widget",
                agent_info is not None,
                "Agent info display created successfully"
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
        """Test automation systems."""
        print("\n🔍 Testing Automation Systems...")
        
        try:
            if not self.client:
                self.log_test_result("Automation Systems", False, "No client available")
                return False
            
            # Test automation manager
            from automation import AutomationManager
            
            automation_manager = AutomationManager(self.client)
            
            self.log_test_result(
                "Automation Manager",
                automation_manager is not None,
                "Automation manager created successfully"
            )
            
            # Test ship automation
            from automation import ShipAutomation
            
            ships_response = await self.client.get_ships()
            ships = ships_response['data']
            if ships:
                ship_automation = ShipAutomation(self.client, ships[0])
                
                self.log_test_result(
                    "Ship Automation",
                    ship_automation is not None,
                    f"Ship automation created for {ships[0].symbol}"
                )
            
            # Test contract automation
            from automation import ContractAutomation
            
            contracts_response = await self.client.get_contracts()
            contracts = contracts_response['data']
            if contracts:
                contract_automation = ContractAutomation(self.client, contracts[0])
                
                self.log_test_result(
                    "Contract Automation",
                    contract_automation is not None,
                    f"Contract automation created for {contracts[0].id}"
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
        """Test utility functions with real data."""
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
            agent = await self.client.get_my_agent()
            formatted_credits = format_credits(agent.credits)
            
            self.log_test_result(
                "Credit Formatting",
                formatted_credits is not None,
                f"Credits: {agent.credits:,} → {formatted_credits}"
            )
            
            # Test ship validation
            ships_response = await self.client.get_ships()
            ships = ships_response['data']
            if ships:
                is_valid = validate_ship_for_task(ships[0], "MINING")
                
                self.log_test_result(
                    "Ship Validation",
                    is_valid is not None,
                    f"Ship {ships[0].symbol} valid for mining: {is_valid}"
                )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Utility Functions",
                False,
                f"Utility function tests failed: {str(e)}"
            )
            return False
    
    async def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n🔍 Testing Error Handling...")
        
        try:
            # Test invalid token
            from spacetraders_client import SpaceTradersClient
            
            invalid_client = SpaceTradersClient("invalid_token")
            
            try:
                await invalid_client.get_my_agent()
                self.log_test_result(
                    "Invalid Token Handling",
                    False,
                    "Should have failed with invalid token"
                )
            except Exception:
                self.log_test_result(
                    "Invalid Token Handling",
                    True,
                    "Properly handled invalid token"
                )
            
            # Test non-existent system
            try:
                await self.client.get_system("INVALID-SYSTEM")
                self.log_test_result(
                    "Invalid System Handling",
                    False,
                    "Should have failed with invalid system"
                )
            except Exception:
                self.log_test_result(
                    "Invalid System Handling",
                    True,
                    "Properly handled invalid system"
                )
            
            # Test UI with empty data
            from terminal_ui.widgets.contracts import ContractWidget
            
            contract_widget = ContractWidget()
            
            try:
                # Test with empty contract list
                empty_display = contract_widget.create_contracts_display([])
                
                self.log_test_result(
                    "Empty Data Handling",
                    empty_display is not None,
                    "UI properly handles empty data"
                )
            except Exception:
                self.log_test_result(
                    "Empty Data Handling",
                    False,
                    "UI failed to handle empty data"
                )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Error Handling",
                False,
                f"Error handling tests failed: {str(e)}"
            )
            return False
    
    async def test_terminal_app_creation(self):
        """Test terminal app creation and basic functionality."""
        print("\n🔍 Testing Terminal App Creation...")
        
        try:
            from terminal_ui.app import SpaceTradersApp
            
            # Create app with test token
            app = SpaceTradersApp(TEST_API_KEY)
            
            self.log_test_result(
                "App Creation",
                app is not None,
                "Terminal app created successfully"
            )
            
            # Test app initialization
            self.log_test_result(
                "App Configuration",
                app.token == TEST_API_KEY,
                "Token configured correctly"
            )
            
            # Test app has required methods
            required_methods = [
                'action_refresh',
                'action_toggle_tab',
                'action_show_dashboard',
                'action_show_ships',
                'action_show_contracts',
                'action_show_agent'
            ]
            
            methods_exist = all(hasattr(app, method) for method in required_methods)
            
            self.log_test_result(
                "App Methods",
                methods_exist,
                f"All required methods exist: {methods_exist}"
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Terminal App Creation",
                False,
                f"App creation failed: {str(e)}"
            )
            return False
    
    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 SpaceTraders Application - Comprehensive Integration Tests")
        print("=" * 70)
        print(f"Test Agent: VOID_IND_01")
        print(f"Started: {datetime.now(timezone.utc).isoformat()}")
        print()
        
        # Test sequence
        test_sequence = [
            ("API Client Authentication", self.test_client_authentication),
            ("Agent Operations", self.test_agent_operations),
            ("Ship Operations", self.test_ship_operations),
            ("Contract Operations", self.test_contract_operations),
            ("System Operations", self.test_system_operations),
            ("Market Operations", self.test_market_operations),
            ("Terminal UI Components", self.test_terminal_ui_components),
            ("Automation Systems", self.test_automation_systems),
            ("Utility Functions", self.test_utility_functions),
            ("Error Handling", self.test_error_handling),
            ("Terminal App Creation", self.test_terminal_app_creation),
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
        print("📊 FINAL TEST RESULTS")
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
            print("\n🎉 ALL TESTS PASSED!")
            print("The SpaceTraders application is functioning correctly.")
            print("All major features have been verified with the test agent.")
            return 0
        else:
            failed_tests = self.total_tests - self.passed_tests
            print(f"\n⚠️  {failed_tests} TEST(S) FAILED")
            print("Some functionality may not be working as expected.")
            print("Please review the failed tests above.")
            return 1

async def main():
    """Main entry point for integration tests."""
    # Set the test token in environment
    os.environ['SPACETRADERS_TOKEN'] = TEST_API_KEY
    
    # Create and run test runner
    runner = IntegrationTestRunner()
    return await runner.run_all_tests()

if __name__ == "__main__":
    exit(asyncio.run(main()))