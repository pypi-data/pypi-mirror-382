#!/usr/bin/env python3
"""
ManimPro Beginner Utility Features
==================================

This module provides utilities specifically designed to lower the learning
curve for beginners. It includes grid helpers, axis labeling, quick drawing
functions, highlighting utilities, and pre-built scene templates.

Features:
- Background grid and axis helpers
- Quick drawing utilities (arrows, highlights)
- Area highlighting and emphasis
- Pre-built scene templates
- Simplified common operations

Usage:
    from manimpro.utils.beginner_helpers import add_grid, draw_arrow, create_template
    
    # Add background grid
    grid = add_grid(spacing=1)
    
    # Draw quick arrow
    arrow = draw_arrow([0, 0, 0], [2, 1, 0], color=RED)
    
    # Create template scene
    template = create_template('graph')
"""

from __future__ import annotations

import numpy as np
from typing import Union, Sequence, TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from ..mobject.mobject import Mobject
    from ..scene.scene import Scene

# Type hints
ColorType = Union[str, tuple, np.ndarray]
NumberType = Union[int, float]
Point3D = Union[Sequence[float], np.ndarray]


def add_grid(spacing: NumberType = 1, x_range: Sequence[NumberType] = None,
            y_range: Sequence[NumberType] = None, color: ColorType = None,
            opacity: NumberType = 0.3, **kwargs) -> "Mobject":
    """
    Add a background grid for reference.
    
    This creates a coordinate grid that helps beginners understand positioning
    and provides visual reference for their animations.
    
    Args:
        spacing: Distance between grid lines
        x_range: Range of x values as [x_min, x_max] (auto-detected if None)
        y_range: Range of y values as [y_min, y_max] (auto-detected if None)
        color: Color of the grid lines
        opacity: Opacity of the grid lines
        **kwargs: Additional arguments for line creation
        
    Returns:
        VGroup containing all grid lines
        
    Examples:
        # Basic grid
        grid = add_grid()
        self.add(grid)
        
        # Custom spacing and color
        grid = add_grid(spacing=0.5, color=BLUE, opacity=0.5)
        
        # Custom range
        grid = add_grid(x_range=[-5, 5], y_range=[-3, 3], spacing=1)
    """
    from ..mobject.geometry.line import Line
    from ..mobject.types.vectorized_mobject import VGroup
    from ..utils.color import GRAY
    from .. import config
    
    if color is None:
        color = GRAY
    
    # Default ranges based on frame size
    if x_range is None:
        x_range = [-config.frame_width/2, config.frame_width/2]
    if y_range is None:
        y_range = [-config.frame_height/2, config.frame_height/2]
    
    grid = VGroup()
    
    # Vertical lines
    x = x_range[0]
    while x <= x_range[1]:
        line = Line(
            [x, y_range[0], 0], 
            [x, y_range[1], 0],
            color=color,
            stroke_opacity=opacity,
            **kwargs
        )
        grid.add(line)
        x += spacing
    
    # Horizontal lines
    y = y_range[0]
    while y <= y_range[1]:
        line = Line(
            [x_range[0], y, 0], 
            [x_range[1], y, 0],
            color=color,
            stroke_opacity=opacity,
            **kwargs
        )
        grid.add(line)
        y += spacing
    
    return grid


