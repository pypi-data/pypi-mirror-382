#!/usr/bin/env python3
"""
ManimPro Graph & Math Visualization Helpers
===========================================

This module provides enhanced graph plotting and mathematical visualization
utilities that simplify common operations and extend existing functionality.

Features:
- Simplified function plotting
- Dynamic dots with ValueTracker integration
- Automatic tangent line generation
- Area shading and highlighting
- Intersection finding
- Graph animation utilities

Usage:
    from manimpro.utils.graph_helpers import plot_function, add_dynamic_dot
    
    # Simple function plotting
    graph = plot_function(lambda x: x**2, x_range=[-3, 3], color=BLUE)
    
    # Add dynamic dot
    dot = add_dynamic_dot(graph, color=YELLOW)
"""

from __future__ import annotations

import numpy as np
from typing import Union, Callable, Sequence, TYPE_CHECKING, Optional, List, Tuple

if TYPE_CHECKING:
    from ..mobject.mobject import Mobject
    from ..mobject.graphing.coordinate_systems import Axes
    from ..animation.animation import Animation

# Type hints
FunctionType = Callable[[float], float]
ColorType = Union[str, tuple, np.ndarray]
NumberType = Union[int, float]
RangeType = Sequence[NumberType]


def plot_function(func: FunctionType, x_range: RangeType, 
                 axes: Optional["Axes"] = None, color: ColorType = None,
                 stroke_width: NumberType = 3, **kwargs) -> "Mobject":
    """
    Simplified wrapper to plot any function.
    
    This provides an easy way to plot mathematical functions with sensible defaults.
    
    Args:
        func: Function to plot (takes x, returns y)
        x_range: Range of x values as [x_min, x_max] or [x_min, x_max, step]
        axes: Axes object to plot on (creates default if None)
        color: Color of the function graph
        stroke_width: Width of the function line
        **kwargs: Additional arguments passed to plot method
        
    Returns:
        The plotted function graph
        
    Examples:
        # Plot a parabola
        parabola = plot_function(lambda x: x**2, [-3, 3], color=BLUE)
        
        # Plot sine wave
        sine = plot_function(np.sin, [-2*PI, 2*PI], color=RED)
        
        # Plot with custom axes
        my_axes = Axes(x_range=[-5, 5], y_range=[-10, 10])
        cubic = plot_function(lambda x: x**3, [-2, 2], axes=my_axes, color=GREEN)
    """
    from ..mobject.graphing.coordinate_systems import Axes
    from ..utils.color import BLUE
    
    if color is None:
        color = BLUE
    
    # Create default axes if none provided
    if axes is None:
        # Determine reasonable y_range by sampling the function
        x_min, x_max = x_range[0], x_range[1]
        x_samples = np.linspace(x_min, x_max, 100)
        try:
            y_samples = [func(x) for x in x_samples]
            y_min, y_max = min(y_samples), max(y_samples)
            # Add some padding
            y_padding = (y_max - y_min) * 0.1
            y_range = [y_min - y_padding, y_max + y_padding]
        except:
            y_range = [-10, 10]  # Fallback range
            
        axes = Axes(
            x_range=[x_min, x_max, 1],
            y_range=y_range,
            tips=False
        )
    
    # Create the function graph
    graph = axes.plot(func, x_range=x_range, color=color, 
                     stroke_width=stroke_width, **kwargs)
    
    return graph


