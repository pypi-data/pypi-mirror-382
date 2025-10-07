#!/usr/bin/env python3
"""
ManimPro Easy Templates - Pre-built Animation Components
=======================================================

This module provides simple, pre-built animation templates that beginners
can use to create complex animations with minimal code.

Examples:
    # Create a math explanation video
    anim = EasyAnimation("My Math Video")
    anim.add_title("Pythagorean Theorem")
    anim.add_equation("a² + b² = c²")
    anim.show_triangle_proof()
    anim.render()
    
    # Create shape transformations
    shapes = SimpleShapes()
    shapes.morph_circle_to_square()
    shapes.add_text("Geometry is Fun!")
    shapes.render()
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from typing import Any, List, Union, Optional

from .. import *
from ..animation.creation import Create, Write, DrawBorderThenFill
from ..animation.transform import Transform, ReplacementTransform
from ..animation.indication import Indicate, Flash, Circumscribe
from ..mobject.geometry.arc import Circle
from ..mobject.geometry.polygram import Square, Triangle, Rectangle
from ..mobject.text.text_mobject import Text
from ..mobject.text.tex_mobject import MathTex
from ..scene.scene import Scene


class EasyAnimation(Scene):
    """
    Beginner-friendly animation class with simple methods.
    
    Makes complex animations accessible through easy-to-understand methods.
    """
    
    def __init__(self, title: str = "My Animation", **kwargs):
        super().__init__(**kwargs)
        self.animation_title = title
        self.elements = []
        self.current_step = 0
        
    def add_title(self, text: str, color: str = "#3B82F6", size: int = 48) -> None:
        """Add a title to your animation."""
        title = Text(text, font_size=size, color=color)
        title.to_edge(UP, buff=1)
        self.elements.append(("title", title))
        
    def add_equation(self, equation: str, color: str = "#FFFFFF") -> None:
        """Add a mathematical equation."""
        eq = MathTex(equation, font_size=40, color=color)
        self.elements.append(("equation", eq))
        
    def add_text(self, text: str, position: str = "center", color: str = "#FFFFFF") -> None:
        """Add text to your animation."""
        text_obj = Text(text, font_size=32, color=color)
        
        if position == "top":
            text_obj.to_edge(UP)
        elif position == "bottom":
            text_obj.to_edge(DOWN)
        elif position == "left":
            text_obj.to_edge(LEFT)
        elif position == "right":
            text_obj.to_edge(RIGHT)
        # center is default
        
        self.elements.append(("text", text_obj))
        
    def add_shape(self, shape_type: str, color: str = "#FF6B6B", size: float = 1.0) -> None:
        """Add a shape to your animation."""
        shapes = {
            "circle": Circle(radius=size, color=color, fill_opacity=0.7),
            "square": Square(side_length=size*2, color=color, fill_opacity=0.7),
            "triangle": Triangle(color=color, fill_opacity=0.7).scale(size),
            "rectangle": Rectangle(width=size*2, height=size, color=color, fill_opacity=0.7)
        }
        
        if shape_type.lower() in shapes:
            shape = shapes[shape_type.lower()]
            self.elements.append(("shape", shape))
        else:
            raise ValueError(f"Unknown shape: {shape_type}. Use: circle, square, triangle, rectangle")
    
    def transform_shape(self, from_shape: str, to_shape: str, color: str = "#4ECDC4") -> None:
        """Transform one shape into another."""
        self.add_shape(from_shape, color)
        self.add_shape(to_shape, color)
        self.elements.append(("transform", (from_shape, to_shape)))
        
    def create_graph(self, function: str, x_range: tuple = (-3, 3), color: str = "#FFE66D") -> None:
        """Create a mathematical function graph."""
        axes = Axes(
            x_range=[x_range[0], x_range[1], 1],
            y_range=[-3, 3, 1],
            axis_config={"color": "#CCCCCC"}
        )
        
        # Simple function parsing
        if function == "x^2" or function == "x²":
            graph = axes.plot(lambda x: x**2, color=color)
        elif function == "sin(x)":
            graph = axes.plot(np.sin, color=color)
        elif function == "cos(x)":
            graph = axes.plot(np.cos, color=color)
        elif function == "x":
            graph = axes.plot(lambda x: x, color=color)
        else:
            # Default to x^2
            graph = axes.plot(lambda x: x**2, color=color)
            
        self.elements.append(("graph", (axes, graph, function)))
        
    def show_pythagorean_proof(self) -> None:
        """Show animated proof of Pythagorean theorem."""
        # Create right triangle
        triangle = Polygon(
            [-2, -1, 0], [1, -1, 0], [-2, 1.5, 0],
            color="#FF6B6B", fill_opacity=0.3
        )
        
        # Labels for sides
        a_label = MathTex("a", color="#FFE66D").next_to(triangle, LEFT)
        b_label = MathTex("b", color="#FFE66D").next_to(triangle, DOWN)
        c_label = MathTex("c", color="#FFE66D").next_to(triangle, RIGHT, buff=0.5)
        
        # Equation
        equation = MathTex("a^2 + b^2 = c^2", font_size=48, color="#4ECDC4")
        equation.to_edge(UP, buff=1)
        
        self.elements.append(("pythagorean", (triangle, a_label, b_label, c_label, equation)))
        
    def construct(self):
        """Build the animation from added elements."""
        if not self.elements:
            # Default demo if no elements added
            self.add_title("Welcome to ManimPro!")
            self.add_text("Making animations easy!", "center")
            self.add_shape("circle")
            
        # Render elements in order
        current_objects = []
        
        for element_type, element_data in self.elements:
            if element_type == "title":
                self.play(Write(element_data), run_time=1.5)
                current_objects.append(element_data)
                self.wait(1)
                
            elif element_type == "equation":
                element_data.shift(UP * 0.5)
                self.play(Write(element_data), run_time=2)
                current_objects.append(element_data)
                self.wait(1)
                
            elif element_type == "text":
                self.play(Write(element_data), run_time=1)
                current_objects.append(element_data)
                self.wait(0.5)
                
            elif element_type == "shape":
                self.play(Create(element_data), run_time=1)
                current_objects.append(element_data)
                self.wait(0.5)
                
            elif element_type == "transform":
                # Find the shapes to transform
                shapes = [obj for obj in current_objects if hasattr(obj, 'fill_opacity')]
                if len(shapes) >= 2:
                    self.play(Transform(shapes[-2], shapes[-1]), run_time=2)
                    self.wait(1)
                    
            elif element_type == "graph":
                axes, graph, func_name = element_data
                self.play(Create(axes), run_time=1)
                self.play(Create(graph), run_time=2)
                
                # Add function label
                func_label = MathTex(f"f(x) = {func_name}", color=graph.color)
                func_label.to_corner(UR)
                self.play(Write(func_label), run_time=1)
                current_objects.extend([axes, graph, func_label])
                self.wait(1)
                
            elif element_type == "pythagorean":
                triangle, a_label, b_label, c_label, equation = element_data
                
                # Show triangle
                self.play(Create(triangle), run_time=1.5)
                self.wait(0.5)
                
                # Show labels
                self.play(
                    Write(a_label),
                    Write(b_label),
                    Write(c_label),
                    run_time=1.5
                )
                self.wait(1)
                
                # Show equation
                self.play(Write(equation), run_time=2)
                self.wait(1)
                
                # Highlight the relationship
                self.play(
                    Indicate(triangle, scale_factor=1.2),
                    Indicate(equation, scale_factor=1.1),
                    run_time=2
                )
                
                current_objects.extend([triangle, a_label, b_label, c_label, equation])
                
        # Final pause
        self.wait(2)


class QuickMath(EasyAnimation):
    """Quick mathematical demonstrations."""
    
    def __init__(self, **kwargs):
        super().__init__("Quick Math Demo", **kwargs)
        
    def show_equation_derivation(self, steps: List[str], title: str = "Equation Derivation"):
        """Show step-by-step equation derivation."""
        self.add_title(title)
        
        for i, step in enumerate(steps):
            self.add_equation(step)
            if i < len(steps) - 1:
                self.elements.append(("wait", 1))
                
    def show_function_transformation(self, functions: List[str], title: str = "Function Transformation"):
        """Show how functions transform."""
        self.add_title(title)
        
        for func in functions:
            self.create_graph(func)
            self.elements.append(("wait", 1.5))


class SimpleShapes(EasyAnimation):
    """Simple shape animations and transformations."""
    
    def __init__(self, **kwargs):
        super().__init__("Shape Animations", **kwargs)
        
    def morph_circle_to_square(self, color: str = "#FF6B6B"):
        """Animate a circle morphing into a square."""
        self.add_title("Circle to Square")
        self.transform_shape("circle", "square", color)
        
    def show_geometry_basics(self):
        """Show basic geometric shapes."""
        self.add_title("Basic Shapes")
        shapes = ["circle", "square", "triangle", "rectangle"]
        colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3"]
        
        for shape, color in zip(shapes, colors):
            self.add_shape(shape, color, 0.8)
            self.elements.append(("wait", 0.8))


def create_animation(animation_type: str = "basic", **kwargs) -> EasyAnimation:
    """
    Factory function to create different types of animations.
    
    Args:
        animation_type: Type of animation ("basic", "math", "shapes")
        **kwargs: Additional arguments for the animation
        
    Returns:
        EasyAnimation instance
    """
    if animation_type == "math":
        return QuickMath(**kwargs)
    elif animation_type == "shapes":
        return SimpleShapes(**kwargs)
    else:
        return EasyAnimation(**kwargs)


def quick_render(animation: EasyAnimation, quality: str = "low", preview: bool = True):
    """
    Quickly render an animation with sensible defaults.
    
    Args:
        animation: EasyAnimation instance
        quality: "low", "medium", or "high"
        preview: Whether to preview the result
    """
    quality_flags = {
        "low": "-ql",
        "medium": "-qm", 
        "high": "-qh"
    }
    
    preview_flag = "-p" if preview else ""
    quality_flag = quality_flags.get(quality, "-ql")
    
    # This would integrate with the CLI system
    print(f"Rendering animation with flags: {quality_flag} {preview_flag}")
    print("Use: manimpro {quality_flag} {preview_flag} your_file.py YourAnimationClass")


if __name__ == "__main__":
    # Example usage
    print("🎬 ManimPro Easy Templates")
    print("=" * 30)
    print("Example usage:")
    print("""
from manimpro.easy import EasyAnimation

# Create a simple animation
anim = EasyAnimation("My First Animation")
anim.add_title("Hello ManimPro!")
anim.add_equation("E = mc^2")
anim.add_shape("circle", "#FF6B6B")
anim.transform_shape("circle", "square")

# The animation will render automatically when you run:
# manimpro -p -ql your_file.py YourAnimationClass
    """)
