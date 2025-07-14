"""
SpaceTraders Python Client

A typed, object-oriented Python client for the SpaceTraders API.
"""

__version__ = "1.0.0"

from .client import SpaceTradersClient, SpaceTradersError
from .models import *

__all__ = [
    "SpaceTradersClient",
    "SpaceTradersError",
]