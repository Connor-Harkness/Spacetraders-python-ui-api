"""
Ships widget for fleet management.
"""

from typing import Optional, List

from textual.widgets import Static, Button, Label
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from spacetraders_client.models import Ship


class ShipWidget(Static):
    """Ships widget for fleet management."""
    
    ships_data = reactive(None)
    
    # Custom messages for ship actions
    class ShipNavigate(Message):
        """Message sent when navigate ship is clicked."""
        def __init__(self, ship_symbol: str):
            self.ship_symbol = ship_symbol
            super().__init__()
    
    class ShipDock(Message):
        """Message sent when dock ship is clicked."""
        def __init__(self, ship_symbol: str):
            self.ship_symbol = ship_symbol
            super().__init__()
    
    class ShipOrbit(Message):
        """Message sent when orbit ship is clicked."""
        def __init__(self, ship_symbol: str):
            self.ship_symbol = ship_symbol
            super().__init__()
    
    class ShipRefuel(Message):
        """Message sent when refuel ship is clicked."""
        def __init__(self, ship_symbol: str):
            self.ship_symbol = ship_symbol
            super().__init__()
    
    class ShipAutomate(Message):
        """Message sent when automate ship is clicked."""
        def __init__(self, ship_symbol: str):
            self.ship_symbol = ship_symbol
            super().__init__()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console = Console()
        
    def compose(self):
        """Compose the ships layout."""
        yield ScrollableContainer(
            Container(
                Label("Loading ships...", classes="ship-header"),
                classes="ships-content"
            ),
            classes="ships-scrollable"
        )
    
    async def update_data(self, ships_data: Optional[List[Ship]]):
        """Update the ships widget with new data."""
        self.ships_data = ships_data
        await self.update_display()
    
    async def update_display(self):
        """Update the ships display."""
        # Clear existing content
        await self.remove_children()
        
        if not self.ships_data:
            container = Container(
                Label("No ships available", classes="ship-header"),
                classes="ships-content"
            )
            scrollable = ScrollableContainer(
                container,
                classes="ships-scrollable"
            )
            await self.mount(scrollable)
            return
        
        # Create ship cards
        ship_cards = []
        for ship in self.ships_data:
            card = self.create_ship_card(ship)
            ship_cards.append(card)
        
        # Create scrollable container
        container = Container(
            *ship_cards,
            classes="ships-content"
        )
        
        scrollable = ScrollableContainer(
            container,
            classes="ships-scrollable"
        )
        
        await self.mount(scrollable)
    
    def create_ship_card(self, ship: Ship) -> Container:
        """Create a card for a single ship."""
        # Ship header with responsive formatting
        header = Text()
        # Truncate ship symbol for small screens
        ship_symbol = ship.symbol[:12] + "..." if len(ship.symbol) > 15 else ship.symbol
        header.append(f"{ship_symbol}", style="bold cyan")
        if ship.registration:
            header.append(f" ({ship.registration.role})", style="dim")
        
        # Ship status
        status_text = Text()
        if ship.nav:
            status_color = "green" if ship.nav.status == "DOCKED" else "yellow" if ship.nav.status == "IN_TRANSIT" else "red"
            status_text.append(f"Status: ", style="bold")
            status_text.append(f"{ship.nav.status}\n", style=status_color)
            
            # Responsive location display
            waypoint_symbol = ship.nav.waypointSymbol
            if len(waypoint_symbol) > 20:
                waypoint_symbol = waypoint_symbol[-20:]  # Show last 20 characters
            status_text.append(f"Location: ", style="bold")
            status_text.append(f"{waypoint_symbol}\n", style="blue")
            
            # Responsive system display
            system_symbol = ship.nav.systemSymbol
            if len(system_symbol) > 15:
                system_symbol = system_symbol[-15:]  # Show last 15 characters
            status_text.append(f"System: ", style="bold")
            status_text.append(f"{system_symbol}\n", style="dim")
        
        # Fuel and cargo info
        details_text = Text()
        if ship.fuel:
            fuel_percent = (ship.fuel.current / ship.fuel.capacity * 100) if ship.fuel.capacity > 0 else 0
            fuel_color = "green" if fuel_percent > 50 else "yellow" if fuel_percent > 25 else "red"
            details_text.append(f"Fuel: ", style="bold")
            details_text.append(f"{ship.fuel.current}/{ship.fuel.capacity} ({fuel_percent:.0f}%)\n", style=fuel_color)
        
        if ship.cargo:
            cargo_percent = (ship.cargo.units / ship.cargo.capacity * 100) if ship.cargo.capacity > 0 else 0
            cargo_color = "red" if cargo_percent > 80 else "yellow" if cargo_percent > 50 else "green"
            details_text.append(f"Cargo: ", style="bold")
            details_text.append(f"{ship.cargo.units}/{ship.cargo.capacity} ({cargo_percent:.0f}%)\n", style=cargo_color)
        
        # Ship specs - shortened for smaller screens
        specs_text = Text()
        if ship.frame:
            frame_name = ship.frame.name[:15] + "..." if len(ship.frame.name) > 18 else ship.frame.name
            specs_text.append(f"Frame: ", style="bold")
            specs_text.append(f"{frame_name}\n", style="white")
        if ship.engine:
            engine_name = ship.engine.name[:15] + "..." if len(ship.engine.name) > 18 else ship.engine.name
            specs_text.append(f"Engine: ", style="bold")
            specs_text.append(f"{engine_name}\n", style="white")
        if ship.reactor:
            reactor_name = ship.reactor.name[:15] + "..." if len(ship.reactor.name) > 18 else ship.reactor.name
            specs_text.append(f"Reactor: ", style="bold")
            specs_text.append(f"{reactor_name}\n", style="white")
        
        # Combine all info
        full_content = Text()
        full_content.append(header)
        full_content.append("\n\n")
        full_content.append(status_text)
        full_content.append("\n")
        full_content.append(details_text)
        full_content.append("\n")
        full_content.append(specs_text)
        
        # Action buttons - make them smaller
        navigate_btn = Button("Nav", variant="primary", classes="ship-button")
        navigate_btn.id = f"navigate-{ship.symbol}"
        
        dock_btn = Button("Dock", classes="ship-button")
        dock_btn.id = f"dock-{ship.symbol}"
        
        orbit_btn = Button("Orbit", classes="ship-button")
        orbit_btn.id = f"orbit-{ship.symbol}"
        
        refuel_btn = Button("Fuel", classes="ship-button")
        refuel_btn.id = f"refuel-{ship.symbol}"
        
        automate_btn = Button("Auto", variant="success", classes="ship-button")
        automate_btn.id = f"automate-{ship.symbol}"
        
        buttons = Horizontal(
            navigate_btn,
            dock_btn,
            orbit_btn,
            refuel_btn,
            automate_btn,
        )
        
        # Create the card with responsive title
        card_title = f"Ship: {ship_symbol}"
        card = Container(
            Static(Panel(full_content, title=card_title, border_style="green"), classes="ship-card"),
            buttons,
            classes="ship-container"
        )
        
        return card

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle ship button presses."""
        button_id = event.button.id
        if not button_id:
            return
            
        # Parse the button ID to get action and ship symbol
        parts = button_id.split("-", 1)
        if len(parts) != 2:
            return
            
        action, ship_symbol = parts
        
        if action == "navigate":
            await self.post_message(self.ShipNavigate(ship_symbol))
        elif action == "dock":
            await self.post_message(self.ShipDock(ship_symbol))
        elif action == "orbit":
            await self.post_message(self.ShipOrbit(ship_symbol))
        elif action == "refuel":
            await self.post_message(self.ShipRefuel(ship_symbol))
        elif action == "automate":
            await self.post_message(self.ShipAutomate(ship_symbol))