#!/usr/bin/env python3
"""
ManimPro Animation Wizard - Interactive Animation Builder
========================================================

This module provides an interactive wizard that guides beginners through
creating animations step-by-step with a simple question-and-answer interface.

Features:
- Interactive CLI wizard
- Step-by-step guidance
- Automatic code generation
- Beginner-friendly prompts
- Template selection

Usage:
    from manimpro.easy import AnimationWizard
    
    wizard = AnimationWizard()
    wizard.start()  # Interactive session
    
    # Or from command line:
    # manimpro wizard
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


@dataclass
class AnimationConfig:
    """Configuration for generated animation."""
    title: str = "My Animation"
    type: str = "basic"  # basic, math, shapes, graph
    elements: List[Dict[str, Any]] = None
    output_file: str = "my_animation.py"
    class_name: str = "MyAnimation"
    
    def __post_init__(self):
        if self.elements is None:
            self.elements = []


class AnimationWizard:
    """Interactive wizard for creating animations."""
    
    def __init__(self):
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        self.config = AnimationConfig()
        
    def print(self, text: str, style: str = None):
        """Print with or without rich formatting."""
        if self.console:
            self.console.print(text, style=style)
        else:
            print(text)
            
    def input(self, prompt: str, default: str = None) -> str:
        """Get user input with or without rich formatting."""
        if self.console and RICH_AVAILABLE:
            return Prompt.ask(prompt, default=default)
        else:
            if default:
                response = input(f"{prompt} [{default}]: ").strip()
                return response if response else default
            return input(f"{prompt}: ").strip()
            
    def confirm(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no confirmation."""
        if self.console and RICH_AVAILABLE:
            return Confirm.ask(prompt, default=default)
        else:
            default_str = "Y/n" if default else "y/N"
            response = input(f"{prompt} [{default_str}]: ").strip().lower()
            if not response:
                return default
            return response.startswith('y')
            
    def show_welcome(self):
        """Show welcome message."""
        welcome_text = """
🎬 Welcome to ManimPro Animation Wizard!

This wizard will help you create beautiful mathematical animations
with just a few simple questions. No coding experience required!

Let's build your animation step by step...
        """
        
        if self.console:
            panel = Panel(welcome_text, title="ManimPro Wizard", border_style="blue")
            self.console.print(panel)
        else:
            print("=" * 60)
            print(welcome_text)
            print("=" * 60)
            
    def choose_animation_type(self):
        """Let user choose animation type."""
        self.print("\n📋 Step 1: Choose Animation Type", style="bold blue")
        
        types = {
            "1": ("basic", "Basic Animation - Text, shapes, simple effects"),
            "2": ("math", "Math Animation - Equations, proofs, derivations"),
            "3": ("shapes", "Shape Animation - Geometry, transformations"),
            "4": ("graph", "Graph Animation - Functions, plots, data"),
        }
        
        if self.console:
            table = Table(title="Animation Types")
            table.add_column("Option", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Description", style="green")
            
            for key, (type_name, description) in types.items():
                table.add_row(key, type_name.title(), description)
            self.console.print(table)
        else:
            print("\nAvailable animation types:")
            for key, (type_name, description) in types.items():
                print(f"  {key}. {type_name.title()} - {description}")
                
        choice = self.input("\nChoose animation type (1-4)", "1")
        
        if choice in types:
            self.config.type = types[choice][0]
            self.print(f"✅ Selected: {types[choice][0].title()} Animation", style="green")
        else:
            self.config.type = "basic"
            self.print("✅ Selected: Basic Animation (default)", style="green")
            
    def get_basic_info(self):
        """Get basic animation information."""
        self.print("\n📝 Step 2: Basic Information", style="bold blue")
        
        self.config.title = self.input("Animation title", "My Awesome Animation")
        self.config.class_name = self.input("Class name (for code)", "MyAnimation")
        self.config.output_file = self.input("Output file name", "my_animation.py")
        
        self.print(f"✅ Title: {self.config.title}", style="green")
        self.print(f"✅ Class: {self.config.class_name}", style="green")
        self.print(f"✅ File: {self.config.output_file}", style="green")
        
    def add_elements(self):
        """Add elements based on animation type."""
        self.print(f"\n🎨 Step 3: Add Elements to Your {self.config.type.title()} Animation", style="bold blue")
        
        if self.config.type == "basic":
            self.add_basic_elements()
        elif self.config.type == "math":
            self.add_math_elements()
        elif self.config.type == "shapes":
            self.add_shape_elements()
        elif self.config.type == "graph":
            self.add_graph_elements()
            
    def add_basic_elements(self):
        """Add basic animation elements."""
        # Title
        if self.confirm("Add a title to your animation?"):
            title_text = self.input("Title text", self.config.title)
            color = self.input("Title color (hex or name)", "#3B82F6")
            self.config.elements.append({
                "type": "title",
                "text": title_text,
                "color": color
            })
            
        # Text
        if self.confirm("Add text to your animation?"):
            text_content = self.input("Text content", "Hello ManimPro!")
            position = self.input("Position (center/top/bottom/left/right)", "center")
            self.config.elements.append({
                "type": "text",
                "text": text_content,
                "position": position
            })
            
        # Shapes
        if self.confirm("Add shapes to your animation?"):
            shape_type = self.input("Shape type (circle/square/triangle/rectangle)", "circle")
            color = self.input("Shape color", "#FF6B6B")
            self.config.elements.append({
                "type": "shape",
                "shape": shape_type,
                "color": color
            })
            
    def add_math_elements(self):
        """Add mathematical elements."""
        # Equation
        if self.confirm("Add a mathematical equation?"):
            equation = self.input("LaTeX equation (e.g., E = mc^2)", "E = mc^2")
            self.config.elements.append({
                "type": "equation",
                "equation": equation
            })
            
        # Proof
        if self.confirm("Add Pythagorean theorem proof?"):
            self.config.elements.append({
                "type": "pythagorean_proof"
            })
            
    def add_shape_elements(self):
        """Add shape transformation elements."""
        if self.confirm("Add shape transformation?"):
            from_shape = self.input("Transform from (circle/square/triangle)", "circle")
            to_shape = self.input("Transform to (circle/square/triangle)", "square")
            color = self.input("Color", "#4ECDC4")
            
            self.config.elements.append({
                "type": "transform",
                "from_shape": from_shape,
                "to_shape": to_shape,
                "color": color
            })
            
    def add_graph_elements(self):
        """Add graph elements."""
        if self.confirm("Add a function graph?"):
            function = self.input("Function (x^2, sin(x), cos(x), x)", "x^2")
            color = self.input("Graph color", "#FFE66D")
            
            self.config.elements.append({
                "type": "graph",
                "function": function,
                "color": color
            })
            
    def generate_code(self) -> str:
        """Generate Python code for the animation."""
        code = f'''#!/usr/bin/env python3
"""
{self.config.title}
Generated by ManimPro Animation Wizard
"""

from manimpro.easy import EasyAnimation

class {self.config.class_name}(EasyAnimation):
    def __init__(self):
        super().__init__("{self.config.title}")
        
        # Add elements
'''
        
        for element in self.config.elements:
            if element["type"] == "title":
                code += f'        self.add_title("{element["text"]}", color="{element["color"]}")\n'
            elif element["type"] == "text":
                code += f'        self.add_text("{element["text"]}", position="{element["position"]}")\n'
            elif element["type"] == "equation":
                code += f'        self.add_equation(r"{element["equation"]}")\n'
            elif element["type"] == "shape":
                code += f'        self.add_shape("{element["shape"]}", color="{element["color"]}")\n'
            elif element["type"] == "transform":
                code += f'        self.transform_shape("{element["from_shape"]}", "{element["to_shape"]}", color="{element["color"]}")\n'
            elif element["type"] == "graph":
                code += f'        self.create_graph("{element["function"]}", color="{element["color"]}")\n'
            elif element["type"] == "pythagorean_proof":
                code += f'        self.show_pythagorean_proof()\n'
                
        code += '''

if __name__ == "__main__":
    # To render this animation, run:
    # manimpro -p -ql ''' + self.config.output_file + ''' ''' + self.config.class_name + '''
    print("🎬 Animation ready!")
    print("Run: manimpro -p -ql ''' + self.config.output_file + ''' ''' + self.config.class_name + '''")
'''
        
        return code
        
    def save_animation(self):
        """Save the generated animation to file."""
        code = self.generate_code()
        
        try:
            with open(self.config.output_file, 'w', encoding='utf-8') as f:
                f.write(code)
                
            self.print(f"\n✅ Animation saved to: {self.config.output_file}", style="bold green")
            return True
        except Exception as e:
            self.print(f"\n❌ Error saving file: {e}", style="bold red")
            return False
            
    def show_summary(self):
        """Show summary of created animation."""
        self.print("\n🎉 Animation Created Successfully!", style="bold green")
        
        if self.console:
            table = Table(title="Animation Summary")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="yellow")
            
            table.add_row("Title", self.config.title)
            table.add_row("Type", self.config.type.title())
            table.add_row("Class Name", self.config.class_name)
            table.add_row("File Name", self.config.output_file)
            table.add_row("Elements", str(len(self.config.elements)))
            
            self.console.print(table)
        else:
            print(f"Title: {self.config.title}")
            print(f"Type: {self.config.type.title()}")
            print(f"Class: {self.config.class_name}")
            print(f"File: {self.config.output_file}")
            print(f"Elements: {len(self.config.elements)}")
            
        self.print(f"\n🚀 To render your animation:", style="bold blue")
        self.print(f"   manimpro -p -ql {self.config.output_file} {self.config.class_name}", style="yellow")
        
        self.print(f"\n🌐 To preview in web browser:", style="bold blue")
        self.print(f"   manimpro preview", style="yellow")
        
    def start(self):
        """Start the interactive wizard."""
        try:
            self.show_welcome()
            self.choose_animation_type()
            self.get_basic_info()
            self.add_elements()
            
            if self.save_animation():
                self.show_summary()
                
                if self.confirm("\nWould you like to render the animation now?"):
                    self.print("🎬 Rendering animation...", style="bold blue")
                    # This would integrate with the CLI system
                    self.print(f"Run: manimpro -p -ql {self.config.output_file} {self.config.class_name}")
                    
        except KeyboardInterrupt:
            self.print("\n\n👋 Wizard cancelled by user.", style="yellow")
        except Exception as e:
            self.print(f"\n❌ Unexpected error: {e}", style="bold red")


def start_wizard():
    """Start the animation wizard."""
    wizard = AnimationWizard()
    wizard.start()


if __name__ == "__main__":
    start_wizard()