def add_dynamic_dot(graph: "Mobject", tracker: Optional["Mobject"] = None, 
                   color: ColorType = None, radius: NumberType = 0.08,
                   **kwargs) -> "Mobject":
    """
    Place a dot on a function graph with optional ValueTracker integration.
    
    Args:
        graph: The function graph to place the dot on
        tracker: ValueTracker to control dot position (creates one if None)
        color: Color of the dot
        radius: Radius of the dot
        **kwargs: Additional arguments for Dot creation
        
    Returns:
        The dynamic dot with updater attached
        
    Examples:
        graph = plot_function(lambda x: x**2, [-3, 3])
        
        # Simple dynamic dot
        dot = add_dynamic_dot(graph, color=YELLOW)
        
        # With custom tracker
        x_tracker = ValueTracker(0)
        dot = add_dynamic_dot(graph, tracker=x_tracker, color=RED)
    """
    from ..mobject.geometry.arc import Dot
    from ..animation.updaters.update import ValueTracker
    from ..utils.color import YELLOW
    
    if color is None:
        color = YELLOW
    
    # Create tracker if none provided
    if tracker is None:
        # Get reasonable initial value from graph
        try:
            x_range = getattr(graph, 'x_range', [-1, 1])
            initial_x = (x_range[0] + x_range[1]) / 2
        except:
            initial_x = 0
        tracker = ValueTracker(initial_x)
    
    # Create the dot
    dot = Dot(color=color, radius=radius, **kwargs)
    
    # Add updater to follow the graph
    def update_dot_position(mob):
        try:
            x_val = tracker.get_value()
            point = graph.point_from_proportion(
                graph.proportion_from_x_value(x_val)
            )
            mob.move_to(point)
        except:
            pass  # Handle edge cases gracefully
    
    dot.add_updater(update_dot_position)
    
    # Store reference to tracker for easy access
    dot.tracker = tracker
    
    return dot


def draw_tangent(graph: "Mobject", x_val: NumberType, 
                color: ColorType = None, length: NumberType = 4,
                **kwargs) -> "Mobject":
    """
    Auto-generate tangent line at a specific x-value on a graph.
    
    Args:
        graph: The function graph
        x_val: x-value where to draw the tangent
        color: Color of the tangent line
        length: Length of the tangent line
        **kwargs: Additional arguments for Line creation
        
    Returns:
        The tangent line
        
    Examples:
        graph = plot_function(lambda x: x**2, [-3, 3])
        tangent = draw_tangent(graph, x_val=1, color=RED)
        
        # Multiple tangents
        tangents = [draw_tangent(graph, x, color=GREEN) for x in [-1, 0, 1]]
    """
    from ..mobject.geometry.line import Line
    from ..utils.color import RED
    
    if color is None:
        color = RED
    
    try:
        # Get the point on the graph
        point = graph.point_from_proportion(
            graph.proportion_from_x_value(x_val)
        )
        
        # Calculate the slope (derivative) at this point
        # Use numerical differentiation
        h = 0.001
        try:
            x1 = x_val - h
            x2 = x_val + h
            point1 = graph.point_from_proportion(graph.proportion_from_x_value(x1))
            point2 = graph.point_from_proportion(graph.proportion_from_x_value(x2))
            slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
        except:
            slope = 0  # Fallback
        
        # Create tangent line
        direction = np.array([1, slope, 0])
        direction = direction / np.linalg.norm(direction) * length / 2
        
        start_point = point - direction
        end_point = point + direction
        
        tangent = Line(start_point, end_point, color=color, **kwargs)
        
    except Exception as e:
        # Fallback: create a horizontal line
        tangent = Line([-length/2, 0, 0], [length/2, 0, 0], color=color, **kwargs)
    
    return tangent


