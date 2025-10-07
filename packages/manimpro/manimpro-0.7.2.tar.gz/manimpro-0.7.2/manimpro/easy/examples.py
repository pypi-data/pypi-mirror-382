#!/usr/bin/env python3
"""
ManimPro Easy Examples - Beginner-Friendly Animation Examples
============================================================

This module provides complete, ready-to-run examples that beginners
can use to learn ManimPro step by step.

Features:
- Complete working examples
- Commented code for learning
- Progressive difficulty levels
- Copy-paste ready animations

Usage:
    from manimpro.easy.examples import *
    
    # Run any example directly
    example = HelloWorldExample()
    # Save and render: manimpro -p -ql examples.py HelloWorldExample
"""

from __future__ import annotations

from .templates import EasyAnimation, QuickMath, SimpleShapes
from .. import *


class HelloWorldExample(EasyAnimation):
    """
    🌟 BEGINNER LEVEL: Your First Animation
    
    This is the simplest possible ManimPro animation.
    Perfect for complete beginners!
    """
    
    def __init__(self):
        super().__init__("Hello World")
        
        # Add a simple title
        self.add_title("Hello ManimPro!", color="#3B82F6")
        
        # Add some text
        self.add_text("Your first animation!", position="center", color="#4ECDC4")
        
        # Add a shape
        self.add_shape("circle", color="#FF6B6B")


class SimpleEquationExample(EasyAnimation):
    """
    📚 BEGINNER LEVEL: Show a Mathematical Equation
    
    Learn how to display beautiful mathematical equations.
    """
    
    def __init__(self):
        super().__init__("Simple Equation")
        
        # Title for our equation
        self.add_title("Famous Equation", color="#8B5CF6")
        
        # Einstein's mass-energy equivalence
        self.add_equation("E = mc^2")
        
        # Explanation
        self.add_text("Energy equals mass times speed of light squared", 
                     position="bottom", color="#95E1D3")


class ShapeTransformExample(SimpleShapes):
    """
    🔄 BEGINNER LEVEL: Transform Shapes
    
    Watch a circle magically transform into a square!
    """
    
    def __init__(self):
        super().__init__()
        
        # Title
        self.add_title("Shape Magic", color="#FFE66D")
        
        # Transform circle to square
        self.transform_shape("circle", "square", color="#FF6B6B")
        
        # Add explanation
        self.add_text("Smooth transformations!", position="bottom")


class FunctionGraphExample(EasyAnimation):
    """
    📈 INTERMEDIATE LEVEL: Graph Mathematical Functions
    
    Create beautiful graphs of mathematical functions.
    """
    
    def __init__(self):
        super().__init__("Function Graph")
        
        # Title
        self.add_title("Quadratic Function", color="#4ECDC4")
        
        # Create a parabola
        self.create_graph("x^2", color="#FF6B6B")
        
        # Add explanation
        self.add_text("f(x) = x² creates a parabola", position="bottom")


class PythagoreanProofExample(EasyAnimation):
    """
    🔺 INTERMEDIATE LEVEL: Mathematical Proof
    
    Animated proof of the famous Pythagorean theorem.
    """
    
    def __init__(self):
        super().__init__("Pythagorean Proof")
        
        # Show the proof
        self.show_pythagorean_proof()
        
        # Add conclusion
        self.add_text("Proven for over 2000 years!", position="bottom", color="#95E1D3")


class MultipleEquationsExample(QuickMath):
    """
    🧮 INTERMEDIATE LEVEL: Step-by-Step Math
    
    Show mathematical derivation step by step.
    """
    
    def __init__(self):
        super().__init__()
        
        # Show algebraic steps
        steps = [
            "2x + 5 = 15",
            "2x = 15 - 5", 
            "2x = 10",
            "x = 5"
        ]
        
        self.show_equation_derivation(steps, "Solving for x")