def show_axes_labels(axes: "Mobject" = None, x_label: str = "x", y_label: str = "y",
                    font_size: NumberType = 24, color: ColorType = None,
                    **kwargs) -> "Mobject":
    """
    Automatically label X and Y axes.
    
    Args:
        axes: Axes object to label (creates default if None)
        x_label: Label for x-axis
        y_label: Label for y-axis
        font_size: Size of the labels
        color: Color of the labels
        **kwargs: Additional arguments for Text creation
        
    Returns:
        VGroup containing the axis labels
        
    Examples:
        # Label existing axes
        axes = Axes()
        labels = show_axes_labels(axes)
        self.add(axes, labels)
        
        # Custom labels
        labels = show_axes_labels(axes, x_label="Time", y_label="Position")
        
        # Styled labels
        labels = show_axes_labels(axes, font_size=30, color=BLUE, weight="bold")
    """
    from ..mobject.text.text_mobject import Text
    from ..mobject.types.vectorized_mobject import VGroup
    from ..mobject.graphing.coordinate_systems import Axes
    from ..utils.color import WHITE
    
    if color is None:
        color = WHITE
    
    # Create default axes if none provided
    if axes is None:
        axes = Axes()
    
    labels = VGroup()
    
    try:
        # Create x-axis label
        x_text = Text(x_label, font_size=font_size, color=color, **kwargs)
        
        # Position at the end of x-axis
        x_end = axes.get_x_axis().get_end()
        x_text.next_to(x_end, direction=[0.5, -0.5, 0], buff=0.2)
        labels.add(x_text)
        
        # Create y-axis label
        y_text = Text(y_label, font_size=font_size, color=color, **kwargs)
        
        # Position at the end of y-axis
        y_end = axes.get_y_axis().get_end()
        y_text.next_to(y_end, direction=[-0.5, 0.5, 0], buff=0.2)
        labels.add(y_text)
        
    except:
        # Fallback: position labels at standard locations
        x_text = Text(x_label, font_size=font_size, color=color, **kwargs)
        x_text.move_to([6, -0.5, 0])
        labels.add(x_text)
        
        y_text = Text(y_label, font_size=font_size, color=color, **kwargs)
        y_text.move_to([-0.5, 3.5, 0])
        labels.add(y_text)
    
    return labels


def draw_arrow(start: Point3D, end: Point3D, color: ColorType = None,
              tip_length: NumberType = 0.25, stroke_width: NumberType = 3,
              **kwargs) -> "Mobject":
    """
    Quick arrow helper for drawing arrows between points.
    
    Args:
        start: Starting point of the arrow
        end: Ending point of the arrow
        color: Color of the arrow
        tip_length: Length of the arrow tip
        stroke_width: Width of the arrow line
        **kwargs: Additional arguments for Arrow creation
        
    Returns:
        Arrow object
        
    Examples:
        # Basic arrow
        arrow = draw_arrow([0, 0, 0], [2, 1, 0])
        
        # Styled arrow
        arrow = draw_arrow(
            start=LEFT*2, 
            end=RIGHT*2, 
            color=RED, 
            stroke_width=5
        )
        
        # Multiple arrows
        arrows = [
            draw_arrow([0, 0, 0], [1, 1, 0], color=RED),
            draw_arrow([0, 0, 0], [1, -1, 0], color=BLUE),
            draw_arrow([0, 0, 0], [-1, 0, 0], color=GREEN)
        ]
    """
    from ..mobject.geometry.line import Arrow
    from ..utils.color import WHITE
    
    if color is None:
        color = WHITE
    
    start = np.array(start)
    end = np.array(end)
    
    arrow = Arrow(
        start=start,
        end=end,
        color=color,
        tip_length=tip_length,
        stroke_width=stroke_width,
        **kwargs
    )
    
    return arrow


def highlight_area(area: "Mobject", duration: NumberType = 1, 
                  highlight_color: ColorType = None, scale_factor: NumberType = 1.1,
                  **kwargs) -> "Animation":
    """
    Flash or emphasize parts of graphs or objects.
    
    Args:
        area: The Mobject to highlight
        duration: Duration of the highlight effect
        highlight_color: Color for highlighting
        scale_factor: How much to scale during highlight
        **kwargs: Additional animation arguments
        
    Returns:
        Animation that highlights the area
        
    Examples:
        circle = Circle()
        
        # Basic highlight
        highlight_anim = highlight_area(circle)
        self.play(highlight_anim)
        
        # Custom highlight
        highlight_anim = highlight_area(
            circle, 
            duration=2, 
            highlight_color=YELLOW,
            scale_factor=1.2
        )
    """
    from ..animation.indication import Indicate, Flash
    from ..utils.color import YELLOW
    
    if highlight_color is None:
        highlight_color = YELLOW
    
    try:
        # Use Indicate animation for scaling highlight
        return Indicate(area, color=highlight_color, scale_factor=scale_factor, 
                       run_time=duration, **kwargs)
    except:
        # Fallback to Flash
        return Flash(area, color=highlight_color, run_time=duration, **kwargs)


