"""
Ship automation system for handling individual ship operations.
"""

import asyncio
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum

from spacetraders_client import SpaceTradersClient, SpaceTradersError
from spacetraders_client.models import Ship, Contract, Waypoint

from .navigation import NavigationHelper
from .resource_management import ResourceManager


class ShipAutomationState(Enum):
    """Ship automation states."""
    IDLE = "idle"
    NAVIGATING = "navigating"
    MINING = "mining"
    TRADING = "trading"
    REFUELING = "refueling"
    DELIVERING = "delivering"
    ERROR = "error"


class ShipAutomation:
    """Automation for individual ship operations."""
    
    def __init__(self, client: SpaceTradersClient, ship: Ship, navigation_helper: NavigationHelper, resource_manager: ResourceManager):
        self.client = client
        self.ship = ship
        self.navigation_helper = navigation_helper
        self.resource_manager = resource_manager
        
        # State tracking
        self.current_status = ShipAutomationState.IDLE
        self.last_action = "Initialized"
        self.error_count = 0
        self.is_running = False
        
        # Automation settings
        self.automation_type = "general"
        self.assigned_contract: Optional[Contract] = None
        self.target_resources: List[str] = []
        
    async def run_automation(self, automation_type: str = "general"):
        """
        Run the main automation loop.
        
        Args:
            automation_type: Type of automation ("general", "mining", "trading", "contract")
        """
        self.automation_type = automation_type
        self.is_running = True
        
        print(f"🤖 Starting {automation_type} automation for {self.ship.symbol}")
        
        while self.is_running:
            try:
                # Update ship state
                self.ship = await self.client.get_ship(self.ship.symbol)
                
                # Handle cooldown
                if self.ship.cooldown and self.ship.cooldown.remainingSeconds > 0:
                    await self._handle_cooldown()
                    continue
                
                # Execute automation based on type
                if automation_type == "mining":
                    await self._mining_automation()
                elif automation_type == "trading":
                    await self._trading_automation()
                elif automation_type == "contract":
                    await self._contract_automation()
                else:
                    await self._general_automation()
                
                # Brief pause between actions
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                print(f"🛑 Automation cancelled for {self.ship.symbol}")
                break
            except SpaceTradersError as e:
                self.error_count += 1
                self.current_status = ShipAutomationState.ERROR
                print(f"❌ SpaceTraders error for {self.ship.symbol}: {e.message}")
                
                if self.error_count >= 5:
                    print(f"❌ Too many errors for {self.ship.symbol}, stopping automation")
                    break
                
                await asyncio.sleep(60)  # Wait longer on error
                
            except Exception as e:
                self.error_count += 1
                self.current_status = ShipAutomationState.ERROR
                print(f"❌ Unexpected error for {self.ship.symbol}: {e}")
                
                if self.error_count >= 5:
                    print(f"❌ Too many errors for {self.ship.symbol}, stopping automation")
                    break
                
                await asyncio.sleep(60)  # Wait longer on error
        
        self.is_running = False
        print(f"🛑 Automation stopped for {self.ship.symbol}")
    
    async def _handle_cooldown(self):
        """Handle ship cooldown periods."""
        if not self.ship.cooldown:
            return
        
        cooldown_seconds = self.ship.cooldown.remainingSeconds
        self.last_action = f"Cooling down for {cooldown_seconds}s"
        
        print(f"❄️  {self.ship.symbol} cooling down for {cooldown_seconds} seconds")
        await asyncio.sleep(min(cooldown_seconds + 1, 60))  # Wait but not more than 60s
    
    async def _mining_automation(self):
        """Handle mining automation."""
        self.current_status = ShipAutomationState.MINING
        
        # Check if ship can mine
        if not self._can_ship_mine():
            print(f"⚠️  {self.ship.symbol} cannot mine, switching to general automation")
            await self._general_automation()
            return
        
        # Check cargo space
        if self.ship.cargo and self.ship.cargo.units >= self.ship.cargo.capacity * 0.9:
            await self._handle_full_cargo()
            return
        
        # Find mining location
        mining_locations = await self.navigation_helper.find_mining_locations(self.ship)
        
        if not mining_locations:
            print(f"⚠️  No mining locations found for {self.ship.symbol}")
            await self._general_automation()
            return
        
        # Navigate to mining location
        nearest_mining = mining_locations[0]  # Simple selection
        success = await self.navigation_helper.navigate_to_waypoint(self.ship, nearest_mining.symbol, "ORBIT")
        
        if not success:
            return
        
        # Mine
        await self._perform_mining()
        self.last_action = "Mining"
    
    async def _trading_automation(self):
        """Handle trading automation."""
        self.current_status = ShipAutomationState.TRADING
        
        # Find profitable trading opportunities
        markets = await self.navigation_helper.get_markets(self.ship)
        
        if not markets:
            print(f"⚠️  No markets found for {self.ship.symbol}")
            await self._general_automation()
            return
        
        # Simple trading logic - navigate between markets
        # This is a placeholder for more complex trading logic
        target_market = markets[0]
        success = await self.navigation_helper.navigate_to_waypoint(self.ship, target_market.symbol, "DOCKED")
        
        if success:
            self.last_action = f"Trading at {target_market.symbol}"
            await asyncio.sleep(10)  # Simulate trading time
    
    async def _contract_automation(self):
        """Handle contract fulfillment automation."""
        self.current_status = ShipAutomationState.DELIVERING
        
        if not self.assigned_contract:
            print(f"⚠️  No contract assigned to {self.ship.symbol}")
            await self._general_automation()
            return
        
        # Check if contract is fulfilled
        if self.assigned_contract.fulfilled:
            print(f"✅ Contract fulfilled for {self.ship.symbol}")
            self.assigned_contract = None
            await self._general_automation()
            return
        
        # Handle contract delivery
        await self._handle_contract_delivery()
        self.last_action = "Contract fulfillment"
    
    async def _general_automation(self):
        """Handle general automation - decide what to do."""
        self.current_status = ShipAutomationState.IDLE
        
        # Check fuel
        if self.ship.fuel and self.ship.fuel.current < self.ship.fuel.capacity * 0.3:
            await self._ensure_fuel()
            return
        
        # Check cargo
        if self.ship.cargo and self.ship.cargo.units >= self.ship.cargo.capacity * 0.8:
            await self._handle_full_cargo()
            return
        
        # Default action based on ship role
        if self.ship.registration and self.ship.registration.role in ["EXCAVATOR", "HARVESTER"]:
            await self._mining_automation()
        elif self.ship.registration and self.ship.registration.role in ["HAULER", "TRANSPORT"]:
            await self._trading_automation()
        else:
            # Default to mining if ship is capable
            if self._can_ship_mine():
                await self._mining_automation()
            else:
                await self._trading_automation()
    
    async def _handle_full_cargo(self):
        """Handle full cargo situation."""
        self.current_status = ShipAutomationState.TRADING
        
        # Try to manage cargo (sell or jettison)
        contract_items = []
        if self.assigned_contract:
            contract_items = [item.tradeSymbol for item in self.assigned_contract.terms.deliver or []]
        
        success = await self.resource_manager.manage_cargo(self.ship, contract_items)
        
        if success:
            self.last_action = "Cargo managed"
        else:
            self.last_action = "Cargo management failed"
    
    async def _handle_contract_delivery(self):
        """Handle contract delivery."""
        if not self.assigned_contract or not self.assigned_contract.terms.deliver:
            return
        
        # Find items to deliver
        for delivery in self.assigned_contract.terms.deliver:
            if delivery.unitsFulfilled >= delivery.unitsRequired:
                continue  # Already fulfilled
            
            # Check if we have the item in cargo
            has_item = False
            if self.ship.cargo:
                for cargo_item in self.ship.cargo.inventory:
                    if cargo_item.symbol == delivery.tradeSymbol:
                        has_item = True
                        break
            
            if has_item:
                # Navigate to delivery location
                success = await self.navigation_helper.navigate_to_waypoint(
                    self.ship, delivery.destinationSymbol, "DOCKED"
                )
                
                if success:
                    # Deliver items
                    await self._deliver_contract_items(delivery)
            else:
                # Need to acquire items
                await self._acquire_contract_items(delivery)
    
    async def _deliver_contract_items(self, delivery):
        """Deliver items for contract."""
        try:
            # Note: This is a simplified example - actual delivery would require
            # the appropriate API call
            print(f"📦 Would deliver {delivery.tradeSymbol} for contract")
            # await self.client.deliver_contract(self.assigned_contract.id, delivery.tradeSymbol, quantity)
            
        except Exception as e:
            print(f"❌ Error delivering contract items: {e}")
    
    async def _acquire_contract_items(self, delivery):
        """Acquire items needed for contract."""
        # This would involve finding sources of the required items
        # and acquiring them through mining, trading, etc.
        print(f"🔍 Need to acquire {delivery.tradeSymbol} for contract")
    
    async def _ensure_fuel(self):
        """Ensure ship has enough fuel."""
        self.current_status = ShipAutomationState.REFUELING
        
        success = await self.resource_manager.ensure_fuel(self.ship)
        
        if success:
            self.last_action = "Refueled"
        else:
            self.last_action = "Refuel failed"
    
    async def _perform_mining(self):
        """Perform mining operation."""
        try:
            # Note: This is a simplified example - actual mining would require
            # the appropriate API call and survey handling
            print(f"⛏️  {self.ship.symbol} mining at {self.ship.nav.waypointSymbol}")
            # await self.client.extract_resources(self.ship.symbol)
            
        except Exception as e:
            print(f"❌ Error mining: {e}")
    
    def _can_ship_mine(self) -> bool:
        """Check if ship can perform mining operations."""
        if not self.ship.mounts:
            return False
        
        # Check for mining equipment
        for mount in self.ship.mounts:
            if "MINING" in mount.symbol or "LASER" in mount.symbol:
                return True
        
        return False
    
    def assign_contract(self, contract: Contract):
        """Assign a contract to this ship."""
        self.assigned_contract = contract
        self.automation_type = "contract"
        print(f"📋 Contract {contract.id} assigned to {self.ship.symbol}")
    
    def stop_automation(self):
        """Stop the automation loop."""
        self.is_running = False
        print(f"🛑 Stopping automation for {self.ship.symbol}")
    
    def get_status(self) -> Dict:
        """Get current automation status."""
        return {
            "ship_symbol": self.ship.symbol,
            "status": self.current_status.value,
            "last_action": self.last_action,
            "error_count": self.error_count,
            "is_running": self.is_running,
            "automation_type": self.automation_type,
            "assigned_contract": self.assigned_contract.id if self.assigned_contract else None,
            "fuel_level": self.ship.fuel.current / self.ship.fuel.capacity if self.ship.fuel else 1.0,
            "cargo_level": self.ship.cargo.units / self.ship.cargo.capacity if self.ship.cargo else 0.0,
        }