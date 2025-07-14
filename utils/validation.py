"""
Validation utilities for ships and contracts.
"""

from typing import List, Optional, Dict, Any

from spacetraders_client.models import Ship, Contract, ShipMount, ShipModule


def validate_ship_for_task(ship: Ship, task_type: str) -> Dict[str, Any]:
    """
    Validate if a ship is suitable for a specific task.
    
    Args:
        ship: Ship to validate
        task_type: Type of task ("mining", "trading", "transport", "exploration")
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "suitable": False,
        "reason": "",
        "requirements_met": [],
        "requirements_missing": [],
        "recommendations": []
    }
    
    if task_type == "mining":
        return _validate_mining_ship(ship, validation_result)
    elif task_type == "trading":
        return _validate_trading_ship(ship, validation_result)
    elif task_type == "transport":
        return _validate_transport_ship(ship, validation_result)
    elif task_type == "exploration":
        return _validate_exploration_ship(ship, validation_result)
    else:
        validation_result["reason"] = f"Unknown task type: {task_type}"
        return validation_result


def _validate_mining_ship(ship: Ship, result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate ship for mining tasks."""
    has_mining_equipment = False
    has_cargo_space = False
    has_surveyor = False
    
    # Check for mining equipment
    if ship.mounts:
        for mount in ship.mounts:
            if "MINING" in mount.symbol or "LASER" in mount.symbol:
                has_mining_equipment = True
                result["requirements_met"].append("Mining equipment")
                break
    
    if not has_mining_equipment:
        result["requirements_missing"].append("Mining equipment (Mining Laser)")
        result["recommendations"].append("Install mining laser mounts")
    
    # Check for cargo space
    if ship.cargo and ship.cargo.capacity > 0:
        has_cargo_space = True
        result["requirements_met"].append(f"Cargo space ({ship.cargo.capacity} units)")
    else:
        result["requirements_missing"].append("Cargo space")
        result["recommendations"].append("Install cargo hold modules")
    
    # Check for surveyor equipment (optional but recommended)
    if ship.mounts:
        for mount in ship.mounts:
            if "SURVEYOR" in mount.symbol:
                has_surveyor = True
                result["requirements_met"].append("Surveyor equipment")
                break
    
    if not has_surveyor:
        result["recommendations"].append("Install surveyor for better mining efficiency")
    
    # Overall suitability
    result["suitable"] = has_mining_equipment and has_cargo_space
    
    if not result["suitable"]:
        result["reason"] = "Missing essential mining equipment or cargo space"
    else:
        result["reason"] = "Ship is suitable for mining"
    
    return result


