"""
Automation system for SpaceTraders ships and contracts.
"""

from .manager import AutomationManager
from .ship_automation import ShipAutomation
from .contract_automation import ContractAutomation
from .navigation import NavigationHelper
from .resource_management import ResourceManager

__all__ = [
    "AutomationManager",
    "ShipAutomation", 
    "ContractAutomation",
    "NavigationHelper",
    "ResourceManager"
]