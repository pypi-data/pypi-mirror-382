#!/usr/bin/env python3
"""
ManimPro Global Positioning Utilities
=====================================

This module provides global positioning functions that can be used anywhere
in ManimPro without needing scene context. These functions work seamlessly
with ValueTracker, always_redraw, and other ManimPro utilities.

Key Features:
- Global set_position() function callable anywhere
- Full compatibility with existing ManimPro pipeline
- Works with updaters, animations, and custom functions
- Maintains backward compatibility

Usage:
    from manimpro.utils.positioning import set_position
    
    # Use anywhere without self
    dot = Dot()
    set_position(dot, UP * 2)
    
    # Works in updaters
    def update_func():
        set_position(moving_dot, tracker.get_value() * RIGHT)
    
    # Works with always_redraw
    line = always_redraw(lambda: Line(ORIGIN, get_position(dot)))
"""

from __future__ import annotations

import numpy as np
from typing import Union, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from ..mobject.mobject import Mobject

# Type hints for positioning
Point3D = Union[Sequence[float], np.ndarray]
Point2D = Union[Sequence[float], np.ndarray]


def set_position(mobject: "Mobject", position: Union[Point3D, str, "Mobject"], 
                 alignment: Point3D = None, buff: float = 0, **kwargs) -> "Mobject":
    """
    Set the position of any Mobject using various positioning methods.
    
    This is a global function that can be called anywhere without needing
    scene context. It provides a unified interface for positioning Mobjects
    and works seamlessly with ValueTracker, always_redraw, and other utilities.
    
    Args:
        mobject: The Mobject to position
        position: Target position. Can be:
            - A 3D point/vector (e.g., [1, 2, 0], ORIGIN, UP, etc.)
            - A string constant (e.g., "CENTER", "UP", "DOWN", "LEFT", "RIGHT")
            - Another Mobject to position relative to
        alignment: How to align the Mobject relative to the target position.
            Default is ORIGIN (center alignment). Use UP, DOWN, LEFT, RIGHT, etc.
        buff: Buffer distance when positioning relative to edges or other objects
        **kwargs: Additional arguments passed to underlying positioning methods
        
    Returns:
        The positioned Mobject (for method chaining)
        
    Examples:
        # Basic usage
        dot = Dot()
        set_position(dot, UP * 2)
        
        # String constants
        set_position(dot, "UP")
        set_position(dot, "UL")  # Upper left corner
        
        # Relative positioning
        circle = Circle()
        set_position(dot, circle, alignment=UP, buff=0.5)
        
        # In updaters
        def update_func():
            set_position(moving_dot, tracker.get_value() * RIGHT)
            
        # With always_redraw
        line = always_redraw(lambda: Line(ORIGIN, get_position(dot)))
        
        # Method chaining
        set_position(set_position(dot1, LEFT), UP)
    """
    # Use default alignment if not provided
    if alignment is None:
        alignment = np.array([0, 0, 0])  # ORIGIN equivalent
    
    # Call the Mobject's set_position method which handles all the logic
    return mobject.set_position(position, alignment=alignment, buff=buff, **kwargs)


def get_position(mobject: "Mobject") -> np.ndarray:
    """
    Get the current position of any Mobject.
    
    This is a global function that returns the center point of a Mobject.
    
    Args:
        mobject: The Mobject to get position from
        
    Returns:
        Position as numpy array [x, y, z]
        
    Examples:
        dot = Dot()
        pos = get_position(dot)
        print(f"Dot is at: {pos}")
    """
    return mobject.get_center()


def shift_position(mobject: "Mobject", vector: Point3D) -> "Mobject":
    """
    Shift the position of any Mobject by a vector.
    
    This is a global function equivalent to mobject.shift(vector).
    
    Args:
        mobject: The Mobject to shift
        vector: Shift vector as [x, y, z] or numpy array
        
    Returns:
        The shifted Mobject (for method chaining)
        
    Examples:
        dot = Dot()
        shift_position(dot, UP * 2)  # Move up by 2 units
    """
    return mobject.shift(vector)


def align_position(mobject: "Mobject", target: "Mobject", direction: Point3D) -> "Mobject":
    """
    Align one Mobject with another in a specific direction.
    
    Args:
        mobject: The Mobject to align
        target: The target Mobject to align with
        direction: Direction vector for alignment
        
    Returns:
        The aligned Mobject (for method chaining)
        
    Examples:
        dot1 = Dot()
        dot2 = Dot(UP)
        align_position(dot1, dot2, UP)  # Align dot1 with dot2 vertically
    """
    return mobject.align_to(target, direction)


def position_relative(mobject: "Mobject", target: "Mobject", 
                     direction: Point3D, buff: float = 0.25) -> "Mobject":
    """
    Position a Mobject relative to another Mobject.
    
    Args:
        mobject: The Mobject to position
        target: The reference Mobject
        direction: Direction from target (UP, DOWN, LEFT, RIGHT, etc.)
        buff: Buffer distance between objects
        
    Returns:
        The positioned Mobject (for method chaining)
        
    Examples:
        text = Text("Hello")
        dot = Dot()
        position_relative(text, dot, UP, buff=0.5)  # Position text above dot
    """
    return mobject.next_to(target, direction, buff=buff)


