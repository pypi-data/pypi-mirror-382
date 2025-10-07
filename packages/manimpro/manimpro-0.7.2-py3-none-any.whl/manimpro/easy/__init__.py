"""
ManimPro Easy Mode - Making Complex Animations Child's Play
==========================================================

This module provides beginner-friendly interfaces, templates, and wizards
to make creating complex mathematical animations as easy as possible.

Features:
- Simple animation templates
- Interactive animation wizard
- Preset configurations
- Beginner-friendly examples
- Step-by-step tutorials

Usage:
    from manimpro.easy import *
    
    # Create animations with simple commands
    anim = EasyAnimation()
    anim.add_title("My First Animation")
    anim.add_equation("E = mc^2")
    anim.transform_shape(Circle(), Square())
    anim.render()
"""

from .templates import *
from .wizard import *
from .presets import *
from .examples import *

__all__ = [
    "EasyAnimation",
    "QuickMath",
    "SimpleShapes",
    "AnimationWizard",
    "create_animation",
    "quick_render",
]
