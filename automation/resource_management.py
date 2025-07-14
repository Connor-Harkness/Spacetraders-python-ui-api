"""
Resource management system for cargo, fuel, and trading.
"""

import asyncio
from typing import List, Optional, Dict, Set
from dataclasses import dataclass

from spacetraders_client import SpaceTradersClient, SpaceTradersError
from spacetraders_client.models import Ship, Market, TradeSymbol, ShipCargoItem


@dataclass
class ResourcePriority:
    """Resource priority for contract fulfillment."""
    symbol: str
    priority: int  # 1 = highest, 10 = lowest
    keep_amount: int = 0  # Amount to keep in cargo
    contract_required: bool = False


class ResourceManager:
    """Manager for ship resources, cargo, and fuel."""
    
    def __init__(self, client: SpaceTradersClient):
        self.client = client
        self.resource_priorities: Dict[str, ResourcePriority] = {}
        
    async def manage_cargo(self, ship: Ship, contract_items: List[str] = None) -> bool:
        """
        Manage ship cargo, selling non-essential items when full.
        
        Args:
            ship: The ship to manage
            contract_items: List of trade symbols needed for contracts
            
        Returns:
            True if cargo was successfully managed, False otherwise
        """
        try:
            # Get current ship state
            current_ship = await self.client.get_ship(ship.symbol)
            
            if not current_ship.cargo:
                return True
            
            # Check if cargo is full or nearly full
            cargo_percent = current_ship.cargo.units / current_ship.cargo.capacity
            
            if cargo_percent < 0.9:  # Not nearly full
                return True
            
            print(f"📦 {ship.symbol} cargo is {cargo_percent:.1%} full, managing resources")
            
            # Prioritize items to keep
            items_to_keep = set(contract_items or [])
            items_to_sell = []
            items_to_jettison = []
            
            for item in current_ship.cargo.inventory:
                if item.symbol in items_to_keep:
                    continue  # Keep contract items
                
                # Check if item can be sold
                if await self._can_sell_item(current_ship, item.symbol):
                    items_to_sell.append(item)
                else:
                    items_to_jettison.append(item)
            
            # Try to sell items first
            if items_to_sell:
                success = await self._sell_items(current_ship, items_to_sell)
                if success:
                    print(f"💰 {ship.symbol} sold {len(items_to_sell)} item types")
                    return True
            
            # If selling fails, jettison items
            if items_to_jettison:
                success = await self._jettison_items(current_ship, items_to_jettison)
                if success:
                    print(f"🚮 {ship.symbol} jettisoned {len(items_to_jettison)} item types")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error managing cargo for {ship.symbol}: {e}")
            return False
    
    async def _can_sell_item(self, ship: Ship, item_symbol: str) -> bool:
        """Check if an item can be sold at a nearby market."""
        try:
            from .navigation import NavigationHelper
            nav_helper = NavigationHelper(self.client)
            
            # Find nearby markets
            markets = await nav_helper.get_markets(ship)
            
            for market_waypoint in markets:
                try:
                    market = await self.client.get_market(ship.nav.systemSymbol, market_waypoint.symbol)
                    
                    # Check if market accepts this item
                    if market.tradeGoods:
                        for trade_good in market.tradeGoods:
                            if trade_good.symbol == item_symbol:
                                return True
                    
                    # Check imports
                    if market.imports:
                        for import_good in market.imports:
                            if import_good.symbol == item_symbol:
                                return True
                
                except SpaceTradersError:
                    continue  # Market not accessible
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking if item can be sold: {e}")
            return False
    
    async def _sell_items(self, ship: Ship, items: List[ShipCargoItem]) -> bool:
        """Sell items at the nearest market."""
        try:
            from .navigation import NavigationHelper
            nav_helper = NavigationHelper(self.client)
            
            # Find nearest market
            nearest_market = await nav_helper.find_nearest_waypoint(ship, trait="MARKETPLACE")
            
            if not nearest_market:
                print(f"⚠️  No markets found for {ship.symbol}")
                return False
            
            # Navigate to market
            success = await nav_helper.navigate_to_waypoint(ship, nearest_market.symbol, "DOCKED")
            if not success:
                return False
            
            # Sell items
            for item in items:
                try:
                    # Note: This is a simplified example - actual selling would require
                    # checking market data and handling the sell transaction
                    print(f"💰 Would sell {item.units} {item.symbol} at {nearest_market.symbol}")
                    # await self.client.sell_cargo(ship.symbol, item.symbol, item.units)
                    
                except SpaceTradersError as e:
                    print(f"❌ Failed to sell {item.symbol}: {e.message}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error selling items: {e}")
            return False
    
    async def _jettison_items(self, ship: Ship, items: List[ShipCargoItem]) -> bool:
        """Jettison items to free up cargo space."""
        try:
            for item in items:
                try:
                    # Note: This is a simplified example - actual jettisoning would require
                    # the appropriate API call
                    print(f"🚮 Would jettison {item.units} {item.symbol}")
                    # await self.client.jettison_cargo(ship.symbol, item.symbol, item.units)
                    
                except SpaceTradersError as e:
                    print(f"❌ Failed to jettison {item.symbol}: {e.message}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error jettisoning items: {e}")
            return False
    
    async def ensure_fuel(self, ship: Ship, required_fuel: int = None) -> bool:
        """
        Ensure ship has enough fuel for operations.
        
        Args:
            ship: The ship to refuel
            required_fuel: Minimum fuel required, defaults to full tank
            
        Returns:
            True if ship has enough fuel, False otherwise
        """
        try:
            # Get current ship state
            current_ship = await self.client.get_ship(ship.symbol)
            
            if not current_ship.fuel:
                return True  # Ship doesn't use fuel
            
            # Determine fuel requirement
            if required_fuel is None:
                required_fuel = current_ship.fuel.capacity
            
            # Check if fuel is sufficient
            if current_ship.fuel.current >= required_fuel:
                return True
            
            print(f"⛽ {ship.symbol} needs refuel ({current_ship.fuel.current}/{current_ship.fuel.capacity})")
            
            # Find nearest fuel station
            from .navigation import NavigationHelper
            nav_helper = NavigationHelper(self.client)
            
            fuel_stations = await nav_helper.get_fuel_stations(ship)
            if not fuel_stations:
                # Try markets instead
                markets = await nav_helper.get_markets(ship)
                fuel_stations = []
                for market_waypoint in markets:
                    try:
                        market = await self.client.get_market(ship.nav.systemSymbol, market_waypoint.symbol)
                        # Check if market sells fuel
                        if market.tradeGoods:
                            for trade_good in market.tradeGoods:
                                if trade_good.symbol == "FUEL":
                                    fuel_stations.append(market_waypoint)
                                    break
                    except SpaceTradersError:
                        continue
            
            if not fuel_stations:
                print(f"⚠️  No fuel stations found for {ship.symbol}")
                return False
            
            # Navigate to nearest fuel station
            nearest_station = fuel_stations[0]  # Simple selection
            success = await nav_helper.navigate_to_waypoint(ship, nearest_station.symbol, "DOCKED")
            
            if not success:
                return False
            
            # Refuel
            try:
                # Note: This is a simplified example - actual refueling would require
                # the appropriate API call
                print(f"⛽ Would refuel {ship.symbol} at {nearest_station.symbol}")
                # await self.client.refuel_ship(ship.symbol)
                return True
                
            except SpaceTradersError as e:
                print(f"❌ Failed to refuel {ship.symbol}: {e.message}")
                return False
            
        except Exception as e:
            print(f"❌ Error ensuring fuel for {ship.symbol}: {e}")
            return False
    
    async def optimize_cargo_for_contract(self, ship: Ship, contract_items: List[str]) -> bool:
        """
        Optimize cargo space for contract fulfillment.
        
        Args:
            ship: The ship to optimize
            contract_items: List of trade symbols needed for the contract
            
        Returns:
            True if optimization was successful, False otherwise
        """
        try:
            # Get current ship state
            current_ship = await self.client.get_ship(ship.symbol)
            
            if not current_ship.cargo:
                return True
            
            # Calculate space needed for contract items
            contract_space_needed = len(contract_items) * 10  # Rough estimate
            available_space = current_ship.cargo.capacity - current_ship.cargo.units
            
            if available_space >= contract_space_needed:
                return True  # Already have enough space
            
            # Need to free up space
            space_to_free = contract_space_needed - available_space
            
            # Identify items to remove
            items_to_remove = []
            space_freed = 0
            
            for item in current_ship.cargo.inventory:
                if item.symbol not in contract_items:
                    items_to_remove.append(item)
                    space_freed += item.units
                    
                    if space_freed >= space_to_free:
                        break
            
            if space_freed < space_to_free:
                print(f"⚠️  Cannot free enough space for contract items")
                return False
            
            # Remove items (sell or jettison)
            if items_to_remove:
                return await self._sell_items(current_ship, items_to_remove)
            
            return True
            
        except Exception as e:
            print(f"❌ Error optimizing cargo for {ship.symbol}: {e}")
            return False
    
    def set_resource_priority(self, symbol: str, priority: int, keep_amount: int = 0, contract_required: bool = False):
        """Set priority for a resource type."""
        self.resource_priorities[symbol] = ResourcePriority(
            symbol=symbol,
            priority=priority,
            keep_amount=keep_amount,
            contract_required=contract_required
        )
    
    def get_resource_priority(self, symbol: str) -> int:
        """Get priority for a resource type."""
        return self.resource_priorities.get(symbol, ResourcePriority(symbol, 5)).priority
    
    async def get_cargo_value(self, ship: Ship) -> int:
        """Estimate the total value of cargo."""
        try:
            current_ship = await self.client.get_ship(ship.symbol)
            
            if not current_ship.cargo or not current_ship.cargo.inventory:
                return 0
            
            total_value = 0
            
            # This is a simplified estimate - actual implementation would
            # need to check market prices
            for item in current_ship.cargo.inventory:
                estimated_value = item.units * 10  # Rough estimate
                total_value += estimated_value
            
            return total_value
            
        except Exception as e:
            print(f"❌ Error calculating cargo value: {e}")
            return 0