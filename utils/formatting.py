"""
Formatting utilities for display in the terminal UI.
"""

from datetime import datetime, timedelta
from typing import Optional

from spacetraders_client.models import Ship, ShipCargo, ShipFuel


def format_credits(credits: int) -> str:
    """
    Format credits with appropriate units (K, M, B).
    
    Args:
        credits: Credit amount
        
    Returns:
        Formatted credit string
    """
    if credits < 0:
        return f"-{format_credits(-credits)}"
    
    if credits >= 1_000_000_000:
        return f"{credits / 1_000_000_000:.1f}B"
    elif credits >= 1_000_000:
        return f"{credits / 1_000_000:.1f}M"
    elif credits >= 1_000:
        return f"{credits / 1_000:.1f}K"
    else:
        return str(credits)


def format_time_remaining(target_time: datetime) -> str:
    """
    Format time remaining until target time.
    
    Args:
        target_time: Target datetime
        
    Returns:
        Formatted time remaining string
    """
    now = datetime.now(target_time.tzinfo) if target_time.tzinfo else datetime.now()
    time_diff = target_time - now
    
    if time_diff.total_seconds() <= 0:
        return "EXPIRED"
    
    days = time_diff.days
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60
    seconds = time_diff.seconds % 60
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def format_cargo_status(cargo: Optional[ShipCargo]) -> str:
    """
    Format cargo status for display.
    
    Args:
        cargo: Ship cargo object
        
    Returns:
        Formatted cargo status string
    """
    if not cargo:
        return "No cargo hold"
    
    percentage = (cargo.units / cargo.capacity * 100) if cargo.capacity > 0 else 0
    
    if percentage >= 100:
        return f"🟥 FULL ({cargo.units}/{cargo.capacity})"
    elif percentage >= 80:
        return f"🟨 {percentage:.0f}% ({cargo.units}/{cargo.capacity})"
    elif percentage >= 50:
        return f"🟩 {percentage:.0f}% ({cargo.units}/{cargo.capacity})"
    else:
        return f"⬜ {percentage:.0f}% ({cargo.units}/{cargo.capacity})"


def format_fuel_status(fuel: Optional[ShipFuel]) -> str:
    """
    Format fuel status for display.
    
    Args:
        fuel: Ship fuel object
        
    Returns:
        Formatted fuel status string
    """
    if not fuel:
        return "No fuel system"
    
    percentage = (fuel.current / fuel.capacity * 100) if fuel.capacity > 0 else 0
    
    if percentage >= 100:
        return f"⛽ FULL ({fuel.current}/{fuel.capacity})"
    elif percentage >= 50:
        return f"⛽ {percentage:.0f}% ({fuel.current}/{fuel.capacity})"
    elif percentage >= 25:
        return f"⚠️ {percentage:.0f}% ({fuel.current}/{fuel.capacity})"
    else:
        return f"🔴 LOW ({fuel.current}/{fuel.capacity})"


def format_ship_status(ship: Ship) -> str:
    """
    Format comprehensive ship status.
    
    Args:
        ship: Ship object
        
    Returns:
        Formatted ship status string
    """
    if not ship.nav:
        return "Status unknown"
    
    status_icons = {
        "DOCKED": "⚓",
        "IN_ORBIT": "🚀",
        "IN_TRANSIT": "🛸"
    }
    
    icon = status_icons.get(ship.nav.status, "❓")
    status = f"{icon} {ship.nav.status}"
    
    if ship.nav.status == "IN_TRANSIT" and ship.nav.route:
        arrival_time = ship.nav.route.arrival
        time_remaining = format_time_remaining(arrival_time)
        status += f" (arrives in {time_remaining})"
    
    return status


def format_contract_progress(delivered: int, required: int) -> str:
    """
    Format contract delivery progress.
    
    Args:
        delivered: Units delivered
        required: Units required
        
    Returns:
        Formatted progress string
    """
    if required == 0:
        return "✅ Complete"
    
    percentage = (delivered / required * 100)
    
    if percentage >= 100:
        return f"✅ Complete ({delivered}/{required})"
    elif percentage >= 75:
        return f"🟩 {percentage:.0f}% ({delivered}/{required})"
    elif percentage >= 50:
        return f"🟨 {percentage:.0f}% ({delivered}/{required})"
    elif percentage >= 25:
        return f"🟧 {percentage:.0f}% ({delivered}/{required})"
    else:
        return f"🟥 {percentage:.0f}% ({delivered}/{required})"


