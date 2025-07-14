"""
Navigation helper for handling ship movement and pathfinding.
"""

import asyncio
import math
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timedelta

from spacetraders_client import SpaceTradersClient, SpaceTradersError
from spacetraders_client.models import Ship, Waypoint, System, WaypointType


class NavigationHelper:
    """Helper class for ship navigation and pathfinding."""
    
    def __init__(self, client: SpaceTradersClient):
        self.client = client
        self.waypoint_cache: Dict[str, Waypoint] = {}
        self.system_cache: Dict[str, System] = {}
        
    async def navigate_to_waypoint(self, ship: Ship, target_waypoint: str, required_status: str = "ORBIT") -> bool:
        """
        Navigate a ship to a target waypoint.
        
        Args:
            ship: The ship to navigate
            target_waypoint: The target waypoint symbol
            required_status: Required ship status after navigation ("ORBIT" or "DOCK")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if ship is already at target
            if ship.nav.waypointSymbol == target_waypoint:
                return await self._ensure_ship_status(ship, required_status)
            
            # Ensure ship is in orbit before navigation
            if ship.nav.status != "IN_ORBIT":
                if ship.nav.status == "DOCKED":
                    await self.client.orbit_ship(ship.symbol)
                    print(f"🚀 {ship.symbol} moved to orbit")
                else:
                    print(f"⚠️  {ship.symbol} is in unexpected status: {ship.nav.status}")
                    return False
            
            # Navigate to target
            print(f"🎯 {ship.symbol} navigating to {target_waypoint}")
            nav_result = await self.client.navigate_ship(ship.symbol, target_waypoint)
            
            # Wait for arrival if in transit
            if nav_result["nav"]["status"] == "IN_TRANSIT":
                arrival_time = datetime.fromisoformat(nav_result["nav"]["route"]["arrival"].replace("Z", "+00:00"))
                current_time = datetime.now(arrival_time.tzinfo)
                wait_time = (arrival_time - current_time).total_seconds()
                
                if wait_time > 0:
                    print(f"⏳ {ship.symbol} arriving in {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time + 1)  # Add 1 second buffer
            
            # Ensure correct final status
            return await self._ensure_ship_status(ship, required_status)
            
        except SpaceTradersError as e:
            print(f"❌ Navigation failed for {ship.symbol}: {e.message}")
            return False
        except Exception as e:
            print(f"❌ Unexpected navigation error for {ship.symbol}: {e}")
            return False
    
    async def _ensure_ship_status(self, ship: Ship, required_status: str) -> bool:
        """Ensure ship is in the required status."""
        try:
            # Get current ship status
            current_ship = await self.client.get_ship(ship.symbol)
            current_status = current_ship.nav.status
            
            if current_status == required_status:
                return True
            
            # Change status if needed
            if required_status == "DOCKED" and current_status == "IN_ORBIT":
                await self.client.dock_ship(ship.symbol)
                print(f"⚓ {ship.symbol} docked")
                return True
            elif required_status == "IN_ORBIT" and current_status == "DOCKED":
                await self.client.orbit_ship(ship.symbol)
                print(f"🚀 {ship.symbol} moved to orbit")
                return True
            else:
                print(f"⚠️  Cannot change {ship.symbol} from {current_status} to {required_status}")
                return False
                
        except SpaceTradersError as e:
            print(f"❌ Status change failed for {ship.symbol}: {e.message}")
            return False
        except Exception as e:
            print(f"❌ Unexpected status change error for {ship.symbol}: {e}")
            return False
    
    async def find_nearest_waypoint(self, ship: Ship, waypoint_type: WaypointType = None, trait: str = None) -> Optional[Waypoint]:
        """
        Find the nearest waypoint of a specific type or with a specific trait.
        
        Args:
            ship: The ship to find waypoints relative to
            waypoint_type: Optional waypoint type to filter by
            trait: Optional trait to filter by (e.g., "MARKETPLACE", "SHIPYARD")
            
        Returns:
            The nearest matching waypoint, or None if not found
        """
        try:
            # Get current system
            system_symbol = ship.nav.systemSymbol
            system = await self._get_system(system_symbol)
            
            # Get ship's current position
            current_waypoint = await self._get_waypoint(system_symbol, ship.nav.waypointSymbol)
            ship_x, ship_y = current_waypoint.x, current_waypoint.y
            
            # Find matching waypoints
            matching_waypoints = []
            
            for waypoint in system.waypoints:
                # Check type filter
                if waypoint_type and waypoint.type != waypoint_type:
                    continue
                
                # Check trait filter
                if trait:
                    full_waypoint = await self._get_waypoint(system_symbol, waypoint.symbol)
                    if not full_waypoint.traits or not any(t.symbol == trait for t in full_waypoint.traits):
                        continue
                
                matching_waypoints.append(waypoint)
            
            if not matching_waypoints:
                return None
            
            # Calculate distances and find nearest
            nearest_waypoint = None
            min_distance = float('inf')
            
            for waypoint in matching_waypoints:
                distance = self._calculate_distance(ship_x, ship_y, waypoint.x, waypoint.y)
                if distance < min_distance:
                    min_distance = distance
                    nearest_waypoint = waypoint
            
            return await self._get_waypoint(system_symbol, nearest_waypoint.symbol) if nearest_waypoint else None
            
        except Exception as e:
            print(f"❌ Error finding nearest waypoint: {e}")
            return None
    
    async def find_waypoints_with_trait(self, ship: Ship, trait: str) -> List[Waypoint]:
        """
        Find all waypoints in the current system with a specific trait.
        
        Args:
            ship: The ship to find waypoints relative to
            trait: The trait to search for (e.g., "MARKETPLACE", "SHIPYARD")
            
        Returns:
            List of waypoints with the specified trait
        """
        try:
            system_symbol = ship.nav.systemSymbol
            system = await self._get_system(system_symbol)
            
            matching_waypoints = []
            
            for waypoint in system.waypoints:
                full_waypoint = await self._get_waypoint(system_symbol, waypoint.symbol)
                if full_waypoint.traits and any(t.symbol == trait for t in full_waypoint.traits):
                    matching_waypoints.append(full_waypoint)
            
            return matching_waypoints
            
        except Exception as e:
            print(f"❌ Error finding waypoints with trait {trait}: {e}")
            return []
    
    async def find_mining_locations(self, ship: Ship, target_resource: str = None) -> List[Waypoint]:
        """
        Find mining locations (asteroids) in the current system.
        
        Args:
            ship: The ship to find mining locations relative to
            target_resource: Optional specific resource to mine
            
        Returns:
            List of suitable mining waypoints
        """
        try:
            system_symbol = ship.nav.systemSymbol
            system = await self._get_system(system_symbol)
            
            mining_waypoints = []
            
            for waypoint in system.waypoints:
                # Look for asteroid types
                if waypoint.type in ["ASTEROID", "ASTEROID_FIELD", "ENGINEERED_ASTEROID"]:
                    full_waypoint = await self._get_waypoint(system_symbol, waypoint.symbol)
                    
                    # Check for mineral deposits trait
                    if full_waypoint.traits:
                        has_minerals = any(
                            t.symbol in ["MINERAL_DEPOSITS", "COMMON_METAL_DEPOSITS", 
                                        "PRECIOUS_METAL_DEPOSITS", "RARE_METAL_DEPOSITS"]
                            for t in full_waypoint.traits
                        )
                        
                        if has_minerals:
                            mining_waypoints.append(full_waypoint)
            
            return mining_waypoints
            
        except Exception as e:
            print(f"❌ Error finding mining locations: {e}")
            return []
    
    async def _get_system(self, system_symbol: str) -> System:
        """Get system data with caching."""
        if system_symbol not in self.system_cache:
            self.system_cache[system_symbol] = await self.client.get_system(system_symbol)
        return self.system_cache[system_symbol]
    
    async def _get_waypoint(self, system_symbol: str, waypoint_symbol: str) -> Waypoint:
        """Get waypoint data with caching."""
        cache_key = f"{system_symbol}:{waypoint_symbol}"
        if cache_key not in self.waypoint_cache:
            self.waypoint_cache[cache_key] = await self.client.get_waypoint(system_symbol, waypoint_symbol)
        return self.waypoint_cache[cache_key]
    
    def _calculate_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    async def get_fuel_stations(self, ship: Ship) -> List[Waypoint]:
        """Find fuel stations in the current system."""
        return await self.find_waypoints_with_trait(ship, "FUEL_STATION")
    
    async def get_markets(self, ship: Ship) -> List[Waypoint]:
        """Find markets in the current system."""
        return await self.find_waypoints_with_trait(ship, "MARKETPLACE")
    
    async def get_shipyards(self, ship: Ship) -> List[Waypoint]:
        """Find shipyards in the current system."""
        return await self.find_waypoints_with_trait(ship, "SHIPYARD")
    
    async def calculate_fuel_needed(self, ship: Ship, target_waypoint: str) -> int:
        """Calculate fuel needed to reach a target waypoint."""
        try:
            # Get current and target positions
            current_waypoint = await self._get_waypoint(ship.nav.systemSymbol, ship.nav.waypointSymbol)
            target = await self._get_waypoint(ship.nav.systemSymbol, target_waypoint)
            
            # Calculate distance
            distance = self._calculate_distance(current_waypoint.x, current_waypoint.y, target.x, target.y)
            
            # Estimate fuel consumption (this is a rough estimate)
            # Actual consumption depends on ship engine and flight mode
            base_consumption = max(1, int(distance / 10))  # Rough estimate
            
            return base_consumption
            
        except Exception as e:
            print(f"❌ Error calculating fuel needed: {e}")
            return 0