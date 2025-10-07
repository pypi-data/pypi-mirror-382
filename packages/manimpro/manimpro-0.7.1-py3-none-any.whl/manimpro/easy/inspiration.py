#!/usr/bin/env python3
"""
ManimPro Inspiration Gallery - Cool Examples to Motivate Beginners
=================================================================

This module provides an inspiration gallery with amazing examples that show
beginners what's possible with ManimPro, encouraging them to explore and create.

Features:
- Showcase gallery of cool animations
- "Wow factor" examples
- Step-by-step recreations
- Inspiration challenges
- Featured creations

Usage:
    from manimpro.easy.inspiration import InspirationGallery
    
    gallery = InspirationGallery()
    gallery.show_gallery()
    gallery.create_featured_animation("golden_spiral")
"""

from __future__ import annotations

import random
from typing import Dict, List, Any, Optional
from .templates import EasyAnimation
from .. import *

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


class CoolAnimation(EasyAnimation):
    """Base class for cool, inspiring animations."""
    
    def __init__(self, title: str, description: str, difficulty: str, **kwargs):
        super().__init__(title, **kwargs)
        self.description = description
        self.difficulty = difficulty
        self.wow_factor = "⭐⭐⭐"


class GoldenSpiralAnimation(CoolAnimation):
    """Beautiful golden spiral animation - very inspiring!"""
    
    def __init__(self):
        super().__init__(
            "Golden Spiral",
            "Watch the mesmerizing golden ratio spiral unfold!",
            "Intermediate"
        )
        self.wow_factor = "⭐⭐⭐⭐⭐"
        
    def construct(self):
        # Title
        title = Text("The Golden Spiral", font_size=48, color="#FFD700")
        title.to_edge(UP, buff=1)
        self.play(Write(title), run_time=2)
        
        # Golden ratio
        phi_eq = MathTex(r"\phi = \frac{1 + \sqrt{5}}{2} \approx 1.618", color="#FFD700")
        phi_eq.next_to(title, DOWN, buff=1)
        self.play(Write(phi_eq), run_time=2)
        
        # Create golden rectangles and spiral
        rectangles = VGroup()
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]
        
        # Start with a square
        current_rect = Square(side_length=2, color=colors[0], fill_opacity=0.3)
        rectangles.add(current_rect)
        
        self.play(Create(current_rect), run_time=1)
        self.wait(0.5)
        
        # Add more rectangles following golden ratio
        for i in range(1, 6):
            # This creates a visual approximation of the golden spiral
            scale_factor = 0.618 ** i
            new_rect = Rectangle(
                width=2 * scale_factor,
                height=2 * scale_factor * 0.618,
                color=colors[i % len(colors)],
                fill_opacity=0.3
            )
            
            # Position relative to previous rectangle
            if i % 4 == 1:
                new_rect.next_to(current_rect, RIGHT, buff=0)
            elif i % 4 == 2:
                new_rect.next_to(current_rect, DOWN, buff=0)
            elif i % 4 == 3:
                new_rect.next_to(current_rect, LEFT, buff=0)
            else:
                new_rect.next_to(current_rect, UP, buff=0)
                
            rectangles.add(new_rect)
            self.play(Create(new_rect), run_time=0.8)
            current_rect = new_rect
            
        # Add spiral curve
        spiral_points = []
        for t in np.linspace(0, 4*PI, 100):
            r = 0.5 * np.exp(0.2 * t)
            x = r * np.cos(t)
            y = r * np.sin(t)
            spiral_points.append([x, y, 0])
            
        spiral = VMobject()
        spiral.set_points_as_corners(spiral_points)
        spiral.set_color("#FFD700")
        spiral.set_stroke(width=3)
        
        self.play(Create(spiral), run_time=3)
        
        # Final message
        message = Text("Found everywhere in nature!", font_size=32, color="#95E1D3")
        message.to_edge(DOWN, buff=1)
        self.play(Write(message), run_time=1.5)
        
        self.wait(2)


