#!/usr/bin/env python3
"""
ManimPro Advanced Math & Visualization Features
===============================================

This module provides advanced mathematical visualization utilities for
intermediate and advanced users, including vector fields, parametric curves,
calculus animations, and 3D support.

Features:
- Vector field plotting
- Parametric curve animations
- Integral and derivative visualizations
- 3D surface plotting
- Point motion along paths
- Advanced calculus concepts

Usage:
    from manimpro.utils.advanced_math import plot_vector_field, animate_integral
    
    # Plot a vector field
    field = plot_vector_field(lambda x, y: [y, -x], [-2, 2], [-2, 2])
    
    # Animate an integral
    integral_anim = animate_integral(graph, [-1, 1])
"""

from __future__ import annotations

import numpy as np
from typing import Union, Callable, Sequence, TYPE_CHECKING, Optional, Tuple, List

if TYPE_CHECKING:
    from ..mobject.mobject import Mobject
    from ..animation.animation import Animation

# Type hints
FunctionType = Callable[[float], float]
VectorFieldType = Callable[[float, float], Tuple[float, float]]
ParametricType = Callable[[float], Tuple[float, float]]
ColorType = Union[str, tuple, np.ndarray]
NumberType = Union[int, float]
RangeType = Sequence[NumberType]


def plot_vector_field(vector_func: VectorFieldType, x_range: RangeType, y_range: RangeType,
                     step_multiple: NumberType = 1, length_func: Callable = None,
                     color: ColorType = None, **kwargs) -> "Mobject":
    """
    Plot a 2D vector field.
    
    Args:
        vector_func: Function that takes (x, y) and returns (dx, dy)
        x_range: Range of x values as [x_min, x_max]
        y_range: Range of y values as [y_min, y_max]
        step_multiple: Spacing between field vectors
        length_func: Function to determine vector lengths (optional)
        color: Color of the vectors
        **kwargs: Additional arguments for vector creation
        
    Returns:
        VGroup containing all field vectors
        
    Examples:
        # Circular field
        field = plot_vector_field(
            lambda x, y: [-y, x], 
            [-3, 3], [-3, 3], 
            color=BLUE
        )
        
        # Radial field
        field = plot_vector_field(
            lambda x, y: [x, y], 
            [-2, 2], [-2, 2],
            color=RED
        )
    """
    from ..mobject.geometry.line import Vector
    from ..mobject.types.vectorized_mobject import VGroup
    from ..utils.color import BLUE
    
    if color is None:
        color = BLUE
    
    x_min, x_max = x_range[0], x_range[1]
    y_min, y_max = y_range[0], y_range[1]
    
    # Create grid of points
    x_step = (x_max - x_min) / (10 * step_multiple)
    y_step = (y_max - y_min) / (10 * step_multiple)
    
    vectors = VGroup()
    
    x_vals = np.arange(x_min, x_max + x_step, x_step)
    y_vals = np.arange(y_min, y_max + y_step, y_step)
    
    for x in x_vals:
        for y in y_vals:
            try:
                # Get vector components
                dx, dy = vector_func(x, y)
                
                # Calculate vector length
                if length_func:
                    length = length_func(dx, dy)
                else:
                    length = np.sqrt(dx**2 + dy**2)
                    # Normalize and scale
                    if length > 0:
                        scale = min(0.5, 1.0 / (1 + length))
                        dx *= scale / length
                        dy *= scale / length
                
                # Create vector
                start_point = np.array([x, y, 0])
                direction = np.array([dx, dy, 0])
                
                if np.linalg.norm(direction) > 0.01:  # Only draw non-zero vectors
                    vector = Vector(direction, color=color, **kwargs)
                    vector.shift(start_point)
                    vectors.add(vector)
                    
            except:
                continue  # Skip problematic points
    
    return vectors