class ComplexAnimationExample(EasyAnimation):
    """
    🎬 ADVANCED LEVEL: Multiple Elements
    
    Combine multiple elements for a complete animation.
    """
    
    def __init__(self):
        super().__init__("Complex Animation")
        
        # Title sequence
        self.add_title("Mathematical Beauty", color="#8B5CF6")
        
        # Multiple equations
        self.add_equation("e^{i\\pi} + 1 = 0")  # Euler's identity
        
        # Shape transformation
        self.transform_shape("triangle", "circle", color="#FFE66D")
        
        # Function graph
        self.create_graph("sin(x)", color="#4ECDC4")
        
        # Conclusion
        self.add_text("Mathematics is everywhere!", position="bottom", color="#95E1D3")


class PhysicsFormulaExample(EasyAnimation):
    """
    ⚡ INTERMEDIATE LEVEL: Physics Demonstration
    
    Show famous physics formulas with context.
    """
    
    def __init__(self):
        super().__init__("Physics Formula")
        
        # Title
        self.add_title("Newton's Second Law", color="#FF6B6B")
        
        # The formula
        self.add_equation("F = ma")
        
        # Explanation
        self.add_text("Force = Mass × Acceleration", position="center", color="#4ECDC4")
        self.add_text("Foundation of classical mechanics", position="bottom", color="#95E1D3")


class GeometryShowcaseExample(SimpleShapes):
    """
    📐 BEGINNER LEVEL: Basic Shapes
    
    Showcase different geometric shapes.
    """
    
    def __init__(self):
        super().__init__()
        
        # Show all basic shapes
        self.show_geometry_basics()
        
        # Add title
        self.add_title("Geometric Shapes", color="#3B82F6")


class CalculusIntroExample(EasyAnimation):
    """
    📊 ADVANCED LEVEL: Calculus Concepts
    
    Introduction to calculus with derivatives.
    """
    
    def __init__(self):
        super().__init__("Calculus Introduction")
        
        # Title
        self.add_title("The Power of Calculus", color="#FF6B6B")
        
        # Show derivative
        self.add_equation("\\frac{d}{dx}x^2 = 2x")
        
        # Graph the function
        self.create_graph("x^2", color="#FFE66D")
        
        # Explanation
        self.add_text("Derivatives show rate of change", position="bottom")


# Tutorial Examples with Progressive Difficulty
class Tutorial01_HelloWorld(HelloWorldExample):
    """Tutorial 1: Your very first animation"""
    pass


class Tutorial02_Equations(SimpleEquationExample):
    """Tutorial 2: Adding mathematical equations"""
    pass


class Tutorial03_Shapes(ShapeTransformExample):
    """Tutorial 3: Working with shapes"""
    pass


class Tutorial04_Graphs(FunctionGraphExample):
    """Tutorial 4: Creating function graphs"""
    pass


class Tutorial05_Proofs(PythagoreanProofExample):
    """Tutorial 5: Mathematical proofs"""
    pass


class Tutorial06_Advanced(ComplexAnimationExample):
    """Tutorial 6: Combining multiple elements"""
    pass


# Example library for easy access
EXAMPLE_LIBRARY = {
    "hello": {
        "class": HelloWorldExample,
        "level": "Beginner",
        "description": "Your first ManimPro animation with title and text",
        "concepts": ["titles", "text", "shapes"]
    },
    "equation": {
        "class": SimpleEquationExample,
        "level": "Beginner", 
        "description": "Display mathematical equations beautifully",
        "concepts": ["equations", "LaTeX", "text positioning"]
    },
    "shapes": {
        "class": ShapeTransformExample,
        "level": "Beginner",
        "description": "Transform shapes with smooth animations",
        "concepts": ["shapes", "transformations", "colors"]
    },
    "graph": {
        "class": FunctionGraphExample,
        "level": "Intermediate",
        "description": "Create graphs of mathematical functions",
        "concepts": ["graphs", "functions", "coordinate systems"]
    },
    "proof": {
        "class": PythagoreanProofExample,
        "level": "Intermediate",
        "description": "Animated mathematical proof",
        "concepts": ["proofs", "geometry", "labels"]
    },
    "algebra": {
        "class": MultipleEquationsExample,
        "level": "Intermediate",
        "description": "Step-by-step algebraic solution",
        "concepts": ["step-by-step", "algebra", "derivations"]
    },
    "physics": {
        "class": PhysicsFormulaExample,
        "level": "Intermediate",
        "description": "Physics formulas with explanations",
        "concepts": ["physics", "formulas", "context"]
    },
    "geometry": {
        "class": GeometryShowcaseExample,
        "level": "Beginner",
        "description": "Showcase of basic geometric shapes",
        "concepts": ["geometry", "shapes", "colors"]
    },
    "calculus": {
        "class": CalculusIntroExample,
        "level": "Advanced",
        "description": "Introduction to calculus concepts",
        "concepts": ["calculus", "derivatives", "graphs"]
    },
    "complex": {
        "class": ComplexAnimationExample,
        "level": "Advanced",
        "description": "Complex animation with multiple elements",
        "concepts": ["multiple elements", "composition", "advanced"]
    }
}


