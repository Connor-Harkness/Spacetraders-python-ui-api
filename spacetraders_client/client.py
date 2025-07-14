"""
Main SpaceTraders API client implementation.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin
import httpx
from pydantic import BaseModel

from .models import (
    Agent,
    Contract,
    Faction,
    Ship,
    System,
    Waypoint,
    Market,
    Shipyard,
    PublicAgent,
    Meta,
    FactionSymbol,
    ShipType,
    TradeSymbol,
    WaypointSymbol,
    SystemSymbol,
)


class SpaceTradersError(Exception):
    """Base exception for SpaceTraders API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class SpaceTradersClient:
    """
    Object-oriented Python client for the SpaceTraders API.
    
    This client provides a comprehensive interface to interact with the SpaceTraders API,
    including methods for managing agents, ships, contracts, factions, and more.
    
    Example:
        >>> client = SpaceTradersClient(token="your_token_here")
        >>> agent = await client.get_my_agent()
        >>> print(f"Agent: {agent.symbol}, Credits: {agent.credits}")
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.spacetraders.io/v2",
        timeout: float = 30.0,
    ):
        """
        Initialize the SpaceTraders client.
        
        Args:
            token: Bearer token for authentication. Required for most operations.
            base_url: Base URL for the SpaceTraders API.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url
        self.token = token
        self.timeout = timeout
        
        # Set up HTTP client
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SpaceTraders-Python-Client/1.0.0",
        }
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        auth_required: bool = True,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the SpaceTraders API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON request body
            auth_required: Whether authentication is required
            
        Returns:
            Parsed JSON response
            
        Raises:
            SpaceTradersError: If the request fails
        """
        if auth_required and not self.token:
            raise SpaceTradersError("Authentication token required for this operation")
        
        try:
            response = await self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )
            
            # Handle different response status codes
            if response.status_code == 204:
                return {}
            
            response_data = response.json()
            
            if not response.is_success:
                error_message = "Unknown error"
                error_code = None
                
                if "error" in response_data:
                    error_info = response_data["error"]
                    error_message = error_info.get("message", "Unknown error")
                    error_code = error_info.get("code")
                
                raise SpaceTradersError(
                    error_message,
                    status_code=response.status_code,
                    error_code=error_code,
                )
            
            return response_data
            
        except httpx.RequestError as e:
            raise SpaceTradersError(f"Network error: {str(e)}")
    
    # ============================================================================
    # Global/Status Endpoints
    # ============================================================================
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the game server.
        
        Returns:
            Server status information including version, reset dates, and leaderboards.
        """
        response = await self._request("GET", "/", auth_required=False)
        return response
    
    # ============================================================================
    # Agent Endpoints
    # ============================================================================
    
    async def get_my_agent(self) -> Agent:
        """
        Get your agent's details.
        
        Returns:
            Your agent information.
        """
        response = await self._request("GET", "/my/agent")
        return Agent(**response["data"])
    
    async def get_agents(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        List all public agent details.
        
        Args:
            page: Page number for pagination
            limit: Number of entries per page (1-20)
            
        Returns:
            Dictionary containing agents list and pagination metadata.
        """
        params = {"page": page, "limit": limit}
        response = await self._request("GET", "/agents", params=params, auth_required=False)
        
        return {
            "data": [PublicAgent(**agent) for agent in response["data"]],
            "meta": Meta(**response["meta"]),
        }
    
    async def get_agent(self, agent_symbol: str) -> PublicAgent:
        """
        Get public details for a specific agent.
        
        Args:
            agent_symbol: The agent symbol to look up
            
        Returns:
            Public agent information.
        """
        response = await self._request("GET", f"/agents/{agent_symbol}", auth_required=False)
        return PublicAgent(**response["data"])
    
    # ============================================================================
    # Faction Endpoints
    # ============================================================================
    
    async def get_factions(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        List all factions in the game.
        
        Args:
            page: Page number for pagination
            limit: Number of entries per page (1-20)
            
        Returns:
            Dictionary containing factions list and pagination metadata.
        """
        params = {"page": page, "limit": limit}
        response = await self._request("GET", "/factions", params=params, auth_required=False)
        
        return {
            "data": [Faction(**faction) for faction in response["data"]],
            "meta": Meta(**response["meta"]),
        }
    
    async def get_faction(self, faction_symbol: Union[str, FactionSymbol]) -> Faction:
        """
        Get details of a specific faction.
        
        Args:
            faction_symbol: The faction symbol to look up
            
        Returns:
            Faction information.
        """
        if isinstance(faction_symbol, FactionSymbol):
            faction_symbol = faction_symbol.value
        
        response = await self._request("GET", f"/factions/{faction_symbol}", auth_required=False)
        return Faction(**response["data"])
    
    # ============================================================================
    # Contract Endpoints
    # ============================================================================
    
    async def get_contracts(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        List all your contracts.
        
        Args:
            page: Page number for pagination
            limit: Number of entries per page (1-20)
            
        Returns:
            Dictionary containing contracts list and pagination metadata.
        """
        params = {"page": page, "limit": limit}
        response = await self._request("GET", "/my/contracts", params=params)
        
        return {
            "data": [Contract(**contract) for contract in response["data"]],
            "meta": Meta(**response["meta"]),
        }
    
    async def get_contract(self, contract_id: str) -> Contract:
        """
        Get details of a specific contract.
        
        Args:
            contract_id: The contract ID to look up
            
        Returns:
            Contract information.
        """
        response = await self._request("GET", f"/my/contracts/{contract_id}")
        return Contract(**response["data"])
    
    async def accept_contract(self, contract_id: str) -> Dict[str, Any]:
        """
        Accept a contract.
        
        Args:
            contract_id: The contract ID to accept
            
        Returns:
            Dictionary containing updated contract and agent information.
        """
        response = await self._request("POST", f"/my/contracts/{contract_id}/accept")
        
        return {
            "contract": Contract(**response["data"]["contract"]),
            "agent": Agent(**response["data"]["agent"]),
        }
    
    async def fulfill_contract(self, contract_id: str) -> Dict[str, Any]:
        """
        Fulfill a contract.
        
        Args:
            contract_id: The contract ID to fulfill
            
        Returns:
            Dictionary containing updated contract and agent information.
        """
        response = await self._request("POST", f"/my/contracts/{contract_id}/fulfill")
        
        return {
            "contract": Contract(**response["data"]["contract"]),
            "agent": Agent(**response["data"]["agent"]),
        }
    
    # ============================================================================
    # Fleet/Ship Endpoints
    # ============================================================================
    
    async def get_ships(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        List all ships under your agent's ownership.
        
        Args:
            page: Page number for pagination
            limit: Number of entries per page (1-20)
            
        Returns:
            Dictionary containing ships list and pagination metadata.
        """
        params = {"page": page, "limit": limit}
        response = await self._request("GET", "/my/ships", params=params)
        
        return {
            "data": [Ship(**ship) for ship in response["data"]],
            "meta": Meta(**response["meta"]),
        }
    
    async def get_ship(self, ship_symbol: str) -> Ship:
        """
        Get details of a specific ship.
        
        Args:
            ship_symbol: The ship symbol to look up
            
        Returns:
            Ship information.
        """
        response = await self._request("GET", f"/my/ships/{ship_symbol}")
        return Ship(**response["data"])
    
    async def purchase_ship(
        self, 
        ship_type: Union[str, ShipType], 
        waypoint_symbol: Union[str, WaypointSymbol]
    ) -> Dict[str, Any]:
        """
        Purchase a ship from a shipyard.
        
        Args:
            ship_type: Type of ship to purchase
            waypoint_symbol: Waypoint where the shipyard is located
            
        Returns:
            Dictionary containing new ship, updated agent, and transaction details.
        """
        if isinstance(ship_type, ShipType):
            ship_type = ship_type.value
        if isinstance(waypoint_symbol, WaypointSymbol):
            waypoint_symbol = waypoint_symbol.root
        
        json_data = {
            "shipType": ship_type,
            "waypointSymbol": waypoint_symbol,
        }
        
        response = await self._request("POST", "/my/ships", json_data=json_data)
        
        return {
            "ship": Ship(**response["data"]["ship"]),
            "agent": Agent(**response["data"]["agent"]),
            "transaction": response["data"]["transaction"],
        }
    
    async def dock_ship(self, ship_symbol: str) -> Dict[str, Any]:
        """
        Dock a ship at its current location.
        
        Args:
            ship_symbol: The ship symbol to dock
            
        Returns:
            Updated ship navigation information.
        """
        response = await self._request("POST", f"/my/ships/{ship_symbol}/dock")
        return {"nav": response["data"]["nav"]}
    
    async def orbit_ship(self, ship_symbol: str) -> Dict[str, Any]:
        """
        Move a ship into orbit at its current location.
        
        Args:
            ship_symbol: The ship symbol to orbit
            
        Returns:
            Updated ship navigation information.
        """
        response = await self._request("POST", f"/my/ships/{ship_symbol}/orbit")
        return {"nav": response["data"]["nav"]}
    
    async def navigate_ship(
        self, 
        ship_symbol: str, 
        waypoint_symbol: Union[str, WaypointSymbol]
    ) -> Dict[str, Any]:
        """
        Navigate a ship to a target destination.
        
        Args:
            ship_symbol: The ship symbol to navigate
            waypoint_symbol: The destination waypoint
            
        Returns:
            Dictionary containing updated navigation and fuel information.
        """
        if isinstance(waypoint_symbol, WaypointSymbol):
            waypoint_symbol = waypoint_symbol.root
        
        json_data = {"waypointSymbol": waypoint_symbol}
        response = await self._request("POST", f"/my/ships/{ship_symbol}/navigate", json_data=json_data)
        
        return {
            "nav": response["data"]["nav"],
            "fuel": response["data"]["fuel"],
            "events": response["data"].get("events", []),
        }
    
    async def refuel_ship(self, ship_symbol: str, units: Optional[int] = None) -> Dict[str, Any]:
        """
        Refuel a ship at its current location.
        
        Args:
            ship_symbol: The ship symbol to refuel
            units: Optional number of units to refuel (refuels to max if not specified)
            
        Returns:
            Dictionary containing updated fuel information and transaction details.
        """
        json_data = {}
        if units is not None:
            json_data["units"] = units
        
        response = await self._request("POST", f"/my/ships/{ship_symbol}/refuel", json_data=json_data)
        
        return {
            "fuel": response["data"]["fuel"],
            "transaction": response["data"]["transaction"],
            "agent": response["data"]["agent"],
        }
    
    # ============================================================================
    # System Endpoints
    # ============================================================================
    
    async def get_systems(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        List all systems.
        
        Args:
            page: Page number for pagination
            limit: Number of entries per page (1-20)
            
        Returns:
            Dictionary containing systems list and pagination metadata.
        """
        params = {"page": page, "limit": limit}
        response = await self._request("GET", "/systems", params=params, auth_required=False)
        
        return {
            "data": [System(**system) for system in response["data"]],
            "meta": Meta(**response["meta"]),
        }
    
    async def get_system(self, system_symbol: Union[str, SystemSymbol]) -> System:
        """
        Get details of a specific system.
        
        Args:
            system_symbol: The system symbol to look up
            
        Returns:
            System information.
        """
        if isinstance(system_symbol, SystemSymbol):
            system_symbol = system_symbol.root
        
        response = await self._request("GET", f"/systems/{system_symbol}", auth_required=False)
        return System(**response["data"])
    
    async def get_system_waypoints(
        self,
        system_symbol: Union[str, SystemSymbol],
        page: int = 1,
        limit: int = 10,
        waypoint_type: Optional[str] = None,
        traits: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        List waypoints in a system.
        
        Args:
            system_symbol: The system to list waypoints for
            page: Page number for pagination
            limit: Number of entries per page (1-20)
            waypoint_type: Filter by waypoint type
            traits: Filter by waypoint traits
            
        Returns:
            Dictionary containing waypoints list and pagination metadata.
        """
        if isinstance(system_symbol, SystemSymbol):
            system_symbol = system_symbol.root
        
        params = {"page": page, "limit": limit}
        if waypoint_type:
            params["type"] = waypoint_type
        if traits:
            params["traits"] = traits
        
        response = await self._request(
            "GET", 
            f"/systems/{system_symbol}/waypoints", 
            params=params, 
            auth_required=False
        )
        
        return {
            "data": [Waypoint(**waypoint) for waypoint in response["data"]],
            "meta": Meta(**response["meta"]),
        }
    
    async def get_waypoint(
        self, 
        system_symbol: Union[str, SystemSymbol], 
        waypoint_symbol: Union[str, WaypointSymbol]
    ) -> Waypoint:
        """
        Get details of a specific waypoint.
        
        Args:
            system_symbol: The system containing the waypoint
            waypoint_symbol: The waypoint symbol to look up
            
        Returns:
            Waypoint information.
        """
        if isinstance(system_symbol, SystemSymbol):
            system_symbol = system_symbol.root
        if isinstance(waypoint_symbol, WaypointSymbol):
            waypoint_symbol = waypoint_symbol.root
        
        response = await self._request(
            "GET", 
            f"/systems/{system_symbol}/waypoints/{waypoint_symbol}", 
            auth_required=False
        )
        return Waypoint(**response["data"])
    
    async def get_market(
        self, 
        system_symbol: Union[str, SystemSymbol], 
        waypoint_symbol: Union[str, WaypointSymbol]
    ) -> Market:
        """
        Get market information for a waypoint.
        
        Args:
            system_symbol: The system containing the waypoint
            waypoint_symbol: The waypoint with the market
            
        Returns:
            Market information.
        """
        if isinstance(system_symbol, SystemSymbol):
            system_symbol = system_symbol.root
        if isinstance(waypoint_symbol, WaypointSymbol):
            waypoint_symbol = waypoint_symbol.root
        
        response = await self._request(
            "GET", 
            f"/systems/{system_symbol}/waypoints/{waypoint_symbol}/market", 
            auth_required=False
        )
        return Market(**response["data"])
    
    async def get_shipyard(
        self, 
        system_symbol: Union[str, SystemSymbol], 
        waypoint_symbol: Union[str, WaypointSymbol]
    ) -> Shipyard:
        """
        Get shipyard information for a waypoint.
        
        Args:
            system_symbol: The system containing the waypoint
            waypoint_symbol: The waypoint with the shipyard
            
        Returns:
            Shipyard information.
        """
        if isinstance(system_symbol, SystemSymbol):
            system_symbol = system_symbol.root
        if isinstance(waypoint_symbol, WaypointSymbol):
            waypoint_symbol = waypoint_symbol.root
        
        response = await self._request(
            "GET", 
            f"/systems/{system_symbol}/waypoints/{waypoint_symbol}/shipyard", 
            auth_required=False
        )
        return Shipyard(**response["data"])
    
    # ============================================================================
    # Registration
    # ============================================================================
    
    @classmethod
    async def register_new_agent(
        cls,
        symbol: str,
        faction: Union[str, FactionSymbol],
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new agent and create a new client instance.
        
        Args:
            symbol: Desired agent symbol (3-14 characters)
            faction: Starting faction
            email: Optional email for account
            
        Returns:
            Dictionary containing token, agent, faction, contract, and ships.
        """
        if isinstance(faction, FactionSymbol):
            faction = faction.value
        
        json_data = {
            "symbol": symbol,
            "faction": faction,
        }
        if email:
            json_data["email"] = email
        
        # Create a temporary client without authentication for registration
        temp_client = httpx.AsyncClient(
            base_url="https://api.spacetraders.io/v2",
            headers={"Content-Type": "application/json"},
        )
        
        try:
            response = await temp_client.post("/register", json=json_data)
            response.raise_for_status()
            response_data = response.json()
            
            return {
                "token": response_data["data"]["token"],
                "agent": Agent(**response_data["data"]["agent"]),
                "faction": Faction(**response_data["data"]["faction"]),
                "contract": Contract(**response_data["data"]["contract"]),
                "ships": [Ship(**ship) for ship in response_data["data"]["ships"]],
            }
            
        finally:
            await temp_client.aclose()