def create_template(scene_type: str = 'basic', **kwargs) -> Dict[str, Any]:
    """
    Create prebuilt scene templates for common scenarios.
    
    Args:
        scene_type: Type of template ('basic', 'graph', 'parabola', 'trig', 'sine_wave')
        **kwargs: Additional configuration options
        
    Returns:
        Dictionary with template configuration and setup functions
        
    Examples:
        # Create graph template
        template = create_template('graph')
        
        class MyScene(Scene):
            def construct(self):
                # Apply template
                template['setup'](self)
                
                # Your animation code here
                circle = Circle()
                self.play(Create(circle))
    """
    templates = {
        'basic': _create_basic_template,
        'graph': _create_graph_template,
        'parabola': _create_parabola_template,
        'trig': _create_trig_template,
        'sine_wave': _create_sine_wave_template,
        'coordinate_plane': _create_coordinate_plane_template,
        'number_line': _create_number_line_template,
    }
    
    if scene_type not in templates:
        raise ValueError(f"Unknown template type: {scene_type}. "
                        f"Available types: {list(templates.keys())}")
    
    return templates[scene_type](**kwargs)


def _create_basic_template(**kwargs) -> Dict[str, Any]:
    """Create a basic scene template with grid and title."""
    def setup(scene):
        # Add grid
        grid = add_grid(spacing=1, opacity=0.2)
        scene.add(grid)
        
        # Add title if provided
        title = kwargs.get('title')
        if title:
            from ..mobject.text.text_mobject import Text
            title_text = Text(title, font_size=48)
            title_text.to_edge([0, 1, 0], buff=0.5)
            scene.add(title_text)
    
    return {
        'type': 'basic',
        'setup': setup,
        'description': 'Basic scene with grid and optional title'
    }


def _create_graph_template(**kwargs) -> Dict[str, Any]:
    """Create a graph template with axes and labels."""
    def setup(scene):
        from ..mobject.graphing.coordinate_systems import Axes
        
        # Create axes
        x_range = kwargs.get('x_range', [-5, 5, 1])
        y_range = kwargs.get('y_range', [-3, 3, 1])
        
        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            tips=True,
            axis_config={"include_numbers": True}
        )
        scene.add(axes)
        
        # Add labels
        labels = show_axes_labels(
            axes, 
            x_label=kwargs.get('x_label', 'x'),
            y_label=kwargs.get('y_label', 'y')
        )
        scene.add(labels)
        
        # Store for easy access
        scene.axes = axes
        scene.labels = labels
    
    return {
        'type': 'graph',
        'setup': setup,
        'description': 'Graph template with labeled axes'
    }


def _create_parabola_template(**kwargs) -> Dict[str, Any]:
    """Create a parabola template with pre-plotted parabola."""
    def setup(scene):
        from ..mobject.graphing.coordinate_systems import Axes
        from ..utils.graph_helpers import plot_function
        
        # Create axes
        axes = Axes(x_range=[-3, 3, 1], y_range=[0, 9, 1], tips=True)
        scene.add(axes)
        
        # Plot parabola
        parabola = plot_function(lambda x: x**2, [-3, 3], axes=axes, color=kwargs.get('color', 'BLUE'))
        scene.add(parabola)
        
        # Add labels
        labels = show_axes_labels(axes)
        scene.add(labels)
        
        # Store for easy access
        scene.axes = axes
        scene.parabola = parabola
        scene.labels = labels
    
    return {
        'type': 'parabola',
        'setup': setup,
        'description': 'Parabola template with y = x² plotted'
    }


def _create_trig_template(**kwargs) -> Dict[str, Any]:
    """Create a trigonometry template with unit circle."""
    def setup(scene):
        from ..mobject.graphing.coordinate_systems import Axes
        from ..mobject.geometry.arc import Circle
        
        # Create axes
        axes = Axes(x_range=[-2, 2, 0.5], y_range=[-2, 2, 0.5], tips=True)
        scene.add(axes)
        
        # Add unit circle
        unit_circle = Circle(radius=1, color=kwargs.get('circle_color', 'WHITE'))
        scene.add(unit_circle)
        
        # Add labels
        labels = show_axes_labels(axes)
        scene.add(labels)
        
        # Store for easy access
        scene.axes = axes
        scene.unit_circle = unit_circle
        scene.labels = labels
    
    return {
        'type': 'trig',
        'setup': setup,
        'description': 'Trigonometry template with unit circle'
    }