def _validate_trading_ship(ship: Ship, result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate ship for trading tasks."""
    has_cargo_space = False
    has_good_fuel_capacity = False
    
    # Check for cargo space
    if ship.cargo and ship.cargo.capacity >= 10:  # Minimum cargo for trading
        has_cargo_space = True
        result["requirements_met"].append(f"Cargo space ({ship.cargo.capacity} units)")
        
        if ship.cargo.capacity >= 50:
            result["requirements_met"].append("Large cargo capacity")
        elif ship.cargo.capacity >= 25:
            result["requirements_met"].append("Medium cargo capacity")
    else:
        result["requirements_missing"].append("Sufficient cargo space (minimum 10 units)")
        result["recommendations"].append("Install larger cargo hold modules")
    
    # Check fuel capacity for long routes
    if ship.fuel and ship.fuel.capacity >= 100:
        has_good_fuel_capacity = True
        result["requirements_met"].append(f"Good fuel capacity ({ship.fuel.capacity} units)")
    else:
        result["recommendations"].append("Consider fuel efficiency for long trading routes")
    
    # Check for useful modules
    if ship.modules:
        for module in ship.modules:
            if "CARGO_HOLD" in module.symbol:
                result["requirements_met"].append("Cargo hold modules")
            elif "FUEL_REFINERY" in module.symbol:
                result["requirements_met"].append("Fuel refinery")
                result["recommendations"].append("Fuel refinery can help with long routes")
    
    # Overall suitability
    result["suitable"] = has_cargo_space
    
    if not result["suitable"]:
        result["reason"] = "Insufficient cargo space for trading"
    else:
        result["reason"] = "Ship is suitable for trading"
    
    return result


def _validate_transport_ship(ship: Ship, result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate ship for transport tasks."""
    has_large_cargo = False
    has_good_speed = False
    
    # Check for large cargo capacity
    if ship.cargo and ship.cargo.capacity >= 50:
        has_large_cargo = True
        result["requirements_met"].append(f"Large cargo capacity ({ship.cargo.capacity} units)")
    elif ship.cargo and ship.cargo.capacity >= 25:
        result["requirements_met"].append(f"Medium cargo capacity ({ship.cargo.capacity} units)")
        result["recommendations"].append("Consider larger cargo hold for better efficiency")
    else:
        result["requirements_missing"].append("Large cargo capacity (minimum 50 units)")
        result["recommendations"].append("Install large cargo hold modules")
    
    # Check engine for speed
    if ship.engine and ship.engine.speed >= 30:
        has_good_speed = True
        result["requirements_met"].append(f"Good speed ({ship.engine.speed})")
    else:
        result["recommendations"].append("Consider engine upgrades for faster transport")
    
    # Overall suitability
    result["suitable"] = has_large_cargo
    
    if not result["suitable"]:
        result["reason"] = "Insufficient cargo capacity for transport"
    else:
        result["reason"] = "Ship is suitable for transport"
    
    return result


def _validate_exploration_ship(ship: Ship, result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate ship for exploration tasks."""
    has_sensor_array = False
    has_good_fuel = False
    has_surveyor = False
    
    # Check for sensor array
    if ship.mounts:
        for mount in ship.mounts:
            if "SENSOR_ARRAY" in mount.symbol:
                has_sensor_array = True
                result["requirements_met"].append("Sensor array")
                break
    
    if not has_sensor_array:
        result["requirements_missing"].append("Sensor array")
        result["recommendations"].append("Install sensor array for better exploration")
    
    # Check for surveyor equipment
    if ship.mounts:
        for mount in ship.mounts:
            if "SURVEYOR" in mount.symbol:
                has_surveyor = True
                result["requirements_met"].append("Surveyor equipment")
                break
    
    if not has_surveyor:
        result["recommendations"].append("Install surveyor for resource scanning")
    
    # Check fuel capacity for long exploration
    if ship.fuel and ship.fuel.capacity >= 200:
        has_good_fuel = True
        result["requirements_met"].append(f"Good fuel capacity ({ship.fuel.capacity} units)")
    else:
        result["recommendations"].append("Consider larger fuel capacity for long exploration")
    
    # Overall suitability (exploration ships are generally more flexible)
    result["suitable"] = True
    
    if has_sensor_array and has_surveyor and has_good_fuel:
        result["reason"] = "Ship is excellent for exploration"
    elif has_sensor_array or has_surveyor:
        result["reason"] = "Ship is suitable for exploration"
    else:
        result["reason"] = "Ship can explore but lacks specialized equipment"
    
    return result


def validate_contract_requirements(contract: Contract, available_ships: List[Ship]) -> Dict[str, Any]:
    """
    Validate if available ships can fulfill contract requirements.
    
    Args:
        contract: Contract to validate
        available_ships: List of available ships
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "can_fulfill": False,
        "reason": "",
        "suitable_ships": [],
        "required_capabilities": [],
        "missing_capabilities": [],
        "recommendations": []
    }
    
    # Check contract type
    if contract.type == "PROCUREMENT":
        return _validate_procurement_contract(contract, available_ships, validation_result)
    elif contract.type == "TRANSPORT":
        return _validate_transport_contract(contract, available_ships, validation_result)
    elif contract.type == "SHUTTLE":
        return _validate_shuttle_contract(contract, available_ships, validation_result)
    else:
        validation_result["reason"] = f"Unknown contract type: {contract.type}"
        return validation_result


def _validate_procurement_contract(contract: Contract, ships: List[Ship], result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate procurement contract requirements."""
    result["required_capabilities"].append("Mining capability")
    result["required_capabilities"].append("Cargo space")
    
    suitable_ships = []
    
    for ship in ships:
        ship_validation = validate_ship_for_task(ship, "mining")
        if ship_validation["suitable"]:
            suitable_ships.append({
                "ship": ship,
                "capabilities": ship_validation["requirements_met"]
            })
    
    result["suitable_ships"] = suitable_ships
    result["can_fulfill"] = len(suitable_ships) > 0
    
    if not result["can_fulfill"]:
        result["reason"] = "No ships capable of mining for procurement contract"
        result["missing_capabilities"].append("Mining-capable ships")
        result["recommendations"].append("Acquire ships with mining equipment")
    else:
        result["reason"] = f"Found {len(suitable_ships)} suitable ships for procurement"
    
    return result


def _validate_transport_contract(contract: Contract, ships: List[Ship], result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate transport contract requirements."""
    result["required_capabilities"].append("Large cargo capacity")
    result["required_capabilities"].append("Good fuel capacity")
    
    suitable_ships = []
    
    for ship in ships:
        ship_validation = validate_ship_for_task(ship, "transport")
        if ship_validation["suitable"]:
            suitable_ships.append({
                "ship": ship,
                "capabilities": ship_validation["requirements_met"]
            })
    
    result["suitable_ships"] = suitable_ships
    result["can_fulfill"] = len(suitable_ships) > 0
    
    if not result["can_fulfill"]:
        result["reason"] = "No ships suitable for transport contract"
        result["missing_capabilities"].append("Transport-capable ships")
        result["recommendations"].append("Acquire ships with large cargo capacity")
    else:
        result["reason"] = f"Found {len(suitable_ships)} suitable ships for transport"
    
    return result


def _validate_shuttle_contract(contract: Contract, ships: List[Ship], result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate shuttle contract requirements."""
    result["required_capabilities"].append("Passenger capacity")
    result["required_capabilities"].append("Moderate cargo space")
    
    suitable_ships = []
    
    # Check for passenger modules
    for ship in ships:
        has_passenger_capacity = False
        
        if ship.modules:
            for module in ship.modules:
                if "PASSENGER" in module.symbol or "ENVOY" in module.symbol:
                    has_passenger_capacity = True
                    break
        
        if has_passenger_capacity:
            suitable_ships.append({
                "ship": ship,
                "capabilities": ["Passenger capacity"]
            })
    
    result["suitable_ships"] = suitable_ships
    result["can_fulfill"] = len(suitable_ships) > 0
    
    if not result["can_fulfill"]:
        result["reason"] = "No ships with passenger capacity for shuttle contract"
        result["missing_capabilities"].append("Passenger-capable ships")
        result["recommendations"].append("Install passenger modules on ships")
    else:
        result["reason"] = f"Found {len(suitable_ships)} suitable ships for shuttle"
    
    return result


def validate_ship_fuel_for_journey(ship: Ship, estimated_fuel_needed: int) -> Dict[str, Any]:
    """
    Validate if ship has enough fuel for a journey.
    
    Args:
        ship: Ship to validate
        estimated_fuel_needed: Estimated fuel requirement
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "sufficient_fuel": False,
        "current_fuel": 0,
        "fuel_capacity": 0,
        "fuel_needed": estimated_fuel_needed,
        "fuel_after_journey": 0,
        "recommendation": ""
    }
    
    if not ship.fuel:
        validation_result["recommendation"] = "Ship does not use fuel"
        validation_result["sufficient_fuel"] = True
        return validation_result
    
    validation_result["current_fuel"] = ship.fuel.current
    validation_result["fuel_capacity"] = ship.fuel.capacity
    validation_result["fuel_after_journey"] = ship.fuel.current - estimated_fuel_needed
    
    if ship.fuel.current >= estimated_fuel_needed:
        validation_result["sufficient_fuel"] = True
        
        remaining_percent = (validation_result["fuel_after_journey"] / ship.fuel.capacity) * 100
        
        if remaining_percent < 25:
            validation_result["recommendation"] = "Consider refueling after journey"
        elif remaining_percent < 50:
            validation_result["recommendation"] = "Fuel level will be moderate after journey"
        else:
            validation_result["recommendation"] = "Sufficient fuel for journey"
    else:
        validation_result["sufficient_fuel"] = False
        fuel_deficit = estimated_fuel_needed - ship.fuel.current
        validation_result["recommendation"] = f"Need {fuel_deficit} more fuel units"
    
    return validation_result