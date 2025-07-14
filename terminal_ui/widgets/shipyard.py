"""
Shipyard widget for ship purchasing and management.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from textual.widgets import Static, Button, Label, Select, Input
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from spacetraders_client.models import Shipyard, ShipyardShip, System, Waypoint


class ShipyardWidget(Static):
    """Shipyard widget for ship purchasing and management."""
    
    systems_data = reactive(None)
    current_system = reactive(None)
    shipyards_data = reactive(None)
    current_shipyard = reactive(None)
    
    # Custom messages for shipyard actions
    class ShipPurchase(Message):
        """Message sent when purchase ship is clicked."""
        def __init__(self, ship_type: str, waypoint_symbol: str, price: int):
            self.ship_type = ship_type
            self.waypoint_symbol = waypoint_symbol
            self.price = price
            super().__init__()
    
    class ShipyardRefresh(Message):
        """Message sent when shipyard refresh is requested."""
        def __init__(self, system_symbol: str, waypoint_symbol: str):
            self.system_symbol = system_symbol
            self.waypoint_symbol = waypoint_symbol
            super().__init__()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console = Console()
        
    def compose(self):
        """Compose the shipyard layout."""
        yield Container(
            Label("Loading shipyards...", classes="shipyard-header"),
            classes="scrollable"
        )
    
    async def update_data(self, systems_data: Optional[List[System]], shipyards_data: Optional[Dict[str, Shipyard]]):
        """Update the shipyard widget with new data."""
        self.systems_data = systems_data
        self.shipyards_data = shipyards_data
        await self.update_display()
    
    async def update_display(self):
        """Update the shipyard display."""
        # Clear existing content
        await self.remove_children()
        
        if not self.systems_data:
            container = Container(
                Label("No systems data available", classes="shipyard-header"),
                classes="scrollable"
            )
            await self.mount(container)
            return
        
        # Create system selector and shipyard content
        system_selector = self.create_system_selector()
        shipyard_content = self.create_shipyard_content()
        
        # Create main container
        main_container = Container(
            system_selector,
            shipyard_content,
            classes="shipyard-container"
        )
        
        await self.mount(main_container)
    
    def create_system_selector(self) -> Container:
        """Create system selection interface."""
        if not self.systems_data:
            return Container(
                Label("No systems available", classes="shipyard-header"),
                classes="system-selector"
            )
        
        # Create system options
        system_options = []
        for system in self.systems_data:
            system_options.append((system.symbol, system.symbol))
        
        # System selection
        system_select = Select(
            options=system_options,
            id="system-select",
            classes="system-select"
        )
        
        return Container(
            Label("Select System:", classes="shipyard-label"),
            system_select,
            classes="system-selector"
        )
    
    def create_shipyard_content(self) -> Container:
        """Create shipyard content display."""
        if not self.shipyards_data:
            return Container(
                Label("Select a system to view shipyards", classes="shipyard-info"),
                classes="shipyard-content"
            )
        
        # Create shipyard cards
        shipyard_cards = []
        for waypoint_symbol, shipyard in self.shipyards_data.items():
            card = self.create_shipyard_card(waypoint_symbol, shipyard)
            shipyard_cards.append(card)
        
        if not shipyard_cards:
            return Container(
                Label("No shipyards found in selected system", classes="shipyard-info"),
                classes="shipyard-content"
            )
        
        # Create scrollable container
        scrollable = ScrollableContainer(
            *shipyard_cards,
            classes="shipyard-scrollable"
        )
        
        return Container(
            Label(f"Shipyards ({len(shipyard_cards)} found):", classes="shipyard-header"),
            scrollable,
            classes="shipyard-content"
        )
    
    def create_shipyard_card(self, waypoint_symbol: str, shipyard: Shipyard) -> Container:
        """Create a card for a single shipyard."""
        # Shipyard header
        header = Text()
        header.append(f"{waypoint_symbol}", style="bold cyan")
        header.append(" Shipyard", style="dim")
        
        # Shipyard info
        info_text = Text()
        info_text.append(f"Available Ship Types: ", style="bold")
        info_text.append(f"{len(shipyard.shipTypes)}\\n", style="white")
        info_text.append(f"Modification Fee: ", style="bold")
        info_text.append(f"{shipyard.modificationsFee:,} credits\\n", style="yellow")
        
        # Available ships
        ships_text = Text()
        if shipyard.ships:
            ships_text.append(f"Ships Available for Purchase:\\n", style="bold")
            for ship in shipyard.ships:
                ships_text.append(f"  {ship.name} ({ship.type.value}): ", style="white")
                ships_text.append(f"{ship.purchasePrice:,} credits", style="green")
                ships_text.append(f" - {ship.supply.value} supply\\n", style="dim")
        else:
            ships_text.append("No ships currently available\\n", style="red")
        
        # Combine all info
        full_content = Text()
        full_content.append(header)
        full_content.append("\\n\\n")
        full_content.append(info_text)
        full_content.append("\\n")
        full_content.append(ships_text)
        
        # Purchase buttons
        buttons = []
        if shipyard.ships:
            for ship in shipyard.ships:
                purchase_btn = Button(
                    f"Buy {ship.name} ({ship.purchasePrice:,}c)",
                    variant="primary",
                    classes="shipyard-button"
                )
                purchase_btn.id = f"purchase-{ship.type.value}-{waypoint_symbol}-{ship.purchasePrice}"
                buttons.append(purchase_btn)
        
        # Refresh button
        refresh_btn = Button("Refresh", classes="shipyard-button")
        refresh_btn.id = f"refresh-{waypoint_symbol}"
        buttons.append(refresh_btn)
        
        button_row = Horizontal(*buttons) if buttons else Container()
        
        # Create the card
        card = Container(
            Static(Panel(full_content, title=f"Shipyard: {waypoint_symbol}", border_style="blue"), classes="shipyard-card"),
            button_row,
            classes="shipyard-card-container"
        )
        
        return card
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle shipyard button presses."""
        button_id = event.button.id
        if not button_id:
            return
        
        # Parse the button ID
        parts = button_id.split("-")
        if len(parts) < 2:
            return
        
        action = parts[0]
        
        if action == "purchase" and len(parts) >= 4:
            # purchase-{ship_type}-{waypoint_symbol}-{price}
            ship_type = parts[1]
            waypoint_symbol = parts[2]
            price = int(parts[3])
            
            await self.post_message(self.ShipPurchase(ship_type, waypoint_symbol, price))
        
        elif action == "refresh" and len(parts) >= 2:
            # refresh-{waypoint_symbol}
            waypoint_symbol = parts[1]
            
            # Get the system symbol from the waypoint symbol
            system_symbol = "-".join(waypoint_symbol.split("-")[:-1])
            
            await self.post_message(self.ShipyardRefresh(system_symbol, waypoint_symbol))
    
    async def on_select_changed(self, event: Select.Changed) -> None:
        """Handle system selection change."""
        if event.select.id == "system-select":
            selected_system = event.value
            if selected_system:
                # Request shipyard data for the selected system
                await self.post_message(self.ShipyardRefresh(selected_system, ""))