def format_distance(distance: float) -> str:
    """
    Format distance for display.
    
    Args:
        distance: Distance value
        
    Returns:
        Formatted distance string
    """
    if distance >= 1000:
        return f"{distance / 1000:.1f}K units"
    elif distance >= 100:
        return f"{distance:.0f} units"
    else:
        return f"{distance:.1f} units"


def format_waypoint_type(waypoint_type: str) -> str:
    """
    Format waypoint type for display.
    
    Args:
        waypoint_type: Waypoint type string
        
    Returns:
        Formatted waypoint type with icon
    """
    type_icons = {
        "PLANET": "🌍",
        "GAS_GIANT": "🪐",
        "MOON": "🌙",
        "ORBITAL_STATION": "🛰️",
        "JUMP_GATE": "🌌",
        "ASTEROID_FIELD": "☄️",
        "ASTEROID": "🪨",
        "ENGINEERED_ASTEROID": "⚙️",
        "ASTEROID_BASE": "🏭",
        "NEBULA": "🌌",
        "DEBRIS_FIELD": "💥",
        "GRAVITY_WELL": "🌀",
        "ARTIFICIAL_GRAVITY_WELL": "⚡",
        "FUEL_STATION": "⛽"
    }
    
    icon = type_icons.get(waypoint_type, "❓")
    return f"{icon} {waypoint_type.replace('_', ' ').title()}"


def format_trait(trait: str) -> str:
    """
    Format waypoint trait for display.
    
    Args:
        trait: Trait string
        
    Returns:
        Formatted trait with icon
    """
    trait_icons = {
        "MARKETPLACE": "🏪",
        "SHIPYARD": "🏗️",
        "OUTPOST": "🏭",
        "SCATTERED_SETTLEMENTS": "🏘️",
        "SPRAWLING_CITIES": "🌆",
        "MEGA_STRUCTURES": "🏢",
        "PIRATE_BASE": "🏴‍☠️",
        "OVERCROWDED": "👥",
        "HIGH_TECH": "🔬",
        "INDUSTRIAL": "🏭",
        "MINERAL_DEPOSITS": "💎",
        "COMMON_METAL_DEPOSITS": "⚙️",
        "PRECIOUS_METAL_DEPOSITS": "💰",
        "RARE_METAL_DEPOSITS": "✨",
        "METHANE_POOLS": "🧪",
        "ICE_CRYSTALS": "❄️",
        "EXPLOSIVE_GASES": "💥",
        "FUEL_STATION": "⛽"
    }
    
    icon = trait_icons.get(trait, "")
    formatted_trait = trait.replace('_', ' ').title()
    return f"{icon} {formatted_trait}" if icon else formatted_trait


def format_ship_role(role: str) -> str:
    """
    Format ship role for display.
    
    Args:
        role: Ship role string
        
    Returns:
        Formatted role with icon
    """
    role_icons = {
        "FABRICATOR": "🔧",
        "HARVESTER": "🚜",
        "HAULER": "🚛",
        "INTERCEPTOR": "⚡",
        "EXCAVATOR": "⛏️",
        "TRANSPORT": "🚚",
        "REPAIR": "🔧",
        "SURVEYOR": "🔍",
        "COMMAND": "👑",
        "CARRIER": "🛳️",
        "PATROL": "🚓",
        "SATELLITE": "📡",
        "EXPLORER": "🧭",
        "REFINERY": "🏭"
    }
    
    icon = role_icons.get(role, "🚀")
    formatted_role = role.replace('_', ' ').title()
    return f"{icon} {formatted_role}"


def format_percentage(value: float, total: float) -> str:
    """
    Format a percentage with appropriate color coding.
    
    Args:
        value: Current value
        total: Total/maximum value
        
    Returns:
        Formatted percentage string
    """
    if total == 0:
        return "0%"
    
    percentage = (value / total * 100)
    
    if percentage >= 90:
        return f"🟩 {percentage:.0f}%"
    elif percentage >= 70:
        return f"🟨 {percentage:.0f}%"
    elif percentage >= 50:
        return f"🟧 {percentage:.0f}%"
    elif percentage >= 25:
        return f"🟥 {percentage:.0f}%"
    else:
        return f"⬛ {percentage:.0f}%"


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to fit within maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"