class FourierSeriesAnimation(CoolAnimation):
    """Mind-blowing Fourier series visualization."""
    
    def __init__(self):
        super().__init__(
            "Fourier Magic",
            "See how circles create any wave - pure mathematical magic!",
            "Advanced"
        )
        self.wow_factor = "⭐⭐⭐⭐⭐"
        
    def construct(self):
        # Title
        title = Text("Fourier Series Magic", font_size=48, color="#8B5CF6")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=2)
        
        # Equation
        equation = MathTex(
            r"f(x) = \sum_{n=1}^{\infty} \frac{4}{n\pi} \sin(nx)",
            color="#4ECDC4"
        )
        equation.next_to(title, DOWN, buff=0.5)
        self.play(Write(equation), run_time=2)
        
        # Create axes
        axes = Axes(
            x_range=[-PI, PI, PI/2],
            y_range=[-1.5, 1.5, 0.5],
            axis_config={"color": "#CCCCCC"}
        ).scale(0.7).shift(DOWN*0.5)
        
        self.play(Create(axes), run_time=1)
        
        # Show individual sine waves building up
        colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3", "#DDA0DD"]
        waves = []
        
        for n in range(1, 6):
            wave = axes.plot(
                lambda x: (4/(n*PI)) * np.sin(n*x),
                color=colors[(n-1) % len(colors)],
                stroke_width=2
            )
            waves.append(wave)
            
            # Show each wave
            self.play(Create(wave), run_time=1)
            
            # Show sum so far
            if n > 1:
                sum_wave = axes.plot(
                    lambda x: sum((4/(k*PI)) * np.sin(k*x) for k in range(1, n+1)),
                    color="#FFFFFF",
                    stroke_width=4
                )
                self.play(Create(sum_wave), run_time=1)
                if n < 5:  # Don't remove the final sum
                    self.play(FadeOut(sum_wave), run_time=0.5)
                    
        # Final message
        message = Text("Infinite circles create perfect squares!", 
                      font_size=28, color="#FFE66D")
        message.to_edge(DOWN, buff=0.5)
        self.play(Write(message), run_time=1.5)
        
        self.wait(3)


class DNA3DAnimation(CoolAnimation):
    """Stunning 3D DNA double helix."""
    
    def __init__(self):
        super().__init__(
            "DNA Double Helix",
            "Explore the beautiful structure of life itself!",
            "Advanced"
        )
        self.wow_factor = "⭐⭐⭐⭐⭐"
        
    def construct(self):
        # Set up 3D scene
        self.set_camera_orientation(phi=75 * DEGREES, theta=45 * DEGREES)
        
        # Title
        title = Text("DNA Double Helix", font_size=48, color="#4ECDC4")
        title.to_edge(UP, buff=1)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=2)
        
        # Create DNA helix
        helix1_points = []
        helix2_points = []
        base_pairs = []
        
        for t in np.linspace(0, 4*PI, 100):
            # First helix
            x1 = 2 * np.cos(t)
            y1 = 2 * np.sin(t)
            z1 = t * 0.5
            helix1_points.append([x1, y1, z1])
            
            # Second helix (opposite phase)
            x2 = 2 * np.cos(t + PI)
            y2 = 2 * np.sin(t + PI)
            z2 = t * 0.5
            helix2_points.append([x2, y2, z2])
            
            # Base pairs (every few points)
            if int(t * 10) % 8 == 0:
                base_pair = Line3D(
                    start=[x1, y1, z1],
                    end=[x2, y2, z2],
                    color="#FFE66D",
                    stroke_width=3
                )
                base_pairs.append(base_pair)
        
        # Create helix curves
        helix1 = VMobject()
        helix1.set_points_as_corners(helix1_points)
        helix1.set_color("#FF6B6B")
        helix1.set_stroke(width=4)
        
        helix2 = VMobject()
        helix2.set_points_as_corners(helix2_points)
        helix2.set_color("#4ECDC4")
        helix2.set_stroke(width=4)
        
        # Animate creation
        self.play(Create(helix1), run_time=3)
        self.play(Create(helix2), run_time=3)
        
        # Add base pairs
        for base_pair in base_pairs[::2]:  # Every other one
            self.play(Create(base_pair), run_time=0.2)
            
        # Rotate the DNA
        self.begin_ambient_camera_rotation(rate=0.3)
        
        # Information
        info = Text("The blueprint of life!", font_size=32, color="#95E1D3")
        info.to_edge(DOWN, buff=1)
        self.add_fixed_in_frame_mobjects(info)
        self.play(Write(info), run_time=1.5)
        
        self.wait(4)
        self.stop_ambient_camera_rotation()