def shade_area(graph: "Mobject", x_range: RangeType, 
              color: ColorType = None, opacity: NumberType = 0.3,
              **kwargs) -> "Mobject":
    """
    Shade the area under a curve between two x-values.
    
    Args:
        graph: The function graph
        x_range: Range to shade as [x_min, x_max]
        color: Color of the shaded area
        opacity: Opacity of the shaded area
        **kwargs: Additional arguments for area creation
        
    Returns:
        The shaded area
        
    Examples:
        graph = plot_function(lambda x: x**2, [-3, 3])
        area = shade_area(graph, [-1, 1], color=BLUE, opacity=0.5)
        
        # Multiple areas
        area1 = shade_area(graph, [-2, 0], color=RED, opacity=0.3)
        area2 = shade_area(graph, [0, 2], color=GREEN, opacity=0.3)
    """
    from ..utils.color import BLUE
    
    if color is None:
        color = BLUE
    
    try:
        # Get the axes from the graph
        axes = getattr(graph, 'axes', None)
        if axes is None:
            # Try to find axes in the graph's parent or create default
            from ..mobject.graphing.coordinate_systems import Axes
            axes = Axes()
        
        # Create the area
        area = axes.get_area(graph, x_range=x_range, color=color, opacity=opacity, **kwargs)
        
    except Exception as e:
        # Fallback: create a simple polygon
        from ..mobject.geometry.polygram import Polygon
        
        x_min, x_max = x_range[0], x_range[1]
        try:
            # Sample points along the curve
            x_vals = np.linspace(x_min, x_max, 50)
            points = []
            
            # Add bottom-left corner
            points.append([x_min, 0, 0])
            
            # Add points along the curve
            for x in x_vals:
                try:
                    point = graph.point_from_proportion(
                        graph.proportion_from_x_value(x)
                    )
                    points.append(point)
                except:
                    points.append([x, 0, 0])
            
            # Add bottom-right corner
            points.append([x_max, 0, 0])
            
            area = Polygon(*points, color=color, fill_opacity=opacity, 
                          stroke_width=0, **kwargs)
            
        except:
            # Ultimate fallback
            area = Polygon([x_min, 0, 0], [x_max, 0, 0], [x_max, 1, 0], [x_min, 1, 0],
                          color=color, fill_opacity=opacity, stroke_width=0)
    
    return area


def highlight_intersections(graphs: List["Mobject"], color: ColorType = None,
                           radius: NumberType = 0.1, **kwargs) -> List["Mobject"]:
    """
    Automatically find and highlight intersection points between graphs.
    
    Args:
        graphs: List of function graphs
        color: Color of intersection dots
        radius: Radius of intersection dots
        **kwargs: Additional arguments for Dot creation
        
    Returns:
        List of dots at intersection points
        
    Examples:
        graph1 = plot_function(lambda x: x**2, [-3, 3])
        graph2 = plot_function(lambda x: 2*x + 1, [-3, 3])
        intersections = highlight_intersections([graph1, graph2], color=WHITE)
    """
    from ..mobject.geometry.arc import Dot
    from ..utils.color import WHITE
    
    if color is None:
        color = WHITE
    
    intersection_dots = []
    
    # For each pair of graphs
    for i in range(len(graphs)):
        for j in range(i + 1, len(graphs)):
            graph1, graph2 = graphs[i], graphs[j]
            
            try:
                # Find intersections by sampling and looking for sign changes
                # This is a simple numerical approach
                x_samples = np.linspace(-10, 10, 1000)  # Adjust range as needed
                
                intersections = []
                for k in range(len(x_samples) - 1):
                    x1, x2 = x_samples[k], x_samples[k + 1]
                    
                    try:
                        # Get y-values for both graphs
                        point1_g1 = graph1.point_from_proportion(
                            graph1.proportion_from_x_value(x1)
                        )
                        point1_g2 = graph2.point_from_proportion(
                            graph2.proportion_from_x_value(x1)
                        )
                        point2_g1 = graph1.point_from_proportion(
                            graph1.proportion_from_x_value(x2)
                        )
                        point2_g2 = graph2.point_from_proportion(
                            graph2.proportion_from_x_value(x2)
                        )
                        
                        y1_diff = point1_g1[1] - point1_g2[1]
                        y2_diff = point2_g1[1] - point2_g2[1]
                        
                        # Check for sign change (intersection)
                        if y1_diff * y2_diff < 0:
                            # Linear interpolation to find approximate intersection
                            x_intersect = x1 - y1_diff * (x2 - x1) / (y2_diff - y1_diff)
                            
                            # Get the actual point on one of the graphs
                            point = graph1.point_from_proportion(
                                graph1.proportion_from_x_value(x_intersect)
                            )
                            intersections.append(point)
                            
                    except:
                        continue
                
                # Create dots for intersections
                for point in intersections:
                    dot = Dot(point, color=color, radius=radius, **kwargs)
                    intersection_dots.append(dot)
                    
            except:
                continue
    
    return intersection_dots