def list_examples():
    """List all available examples with details."""
    print("🎬 ManimPro Easy Examples")
    print("=" * 50)
    
    # Group by level
    levels = {"Beginner": [], "Intermediate": [], "Advanced": []}
    
    for name, info in EXAMPLE_LIBRARY.items():
        levels[info["level"]].append((name, info))
    
    for level, examples in levels.items():
        print(f"\n📚 {level.upper()} LEVEL")
        print("-" * 30)
        
        for name, info in examples:
            print(f"🎯 {name}")
            print(f"   Description: {info['description']}")
            print(f"   Concepts: {', '.join(info['concepts'])}")
            print(f"   Class: {info['class'].__name__}")
            print()
    
    print("💡 Usage:")
    print("1. Copy any example class to your Python file")
    print("2. Run: manimpro -p -ql your_file.py ExampleClassName")
    print("3. Watch your animation!")
    
    print("\n🚀 Quick Start:")
    print("from manimpro.easy.examples import HelloWorldExample")
    print("# Save to file and render!")


def get_example_code(example_name: str) -> str:
    """Get the complete code for an example."""
    if example_name not in EXAMPLE_LIBRARY:
        return f"Example '{example_name}' not found. Available: {list(EXAMPLE_LIBRARY.keys())}"
    
    info = EXAMPLE_LIBRARY[example_name]
    class_name = info["class"].__name__
    
    code = f'''#!/usr/bin/env python3
"""
{info["description"]}
Level: {info["level"]}
Concepts: {", ".join(info["concepts"])}
"""

from manimpro.easy.examples import {class_name}

# Your animation is ready!
# To render: manimpro -p -ql this_file.py {class_name}

if __name__ == "__main__":
    print("🎬 Ready to render {class_name}!")
    print("Run: manimpro -p -ql this_file.py {class_name}")
'''
    
    return code


def create_tutorial_series():
    """Create a complete tutorial series."""
    tutorials = [
        ("tutorial_01_hello.py", Tutorial01_HelloWorld),
        ("tutorial_02_equations.py", Tutorial02_Equations),
        ("tutorial_03_shapes.py", Tutorial03_Shapes),
        ("tutorial_04_graphs.py", Tutorial04_Graphs),
        ("tutorial_05_proofs.py", Tutorial05_Proofs),
        ("tutorial_06_advanced.py", Tutorial06_Advanced),
    ]
    
    print("📚 Creating ManimPro Tutorial Series...")
    
    for filename, tutorial_class in tutorials:
        code = f'''#!/usr/bin/env python3
"""
ManimPro Tutorial: {tutorial_class.__doc__}
"""

from manimpro.easy.examples import {tutorial_class.__name__}

# To render this tutorial:
# manimpro -p -ql {filename} {tutorial_class.__name__}

if __name__ == "__main__":
    print("🎓 Tutorial: {tutorial_class.__doc__}")
    print("Run: manimpro -p -ql {filename} {tutorial_class.__name__}")
'''
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"✅ Created: {filename}")
        except Exception as e:
            print(f"❌ Error creating {filename}: {e}")
    
    print(f"\n🎉 Tutorial series created!")
    print("Start with: manimpro -p -ql tutorial_01_hello.py Tutorial01_HelloWorld")


if __name__ == "__main__":
    list_examples()
