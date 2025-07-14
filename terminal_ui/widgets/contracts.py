"""
Contracts widget for contract management.
"""

from typing import Optional, List
from datetime import datetime, timezone

from textual.widgets import Static, Button, Label
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from spacetraders_client.models import Contract


class ContractWidget(Static):
    """Contracts widget for contract management."""
    
    contracts_data = reactive(None)
    
    # Custom messages for contract actions
    class ContractAccept(Message):
        """Message sent when accept contract is clicked."""
        def __init__(self, contract_id: str):
            self.contract_id = contract_id
            super().__init__()
    
    class ContractFulfill(Message):
        """Message sent when fulfill contract is clicked."""
        def __init__(self, contract_id: str):
            self.contract_id = contract_id
            super().__init__()
    
    class ContractAutomate(Message):
        """Message sent when automate contract is clicked."""
        def __init__(self, contract_id: str):
            self.contract_id = contract_id
            super().__init__()
    
    class ContractDetails(Message):
        """Message sent when view contract details is clicked."""
        def __init__(self, contract_id: str):
            self.contract_id = contract_id
            super().__init__()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console = Console()
        
    def compose(self):
        """Compose the contracts layout."""
        yield ScrollableContainer(
            Container(
                Label("Loading contracts...", classes="contract-header"),
                classes="contracts-content"
            ),
            classes="contracts-scrollable"
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
                classes="contracts-content"
            )
            scrollable = ScrollableContainer(
                container,
                classes="contracts-scrollable"
            )
            await self.mount(scrollable)
            return
        
        # Create contract cards
        contract_cards = []
        for contract in self.contracts_data:
            card = self.create_contract_card(contract)
            contract_cards.append(card)
        
        # Create scrollable container
        container = Container(
            *contract_cards,
            classes="contracts-content"
        )
        
        scrollable = ScrollableContainer(
            container,
            classes="contracts-scrollable"
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
            accept_btn = Button("Accept", variant="primary", classes="contract-button")
            accept_btn.id = f"accept-{contract.id}"
            buttons.append(accept_btn)
        elif contract.accepted and not contract.fulfilled:
            fulfill_btn = Button("Fulfill", variant="success", classes="contract-button")
            fulfill_btn.id = f"fulfill-{contract.id}"
            buttons.append(fulfill_btn)
            
            automate_btn = Button("Automate", variant="primary", classes="contract-button")
            automate_btn.id = f"automate-{contract.id}"
            buttons.append(automate_btn)
        
        details_btn = Button("Details", classes="contract-button")
        details_btn.id = f"details-{contract.id}"
        buttons.append(details_btn)
        
        button_row = Horizontal(*buttons) if buttons else Container()
        
        # Create the card
        card = Container(
            Static(Panel(full_content, title=f"Contract: {contract.type}", border_style=border_style), classes=card_class),
            button_row,
            classes="contract-container"
        )
        
        return card

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle contract button presses."""
        button_id = event.button.id
        if not button_id:
            return
            
        # Parse the button ID to get action and contract ID
        parts = button_id.split("-", 1)
        if len(parts) != 2:
            return
            
        action, contract_id = parts
        
        if action == "accept":
            await self.post_message(self.ContractAccept(contract_id))
        elif action == "fulfill":
            await self.post_message(self.ContractFulfill(contract_id))
        elif action == "automate":
            await self.post_message(self.ContractAutomate(contract_id))
        elif action == "details":
            await self.post_message(self.ContractDetails(contract_id))