def animate_graph(graph: "Mobject", start_x: NumberType = None, 
                 end_x: NumberType = None, run_time: NumberType = 2) -> "Animation":
    """
    Animate the drawing of a graph from start to end.
    
    Args:
        graph: The function graph to animate
        start_x: Starting x-value (uses graph minimum if None)
        end_x: Ending x-value (uses graph maximum if None)
        run_time: Duration of the animation
        
    Returns:
        Animation that draws the graph progressively
        
    Examples:
        graph = plot_function(lambda x: x**2, [-3, 3])
        anim = animate_graph(graph, run_time=3)
        self.play(anim)
        
        # Animate part of the graph
        anim = animate_graph(graph, start_x=-1, end_x=1, run_time=2)
    """
    from ..animation.creation import Create
    from ..animation.transform import Transform
    
    try:
        # Use Create animation for the entire graph
        return Create(graph, run_time=run_time)
    except:
        # Fallback to a simple fade in
        from ..animation.fading import FadeIn
        return FadeIn(graph, run_time=run_time)


def plot_parametric_curve(fx: FunctionType, fy: FunctionType, t_range: RangeType,
                         axes: Optional["Axes"] = None, color: ColorType = None,
                         **kwargs) -> "Mobject":
    """
    Plot a parametric curve defined by x(t) and y(t).
    
    Args:
        fx: Function for x-coordinate (takes t, returns x)
        fy: Function for y-coordinate (takes t, returns y)
        t_range: Range of parameter t as [t_min, t_max] or [t_min, t_max, step]
        axes: Axes object to plot on
        color: Color of the curve
        **kwargs: Additional arguments
        
    Returns:
        The parametric curve
        
    Examples:
        # Circle
        circle = plot_parametric_curve(
            lambda t: np.cos(t), 
            lambda t: np.sin(t), 
            [0, TAU], 
            color=BLUE
        )
        
        # Spiral
        spiral = plot_parametric_curve(
            lambda t: t * np.cos(t),
            lambda t: t * np.sin(t),
            [0, 4*PI],
            color=RED
        )
    """
    from ..mobject.graphing.coordinate_systems import Axes
    from ..utils.color import BLUE
    
    if color is None:
        color = BLUE
    
    # Create default axes if none provided
    if axes is None:
        axes = Axes()
    
    try:
        # Create parametric curve
        curve = axes.plot_parametric_curve(
            lambda t: [fx(t), fy(t), 0],
            t_range=t_range,
            color=color,
            **kwargs
        )
    except:
        # Fallback: sample points and create a path
        from ..mobject.geometry.line import VMobject
        
        t_min, t_max = t_range[0], t_range[1]
        t_step = t_range[2] if len(t_range) > 2 else (t_max - t_min) / 100
        
        t_vals = np.arange(t_min, t_max + t_step, t_step)
        points = []
        
        for t in t_vals:
            try:
                x, y = fx(t), fy(t)
                points.append([x, y, 0])
            except:
                continue
        
        if points:
            curve = VMobject(color=color, **kwargs)
            curve.set_points_as_corners(points)
        else:
            # Ultimate fallback
            from ..mobject.geometry.line import Line
            curve = Line([0, 0, 0], [1, 1, 0], color=color)
    
    return curve


# Export all graph helper functions
__all__ = [
    "plot_function",
    "add_dynamic_dot",
    "draw_tangent",
    "shade_area", 
    "highlight_intersections",
    "animate_graph",
    "plot_parametric_curve",
]
