#!/usr/bin/env python3
"""
ManimPro Easy Presets - Ready-to-Use Animation Presets
=====================================================

This module provides pre-configured animation presets that beginners
can use immediately with minimal customization.

Features:
- One-line animation creation
- Popular animation patterns
- Educational templates
- Customizable presets

Usage:
    from manimpro.easy.presets import *
    
    # Create animations with one line
    create_intro_animation("My Channel")
    create_math_proof("Pythagorean Theorem")
    create_function_demo("x^2")
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from .templates import EasyAnimation, QuickMath, SimpleShapes


class PresetAnimations:
    """Collection of preset animations for common use cases."""
    
    @staticmethod
    def intro_animation(title: str = "Welcome", subtitle: str = "to ManimPro!") -> EasyAnimation:
        """Create a channel/video intro animation."""
        anim = EasyAnimation(f"Intro: {title}")
        anim.add_title(title, color="#3B82F6", size=60)
        anim.add_text(subtitle, position="center", color="#8B5CF6")
        anim.add_shape("circle", color="#FF6B6B", size=0.5)
        anim.transform_shape("circle", "square", color="#4ECDC4")
        return anim
        
    @staticmethod
    def math_equation_reveal(equation: str, title: str = "Mathematical Truth") -> EasyAnimation:
        """Create an equation reveal animation."""
        anim = EasyAnimation(f"Equation: {equation}")
        anim.add_title(title, color="#FFE66D")
        anim.add_equation(equation)
        anim.add_text("Beautiful mathematics!", position="bottom", color="#95E1D3")
        return anim
        
    @staticmethod
    def function_transformation(functions: List[str], title: str = "Function Evolution") -> QuickMath:
        """Create function transformation animation."""
        anim = QuickMath()
        anim.show_function_transformation(functions, title)
        return anim
        
    @staticmethod
    def geometry_showcase(title: str = "Geometric Shapes") -> SimpleShapes:
        """Create geometry showcase animation."""
        anim = SimpleShapes()
        anim.show_geometry_basics()
        return anim
        
    @staticmethod
    def pythagorean_proof(title: str = "Pythagorean Theorem") -> EasyAnimation:
        """Create Pythagorean theorem proof."""
        anim = EasyAnimation(title)
        anim.add_title(title, color="#FF6B6B")
        anim.show_pythagorean_proof()
        return anim
        
    @staticmethod
    def equation_derivation(steps: List[str], title: str = "Step by Step") -> QuickMath:
        """Create step-by-step equation derivation."""
        anim = QuickMath()
        anim.show_equation_derivation(steps, title)
        return anim


# Convenience functions for one-line animation creation
def create_intro_animation(title: str = "Welcome", subtitle: str = "to ManimPro!") -> EasyAnimation:
    """Create intro animation with one line."""
    return PresetAnimations.intro_animation(title, subtitle)


def create_math_proof(theorem: str = "Pythagorean Theorem") -> EasyAnimation:
    """Create mathematical proof animation."""
    if "pythagorean" in theorem.lower():
        return PresetAnimations.pythagorean_proof(theorem)
    else:
        # Generic math animation
        anim = EasyAnimation(f"Proof: {theorem}")
        anim.add_title(theorem, color="#3B82F6")
        anim.add_text("Mathematical proof coming soon!", position="center")
        return anim


def create_function_demo(function: str = "x^2", title: str = None) -> EasyAnimation:
    """Create function demonstration."""
    if title is None:
        title = f"Function: {function}"
        
    anim = EasyAnimation(title)
    anim.add_title(title, color="#FFE66D")
    anim.create_graph(function, color="#4ECDC4")
    return anim


def create_shape_morph(from_shape: str = "circle", to_shape: str = "square") -> EasyAnimation:
    """Create shape morphing animation."""
    anim = SimpleShapes()
    anim.add_title(f"{from_shape.title()} to {to_shape.title()}")
    anim.transform_shape(from_shape, to_shape, color="#FF6B6B")
    return anim


def create_equation_reveal(equation: str, explanation: str = None) -> EasyAnimation:
    """Create equation reveal with explanation."""
    anim = EasyAnimation(f"Equation: {equation}")
    anim.add_title("Mathematical Beauty", color="#8B5CF6")
    anim.add_equation(equation)
    
    if explanation:
        anim.add_text(explanation, position="bottom", color="#95E1D3")
    else:
        anim.add_text("Elegant and powerful!", position="bottom", color="#95E1D3")
        
    return anim


# Popular educational presets
class EducationalPresets:
    """Educational animation presets for common topics."""
    
    @staticmethod
    def algebra_basics() -> EasyAnimation:
        """Basic algebra demonstration."""
        anim = EasyAnimation("Algebra Basics")
        anim.add_title("Solving for x", color="#3B82F6")
        anim.add_equation("2x + 5 = 15")
        anim.add_equation("2x = 10")
        anim.add_equation("x = 5")
        anim.add_text("Step by step!", position="bottom", color="#4ECDC4")
        return anim
        
    @staticmethod
    def calculus_intro() -> EasyAnimation:
        """Introduction to calculus."""
        anim = EasyAnimation("Calculus Introduction")
        anim.add_title("The Power of Calculus", color="#FF6B6B")
        anim.add_equation(r"\frac{d}{dx}x^2 = 2x")
        anim.create_graph("x^2", color="#FFE66D")
        anim.add_text("Derivatives show rate of change", position="bottom")
        return anim
        
    @staticmethod
    def geometry_proof() -> EasyAnimation:
        """Geometric proof demonstration."""
        anim = EasyAnimation("Geometry Proof")
        anim.add_title("Geometric Truth", color="#8B5CF6")
        anim.show_pythagorean_proof()
        return anim
        
    @staticmethod
    def physics_formula(formula: str, title: str = "Physics Formula") -> EasyAnimation:
        """Physics formula demonstration."""
        anim = EasyAnimation(title)
        anim.add_title(title, color="#4ECDC4")
        anim.add_equation(formula)
        
        # Add context based on formula
        if "E = mc" in formula:
            anim.add_text("Einstein's mass-energy equivalence", position="bottom")
        elif "F = ma" in formula:
            anim.add_text("Newton's second law of motion", position="bottom")
        else:
            anim.add_text("Fundamental physics principle", position="bottom")
            
        return anim


# Quick creation functions
def quick_algebra_demo() -> EasyAnimation:
    """Quick algebra demonstration."""
    return EducationalPresets.algebra_basics()


def quick_calculus_intro() -> EasyAnimation:
    """Quick calculus introduction."""
    return EducationalPresets.calculus_intro()


def quick_physics_demo(formula: str = "E = mc^2") -> EasyAnimation:
    """Quick physics demonstration."""
    return EducationalPresets.physics_formula(formula)


def quick_geometry_proof() -> EasyAnimation:
    """Quick geometry proof."""
    return EducationalPresets.geometry_proof()


# Animation library
PRESET_LIBRARY = {
    "intro": {
        "function": create_intro_animation,
        "description": "Channel/video introduction with title and shapes",
        "example": 'create_intro_animation("My Channel", "Welcome!")'
    },
    "equation": {
        "function": create_equation_reveal,
        "description": "Mathematical equation reveal with explanation",
        "example": 'create_equation_reveal("E = mc^2", "Mass-energy equivalence")'
    },
    "function": {
        "function": create_function_demo,
        "description": "Mathematical function graphing demonstration",
        "example": 'create_function_demo("sin(x)", "Sine Wave")'
    },
    "shapes": {
        "function": create_shape_morph,
        "description": "Shape transformation animation",
        "example": 'create_shape_morph("circle", "square")'
    },
    "algebra": {
        "function": quick_algebra_demo,
        "description": "Basic algebra problem solving",
        "example": "quick_algebra_demo()"
    },
    "calculus": {
        "function": quick_calculus_intro,
        "description": "Introduction to calculus concepts",
        "example": "quick_calculus_intro()"
    },
    "physics": {
        "function": quick_physics_demo,
        "description": "Physics formula demonstration",
        "example": 'quick_physics_demo("F = ma")'
    },
    "geometry": {
        "function": quick_geometry_proof,
        "description": "Geometric proof (Pythagorean theorem)",
        "example": "quick_geometry_proof()"
    }
}


def list_presets():
    """List all available presets."""
    print("🎬 ManimPro Animation Presets")
    print("=" * 40)
    
    for name, info in PRESET_LIBRARY.items():
        print(f"\n📋 {name.upper()}")
        print(f"   Description: {info['description']}")
        print(f"   Example: {info['example']}")
        
    print(f"\n✨ Total presets available: {len(PRESET_LIBRARY)}")
    print("\nUsage:")
    print("from manimpro.easy.presets import *")
    print("anim = create_intro_animation('My Title')")
    print("# Save to file and render with: manimpro -p -ql file.py ClassName")


if __name__ == "__main__":
    list_presets()
