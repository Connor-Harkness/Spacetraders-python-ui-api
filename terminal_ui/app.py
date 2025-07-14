"""
Main terminal UI application for SpaceTraders client.
"""

import asyncio
import os
from datetime import datetime
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, Static, TabbedContent, TabPane
from textual.reactive import reactive
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from spacetraders_client import SpaceTradersClient, SpaceTradersError
from .widgets import DashboardWidget, ShipWidget, ContractWidget, AgentWidget, ShipyardWidget
from automation import AutomationManager


class SpaceTradersApp(App):
    """Main SpaceTraders terminal UI application."""
    
    CSS_PATH = "app.tcss"
    TITLE = "SpaceTraders Terminal UI"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "show_dashboard", "Dashboard"),
        Binding("s", "show_ships", "Ships"),
        Binding("c", "show_contracts", "Contracts"),
        Binding("a", "show_agent", "Agent"),
        Binding("y", "show_shipyard", "Shipyard"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    # Reactive variables
    client: Optional[SpaceTradersClient] = reactive(None)
    agent_data = reactive(None)
    ships_data = reactive(None)
    contracts_data = reactive(None)
    systems_data = reactive(None)
    shipyards_data = reactive(None)
    last_refresh = reactive(datetime.now())
    
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.console = Console()
        self.automation_manager = None
        
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        
        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                yield DashboardWidget(id="dashboard_content")
            
            with TabPane("Ships", id="ships"):
                yield ShipWidget(id="ships_content")
                
            with TabPane("Contracts", id="contracts"):
                yield ContractWidget(id="contracts_content")
                
            with TabPane("Agent", id="agent"):
                yield AgentWidget(id="agent_content")
                
            with TabPane("Shipyard", id="shipyard"):
                yield ShipyardWidget(id="shipyard_content")
        
        yield Footer()
    
    async def on_resize(self, event) -> None:
        """Handle terminal resize events."""
        # Refresh the display to adapt to new terminal size
        await self.refresh_display()
        
    async def refresh_display(self) -> None:
        """Refresh the display to adapt to current terminal size."""
        # Update all widgets to adapt to the new size
        dashboard = self.query_one("#dashboard_content", DashboardWidget)
        ships_widget = self.query_one("#ships_content", ShipWidget)
        contracts_widget = self.query_one("#contracts_content", ContractWidget)
        agent_widget = self.query_one("#agent_content", AgentWidget)
        shipyard_widget = self.query_one("#shipyard_content", ShipyardWidget)
        
        # Re-render each widget with current data
        await dashboard.update_data(self.agent_data, self.ships_data, self.contracts_data)
        await ships_widget.update_data(self.ships_data)
        await contracts_widget.update_data(self.contracts_data)
        await agent_widget.update_data(self.agent_data)
        await shipyard_widget.update_data(self.systems_data, self.shipyards_data)
        
    async def on_mount(self) -> None:
        """Initialize the application."""
        await self.initialize_client()
        await self.refresh_data()
        
    async def initialize_client(self) -> None:
        """Initialize the SpaceTraders client."""
        try:
            self.client = SpaceTradersClient(token=self.token)
            # Test the connection
            await self.client.get_my_agent()
            
            # Initialize automation manager
            self.automation_manager = AutomationManager(self.client)
            
            self.notify("Connected to SpaceTraders API", title="Success")
        except SpaceTradersError as e:
            self.notify(f"Failed to connect: {e.message}", title="Error", severity="error")
            self.exit(1)
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
            self.exit(1)
    
    async def refresh_data(self) -> None:
        """Refresh all data from the API."""
        if not self.client:
            return
            
        try:
            # Get agent data
            self.agent_data = await self.client.get_my_agent()
            
            # Get ships data
            ships_response = await self.client.get_ships(limit=20)
            self.ships_data = ships_response["data"]
            
            # Get contracts data
            contracts_response = await self.client.get_contracts(limit=20)
            self.contracts_data = contracts_response["data"]
            
            # Get systems data (for shipyard functionality)
            systems_response = await self.client.get_systems(limit=20)
            self.systems_data = systems_response["data"]
            
            self.last_refresh = datetime.now()
            
            # Update widgets
            dashboard = self.query_one("#dashboard_content", DashboardWidget)
            ships_widget = self.query_one("#ships_content", ShipWidget)
            contracts_widget = self.query_one("#contracts_content", ContractWidget)
            agent_widget = self.query_one("#agent_content", AgentWidget)
            shipyard_widget = self.query_one("#shipyard_content", ShipyardWidget)
            
            await dashboard.update_data(self.agent_data, self.ships_data, self.contracts_data)
            await ships_widget.update_data(self.ships_data)
            await contracts_widget.update_data(self.contracts_data)
            await agent_widget.update_data(self.agent_data)
            await shipyard_widget.update_data(self.systems_data, self.shipyards_data)
            
        except SpaceTradersError as e:
            self.notify(f"Failed to refresh data: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_show_dashboard(self) -> None:
        """Show the dashboard tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "dashboard"
        
    def action_show_ships(self) -> None:
        """Show the ships tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "ships"
        
    def action_show_contracts(self) -> None:
        """Show the contracts tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "contracts"
        
    def action_show_agent(self) -> None:
        """Show the agent tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "agent"
        
    def action_show_shipyard(self) -> None:
        """Show the shipyard tab."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "shipyard"
        
    async def action_refresh(self) -> None:
        """Refresh all data."""
        self.notify("Refreshing data...", title="Info")
        await self.refresh_data()
        self.notify("Data refreshed", title="Success")
    
    async def on_unmount(self) -> None:
        """Clean up when the app shuts down."""
        if self.automation_manager:
            await self.automation_manager.stop()
        if self.client:
            await self.client.close()
    
    # Contract action handlers
    async def on_contract_widget_contract_accept(self, event: ContractWidget.ContractAccept) -> None:
        """Handle contract accept action."""
        try:
            self.notify(f"Accepting contract {event.contract_id}...", title="Contract Action")
            response = await self.client.accept_contract(event.contract_id)
            self.notify(f"Contract {event.contract_id} accepted successfully!", title="Success")
            await self.refresh_data()
        except SpaceTradersError as e:
            self.notify(f"Failed to accept contract: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
    
    async def on_contract_widget_contract_fulfill(self, event: ContractWidget.ContractFulfill) -> None:
        """Handle contract fulfill action."""
        try:
            self.notify(f"Fulfilling contract {event.contract_id}...", title="Contract Action")
            response = await self.client.fulfill_contract(event.contract_id)
            self.notify(f"Contract {event.contract_id} fulfilled successfully!", title="Success")
            await self.refresh_data()
        except SpaceTradersError as e:
            self.notify(f"Failed to fulfill contract: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
    
    async def on_contract_widget_contract_automate(self, event: ContractWidget.ContractAutomate) -> None:
        """Handle contract automate action."""
        try:
            if not self.automation_manager:
                self.notify("Automation manager not initialized", title="Error", severity="error")
                return
            
            self.notify(f"Starting automation for contract {event.contract_id}...", title="Automation")
            
            # Find the contract
            contract = None
            for c in self.contracts_data or []:
                if c.id == event.contract_id:
                    contract = c
                    break
            
            if not contract:
                self.notify("Contract not found", title="Error", severity="error")
                return
            
            # Start contract automation
            await self.automation_manager.start_contract_automation(contract)
            self.notify(f"Automation started for contract {event.contract_id}", title="Success")
            
        except Exception as e:
            self.notify(f"Failed to start automation: {str(e)}", title="Error", severity="error")
    
    async def on_contract_widget_contract_details(self, event: ContractWidget.ContractDetails) -> None:
        """Handle contract details action."""
        try:
            # For now, just show a notification with contract ID
            # In a full implementation, this would open a detailed view
            self.notify(f"Viewing details for contract {event.contract_id}", title="Contract Details")
        except Exception as e:
            self.notify(f"Failed to show contract details: {str(e)}", title="Error", severity="error")
    
    # Ship action handlers
    async def on_ship_widget_ship_navigate(self, event: ShipWidget.ShipNavigate) -> None:
        """Handle ship navigate action."""
        try:
            # For now, just show a notification that navigation would be implemented
            # In a full implementation, this would show a dialog to select destination
            self.notify(f"Navigate functionality for {event.ship_symbol} - destination selection would be implemented here", title="Ship Action")
        except Exception as e:
            self.notify(f"Failed to navigate ship: {str(e)}", title="Error", severity="error")
    
    async def on_ship_widget_ship_dock(self, event: ShipWidget.ShipDock) -> None:
        """Handle ship dock action."""
        try:
            self.notify(f"Docking ship {event.ship_symbol}...", title="Ship Action")
            response = await self.client.dock_ship(event.ship_symbol)
            self.notify(f"Ship {event.ship_symbol} docked successfully!", title="Success")
            await self.refresh_data()
        except SpaceTradersError as e:
            self.notify(f"Failed to dock ship: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
    
    async def on_ship_widget_ship_orbit(self, event: ShipWidget.ShipOrbit) -> None:
        """Handle ship orbit action."""
        try:
            self.notify(f"Orbiting ship {event.ship_symbol}...", title="Ship Action")
            response = await self.client.orbit_ship(event.ship_symbol)
            self.notify(f"Ship {event.ship_symbol} in orbit!", title="Success")
            await self.refresh_data()
        except SpaceTradersError as e:
            self.notify(f"Failed to orbit ship: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
    
    async def on_ship_widget_ship_refuel(self, event: ShipWidget.ShipRefuel) -> None:
        """Handle ship refuel action."""
        try:
            self.notify(f"Refueling ship {event.ship_symbol}...", title="Ship Action")
            response = await self.client.refuel_ship(event.ship_symbol)
            self.notify(f"Ship {event.ship_symbol} refueled successfully!", title="Success")
            await self.refresh_data()
        except SpaceTradersError as e:
            self.notify(f"Failed to refuel ship: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
    
    async def on_ship_widget_ship_automate(self, event: ShipWidget.ShipAutomate) -> None:
        """Handle ship automate action."""
        try:
            if not self.automation_manager:
                self.notify("Automation manager not initialized", title="Error", severity="error")
                return
            
            self.notify(f"Starting automation for ship {event.ship_symbol}...", title="Automation")
            
            # Find the ship
            ship = None
            for s in self.ships_data or []:
                if s.symbol == event.ship_symbol:
                    ship = s
                    break
            
            if not ship:
                self.notify("Ship not found", title="Error", severity="error")
                return
            
            # Start ship automation (default to mining role)
            await self.automation_manager.start_ship_automation(ship, role="mining")
            self.notify(f"Automation started for ship {event.ship_symbol}", title="Success")
            
        except Exception as e:
            self.notify(f"Failed to start automation: {str(e)}", title="Error", severity="error")
    
    # Shipyard action handlers
    async def on_shipyard_widget_ship_purchase(self, event: ShipyardWidget.ShipPurchase) -> None:
        """Handle ship purchase action."""
        try:
            self.notify(f"Purchasing {event.ship_type} for {event.price:,} credits...", title="Ship Purchase")
            response = await self.client.purchase_ship(event.ship_type, event.waypoint_symbol)
            
            # Show success message with ship details
            ship_name = response["ship"].symbol
            agent_credits = response["agent"].credits
            
            self.notify(f"Successfully purchased {ship_name}! Remaining credits: {agent_credits:,}", title="Purchase Success")
            
            # Refresh data to show the new ship
            await self.refresh_data()
            
        except SpaceTradersError as e:
            self.notify(f"Failed to purchase ship: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
    
    async def on_shipyard_widget_shipyard_refresh(self, event: ShipyardWidget.ShipyardRefresh) -> None:
        """Handle shipyard refresh action."""
        try:
            if not event.waypoint_symbol:
                # Refresh all shipyards for a system
                await self.refresh_system_shipyards(event.system_symbol)
            else:
                # Refresh specific shipyard
                await self.refresh_specific_shipyard(event.system_symbol, event.waypoint_symbol)
        except Exception as e:
            self.notify(f"Failed to refresh shipyard: {str(e)}", title="Error", severity="error")
    
    async def refresh_system_shipyards(self, system_symbol: str) -> None:
        """Refresh shipyards for a specific system."""
        try:
            self.notify(f"Loading shipyards for system {system_symbol}...", title="Shipyard Refresh")
            
            # Get all waypoints in the system
            waypoints_response = await self.client.get_system_waypoints(system_symbol, limit=50)
            waypoints = waypoints_response["data"]
            
            # Find waypoints with shipyards
            shipyard_waypoints = []
            for waypoint in waypoints:
                if waypoint.traits:
                    for trait in waypoint.traits:
                        if trait.symbol == "SHIPYARD":
                            shipyard_waypoints.append(waypoint)
                            break
            
            # Get shipyard data for each waypoint
            shipyards = {}
            for waypoint in shipyard_waypoints:
                try:
                    shipyard = await self.client.get_shipyard(system_symbol, waypoint.symbol)
                    shipyards[waypoint.symbol] = shipyard
                except SpaceTradersError:
                    # Skip waypoints where we can't get shipyard data
                    continue
            
            # Update shipyards data
            self.shipyards_data = shipyards
            
            # Update shipyard widget
            shipyard_widget = self.query_one("#shipyard_content", ShipyardWidget)
            await shipyard_widget.update_data(self.systems_data, self.shipyards_data)
            
            self.notify(f"Found {len(shipyards)} shipyards in {system_symbol}", title="Shipyard Refresh")
            
        except SpaceTradersError as e:
            self.notify(f"Failed to refresh shipyards: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")
    
    async def refresh_specific_shipyard(self, system_symbol: str, waypoint_symbol: str) -> None:
        """Refresh a specific shipyard."""
        try:
            self.notify(f"Refreshing shipyard {waypoint_symbol}...", title="Shipyard Refresh")
            
            shipyard = await self.client.get_shipyard(system_symbol, waypoint_symbol)
            
            # Update shipyards data
            if not self.shipyards_data:
                self.shipyards_data = {}
            self.shipyards_data[waypoint_symbol] = shipyard
            
            # Update shipyard widget
            shipyard_widget = self.query_one("#shipyard_content", ShipyardWidget)
            await shipyard_widget.update_data(self.systems_data, self.shipyards_data)
            
            self.notify(f"Shipyard {waypoint_symbol} refreshed", title="Shipyard Refresh")
            
        except SpaceTradersError as e:
            self.notify(f"Failed to refresh shipyard: {e.message}", title="Error", severity="error")
        except Exception as e:
            self.notify(f"Unexpected error: {str(e)}", title="Error", severity="error")


def main():
    """Main entry point for the terminal UI."""
    token = os.getenv("SPACETRADERS_TOKEN")
    if not token:
        print("Error: SPACETRADERS_TOKEN environment variable not set")
        print("Please set your SpaceTraders API token:")
        print("export SPACETRADERS_TOKEN='your_token_here'")
        return 1
    
    app = SpaceTradersApp(token)
    app.run()
    return 0


if __name__ == "__main__":
    exit(main())