def plot_parametric_3d(fx: FunctionType, fy: FunctionType, fz: FunctionType,
                      t_range: RangeType, color: ColorType = None, **kwargs) -> "Mobject":
    """
    Plot a 3D parametric curve.
    
    Args:
        fx: Function for x-coordinate (takes t, returns x)
        fy: Function for y-coordinate (takes t, returns y)  
        fz: Function for z-coordinate (takes t, returns z)
        t_range: Range of parameter t
        color: Color of the curve
        **kwargs: Additional arguments
        
    Returns:
        The 3D parametric curve
        
    Examples:
        # 3D spiral
        spiral = plot_parametric_3d(
            lambda t: np.cos(t),
            lambda t: np.sin(t), 
            lambda t: t/5,
            [0, 4*PI],
            color=BLUE
        )
        
        # DNA helix
        helix = plot_parametric_3d(
            lambda t: np.cos(t),
            lambda t: np.sin(t),
            lambda t: t/2,
            [0, 6*PI],
            color=GREEN
        )
    """
    from ..mobject.geometry.line import VMobject
    from ..utils.color import BLUE
    
    if color is None:
        color = BLUE
    
    t_min, t_max = t_range[0], t_range[1]
    t_step = t_range[2] if len(t_range) > 2 else (t_max - t_min) / 200
    
    t_vals = np.arange(t_min, t_max + t_step, t_step)
    points = []
    
    for t in t_vals:
        try:
            x, y, z = fx(t), fy(t), fz(t)
            points.append([x, y, z])
        except:
            continue
    
    if points:
        curve = VMobject(color=color, **kwargs)
        curve.set_points_as_corners(points)
        return curve
    else:
        # Fallback
        from ..mobject.geometry.line import Line
        return Line([0, 0, 0], [1, 1, 1], color=color)


def animate_integral(graph: "Mobject", x_range: RangeType, 
                    n_rects: int = 50, color: ColorType = None,
                    run_time: NumberType = 3) -> "Animation":
    """
    Show Riemann sums growing dynamically to visualize integration.
    
    Args:
        graph: The function graph to integrate under
        x_range: Integration range as [x_min, x_max]
        n_rects: Number of rectangles in the Riemann sum
        color: Color of the rectangles
        run_time: Duration of the animation
        
    Returns:
        Animation showing the integral approximation
        
    Examples:
        graph = plot_function(lambda x: x**2, [-2, 2])
        integral_anim = animate_integral(graph, [-1, 1], n_rects=20)
        self.play(integral_anim)
    """
    from ..mobject.geometry.polygram import Rectangle
    from ..mobject.types.vectorized_mobject import VGroup
    from ..animation.creation import Create
    from ..animation.composition import AnimationGroup
    from ..utils.color import BLUE
    
    if color is None:
        color = BLUE
    
    x_min, x_max = x_range[0], x_range[1]
    dx = (x_max - x_min) / n_rects
    
    rectangles = VGroup()
    
    for i in range(n_rects):
        x = x_min + i * dx
        try:
            # Get height from graph
            point = graph.point_from_proportion(
                graph.proportion_from_x_value(x + dx/2)
            )
            height = point[1]
            
            if height > 0:  # Only positive areas for now
                rect = Rectangle(
                    width=dx,
                    height=height,
                    color=color,
                    fill_opacity=0.5,
                    stroke_width=1
                )
                rect.move_to([x + dx/2, height/2, 0])
                rectangles.add(rect)
                
        except:
            continue
    
    # Create animation with lag
    return AnimationGroup(
        *[Create(rect) for rect in rectangles],
        lag_ratio=0.1,
        run_time=run_time
    )