def interpolate_position(mobject: "Mobject", start_pos: Point3D, 
                        end_pos: Point3D, alpha: float) -> "Mobject":
    """
    Set Mobject position by interpolating between two points.
    
    Args:
        mobject: The Mobject to position
        start_pos: Starting position
        end_pos: Ending position
        alpha: Interpolation factor (0.0 to 1.0)
        
    Returns:
        The positioned Mobject (for method chaining)
        
    Examples:
        dot = Dot()
        # Position dot halfway between LEFT and RIGHT
        interpolate_position(dot, LEFT, RIGHT, 0.5)
    """
    from ..utils.space_ops import interpolate
    target_pos = interpolate(start_pos, end_pos, alpha)
    return set_position(mobject, target_pos)


def position_on_circle(mobject: "Mobject", center: Point3D, 
                      radius: float, angle: float) -> "Mobject":
    """
    Position a Mobject on a circle.
    
    Args:
        mobject: The Mobject to position
        center: Center of the circle
        radius: Radius of the circle
        angle: Angle in radians (0 = right, π/2 = up)
        
    Returns:
        The positioned Mobject (for method chaining)
        
    Examples:
        dot = Dot()
        # Position dot on circle at 45 degrees
        position_on_circle(dot, ORIGIN, 2, PI/4)
    """
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    z = center[2] if len(center) > 2 else 0
    return set_position(mobject, [x, y, z])


def position_in_grid(mobjects: Sequence["Mobject"], rows: int, cols: int,
                    spacing: float = 1.0, center: Point3D = None) -> None:
    """
    Position multiple Mobjects in a grid layout.
    
    Args:
        mobjects: List of Mobjects to arrange
        rows: Number of rows in grid
        cols: Number of columns in grid
        spacing: Spacing between grid positions
        center: Center point of the grid (default: ORIGIN)
        
    Examples:
        dots = [Dot() for _ in range(6)]
        position_in_grid(dots, 2, 3, spacing=1.5)  # 2x3 grid
    """
    if center is None:
        center = np.array([0, 0, 0])
    else:
        center = np.array(center)
    
    # Calculate grid dimensions
    grid_width = (cols - 1) * spacing
    grid_height = (rows - 1) * spacing
    
    # Starting position (top-left of grid)
    start_x = center[0] - grid_width / 2
    start_y = center[1] + grid_height / 2
    start_z = center[2]
    
    # Position each mobject
    for i, mobject in enumerate(mobjects):
        if i >= rows * cols:
            break
            
        row = i // cols
        col = i % cols
        
        x = start_x + col * spacing
        y = start_y - row * spacing
        z = start_z
        
        set_position(mobject, [x, y, z])


def position_along_path(mobject: "Mobject", path_points: Sequence[Point3D], 
                       alpha: float) -> "Mobject":
    """
    Position a Mobject along a path defined by points.
    
    Args:
        mobject: The Mobject to position
        path_points: List of points defining the path
        alpha: Position along path (0.0 = start, 1.0 = end)
        
    Returns:
        The positioned Mobject (for method chaining)
        
    Examples:
        dot = Dot()
        path = [LEFT*2, UP, RIGHT*2, DOWN]
        position_along_path(dot, path, 0.5)  # Halfway along path
    """
    if len(path_points) < 2:
        return mobject
    
    # Convert to numpy arrays
    points = [np.array(p) for p in path_points]
    
    # Calculate total path length
    segment_lengths = []
    total_length = 0
    for i in range(len(points) - 1):
        length = np.linalg.norm(points[i + 1] - points[i])
        segment_lengths.append(length)
        total_length += length
    
    if total_length == 0:
        return set_position(mobject, points[0])
    
    # Find target distance along path
    target_distance = alpha * total_length
    
    # Find which segment contains the target point
    current_distance = 0
    for i, segment_length in enumerate(segment_lengths):
        if current_distance + segment_length >= target_distance:
            # Interpolate within this segment
            segment_alpha = (target_distance - current_distance) / segment_length
            target_pos = points[i] + segment_alpha * (points[i + 1] - points[i])
            return set_position(mobject, target_pos)
        current_distance += segment_length
    
    # If we get here, position at the end
    return set_position(mobject, points[-1])


# Convenience functions for common positioning patterns
def center_mobject(mobject: "Mobject") -> "Mobject":
    """Center a Mobject at the origin."""
    return set_position(mobject, np.array([0, 0, 0]))


def position_at_edge(mobject: "Mobject", edge: Point3D, buff: float = 0.1) -> "Mobject":
    """Position a Mobject at the edge of the screen."""
    return mobject.to_edge(edge, buff=buff)


def position_in_corner(mobject: "Mobject", corner: Point3D, buff: float = 0.1) -> "Mobject":
    """Position a Mobject in a corner of the screen."""
    return mobject.to_corner(corner, buff=buff)


# Export all positioning functions
__all__ = [
    "set_position",
    "get_position", 
    "shift_position",
    "align_position",
    "position_relative",
    "interpolate_position",
    "position_on_circle",
    "position_in_grid",
    "position_along_path",
    "center_mobject",
    "position_at_edge",
    "position_in_corner",
]
