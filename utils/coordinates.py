"""
Coordinate system utilities for SpaceTraders.
"""

import math
from typing import List, Tuple, Optional, Dict

from spacetraders_client.models import Waypoint, System, SystemWaypoint


def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
        
    Returns:
        Distance between the points
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def find_closest_waypoint(
    origin_x: int, 
    origin_y: int, 
    waypoints: List[Waypoint]
) -> Optional[Waypoint]:
    """
    Find the closest waypoint to a given position.
    
    Args:
        origin_x, origin_y: Origin position
        waypoints: List of waypoints to search
        
    Returns:
        The closest waypoint, or None if list is empty
    """
    if not waypoints:
        return None
    
    closest_waypoint = None
    min_distance = float('inf')
    
    for waypoint in waypoints:
        distance = calculate_distance(origin_x, origin_y, waypoint.x, waypoint.y)
        if distance < min_distance:
            min_distance = distance
            closest_waypoint = waypoint
    
    return closest_waypoint


def find_closest_system_waypoint(
    origin_x: int, 
    origin_y: int, 
    waypoints: List[SystemWaypoint]
) -> Optional[SystemWaypoint]:
    """
    Find the closest system waypoint to a given position.
    
    Args:
        origin_x, origin_y: Origin position
        waypoints: List of system waypoints to search
        
    Returns:
        The closest system waypoint, or None if list is empty
    """
    if not waypoints:
        return None
    
    closest_waypoint = None
    min_distance = float('inf')
    
    for waypoint in waypoints:
        distance = calculate_distance(origin_x, origin_y, waypoint.x, waypoint.y)
        if distance < min_distance:
            min_distance = distance
            closest_waypoint = waypoint
    
    return closest_waypoint


def sort_waypoints_by_distance(
    origin_x: int, 
    origin_y: int, 
    waypoints: List[Waypoint]
) -> List[Tuple[Waypoint, float]]:
    """
    Sort waypoints by distance from origin.
    
    Args:
        origin_x, origin_y: Origin position
        waypoints: List of waypoints to sort
        
    Returns:
        List of (waypoint, distance) tuples sorted by distance
    """
    waypoint_distances = []
    
    for waypoint in waypoints:
        distance = calculate_distance(origin_x, origin_y, waypoint.x, waypoint.y)
        waypoint_distances.append((waypoint, distance))
    
    return sorted(waypoint_distances, key=lambda x: x[1])


def find_waypoints_within_radius(
    origin_x: int, 
    origin_y: int, 
    waypoints: List[Waypoint], 
    radius: float
) -> List[Waypoint]:
    """
    Find all waypoints within a specified radius.
    
    Args:
        origin_x, origin_y: Origin position
        waypoints: List of waypoints to search
        radius: Search radius
        
    Returns:
        List of waypoints within the radius
    """
    nearby_waypoints = []
    
    for waypoint in waypoints:
        distance = calculate_distance(origin_x, origin_y, waypoint.x, waypoint.y)
        if distance <= radius:
            nearby_waypoints.append(waypoint)
    
    return nearby_waypoints


def get_system_bounds(system: System) -> Dict[str, int]:
    """
    Get the bounding box of a system.
    
    Args:
        system: The system to analyze
        
    Returns:
        Dictionary with min_x, max_x, min_y, max_y
    """
    if not system.waypoints:
        return {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0}
    
    min_x = min(wp.x for wp in system.waypoints)
    max_x = max(wp.x for wp in system.waypoints)
    min_y = min(wp.y for wp in system.waypoints)
    max_y = max(wp.y for wp in system.waypoints)
    
    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y
    }


def calculate_travel_time_estimate(
    distance: float, 
    ship_speed: int = 30,
    flight_mode: str = "CRUISE"
) -> int:
    """
    Estimate travel time between two points.
    
    Args:
        distance: Distance to travel
        ship_speed: Ship speed rating
        flight_mode: Flight mode (affects speed)
        
    Returns:
        Estimated travel time in seconds
    """
    # Speed modifiers for different flight modes
    speed_modifiers = {
        "DRIFT": 0.5,
        "STEALTH": 0.7,
        "CRUISE": 1.0,
        "BURN": 1.5
    }
    
    modifier = speed_modifiers.get(flight_mode, 1.0)
    effective_speed = ship_speed * modifier
    
    # Base travel time calculation (simplified)
    base_time = distance / effective_speed * 60  # Convert to seconds
    
    return max(int(base_time), 1)  # Minimum 1 second


def find_optimal_waypoint_path(
    start_waypoint: Waypoint, 
    target_waypoints: List[Waypoint]
) -> List[Waypoint]:
    """
    Find an optimal path through multiple waypoints (simplified traveling salesman).
    
    Args:
        start_waypoint: Starting waypoint
        target_waypoints: List of waypoints to visit
        
    Returns:
        Ordered list of waypoints representing the optimal path
    """
    if not target_waypoints:
        return []
    
    # Simple greedy approach - visit nearest unvisited waypoint
    path = []
    current_x, current_y = start_waypoint.x, start_waypoint.y
    remaining_waypoints = target_waypoints.copy()
    
    while remaining_waypoints:
        # Find nearest waypoint
        nearest_waypoint = find_closest_waypoint(current_x, current_y, remaining_waypoints)
        
        if nearest_waypoint:
            path.append(nearest_waypoint)
            remaining_waypoints.remove(nearest_waypoint)
            current_x, current_y = nearest_waypoint.x, nearest_waypoint.y
        else:
            break
    
    return path


def get_waypoint_quadrant(waypoint: Waypoint, system_bounds: Dict[str, int]) -> str:
    """
    Determine which quadrant a waypoint is in relative to system center.
    
    Args:
        waypoint: The waypoint to analyze
        system_bounds: System bounds from get_system_bounds()
        
    Returns:
        Quadrant name: "NE", "NW", "SE", "SW"
    """
    center_x = (system_bounds["min_x"] + system_bounds["max_x"]) / 2
    center_y = (system_bounds["min_y"] + system_bounds["max_y"]) / 2
    
    if waypoint.x >= center_x and waypoint.y >= center_y:
        return "NE"
    elif waypoint.x < center_x and waypoint.y >= center_y:
        return "NW"
    elif waypoint.x >= center_x and waypoint.y < center_y:
        return "SE"
    else:
        return "SW"