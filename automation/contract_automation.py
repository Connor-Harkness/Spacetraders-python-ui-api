"""
Contract automation system for handling contract fulfillment.
"""

import asyncio
from typing import List, Optional, Dict, Set
from datetime import datetime, timedelta

from spacetraders_client import SpaceTradersClient, SpaceTradersError
from spacetraders_client.models import Contract, Ship, ContractDeliverGood

from .navigation import NavigationHelper
from .resource_management import ResourceManager


class ContractAutomation:
    """Automation for contract fulfillment."""
    
    def __init__(self, client: SpaceTradersClient, contract: Contract, navigation_helper: NavigationHelper, resource_manager: ResourceManager):
        self.client = client
        self.contract = contract
        self.navigation_helper = navigation_helper
        self.resource_manager = resource_manager
        
        # State tracking
        self.current_status = "initializing"
        self.progress = 0.0
        self.error_count = 0
        self.is_running = False
        
        # Assigned ships
        self.assigned_ships: Set[str] = set()
        
    async def run_automation(self):
        """Run the main contract automation loop."""
        self.is_running = True
        
        print(f"📋 Starting contract automation for {self.contract.id}")
        
        while self.is_running:
            try:
                # Update contract state
                self.contract = await self.client.get_contract(self.contract.id)
                
                # Check if contract is fulfilled
                if self.contract.fulfilled:
                    print(f"✅ Contract {self.contract.id} fulfilled!")
                    self.current_status = "fulfilled"
                    break
                
                # Check if contract is expired
                if datetime.now() > self.contract.terms.deadline:
                    print(f"⏰ Contract {self.contract.id} expired!")
                    self.current_status = "expired"
                    break
                
                # Accept contract if not accepted
                if not self.contract.accepted:
                    await self._accept_contract()
                    continue
                
                # Assign ships if needed
                if not self.assigned_ships:
                    await self._assign_ships()
                
                # Monitor progress
                await self._monitor_progress()
                
                # Update progress
                self._update_progress()
                
                # Wait before next check
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                print(f"🛑 Contract automation cancelled for {self.contract.id}")
                break
            except SpaceTradersError as e:
                self.error_count += 1
                self.current_status = "error"
                print(f"❌ SpaceTraders error for contract {self.contract.id}: {e.message}")
                
                if self.error_count >= 5:
                    print(f"❌ Too many errors for contract {self.contract.id}, stopping automation")
                    break
                
                await asyncio.sleep(60)  # Wait longer on error
                
            except Exception as e:
                self.error_count += 1
                self.current_status = "error"
                print(f"❌ Unexpected error for contract {self.contract.id}: {e}")
                
                if self.error_count >= 5:
                    print(f"❌ Too many errors for contract {self.contract.id}, stopping automation")
                    break
                
                await asyncio.sleep(60)  # Wait longer on error
        
        self.is_running = False
        print(f"🛑 Contract automation stopped for {self.contract.id}")
    
    async def _accept_contract(self):
        """Accept the contract."""
        try:
            result = await self.client.accept_contract(self.contract.id)
            self.contract = result["contract"]
            self.current_status = "accepted"
            print(f"✅ Accepted contract {self.contract.id}")
            
        except SpaceTradersError as e:
            print(f"❌ Failed to accept contract {self.contract.id}: {e.message}")
    
    async def _assign_ships(self):
        """Assign suitable ships to the contract."""
        try:
            # Get all ships
            ships_response = await self.client.get_ships(limit=50)
            ships = ships_response["data"]
            
            # Filter ships based on contract type
            suitable_ships = []
            
            if self.contract.type == "PROCUREMENT":
                # Only assign ships capable of mining
                for ship in ships:
                    if self._can_ship_mine(ship):
                        suitable_ships.append(ship)
            else:
                # For other contract types, any ship can be assigned
                suitable_ships = ships
            
            # Assign ships (limit to avoid over-assignment)
            max_ships = min(len(suitable_ships), 3)  # Limit to 3 ships per contract
            
            for i in range(max_ships):
                ship = suitable_ships[i]
                self.assigned_ships.add(ship.symbol)
                print(f"🚀 Assigned ship {ship.symbol} to contract {self.contract.id}")
            
            if not self.assigned_ships:
                print(f"⚠️  No suitable ships found for contract {self.contract.id}")
                self.current_status = "no_ships"
            else:
                self.current_status = "running"
                
        except Exception as e:
            print(f"❌ Error assigning ships to contract {self.contract.id}: {e}")
    
    async def _monitor_progress(self):
        """Monitor the progress of contract fulfillment."""
        if not self.contract.terms.deliver:
            return
        
        # Check each delivery requirement
        for delivery in self.contract.terms.deliver:
            if delivery.unitsFulfilled >= delivery.unitsRequired:
                continue  # Already fulfilled
            
            # Check if assigned ships are working on this delivery
            await self._ensure_ships_working_on_delivery(delivery)
    
    async def _ensure_ships_working_on_delivery(self, delivery: ContractDeliverGood):
        """Ensure ships are working on a specific delivery."""
        # Get current status of assigned ships
        for ship_symbol in self.assigned_ships:
            try:
                ship = await self.client.get_ship(ship_symbol)
                
                # Check if ship should work on this delivery
                if self._should_ship_work_on_delivery(ship, delivery):
                    await self._direct_ship_to_delivery(ship, delivery)
                
            except SpaceTradersError as e:
                print(f"❌ Error checking ship {ship_symbol}: {e.message}")
                continue
    
    def _should_ship_work_on_delivery(self, ship: Ship, delivery: ContractDeliverGood) -> bool:
        """Check if ship should work on this delivery."""
        # Check if ship has the required item
        if ship.cargo:
            for item in ship.cargo.inventory:
                if item.symbol == delivery.tradeSymbol:
                    return True
        
        # Check if ship can acquire the item
        if self.contract.type == "PROCUREMENT":
            # For procurement contracts, ship should mine the resource
            return self._can_ship_mine(ship)
        
        return True
    
    async def _direct_ship_to_delivery(self, ship: Ship, delivery: ContractDeliverGood):
        """Direct ship to work on specific delivery."""
        # Check if ship has the item
        has_item = False
        if ship.cargo:
            for item in ship.cargo.inventory:
                if item.symbol == delivery.tradeSymbol:
                    has_item = True
                    break
        
        if has_item:
            # Ship has item, navigate to delivery destination
            success = await self.navigation_helper.navigate_to_waypoint(
                ship, delivery.destinationSymbol, "DOCKED"
            )
            
            if success:
                # Deliver items
                await self._deliver_items(ship, delivery)
        else:
            # Ship needs to acquire items
            await self._acquire_items(ship, delivery)
    
    async def _deliver_items(self, ship: Ship, delivery: ContractDeliverGood):
        """Deliver items for the contract."""
        try:
            # Calculate how many items to deliver
            items_to_deliver = 0
            if ship.cargo:
                for item in ship.cargo.inventory:
                    if item.symbol == delivery.tradeSymbol:
                        remaining_needed = delivery.unitsRequired - delivery.unitsFulfilled
                        items_to_deliver = min(item.units, remaining_needed)
                        break
            
            if items_to_deliver > 0:
                # Note: This is a simplified example - actual delivery would require
                # the appropriate API call
                print(f"📦 Would deliver {items_to_deliver} {delivery.tradeSymbol} from {ship.symbol}")
                # await self.client.deliver_contract(self.contract.id, ship.symbol, delivery.tradeSymbol, items_to_deliver)
                
        except Exception as e:
            print(f"❌ Error delivering items: {e}")
    
    async def _acquire_items(self, ship: Ship, delivery: ContractDeliverGood):
        """Acquire items needed for delivery."""
        if self.contract.type == "PROCUREMENT":
            # For procurement contracts, mine the resource
            await self._mine_resource(ship, delivery.tradeSymbol)
        else:
            # For other contracts, try to buy or find the resource
            await self._buy_resource(ship, delivery.tradeSymbol)
    
    async def _mine_resource(self, ship: Ship, resource_symbol: str):
        """Mine a specific resource."""
        try:
            # Find mining locations
            mining_locations = await self.navigation_helper.find_mining_locations(ship, resource_symbol)
            
            if not mining_locations:
                print(f"⚠️  No mining locations found for {resource_symbol}")
                return
            
            # Navigate to mining location
            nearest_mining = mining_locations[0]
            success = await self.navigation_helper.navigate_to_waypoint(ship, nearest_mining.symbol, "ORBIT")
            
            if success:
                # Mine the resource
                print(f"⛏️  {ship.symbol} mining {resource_symbol} at {nearest_mining.symbol}")
                # Note: Actual mining would require API calls
                
        except Exception as e:
            print(f"❌ Error mining resource {resource_symbol}: {e}")
    
    async def _buy_resource(self, ship: Ship, resource_symbol: str):
        """Buy a specific resource from markets."""
        try:
            # Find markets that sell the resource
            markets = await self.navigation_helper.get_markets(ship)
            
            for market_waypoint in markets:
                try:
                    market = await self.client.get_market(ship.nav.systemSymbol, market_waypoint.symbol)
                    
                    # Check if market sells the resource
                    if market.tradeGoods:
                        for trade_good in market.tradeGoods:
                            if trade_good.symbol == resource_symbol:
                                # Navigate to market
                                success = await self.navigation_helper.navigate_to_waypoint(
                                    ship, market_waypoint.symbol, "DOCKED"
                                )
                                
                                if success:
                                    # Buy the resource
                                    print(f"💰 {ship.symbol} buying {resource_symbol} at {market_waypoint.symbol}")
                                    # Note: Actual buying would require API calls
                                    return
                                
                except SpaceTradersError:
                    continue
            
            print(f"⚠️  No markets found selling {resource_symbol}")
            
        except Exception as e:
            print(f"❌ Error buying resource {resource_symbol}: {e}")
    
    def _can_ship_mine(self, ship: Ship) -> bool:
        """Check if ship can perform mining operations."""
        if not ship.mounts:
            return False
        
        # Check for mining equipment
        for mount in ship.mounts:
            if "MINING" in mount.symbol or "LASER" in mount.symbol:
                return True
        
        return False
    
    def _update_progress(self):
        """Update contract progress."""
        if not self.contract.terms.deliver:
            self.progress = 1.0 if self.contract.fulfilled else 0.0
            return
        
        total_required = 0
        total_fulfilled = 0
        
        for delivery in self.contract.terms.deliver:
            total_required += delivery.unitsRequired
            total_fulfilled += delivery.unitsFulfilled
        
        self.progress = total_fulfilled / total_required if total_required > 0 else 0.0
    
    def get_status(self) -> Dict:
        """Get current automation status."""
        return {
            "contract_id": self.contract.id,
            "contract_type": self.contract.type,
            "status": self.current_status,
            "progress": self.progress,
            "error_count": self.error_count,
            "is_running": self.is_running,
            "assigned_ships": list(self.assigned_ships),
            "accepted": self.contract.accepted,
            "fulfilled": self.contract.fulfilled,
            "deadline": self.contract.terms.deadline.isoformat(),
            "deliveries": [
                {
                    "item": delivery.tradeSymbol,
                    "required": delivery.unitsRequired,
                    "fulfilled": delivery.unitsFulfilled,
                    "destination": delivery.destinationSymbol,
                    "progress": delivery.unitsFulfilled / delivery.unitsRequired if delivery.unitsRequired > 0 else 0.0
                }
                for delivery in (self.contract.terms.deliver or [])
            ]
        }
    
    def stop_automation(self):
        """Stop the automation loop."""
        self.is_running = False
        print(f"🛑 Stopping contract automation for {self.contract.id}")
    
    def assign_ship(self, ship_symbol: str):
        """Assign a specific ship to this contract."""
        self.assigned_ships.add(ship_symbol)
        print(f"🚀 Ship {ship_symbol} assigned to contract {self.contract.id}")
    
    def unassign_ship(self, ship_symbol: str):
        """Unassign a ship from this contract."""
        self.assigned_ships.discard(ship_symbol)
        print(f"🚀 Ship {ship_symbol} unassigned from contract {self.contract.id}")