def _create_sine_wave_template(**kwargs) -> Dict[str, Any]:
    """Create a sine wave template."""
    def setup(scene):
        from ..mobject.graphing.coordinate_systems import Axes
        from ..utils.graph_helpers import plot_function
        import numpy as np
        
        # Create axes
        axes = Axes(
            x_range=[0, 4*np.pi, np.pi/2], 
            y_range=[-1.5, 1.5, 0.5], 
            tips=True
        )
        scene.add(axes)
        
        # Plot sine wave
        sine_wave = plot_function(
            np.sin, 
            [0, 4*np.pi], 
            axes=axes, 
            color=kwargs.get('color', 'BLUE')
        )
        scene.add(sine_wave)
        
        # Add labels
        labels = show_axes_labels(axes, x_label="θ", y_label="sin(θ)")
        scene.add(labels)
        
        # Store for easy access
        scene.axes = axes
        scene.sine_wave = sine_wave
        scene.labels = labels
    
    return {
        'type': 'sine_wave',
        'setup': setup,
        'description': 'Sine wave template with sin(x) plotted'
    }


def _create_coordinate_plane_template(**kwargs) -> Dict[str, Any]:
    """Create a coordinate plane template with grid."""
    def setup(scene):
        from ..mobject.graphing.coordinate_systems import Axes
        
        # Create coordinate plane
        axes = Axes(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            tips=True,
            axis_config={"include_numbers": True}
        )
        scene.add(axes)
        
        # Add grid
        grid = add_grid(spacing=1, opacity=0.3)
        scene.add(grid)
        
        # Add labels
        labels = show_axes_labels(axes)
        scene.add(labels)
        
        # Store for easy access
        scene.axes = axes
        scene.grid = grid
        scene.labels = labels
    
    return {
        'type': 'coordinate_plane',
        'setup': setup,
        'description': 'Coordinate plane with grid and numbered axes'
    }


def _create_number_line_template(**kwargs) -> Dict[str, Any]:
    """Create a number line template."""
    def setup(scene):
        from ..mobject.graphing.coordinate_systems import NumberLine
        
        # Create number line
        number_line = NumberLine(
            x_range=[-10, 10, 1],
            length=12,
            include_numbers=True,
            include_tip=True
        )
        scene.add(number_line)
        
        # Store for easy access
        scene.number_line = number_line
    
    return {
        'type': 'number_line',
        'setup': setup,
        'description': 'Number line template'
    }


def quick_text(text: str, position: Point3D = None, font_size: NumberType = 36,
              color: ColorType = None, **kwargs) -> "Mobject":
    """
    Quickly create and position text.
    
    Args:
        text: Text content
        position: Position for the text (center if None)
        font_size: Size of the text
        color: Color of the text
        **kwargs: Additional Text arguments
        
    Returns:
        Text Mobject
        
    Examples:
        title = quick_text("My Animation", position=UP*3, font_size=48, color=BLUE)
        label = quick_text("Important!", position=DOWN*2, color=RED)
    """
    from ..mobject.text.text_mobject import Text
    from ..utils.color import WHITE
    
    if color is None:
        color = WHITE
    
    text_obj = Text(text, font_size=font_size, color=color, **kwargs)
    
    if position is not None:
        text_obj.move_to(position)
    
    return text_obj


def quick_dot(position: Point3D = None, color: ColorType = None, 
             radius: NumberType = 0.08, **kwargs) -> "Mobject":
    """
    Quickly create a dot at a position.
    
    Args:
        position: Position for the dot (origin if None)
        color: Color of the dot
        radius: Radius of the dot
        **kwargs: Additional Dot arguments
        
    Returns:
        Dot Mobject
        
    Examples:
        dot = quick_dot(UP*2, color=RED)
        origin_dot = quick_dot(color=YELLOW, radius=0.1)
    """
    from ..mobject.geometry.arc import Dot
    from ..utils.color import WHITE
    
    if color is None:
        color = WHITE
    if position is None:
        position = [0, 0, 0]
    
    return Dot(point=position, color=color, radius=radius, **kwargs)


# Export all beginner helper functions
__all__ = [
    "add_grid",
    "show_axes_labels",
    "draw_arrow",
    "highlight_area",
    "create_template",
    "quick_text",
    "quick_dot",
]
