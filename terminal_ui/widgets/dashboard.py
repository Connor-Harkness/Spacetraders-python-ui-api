"""
Dashboard widget showing account overview.
"""

from datetime import datetime
from typing import Optional, List

from textual.widgets import Static, Label
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from spacetraders_client.models import Agent, Ship, Contract


class DashboardWidget(Static):
    """Dashboard widget displaying account overview."""
    
    agent_data = reactive(None)
    ships_data = reactive(None) 
    contracts_data = reactive(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console = Console()
        
    def compose(self):
        """Compose the dashboard layout."""
        yield Container(
            self.create_overview_panel(),
            self.create_quick_stats_panel(),
            self.create_recent_activity_panel(),
            classes="dashboard-overview"
        )
    
    def create_overview_panel(self) -> Static:
        """Create the main overview panel."""
        content = Text("Loading agent data...", style="dim")
        return Static(Panel(content, title="Agent Overview", border_style="blue"), classes="dashboard-stats")
    
    def create_quick_stats_panel(self) -> Static:
        """Create the quick statistics panel."""
        content = Text("Loading statistics...", style="dim")
        return Static(Panel(content, title="Quick Stats", border_style="green"), classes="dashboard-stats")
    
    def create_recent_activity_panel(self) -> Static:
        """Create the recent activity panel."""
        content = Text("Loading recent activity...", style="dim")
        return Static(Panel(content, title="Recent Activity", border_style="yellow"), classes="dashboard-stats")
    
    async def update_data(self, agent_data: Optional[Agent], ships_data: Optional[List[Ship]], contracts_data: Optional[List[Contract]]):
        """Update the dashboard with new data."""
        self.agent_data = agent_data
        self.ships_data = ships_data
        self.contracts_data = contracts_data
        
        # Update the display
        await self.update_display()
    
    async def update_display(self):
        """Update the dashboard display."""
        # Clear existing content
        await self.remove_children()
        
        # Create new content
        overview_panel = self.create_updated_overview_panel()
        stats_panel = self.create_updated_stats_panel()
        activity_panel = self.create_updated_activity_panel()
        
        # Add to container
        container = Container(
            overview_panel,
            stats_panel,
            activity_panel,
            classes="dashboard-overview"
        )
        
        await self.mount(container)
    
    def create_updated_overview_panel(self) -> Static:
        """Create updated overview panel with agent data."""
        if not self.agent_data:
            content = Text("No agent data available", style="red")
            return Static(Panel(content, title="Agent Overview", border_style="red"), classes="dashboard-stats")
        
        # Create rich text content
        content = Text()
        content.append(f"Agent: ", style="bold")
        content.append(f"{self.agent_data.symbol}\\n", style="cyan")
        content.append(f"Credits: ", style="bold")
        content.append(f"{self.agent_data.credits:,}\\n", style="green")
        content.append(f"Headquarters: ", style="bold")
        content.append(f"{self.agent_data.headquarters}\\n", style="blue")
        content.append(f"Faction: ", style="bold")
        content.append(f"{self.agent_data.startingFaction}\\n", style="magenta")
        content.append(f"Ships: ", style="bold")
        content.append(f"{self.agent_data.shipCount}", style="yellow")
        
        return Static(Panel(content, title="Agent Overview", border_style="blue"), classes="dashboard-stats")
    
    def create_updated_stats_panel(self) -> Static:
        """Create updated statistics panel."""
        if not self.ships_data or not self.contracts_data:
            content = Text("Loading statistics...", style="dim")
            return Static(Panel(content, title="Quick Stats", border_style="green"), classes="dashboard-stats")
        
        # Calculate stats
        total_ships = len(self.ships_data)
        docked_ships = sum(1 for ship in self.ships_data if ship.nav and ship.nav.status == "DOCKED")
        in_transit_ships = sum(1 for ship in self.ships_data if ship.nav and ship.nav.status == "IN_TRANSIT")
        
        active_contracts = sum(1 for contract in self.contracts_data if contract.accepted and not contract.fulfilled)
        fulfilled_contracts = sum(1 for contract in self.contracts_data if contract.fulfilled)
        
        # Create content
        content = Text()
        content.append("Ships:\\n", style="bold")
        content.append(f"  Total: {total_ships}\\n", style="white")
        content.append(f"  Docked: {docked_ships}\\n", style="green")
        content.append(f"  In Transit: {in_transit_ships}\\n", style="yellow")
        content.append("\\nContracts:\\n", style="bold")
        content.append(f"  Active: {active_contracts}\\n", style="orange")
        content.append(f"  Fulfilled: {fulfilled_contracts}", style="green")
        
        return Static(Panel(content, title="Quick Stats", border_style="green"), classes="dashboard-stats")
    
    def create_updated_activity_panel(self) -> Static:
        """Create updated activity panel."""
        if not self.ships_data:
            content = Text("No ship data available", style="dim")
            return Static(Panel(content, title="Recent Activity", border_style="yellow"), classes="dashboard-stats")
        
        # Create activity summary
        content = Text()
        content.append("Ship Status:\\n", style="bold")
        
        for ship in self.ships_data[:5]:  # Show first 5 ships
            if ship.nav:
                status_color = "green" if ship.nav.status == "DOCKED" else "yellow" if ship.nav.status == "IN_TRANSIT" else "red"
                content.append(f"  {ship.symbol}: ", style="white")
                content.append(f"{ship.nav.status}", style=status_color)
                content.append(f" at {ship.nav.waypointSymbol}\\n", style="dim")
        
        if len(self.ships_data) > 5:
            content.append(f"\\n... and {len(self.ships_data) - 5} more ships", style="dim")
        
        return Static(Panel(content, title="Recent Activity", border_style="yellow"), classes="dashboard-stats")