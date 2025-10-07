#!/usr/bin/env python3
"""
ManimPro Global Mobject Utility Functions
==========================================

This module provides global utility functions for common Mobject operations
that can be used anywhere without needing scene context. These functions
complement the positioning system and make ManimPro more user-friendly.

Features:
- Global color setting and styling
- Scaling and transformation utilities
- Centering and alignment helpers
- Generic animation functions
- Connection and labeling utilities

Usage:
    from manimpro.utils.mobject_helpers import set_color, scale_to, center
    
    # Use anywhere without self
    dot = Dot()
    set_color(dot, RED)
    scale_to(dot, 2.0)
    center(dot)
"""

from __future__ import annotations

import numpy as np
from typing import Union, Sequence, TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..mobject.mobject import Mobject
    from ..animation.animation import Animation

# Type hints
ColorType = Union[str, tuple, np.ndarray]
NumberType = Union[int, float]
Point3D = Union[Sequence[float], np.ndarray]


def set_color(mobject: "Mobject", color: ColorType) -> "Mobject":
    """
    Set the color of any Mobject.
    
    This is a global function that can be called anywhere without needing
    scene context. Works with all color formats supported by ManimPro.
    
    Args:
        mobject: The Mobject to color
        color: Color in any supported format (string, hex, RGB tuple, etc.)
        
    Returns:
        The colored Mobject (for method chaining)
        
    Examples:
        dot = Dot()
        set_color(dot, RED)              # Manim constant
        set_color(dot, "#FF0000")        # Hex color
        set_color(dot, "red")            # String color
        set_color(dot, (1, 0, 0))        # RGB tuple
        
        # Method chaining
        set_color(scale_to(dot, 2), BLUE)
    """
    return mobject.set_color(color)


def scale_to(mobject: "Mobject", factor: NumberType, **kwargs) -> "Mobject":
    """
    Uniformly scale a Mobject by a factor.
    
    This is a global function that scales objects without messing with
    coordinates. The scaling is applied relative to the object's center.
    
    Args:
        mobject: The Mobject to scale
        factor: Scale factor (1.0 = no change, 2.0 = double size, 0.5 = half size)
        **kwargs: Additional arguments passed to scale method
        
    Returns:
        The scaled Mobject (for method chaining)
        
    Examples:
        circle = Circle()
        scale_to(circle, 2.0)            # Double the size
        scale_to(circle, 0.5)            # Half the size
        
        # With additional options
        scale_to(square, 1.5, about_point=ORIGIN)
    """
    return mobject.scale(factor, **kwargs)


def center(mobject: "Mobject") -> "Mobject":
    """
    Center a Mobject on the screen.
    
    This is a global shortcut function for centering any Mobject at the origin.
    
    Args:
        mobject: The Mobject to center
        
    Returns:
        The centered Mobject (for method chaining)
        
    Examples:
        text = Text("Hello World")
        center(text)                     # Center on screen
        
        # Method chaining
        center(set_color(text, BLUE))
    """
    return mobject.move_to(np.array([0, 0, 0]))


def animate_property(mobject: "Mobject", property_name: str, value: Any, 
                    run_time: float = 1, **kwargs) -> "Animation":
    """
    Generic animation function for any Mobject property.
    
    This creates an animation that changes any property of a Mobject over time.
    
    Args:
        mobject: The Mobject to animate
        property_name: Name of the property to animate (e.g., "fill_opacity")
        value: Target value for the property
        run_time: Duration of the animation in seconds
        **kwargs: Additional animation arguments
        
    Returns:
        Animation object that can be played in a scene
        
    Examples:
        circle = Circle()
        
        # Animate opacity
        anim1 = animate_property(circle, "fill_opacity", 0.5)
        
        # Animate stroke width
        anim2 = animate_property(circle, "stroke_width", 5, run_time=2)
        
        # In a scene
        self.play(animate_property(circle, "fill_opacity", 0.8))
    """
    from ..animation.transform import ApplyMethod
    
    # Create a method that sets the property
    def set_property(mob):
        setattr(mob, property_name, value)
        return mob
    
    return ApplyMethod(set_property, mobject, run_time=run_time, **kwargs)


def connect_dots(dots: Sequence["Mobject"], color: ColorType = None, 
                stroke_width: NumberType = 2, **kwargs) -> "Mobject":
    """
    Automatically create lines connecting a sequence of dots.
    
    This is useful for creating graphs, polygons, or any connected structure.
    
    Args:
        dots: Sequence of Mobjects (typically dots) to connect
        color: Color of the connecting lines (default: WHITE)
        stroke_width: Width of the connecting lines
        **kwargs: Additional arguments for line creation
        
    Returns:
        VGroup containing all the connecting lines
        
    Examples:
        # Create connected dots
        dots = [Dot(UP), Dot(RIGHT), Dot(DOWN), Dot(LEFT)]
        lines = connect_dots(dots, color=BLUE, stroke_width=3)
        
        # Create a polygon
        vertices = [Dot([np.cos(i*TAU/6), np.sin(i*TAU/6), 0]) for i in range(6)]
        hexagon_lines = connect_dots(vertices + [vertices[0]], color=GREEN)
    """
    from ..mobject.geometry.line import Line
    from ..mobject.types.vectorized_mobject import VGroup
    from ..utils.color import WHITE
    
    if color is None:
        color = WHITE
    
    if len(dots) < 2:
        return VGroup()  # Return empty group if not enough dots
    
    lines = VGroup()
    
    for i in range(len(dots) - 1):
        start_pos = dots[i].get_center()
        end_pos = dots[i + 1].get_center()
        line = Line(start_pos, end_pos, color=color, stroke_width=stroke_width, **kwargs)
        lines.add(line)
    
    return lines