def animate_derivative(graph: "Mobject", x_tracker: "Mobject" = None,
                      tangent_color: ColorType = None, 
                      run_time: NumberType = 4) -> Tuple["Animation", "Mobject"]:
    """
    Display tangent slopes dynamically along a graph to show derivatives.
    
    Args:
        graph: The function graph
        x_tracker: ValueTracker for x position (creates one if None)
        tangent_color: Color of the tangent line
        run_time: Duration of the animation
        
    Returns:
        Tuple of (animation, tangent_line_mobject)
        
    Examples:
        graph = plot_function(lambda x: x**3, [-2, 2])
        anim, tangent = animate_derivative(graph, tangent_color=RED)
        self.play(anim)
    """
    from ..animation.updaters.update import ValueTracker
    from ..mobject.geometry.line import Line
    from ..utils.color import RED
    from ..animation.transform import Transform
    
    if tangent_color is None:
        tangent_color = RED
    
    if x_tracker is None:
        # Get reasonable range from graph
        try:
            x_range = getattr(graph, 'x_range', [-2, 2])
            x_tracker = ValueTracker(x_range[0])
        except:
            x_tracker = ValueTracker(-2)
    
    # Create initial tangent line
    tangent = Line([-1, 0, 0], [1, 0, 0], color=tangent_color)
    
    def update_tangent(mob):
        try:
            x_val = x_tracker.get_value()
            
            # Get point on graph
            point = graph.point_from_proportion(
                graph.proportion_from_x_value(x_val)
            )
            
            # Calculate slope numerically
            h = 0.01
            try:
                point1 = graph.point_from_proportion(
                    graph.proportion_from_x_value(x_val - h)
                )
                point2 = graph.point_from_proportion(
                    graph.proportion_from_x_value(x_val + h)
                )
                slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
            except:
                slope = 0
            
            # Update tangent line
            length = 2
            direction = np.array([1, slope, 0])
            direction = direction / np.linalg.norm(direction) * length / 2
            
            new_start = point - direction
            new_end = point + direction
            
            mob.put_start_and_end_on(new_start, new_end)
            
        except:
            pass
    
    tangent.add_updater(update_tangent)
    
    # Create animation that moves the tracker
    try:
        x_range = getattr(graph, 'x_range', [-2, 2])
        anim = x_tracker.animate.set_value(x_range[1])
        anim.run_time = run_time
    except:
        from ..animation.transform import ApplyMethod
        anim = ApplyMethod(x_tracker.set_value, 2, run_time=run_time)
    
    return anim, tangent


def plot_3d_surface(func: Callable[[float, float], float], 
                   x_range: RangeType, y_range: RangeType,
                   resolution: int = 20, color: ColorType = None,
                   **kwargs) -> "Mobject":
    """
    Plot a 3D surface defined by z = f(x, y).
    
    Args:
        func: Function that takes (x, y) and returns z
        x_range: Range of x values
        y_range: Range of y values
        resolution: Number of grid points per axis
        color: Color of the surface
        **kwargs: Additional arguments
        
    Returns:
        The 3D surface
        
    Examples:
        # Paraboloid
        surface = plot_3d_surface(
            lambda x, y: x**2 + y**2,
            [-2, 2], [-2, 2],
            color=BLUE
        )
        
        # Saddle point
        surface = plot_3d_surface(
            lambda x, y: x**2 - y**2,
            [-2, 2], [-2, 2],
            color=RED
        )
    """
    from ..mobject.three_d.three_dimensions import Surface
    from ..utils.color import BLUE
    
    if color is None:
        color = BLUE
    
    try:
        # Create 3D surface
        surface = Surface(
            lambda u, v: [u, v, func(u, v)],
            u_range=x_range,
            v_range=y_range,
            resolution=(resolution, resolution),
            color=color,
            **kwargs
        )
        return surface
        
    except:
        # Fallback: create a mesh of lines
        from ..mobject.types.vectorized_mobject import VGroup
        from ..mobject.geometry.line import Line
        
        x_min, x_max = x_range[0], x_range[1]
        y_min, y_max = y_range[0], y_range[1]
        
        x_vals = np.linspace(x_min, x_max, resolution)
        y_vals = np.linspace(y_min, y_max, resolution)
        
        lines = VGroup()
        
        # Create grid lines
        for i, x in enumerate(x_vals):
            points = []
            for y in y_vals:
                try:
                    z = func(x, y)
                    points.append([x, y, z])
                except:
                    points.append([x, y, 0])
            
            if len(points) > 1:
                for j in range(len(points) - 1):
                    line = Line(points[j], points[j + 1], color=color, stroke_width=1)
                    lines.add(line)
        
        for j, y in enumerate(y_vals):
            points = []
            for x in x_vals:
                try:
                    z = func(x, y)
                    points.append([x, y, z])
                except:
                    points.append([x, y, 0])
            
            if len(points) > 1:
                for i in range(len(points) - 1):
                    line = Line(points[i], points[i + 1], color=color, stroke_width=1)
                    lines.add(line)
        
        return lines


