"""
Contracts widget for contract management.
"""

from typing import Optional, List
from datetime import datetime, timezone

from textual.widgets import Static, Button, Label
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from spacetraders_client.models import Contract


class ContractWidget(Static):
    """Contracts widget for contract management."""
    
    contracts_data = reactive(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console = Console()
        
    def compose(self):
        """Compose the contracts layout."""
        yield Container(
            Label("Loading contracts...", classes="contract-header"),
            classes="scrollable"
        )
    
    async def update_data(self, contracts_data: Optional[List[Contract]]):
        """Update the contracts widget with new data."""
        self.contracts_data = contracts_data
        await self.update_display()
    
    async def update_display(self):
        """Update the contracts display."""
        # Clear existing content
        await self.remove_children()
        
        if not self.contracts_data:
            container = Container(
                Label("No contracts available", classes="contract-header"),
                classes="scrollable"
            )
            await self.mount(container)
            return
        
        # Create contract cards
        contract_cards = []
        for contract in self.contracts_data:
            card = self.create_contract_card(contract)
            contract_cards.append(card)
        
        # Create scrollable container
        scrollable = ScrollableContainer(
            *contract_cards,
            classes="scrollable"
        )
        
        await self.mount(scrollable)
    
    def create_contract_card(self, contract: Contract) -> Container:
        """Create a card for a single contract."""
        # Contract header
        header = Text()
        header.append(f"{contract.id}", style="bold orange")
        header.append(f" ({contract.type})", style="dim")
        
        # Contract status
        status_text = Text()
        status_text.append(f"Status: ", style="bold")
        
        if contract.fulfilled:
            status_text.append("FULFILLED", style="green")
        elif contract.accepted:
            status_text.append("ACCEPTED", style="yellow")
        else:
            status_text.append("AVAILABLE", style="blue")
        
        status_text.append("\n")
        status_text.append(f"Faction: ", style="bold")
        status_text.append(f"{contract.factionSymbol}\n", style="magenta")
        
        # Payment info
        payment_text = Text()
        if contract.terms.payment:
            payment_text.append(f"Payment:\n", style="bold")
            payment_text.append(f"  On Accept: ", style="bold")
            payment_text.append(f"{contract.terms.payment.onAccepted:,} credits\n", style="green")
            payment_text.append(f"  On Fulfill: ", style="bold")
            payment_text.append(f"{contract.terms.payment.onFulfilled:,} credits\n", style="green")
        
        # Delivery requirements
        delivery_text = Text()
        if contract.terms.deliver:
            delivery_text.append(f"Deliveries:\n", style="bold")
            for delivery in contract.terms.deliver:
                progress = delivery.unitsFulfilled / delivery.unitsRequired if delivery.unitsRequired > 0 else 0
                progress_color = "green" if progress >= 1.0 else "yellow" if progress > 0 else "red"
                delivery_text.append(f"  {delivery.tradeSymbol}: ", style="white")
                delivery_text.append(f"{delivery.unitsFulfilled}/{delivery.unitsRequired}", style=progress_color)
                delivery_text.append(f" → {delivery.destinationSymbol}\n", style="blue")
        
        # Deadline info
        deadline_text = Text()
        deadline_text.append(f"Deadline: ", style="bold")
        deadline_str = contract.terms.deadline.strftime("%Y-%m-%d %H:%M:%S")
        
        # Color code based on time remaining
        time_remaining = contract.terms.deadline - datetime.now(timezone.utc)
        if time_remaining.days < 1:
            deadline_color = "red"
        elif time_remaining.days < 3:
            deadline_color = "yellow"
        else:
            deadline_color = "green"
        
        deadline_text.append(f"{deadline_str}\n", style=deadline_color)
        deadline_text.append(f"Time remaining: ", style="bold")
        deadline_text.append(f"{time_remaining.days} days, {time_remaining.seconds // 3600} hours", style=deadline_color)
        
        # Combine all info
        full_content = Text()
        full_content.append(header)
        full_content.append("\n\n")
        full_content.append(status_text)
        full_content.append("\n")
        full_content.append(payment_text)
        full_content.append("\n")
        full_content.append(delivery_text)
        full_content.append("\n")
        full_content.append(deadline_text)
        
        # Determine card style based on status
        if contract.fulfilled:
            border_style = "green"
            card_class = "contract-fulfilled"
        elif contract.accepted:
            border_style = "yellow"
            card_class = "contract-accepted"
        else:
            border_style = "blue"
            card_class = "contract-card"
        
        # Action buttons
        buttons = []
        if not contract.accepted and not contract.fulfilled:
            buttons.append(Button("Accept", variant="primary", classes="contract-button"))
        elif contract.accepted and not contract.fulfilled:
            buttons.append(Button("Fulfill", variant="success", classes="contract-button"))
            buttons.append(Button("Automate", variant="primary", classes="contract-button"))
        
        buttons.append(Button("Details", classes="contract-button"))
        
        button_row = Horizontal(*buttons) if buttons else Container()
        
        # Create the card
        card = Container(
            Static(Panel(full_content, title=f"Contract: {contract.type}", border_style=border_style), classes=card_class),
            button_row,
            classes="contract-container"
        )
        
        return card