class FractalTreeAnimation(CoolAnimation):
    """Beautiful recursive fractal tree."""
    
    def __init__(self):
        super().__init__(
            "Fractal Tree",
            "Watch nature's patterns emerge through recursion!",
            "Intermediate"
        )
        self.wow_factor = "⭐⭐⭐⭐"
        
    def construct(self):
        # Title
        title = Text("Fractal Tree", font_size=48, color="#2ECC71")
        title.to_edge(UP, buff=1)
        self.play(Write(title), run_time=2)
        
        def create_tree(start_point, angle, length, depth, color_intensity=1.0):
            """Recursively create tree branches."""
            if depth == 0 or length < 0.1:
                return VGroup()
                
            # Calculate end point
            end_point = start_point + length * np.array([
                np.cos(angle), np.sin(angle), 0
            ])
            
            # Create branch
            branch_color = interpolate_color("#8B4513", "#2ECC71", color_intensity)
            branch = Line(start_point, end_point, color=branch_color, stroke_width=depth+1)
            
            # Create sub-branches
            left_tree = create_tree(
                end_point, angle + PI/6, length * 0.7, depth - 1, color_intensity * 0.9
            )
            right_tree = create_tree(
                end_point, angle - PI/6, length * 0.7, depth - 1, color_intensity * 0.9
            )
            
            return VGroup(branch, left_tree, right_tree)
        
        # Create the tree
        tree = create_tree(
            start_point=np.array([0, -3, 0]),
            angle=PI/2,
            length=2,
            depth=6
        )
        
        # Animate tree growth
        self.play(Create(tree), run_time=4)
        
        # Add leaves (small circles at the tips)
        leaves = VGroup()
        for branch in tree.submobjects:
            if isinstance(branch, Line) and len(branch.get_start()) > 0:
                # Add leaf at end of small branches
                if np.linalg.norm(branch.get_end() - branch.get_start()) < 0.5:
                    leaf = Circle(radius=0.05, color="#2ECC71", fill_opacity=0.8)
                    leaf.move_to(branch.get_end())
                    leaves.add(leaf)
        
        self.play(Create(leaves), run_time=2)
        
        # Message
        message = Text("Mathematics creates natural beauty!", 
                      font_size=32, color="#27AE60")
        message.to_edge(DOWN, buff=1)
        self.play(Write(message), run_time=1.5)
        
        self.wait(2)


class InspirationGallery:
    """Gallery of inspiring animations to motivate beginners."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        
        # Gallery of cool animations
        self.featured_animations = {
            "golden_spiral": {
                "class": GoldenSpiralAnimation,
                "title": "Golden Spiral",
                "description": "The mesmerizing golden ratio spiral found everywhere in nature",
                "difficulty": "Intermediate",
                "wow_factor": "⭐⭐⭐⭐⭐",
                "category": "Mathematics",
                "time_to_create": "10 minutes",
                "skills_learned": ["Mathematical constants", "Geometric sequences", "Spiral curves"]
            },
            "fourier_magic": {
                "class": FourierSeriesAnimation,
                "title": "Fourier Magic",
                "description": "See how circles create any wave - pure mathematical magic!",
                "difficulty": "Advanced",
                "wow_factor": "⭐⭐⭐⭐⭐",
                "category": "Signal Processing",
                "time_to_create": "15 minutes",
                "skills_learned": ["Fourier series", "Wave functions", "Infinite sums"]
            },
            "dna_helix": {
                "class": DNA3DAnimation,
                "title": "DNA Double Helix",
                "description": "Explore the beautiful 3D structure of life itself!",
                "difficulty": "Advanced",
                "wow_factor": "⭐⭐⭐⭐⭐",
                "category": "Biology",
                "time_to_create": "20 minutes",
                "skills_learned": ["3D animation", "Parametric curves", "Biological structures"]
            },
            "fractal_tree": {
                "class": FractalTreeAnimation,
                "title": "Fractal Tree",
                "description": "Watch nature's patterns emerge through recursion!",
                "difficulty": "Intermediate",
                "wow_factor": "⭐⭐⭐⭐",
                "category": "Fractals",
                "time_to_create": "12 minutes",
                "skills_learned": ["Recursion", "Fractals", "Natural patterns"]
            }
        }
        
        # Motivational quotes
        self.inspiration_quotes = [
            "Every expert was once a beginner! 🌟",
            "Your next animation could be your masterpiece! 🎨",
            "Mathematics is the art of the infinite! ∞",
            "Creativity is intelligence having fun! 🧠",
            "The best way to learn is by doing! 🚀",
            "Every animation tells a story! 📖",
            "You're capable of creating amazing things! ⭐",
            "Practice makes progress, not perfection! 💪"
        ]
        
    def show_gallery(self):
        """Display the inspiration gallery."""
        if self.console:
            self.console.print("\n🎨 ManimPro Inspiration Gallery 🎨", style="bold magenta")
            self.console.print("Discover what's possible with ManimPro!\n")
            
            # Show featured animations
            panels = []
            for anim_id, info in self.featured_animations.items():
                content = f"""
{info['wow_factor']} {info['title']}