def animate_point_motion(path_func: ParametricType, t_range: RangeType,
                        point_color: ColorType = None, trace_path: bool = True,
                        run_time: NumberType = 4) -> Tuple["Animation", "Mobject"]:
    """
    Animate a point moving along a function or parametric path.
    
    Args:
        path_func: Function that takes t and returns (x, y)
        t_range: Range of parameter t
        point_color: Color of the moving point
        trace_path: Whether to show the path being traced
        run_time: Duration of the animation
        
    Returns:
        Tuple of (animation, point_mobject)
        
    Examples:
        # Point moving in circle
        anim, point = animate_point_motion(
            lambda t: (np.cos(t), np.sin(t)),
            [0, TAU],
            point_color=YELLOW
        )
        self.play(anim)
        
        # Point moving along parabola
        anim, point = animate_point_motion(
            lambda t: (t, t**2),
            [-2, 2],
            trace_path=True
        )
    """
    from ..mobject.geometry.arc import Dot
    from ..animation.updaters.update import ValueTracker
    from ..utils.color import YELLOW
    from ..animation.transform import Transform
    
    if point_color is None:
        point_color = YELLOW
    
    # Create the moving point
    point = Dot(color=point_color, radius=0.08)
    
    # Create parameter tracker
    t_min, t_max = t_range[0], t_range[1]
    t_tracker = ValueTracker(t_min)
    
    # Path tracing
    if trace_path:
        from ..mobject.geometry.line import VMobject
        path_trace = VMobject(color=point_color, stroke_width=2)
        traced_points = []
        
        def update_point_and_trace(mob):
            try:
                t = t_tracker.get_value()
                x, y = path_func(t)
                new_pos = np.array([x, y, 0])
                
                # Update point position
                point.move_to(new_pos)
                
                # Update trace
                traced_points.append(new_pos)
                if len(traced_points) > 1:
                    path_trace.set_points_as_corners(traced_points)
                    
            except:
                pass
        
        point.add_updater(update_point_and_trace)
        
    else:
        def update_point_position(mob):
            try:
                t = t_tracker.get_value()
                x, y = path_func(t)
                mob.move_to([x, y, 0])
            except:
                pass
        
        point.add_updater(update_point_position)
    
    # Create animation
    anim = t_tracker.animate.set_value(t_max)
    anim.run_time = run_time
    
    return anim, point


def create_gradient_field(func: Callable[[float, float], float],
                         x_range: RangeType, y_range: RangeType,
                         step_multiple: NumberType = 1, color: ColorType = None) -> "Mobject":
    """
    Create a gradient vector field for a scalar function.
    
    Args:
        func: Scalar function f(x, y)
        x_range: Range of x values
        y_range: Range of y values  
        step_multiple: Spacing between vectors
        color: Color of gradient vectors
        
    Returns:
        VGroup of gradient vectors
        
    Examples:
        # Gradient of paraboloid
        grad_field = create_gradient_field(
            lambda x, y: x**2 + y**2,
            [-2, 2], [-2, 2],
            color=GREEN
        )
    """
    def gradient_func(x, y):
        h = 0.01
        try:
            # Numerical gradient
            df_dx = (func(x + h, y) - func(x - h, y)) / (2 * h)
            df_dy = (func(x, y + h) - func(x, y - h)) / (2 * h)
            return df_dx, df_dy
        except:
            return 0, 0
    
    return plot_vector_field(gradient_func, x_range, y_range, 
                           step_multiple=step_multiple, color=color)


# Export all advanced math functions
__all__ = [
    "plot_vector_field",
    "plot_parametric_3d",
    "animate_integral",
    "animate_derivative",
    "plot_3d_surface",
    "animate_point_motion",
    "create_gradient_field",
]
