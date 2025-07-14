"""
Agent widget for agent information and settings.
"""

from typing import Optional

from textual.widgets import Static, Button, Label
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from spacetraders_client.models import Agent


class AgentWidget(Static):
    """Agent widget for agent information."""
    
    agent_data = reactive(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console = Console()
        
    def compose(self):
        """Compose the agent layout."""
        yield Container(
            Label("Loading agent data...", classes="agent-header"),
            classes="agent-info"
        )
    
    async def update_data(self, agent_data: Optional[Agent]):
        """Update the agent widget with new data."""
        self.agent_data = agent_data
        await self.update_display()
    
    async def update_display(self):
        """Update the agent display."""
        # Clear existing content
        await self.remove_children()
        
        if not self.agent_data:
            container = Container(
                Label("No agent data available", classes="agent-header"),
                classes="agent-info"
            )
            await self.mount(container)
            return
        
        # Create agent information display
        info_panel = self.create_agent_info_panel()
        settings_panel = self.create_settings_panel()
        
        container = Container(
            info_panel,
            settings_panel,
            classes="agent-info"
        )
        
        await self.mount(container)
    
    def create_agent_info_panel(self) -> Container:
        """Create the agent information panel."""
        # Agent details
        content = Text()
        content.append("Agent Information\\n", style="bold magenta")
        content.append("=" * 40 + "\\n", style="dim")
        
        content.append(f"Symbol: ", style="bold")
        content.append(f"{self.agent_data.symbol}\\n", style="cyan")
        
        content.append(f"Account ID: ", style="bold")
        content.append(f"{self.agent_data.accountId}\\n", style="dim")
        
        content.append(f"Credits: ", style="bold")
        content.append(f"{self.agent_data.credits:,}\\n", style="green")
        
        content.append(f"Headquarters: ", style="bold")
        content.append(f"{self.agent_data.headquarters}\\n", style="blue")
        
        content.append(f"Starting Faction: ", style="bold")
        content.append(f"{self.agent_data.startingFaction}\\n", style="magenta")
        
        content.append(f"Ship Count: ", style="bold")
        content.append(f"{self.agent_data.shipCount}\\n", style="yellow")
        
        # Credit status analysis
        content.append("\\nCredit Status:\\n", style="bold")
        if self.agent_data.credits < 0:
            content.append("⚠️  OVERDRAWN", style="red bold")
        elif self.agent_data.credits < 10000:
            content.append("💰 Low Credits", style="yellow")
        elif self.agent_data.credits < 100000:
            content.append("💰 Moderate Credits", style="green")
        else:
            content.append("💰 High Credits", style="bright_green")
        
        panel = Static(
            Panel(content, title="Agent Details", border_style="magenta"),
            classes="agent-info"
        )
        
        return panel
    
    def create_settings_panel(self) -> Container:
        """Create the settings/actions panel."""
        # Settings content
        content = Text()
        content.append("Agent Settings & Actions\\n", style="bold cyan")
        content.append("=" * 40 + "\\n", style="dim")
        
        content.append("• Automation Settings\\n", style="white")
        content.append("• Fleet Management\\n", style="white")
        content.append("• Contract Preferences\\n", style="white")
        content.append("• Trading Strategies\\n", style="white")
        content.append("• Refuel Automation\\n", style="white")
        
        # Action buttons
        buttons = Horizontal(
            Button("Refresh Data", variant="primary", classes="agent-button"),
            Button("Fleet Overview", classes="agent-button"),
            Button("Contract Summary", classes="agent-button"),
            Button("Settings", classes="agent-button"),
        )
        
        panel = Container(
            Static(Panel(content, title="Settings & Actions", border_style="cyan"), classes="agent-info"),
            buttons,
            classes="agent-container"
        )
        
        return panel