def create_label(mobject: "Mobject", text: str, font_size: NumberType = 24, 
                color: ColorType = None, direction: Point3D = None, 
                buff: float = 0.25, **kwargs) -> "Mobject":
    """
    Create a text label for any Mobject.
    
    This dynamically creates and positions a text label relative to a Mobject.
    
    Args:
        mobject: The Mobject to label
        text: Text content for the label
        font_size: Size of the label text
        color: Color of the label text (default: WHITE)
        direction: Direction to place label relative to object (default: UP)
        buff: Buffer distance between object and label
        **kwargs: Additional arguments for Text creation
        
    Returns:
        Text Mobject positioned as a label
        
    Examples:
        dot = Dot()
        label = create_label(dot, "Point A", font_size=20, color=YELLOW)
        
        # Label below the object
        label2 = create_label(circle, "Circle", direction=DOWN, buff=0.5)
        
        # Custom styling
        label3 = create_label(square, "Square", font_size=30, color=RED, 
                             font="Arial", weight="bold")
    """
    from ..mobject.text.text_mobject import Text
    from ..utils.color import WHITE
    
    if color is None:
        color = WHITE
    if direction is None:
        direction = np.array([0, 1, 0])  # UP
    
    # Create the text label
    label = Text(text, font_size=font_size, color=color, **kwargs)
    
    # Position it relative to the mobject
    label.next_to(mobject, direction, buff=buff)
    
    return label


def set_opacity(mobject: "Mobject", opacity: NumberType) -> "Mobject":
    """
    Set the opacity of any Mobject.
    
    Args:
        mobject: The Mobject to modify
        opacity: Opacity value (0.0 = transparent, 1.0 = opaque)
        
    Returns:
        The modified Mobject (for method chaining)
        
    Examples:
        circle = Circle()
        set_opacity(circle, 0.5)         # Semi-transparent
        set_opacity(circle, 0.0)         # Fully transparent
    """
    if hasattr(mobject, 'set_fill_opacity'):
        mobject.set_fill_opacity(opacity)
    if hasattr(mobject, 'set_stroke_opacity'):
        mobject.set_stroke_opacity(opacity)
    return mobject


def set_stroke_width(mobject: "Mobject", width: NumberType) -> "Mobject":
    """
    Set the stroke width of any Mobject.
    
    Args:
        mobject: The Mobject to modify
        width: Stroke width in pixels
        
    Returns:
        The modified Mobject (for method chaining)
        
    Examples:
        circle = Circle()
        set_stroke_width(circle, 5)      # Thick outline
        set_stroke_width(circle, 0)      # No outline
    """
    return mobject.set_stroke(width=width)


def rotate_to(mobject: "Mobject", angle: NumberType, **kwargs) -> "Mobject":
    """
    Rotate a Mobject to a specific angle.
    
    Args:
        mobject: The Mobject to rotate
        angle: Target angle in radians
        **kwargs: Additional arguments for rotation
        
    Returns:
        The rotated Mobject (for method chaining)
        
    Examples:
        square = Square()
        rotate_to(square, PI/4)          # 45 degrees
        rotate_to(square, TAU/3)         # 120 degrees
    """
    return mobject.rotate(angle, **kwargs)


def copy_mobject(mobject: "Mobject") -> "Mobject":
    """
    Create a copy of any Mobject.
    
    Args:
        mobject: The Mobject to copy
        
    Returns:
        A new Mobject that's a copy of the original
        
    Examples:
        original = Circle()
        copy = copy_mobject(original)
        set_color(copy, RED)             # Color the copy differently
    """
    return mobject.copy()


def make_group(*mobjects: "Mobject") -> "Mobject":
    """
    Group multiple Mobjects together.
    
    Args:
        *mobjects: Variable number of Mobjects to group
        
    Returns:
        VGroup containing all the Mobjects
        
    Examples:
        dot1, dot2, dot3 = Dot(), Dot(), Dot()
        group = make_group(dot1, dot2, dot3)
        center(group)                    # Center the entire group
    """
    from ..mobject.types.vectorized_mobject import VGroup
    return VGroup(*mobjects)


def apply_to_all(mobjects: Sequence["Mobject"], func, *args, **kwargs):
    """
    Apply a function to all Mobjects in a sequence.
    
    Args:
        mobjects: Sequence of Mobjects
        func: Function to apply to each Mobject
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        List of results from applying the function
        
    Examples:
        dots = [Dot() for _ in range(5)]
        apply_to_all(dots, set_color, RED)           # Color all dots red
        apply_to_all(dots, scale_to, 1.5)            # Scale all dots
        apply_to_all(dots, set_opacity, 0.7)         # Make all semi-transparent
    """
    results = []
    for mobject in mobjects:
        result = func(mobject, *args, **kwargs)
        results.append(result)
    return results


# Export all utility functions
__all__ = [
    "set_color",
    "scale_to", 
    "center",
    "animate_property",
    "connect_dots",
    "create_label",
    "set_opacity",
    "set_stroke_width",
    "rotate_to",
    "copy_mobject",
    "make_group",
    "apply_to_all",
]