{info['description']}

📊 Difficulty: {info['difficulty']}
🏷️ Category: {info['category']}
⏱️ Time: {info['time_to_create']}

Skills you'll learn:
{chr(10).join(f"• {skill}" for skill in info['skills_learned'])}

Try it: manimpro wizard inspiration --create {anim_id}
                """
                
                panel = Panel(
                    content.strip(),
                    title=f"✨ {info['title']}",
                    border_style="magenta",
                    padding=(1, 2)
                )
                panels.append(panel)
                
            # Display in columns
            self.console.print(Columns(panels, equal=True, expand=True))
            
            # Motivational quote
            quote = random.choice(self.inspiration_quotes)
            quote_panel = Panel(
                quote,
                title="💫 Daily Inspiration",
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(quote_panel)
            
        else:
            print("\n🎨 ManimPro Inspiration Gallery 🎨")
            print("Discover what's possible with ManimPro!")
            print()
            
            for anim_id, info in self.featured_animations.items():
                print(f"{info['wow_factor']} {info['title']}")
                print(f"   {info['description']}")
                print(f"   Difficulty: {info['difficulty']} | Time: {info['time_to_create']}")
                print(f"   Try it: manimpro wizard inspiration --create {anim_id}")
                print()
                
            # Random quote
            print(f"💫 {random.choice(self.inspiration_quotes)}")
            print()
            
    def create_featured_animation(self, animation_id: str) -> Optional[CoolAnimation]:
        """Create a featured animation by ID."""
        if animation_id not in self.featured_animations:
            if self.console:
                self.console.print(f"[red]Animation '{animation_id}' not found![/red]")
                self.console.print(f"Available: {', '.join(self.featured_animations.keys())}")
            else:
                print(f"Animation '{animation_id}' not found!")
                print(f"Available: {', '.join(self.featured_animations.keys())}")
            return None
            
        info = self.featured_animations[animation_id]
        animation_class = info["class"]
        
        if self.console:
            self.console.print(f"[green]✨ Creating {info['title']}...[/green]")
            self.console.print(f"[yellow]This {info['difficulty'].lower()} animation will take about {info['time_to_create']}[/yellow]")
        else:
            print(f"✨ Creating {info['title']}...")
            print(f"This {info['difficulty'].lower()} animation will take about {info['time_to_create']}")
            
        return animation_class()
        
    def get_random_inspiration(self) -> str:
        """Get a random inspirational message."""
        return random.choice(self.inspiration_quotes)
        
    def suggest_next_challenge(self, current_level: str = "beginner") -> Dict[str, Any]:
        """Suggest next challenge based on current level."""
        if current_level.lower() == "beginner":
            suggestions = [anim for anim in self.featured_animations.values() 
                          if anim["difficulty"] == "Intermediate"]
        elif current_level.lower() == "intermediate":
            suggestions = [anim for anim in self.featured_animations.values() 
                          if anim["difficulty"] == "Advanced"]
        else:
            suggestions = list(self.featured_animations.values())
            
        if suggestions:
            return random.choice(suggestions)
        else:
            return random.choice(list(self.featured_animations.values()))


# Convenience functions
def show_inspiration_gallery():
    """Show the inspiration gallery."""
    gallery = InspirationGallery()
    gallery.show_gallery()


def get_daily_inspiration() -> str:
    """Get daily inspirational quote."""
    gallery = InspirationGallery()
    return gallery.get_random_inspiration()


if __name__ == "__main__":
    # Demo the inspiration gallery
    gallery = InspirationGallery()
    gallery.show_gallery()
