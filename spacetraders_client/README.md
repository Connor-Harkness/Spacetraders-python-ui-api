# SpaceTraders Python Client

A modern, typed, object-oriented Python client for the [SpaceTraders API](https://docs.spacetraders.io/).

## Features

- **Fully Typed**: Built with Pydantic v2 for comprehensive type safety and validation
- **Object-Oriented Design**: Clean, intuitive interface for all API operations
- **Async/Await Support**: Non-blocking operations using `httpx`
- **Comprehensive Coverage**: All SpaceTraders API v2.3.0 endpoints included
- **Error Handling**: Proper exception handling with detailed error information
- **Auto-generated Models**: Type-safe data models generated from OpenAPI specification

## Installation

Install the required dependencies:

```bash
pip install httpx pydantic typing-extensions
```

## Quick Start

### 1. Register a New Agent

```python
import asyncio
from spacetraders_client import SpaceTradersClient

async def register_agent():
    # Register a new agent
    registration_data = await SpaceTradersClient.register_new_agent(
        symbol="MYAGENT",
        faction="COSMIC"
    )
    
    token = registration_data["token"]
    agent = registration_data["agent"]
    
    print(f"Agent {agent.symbol} registered!")
    print(f"Credits: {agent.credits}")
    print(f"Token: {token}")
    
    return token

# Run the registration
token = asyncio.run(register_agent())
```

### 2. Initialize Client and Explore

```python
import asyncio
from spacetraders_client import SpaceTradersClient

async def explore_universe():
    async with SpaceTradersClient(token="your_token_here") as client:
        # Get your agent info
        agent = await client.get_my_agent()
        print(f"Agent: {agent.symbol}")
        print(f"Headquarters: {agent.headquarters}")
        print(f"Credits: {agent.credits}")
        
        # List your ships
        ships_data = await client.get_ships()
        ships = ships_data["data"]
        print(f"\\nYou have {len(ships)} ships:")
        
        for ship in ships:
            print(f"  - {ship.symbol} ({ship.registration.role})")
            print(f"    Location: {ship.nav.waypointSymbol}")
            print(f"    Status: {ship.nav.status}")
        
        # Get contracts
        contracts_data = await client.get_contracts()
        contracts = contracts_data["data"]
        print(f"\\nYou have {len(contracts)} contracts:")
        
        for contract in contracts:
            print(f"  - {contract.id}")
            print(f"    Type: {contract.type}")
            print(f"    Accepted: {contract.accepted}")
            if contract.terms.payment:
                print(f"    Payment: {contract.terms.payment.onFulfilled} credits")

# Run the exploration
asyncio.run(explore_universe())
```

### 3. Ship Operations

```python
import asyncio
from spacetraders_client import SpaceTradersClient

async def ship_operations():
    async with SpaceTradersClient(token="your_token_here") as client:
        # Get the first ship
        ships_data = await client.get_ships(limit=1)
        ship = ships_data["data"][0]
        ship_symbol = ship.symbol
        
        print(f"Operating ship: {ship_symbol}")
        
        # Dock the ship if it's not already docked
        if ship.nav.status != "DOCKED":
            await client.dock_ship(ship_symbol)
            print("Ship docked!")
        
        # Get current system info
        current_system = ship.nav.systemSymbol
        system = await client.get_system(current_system)
        print(f"\\nCurrent system: {system.symbol}")
        print(f"System type: {system.type}")
        
        # List waypoints in current system
        waypoints_data = await client.get_system_waypoints(current_system, limit=5)
        waypoints = waypoints_data["data"]
        
        print(f"\\nWaypoints in {current_system}:")
        for waypoint in waypoints:
            print(f"  - {waypoint.symbol} ({waypoint.type})")
            if waypoint.traits:
                traits = [trait.symbol for trait in waypoint.traits]
                print(f"    Traits: {', '.join(traits)}")

# Run ship operations
asyncio.run(ship_operations())
```

### 4. Market and Trading

```python
import asyncio
from spacetraders_client import SpaceTradersClient

async def check_markets():
    async with SpaceTradersClient(token="your_token_here") as client:
        # Find waypoints with markets
        ships_data = await client.get_ships(limit=1)
        ship = ships_data["data"][0]
        current_system = ship.nav.systemSymbol
        
        # Get waypoints and filter for markets
        waypoints_data = await client.get_system_waypoints(current_system, limit=20)
        market_waypoints = []
        
        for waypoint in waypoints_data["data"]:
            if waypoint.traits:
                trait_symbols = [trait.symbol for trait in waypoint.traits]
                if "MARKETPLACE" in trait_symbols:
                    market_waypoints.append(waypoint)
        
        print(f"Found {len(market_waypoints)} markets in {current_system}:")
        
        for waypoint in market_waypoints[:3]:  # Check first 3 markets
            try:
                market = await client.get_market(current_system, waypoint.symbol)
                print(f"\\n--- Market at {waypoint.symbol} ---")
                
                if market.imports:
                    print("Imports:")
                    for good in market.imports[:3]:  # Show first 3
                        print(f"  - {good.name} ({good.symbol})")
                
                if market.exports:
                    print("Exports:")
                    for good in market.exports[:3]:  # Show first 3
                        print(f"  - {good.name} ({good.symbol})")
                        
            except Exception as e:
                print(f"Could not access market at {waypoint.symbol}: {e}")

# Run market check
asyncio.run(check_markets())
```

## API Reference

### Client Initialization

```python
client = SpaceTradersClient(
    token="your_bearer_token",          # Required for most operations
    base_url="https://api.spacetraders.io/v2",  # Optional, defaults to official API
    timeout=30.0                        # Optional, request timeout in seconds
)
```

### Main API Categories

#### Agent Operations
- `get_my_agent()` - Get your agent details
- `get_agents(page, limit)` - List all public agents
- `get_agent(agent_symbol)` - Get specific agent details

#### Fleet Management
- `get_ships(page, limit)` - List your ships
- `get_ship(ship_symbol)` - Get ship details
- `purchase_ship(ship_type, waypoint_symbol)` - Buy a new ship
- `dock_ship(ship_symbol)` - Dock ship
- `orbit_ship(ship_symbol)` - Move ship to orbit
- `navigate_ship(ship_symbol, waypoint_symbol)` - Navigate to destination

#### Contracts
- `get_contracts(page, limit)` - List your contracts
- `get_contract(contract_id)` - Get contract details
- `accept_contract(contract_id)` - Accept a contract
- `fulfill_contract(contract_id)` - Fulfill a contract

#### Factions
- `get_factions(page, limit)` - List all factions
- `get_faction(faction_symbol)` - Get faction details

#### Systems & Universe
- `get_systems(page, limit)` - List systems
- `get_system(system_symbol)` - Get system details
- `get_system_waypoints(system_symbol, ...)` - List waypoints in system
- `get_waypoint(system_symbol, waypoint_symbol)` - Get waypoint details
- `get_market(system_symbol, waypoint_symbol)` - Get market data
- `get_shipyard(system_symbol, waypoint_symbol)` - Get shipyard data

#### Utility
- `get_status()` - Get server status

### Error Handling

All API methods can raise `SpaceTradersError` exceptions:

```python
from spacetraders_client import SpaceTradersClient, SpaceTradersError

async def handle_errors():
    async with SpaceTradersClient(token="invalid_token") as client:
        try:
            agent = await client.get_my_agent()
        except SpaceTradersError as e:
            print(f"API Error: {e.message}")
            print(f"Status Code: {e.status_code}")
            print(f"Error Code: {e.error_code}")
```

### Context Manager

The client supports async context managers for automatic cleanup:

```python
async with SpaceTradersClient(token="your_token") as client:
    # Use client here
    agent = await client.get_my_agent()
# Client is automatically closed
```

Or manual cleanup:

```python
client = SpaceTradersClient(token="your_token")
try:
    agent = await client.get_my_agent()
finally:
    await client.close()
```

## Data Models

All API responses are parsed into type-safe Pydantic models. Key models include:

- `Agent` - Player agent information
- `Ship` - Ship details including navigation, cargo, modules
- `Contract` - Contract terms and status
- `Faction` - Faction information and traits
- `System` - Star system with waypoints
- `Waypoint` - Locations within systems
- `Market` - Trading post information
- `Shipyard` - Ship purchasing and modification

See the `models.py` file for complete model definitions.

## Advanced Usage

### Custom Base URL

```python
# For testing or private servers
client = SpaceTradersClient(
    token="your_token",
    base_url="https://your-custom-server.com/v2"
)
```

### Request Timeout

```python
# Increase timeout for slow connections
client = SpaceTradersClient(
    token="your_token",
    timeout=60.0
)
```

## Requirements

- Python 3.8+
- httpx >= 0.23.0
- pydantic >= 2.0.0
- typing-extensions >= 4.0.0

## Contributing

This client is generated from the official SpaceTraders OpenAPI specification. To contribute:

1. Update the OpenAPI spec if needed
2. Regenerate models using `datamodel-codegen`
3. Update the client code as needed
4. Add tests and examples

## License

This project is open source. See the SpaceTraders API documentation for terms of use.

## Links

- [SpaceTraders Game](https://spacetraders.io/)
- [Official API Documentation](https://docs.spacetraders.io/)
- [OpenAPI Specification](https://stoplight.io/p/docs/gh/SpaceTradersAPI/api-docs)