#!/usr/bin/env python3
"""
SpaceTraders Python Client Example

This example demonstrates basic usage of the SpaceTraders Python client.
Run this script to see the client in action.

To use this script:
1. Install dependencies: pip install httpx pydantic typing-extensions
2. Set your token as an environment variable: export SPACETRADERS_TOKEN="your_token_here"
3. Run: python3 example.py
"""

import asyncio
import os
import sys
from typing import Optional

# Add the parent directory to the path so we can import spacetraders_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from spacetraders_client import SpaceTradersClient, SpaceTradersError


async def demo_server_status():
    """Demonstrate getting server status (no auth required)."""
    print("=== Server Status ===")
    
    async with SpaceTradersClient() as client:
        try:
            status = await client.get_status()
            print(f"Server Status: {status.get('status', 'Unknown')}")
            print(f"Version: {status.get('version', 'Unknown')}")
            print(f"Reset Date: {status.get('resetDate', 'Unknown')}")
            
            # Show some statistics
            stats = status.get('stats', {})
            if stats:
                print(f"Total Agents: {stats.get('agents', 'Unknown')}")
                print(f"Total Ships: {stats.get('ships', 'Unknown')}")
                print(f"Total Systems: {stats.get('systems', 'Unknown')}")
        
        except SpaceTradersError as e:
            print(f"Error getting server status: {e}")


async def demo_public_data():
    """Demonstrate accessing public data (no auth required)."""
    print("\\n=== Public Data ===")
    
    async with SpaceTradersClient() as client:
        try:
            # Get some factions
            print("\\nFactions:")
            factions_data = await client.get_factions(limit=5)
            factions = factions_data["data"]
            
            for faction in factions:
                print(f"  - {faction.symbol}: {faction.name}")
                print(f"    Recruiting: {faction.isRecruiting}")
                print(f"    HQ: {faction.headquarters}")
            
            # Get some public agents
            print("\\nPublic Agents:")
            agents_data = await client.get_agents(limit=5)
            agents = agents_data["data"]
            
            for agent in agents:
                print(f"  - {agent.symbol} (Credits: {agent.credits:,})")
                print(f"    Ships: {agent.shipCount}, Faction: {agent.startingFaction}")
        
        except SpaceTradersError as e:
            print(f"Error getting public data: {e}")


async def demo_agent_registration():
    """Demonstrate new agent registration."""
    print("\\n=== Agent Registration Demo ===")
    print("This would register a new agent (commented out to avoid creating test agents)")
    
    # Uncomment the following to actually register a new agent:
    
    # try:
    #     import random
    #     import string
    #     
    #     # Generate a random agent name
    #     random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    #     agent_symbol = f"DEMO{random_suffix}"
    #     
    #     print(f"Registering agent: {agent_symbol}")
    #     
    #     registration_data = await SpaceTradersClient.register_new_agent(
    #         symbol=agent_symbol,
    #         faction="COSMIC"
    #     )
    #     
    #     print(f"Success! Agent {registration_data['agent'].symbol} registered")
    #     print(f"Token: {registration_data['token']}")
    #     print(f"Starting credits: {registration_data['agent'].credits}")
    #     print(f"Starting ships: {len(registration_data['ships'])}")
    #     
    #     return registration_data['token']
    #     
    # except SpaceTradersError as e:
    #     print(f"Registration failed: {e}")
    
    return None


async def demo_authenticated_operations(token: str):
    """Demonstrate operations that require authentication."""
    print(f"\\n=== Authenticated Operations ===")
    
    async with SpaceTradersClient(token=token) as client:
        try:
            # Get agent info
            print("\\nYour Agent:")
            agent = await client.get_my_agent()
            print(f"  Symbol: {agent.symbol}")
            print(f"  Credits: {agent.credits:,}")
            print(f"  Headquarters: {agent.headquarters}")
            print(f"  Starting Faction: {agent.startingFaction}")
            print(f"  Ships: {agent.shipCount}")
            
            # Get ships
            print("\\nYour Ships:")
            ships_data = await client.get_ships(limit=10)
            ships = ships_data["data"]
            
            for ship in ships:
                print(f"  - {ship.symbol} ({ship.registration.role})")
                print(f"    Location: {ship.nav.waypointSymbol}")
                print(f"    Status: {ship.nav.status}")
                print(f"    Fuel: {ship.fuel.current}/{ship.fuel.capacity}")
            
            # Get contracts
            print("\\nYour Contracts:")
            contracts_data = await client.get_contracts(limit=5)
            contracts = contracts_data["data"]
            
            for contract in contracts:
                print(f"  - {contract.id} ({contract.type})")
                print(f"    Accepted: {contract.accepted}")
                print(f"    Fulfilled: {contract.fulfilled}")
                if contract.terms.payment:
                    print(f"    Payment: {contract.terms.payment.onFulfilled:,} credits")
            
            # If we have ships, demonstrate some operations
            if ships:
                ship = ships[0]
                ship_symbol = ship.symbol
                
                print(f"\\nDemonstrating operations with ship {ship_symbol}:")
                
                # Get detailed ship info
                detailed_ship = await client.get_ship(ship_symbol)
                print(f"  Frame: {detailed_ship.frame.name}")
                print(f"  Engine: {detailed_ship.engine.name}")
                print(f"  Reactor: {detailed_ship.reactor.name}")
                
                # Show current system info
                current_system = ship.nav.systemSymbol
                system = await client.get_system(current_system)
                print(f"  Current System: {system.symbol} ({system.type})")
                
                # List nearby waypoints
                waypoints_data = await client.get_system_waypoints(current_system, limit=5)
                waypoints = waypoints_data["data"]
                print(f"  Nearby Waypoints ({len(waypoints)}):")
                
                for waypoint in waypoints:
                    traits = []
                    if waypoint.traits:
                        traits = [trait.symbol for trait in waypoint.traits]
                    traits_str = f" [{', '.join(traits)}]" if traits else ""
                    print(f"    - {waypoint.symbol} ({waypoint.type}){traits_str}")
        
        except SpaceTradersError as e:
            print(f"Error in authenticated operations: {e}")


async def main():
    """Main demo function."""
    print("SpaceTraders Python Client Demo")
    print("=" * 40)
    
    # Demo 1: Server status (no auth required)
    await demo_server_status()
    
    # Demo 2: Public data (no auth required)
    await demo_public_data()
    
    # Demo 3: Agent registration (creates new agent)
    new_token = await demo_agent_registration()
    
    # Demo 4: Authenticated operations
    # Try to use token from environment variable or newly registered agent
    token = os.getenv("SPACETRADERS_TOKEN") or new_token
    
    if token:
        await demo_authenticated_operations(token)
    else:
        print("\\n=== Authenticated Operations ===")
        print("No token available. Set SPACETRADERS_TOKEN environment variable")
        print("or uncomment the registration code to create a new agent.")
    
    print("\\n" + "=" * 40)
    print("Demo complete!")


if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nDemo interrupted by user.")
    except Exception as e:
        print(f"\\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()