"""
Rate-limited SpaceTraders API client for the WebUI.
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any, Union
from config import Config
from rate_limiter import RateLimiter, rate_limited

class SpaceTradersAPIClient:
    """Rate-limited SpaceTraders API client."""
    
    def __init__(self, token: str):
        """
        Initialize the API client.
        
        Args:
            token: SpaceTraders API token
        """
        self.token = token
        self.base_url = Config.SPACETRADERS_BASE_URL
        self.rate_limiter = RateLimiter(
            max_requests=Config.RATE_LIMIT_REQUESTS,
            time_window=Config.RATE_LIMIT_WINDOW
        )
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": f"{Config.APP_NAME}/1.0.0"
            },
            timeout=30.0
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    @rate_limited
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make a rate-limited HTTP request to the SpaceTraders API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for httpx request
            
        Returns:
            JSON response data
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # Log error and re-raise
            print(f"API request failed: {method} {url} - {e}")
            raise
    
    async def get_agent(self) -> Dict[str, Any]:
        """Get the current agent's information."""
        return await self._request("GET", "/my/agent")
    
    async def get_ships(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Get the list of ships owned by the agent.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
        """
        params = {"page": page, "limit": limit}
        return await self._request("GET", "/my/ships", params=params)
    
    async def get_ship(self, ship_symbol: str) -> Dict[str, Any]:
        """
        Get details for a specific ship.
        
        Args:
            ship_symbol: Symbol of the ship to get details for
        """
        return await self._request("GET", f"/my/ships/{ship_symbol}")
    
    async def get_contracts(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Get the list of contracts for the agent.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
        """
        params = {"page": page, "limit": limit}
        return await self._request("GET", "/my/contracts", params=params)
    
    async def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """
        Get details for a specific contract.
        
        Args:
            contract_id: ID of the contract to get details for
        """
        return await self._request("GET", f"/my/contracts/{contract_id}")
    
    async def get_systems(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Get the list of systems.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
        """
        params = {"page": page, "limit": limit}
        return await self._request("GET", "/systems", params=params)
    
    async def get_waypoints(self, system_symbol: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Get waypoints in a system.
        
        Args:
            system_symbol: Symbol of the system
            page: Page number for pagination
            limit: Number of items per page
        """
        params = {"page": page, "limit": limit}
        return await self._request("GET", f"/systems/{system_symbol}/waypoints", params=params)
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get the current server status and game information."""
        return await self._request("GET", "/")