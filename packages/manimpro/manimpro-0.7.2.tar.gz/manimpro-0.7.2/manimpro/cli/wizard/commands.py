"""
ManimPro CLI Wizard Commands - Clean Version
============================================

Command-line interface for the ManimPro animation wizard and beginner tools.
Provides easy-to-use commands for creating animations without coding.
"""

from __future__ import annotations

import click
import cloup
from pathlib import Path

from ...easy.wizard import start_wizard
from ...easy.examples import list_examples, get_example_code, create_tutorial_series, EXAMPLE_LIBRARY
from ...easy.presets import list_presets, PRESET_LIBRARY
from ...easy.achievements import get_achievement_tracker, show_progress as show_achievements, show_next_goals
from ...easy.inspiration import InspirationGallery, show_inspiration_gallery
from ...easy.challenges import ChallengeManager, show_daily_challenge, show_all_challenges, start_challenge
from ...easy.progress import get_progress_tracker, show_progress as show_progress_dashboard, show_weekly_summary
from ... import console


@cloup.group(
    name="wizard",
    help="Interactive tools for beginners to create animations easily",
    invoke_without_command=True,
)
@click.pass_context
def wizard_group(ctx):
    """ManimPro beginner-friendly tools and wizards."""
    if ctx.invoked_subcommand is None:
        # If no subcommand is provided, start the wizard
        try:
            console.print("[green]🧙 Starting ManimPro Animation Wizard...[/green]")
            start_wizard()
            
            # Unlock achievement for using wizard
            achievement_tracker = get_achievement_tracker()
            achievement_tracker.unlock_achievement("first_wizard")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Wizard cancelled.[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Error starting wizard: {e}[/red]")


@wizard_group.command(
    name="create",
    help="Interactive wizard to create animations step-by-step",
)
def create_wizard():
    """
    Launch the interactive animation creation wizard.
    
    This wizard guides you through creating animations with simple questions.
    No coding experience required!
    
    Example:
        manimpro wizard create
    """
    try:
        console.print("[green]🧙 Starting ManimPro Animation Wizard...[/green]")
        start_wizard()
        
        # Unlock achievement for using wizard
        achievement_tracker = get_achievement_tracker()
        achievement_tracker.unlock_achievement("first_wizard")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Wizard cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error starting wizard: {e}[/red]")


@wizard_group.command(
    name="examples",
    help="List available beginner examples",
)
@cloup.option(
    "--level",
    type=click.Choice(["beginner", "intermediate", "advanced", "all"]),
    default="all",
    help="Filter examples by difficulty level",
)
@cloup.option(
    "--copy",
    type=str,
    help="Copy example code to file (e.g., --copy hello)",
)
def list_examples_command(level: str, copy: str):
    """
    List available beginner-friendly examples.
    
    Examples are organized by difficulty level:
    - Beginner: Simple animations with basic concepts
    - Intermediate: More complex animations with multiple elements
    - Advanced: Complex animations combining many features
    
    Examples:
        manimpro wizard examples
        manimpro wizard examples --level beginner
        manimpro wizard examples --copy hello
    """
    if copy:
        if copy not in EXAMPLE_LIBRARY:
            console.print(f"[red]❌ Example '{copy}' not found.[/red]")
            console.print(f"Available examples: {', '.join(EXAMPLE_LIBRARY.keys())}")
            return
            
        filename = f"{copy}_example.py"
        code = get_example_code(copy)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            console.print(f"[green]✅ Example copied to: {filename}[/green]")
            console.print(f"[blue]🚀 To render: manimpro -p -ql {filename} {EXAMPLE_LIBRARY[copy]['class'].__name__}[/blue]")
            
            # Unlock achievement for using examples
            achievement_tracker = get_achievement_tracker()
            achievement_tracker.unlock_achievement("first_example")
            
        except Exception as e:
            console.print(f"[red]❌ Error copying example: {e}[/red]")
    else:
        console.print("[green]📚 ManimPro Examples[/green]")
        
        if level != "all":
            filtered_examples = {k: v for k, v in EXAMPLE_LIBRARY.items() 
                               if v["level"].lower() == level}
            if not filtered_examples:
                console.print(f"[yellow]No examples found for level: {level}[/yellow]")
                return
        else:
            filtered_examples = EXAMPLE_LIBRARY
            
        # Group by level
        levels = {"Beginner": [], "Intermediate": [], "Advanced": []}
        
        for name, info in filtered_examples.items():
            levels[info["level"]].append((name, info))
        
        for level_name, examples in levels.items():
            if not examples:
                continue
                
            console.print(f"\n[bold blue]📖 {level_name.upper()} LEVEL[/bold blue]")
            
            for name, info in examples:
                console.print(f"  [cyan]🎯 {name}[/cyan]")
                console.print(f"     {info['description']}")
                console.print(f"     [dim]Concepts: {', '.join(info['concepts'])}[/dim]")
                console.print(f"     [dim]Class: {info['class'].__name__}[/dim]")
                console.print()
        
        console.print("[yellow]💡 Usage:[/yellow]")
        console.print("  manimpro wizard examples --copy <example_name>")
        console.print("  manimpro -p -ql example_file.py ExampleClassName")


@wizard_group.command(
    name="presets",
    help="List available animation presets",
)
@cloup.option(
    "--create",
    type=str,
    help="Create animation from preset (e.g., --create intro)",
)
@cloup.option(
    "--title",
    type=str,
    default="My Animation",
    help="Title for created animation",
)
def list_presets_command(create: str, title: str):
    """
    List available animation presets or create one.
    
    Presets are one-line animation creators for common patterns.
    
    Examples:
        manimpro wizard presets
        manimpro wizard presets --create intro --title "My Channel"
    """
    if create:
        if create not in PRESET_LIBRARY:
            console.print(f"[red]❌ Preset '{create}' not found.[/red]")
            console.print(f"Available presets: {', '.join(PRESET_LIBRARY.keys())}")
            return
            
        filename = f"{create}_preset.py"
        preset_info = PRESET_LIBRARY[create]
        
        # Generate code using the preset
        code = f'''#!/usr/bin/env python3
"""
ManimPro Preset: {create.title()}
{preset_info["description"]}
Generated by ManimPro Wizard
"""

from manimpro.easy.presets import {preset_info["function"].__name__}

class {create.title()}Preset:
    def __init__(self):
        # Create animation using preset
        self.animation = {preset_info["example"]}
        
    def construct(self):
        # This will be called by ManimPro
        return self.animation.construct()

# To render: manimpro -p -ql {filename} {create.title()}Preset

if __name__ == "__main__":
    print("🎬 Preset animation ready!")
    print("Run: manimpro -p -ql {filename} {create.title()}Preset")
'''
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            console.print(f"[green]✅ Preset created: {filename}[/green]")
            console.print(f"[blue]🚀 To render: manimpro -p -ql {filename} {create.title()}Preset[/blue]")
            
            # Unlock achievement for using presets
            achievement_tracker = get_achievement_tracker()
            achievement_tracker.unlock_achievement("first_preset")
            
        except Exception as e:
            console.print(f"[red]❌ Error creating preset: {e}[/red]")
    else:
        console.print("[green]🎨 ManimPro Animation Presets[/green]")
        
        for name, info in PRESET_LIBRARY.items():
            console.print(f"\n[cyan]📋 {name.upper()}[/cyan]")
            console.print(f"   {info['description']}")
            console.print(f"   [dim]Example: {info['example']}[/dim]")
        
        console.print(f"\n[yellow]✨ Total presets: {len(PRESET_LIBRARY)}[/yellow]")
        console.print("\n[yellow]💡 Usage:[/yellow]")
        console.print("  manimpro wizard presets --create <preset_name>")
        console.print("  manimpro -p -ql preset_file.py PresetClassName")


@wizard_group.command(
    name="tutorial",
    help="Create complete tutorial series",
)
@cloup.option(
    "--create",
    is_flag=True,
    help="Create all tutorial files",
)
def tutorial_command(create: bool):
    """
    Create a complete ManimPro tutorial series.
    
    This creates 6 tutorial files with progressive difficulty.
    
    Example:
        manimpro wizard tutorial --create
    """
    if create:
        try:
            console.print("[green]📚 Creating ManimPro Tutorial Series...[/green]")
            create_tutorial_series()
            console.print("[green]🎉 Tutorial series created successfully![/green]")
            console.print("\n[blue]🚀 Start with:[/blue]")
            console.print("  manimpro -p -ql tutorial_01_hello.py Tutorial01_HelloWorld")
        except Exception as e:
            console.print(f"[red]❌ Error creating tutorials: {e}[/red]")
    else:
        console.print("[green]📖 ManimPro Tutorial Series[/green]")
        console.print("\nProgressive tutorials for learning ManimPro:")
        
        tutorials = [
            ("Tutorial 1", "Hello World", "Your very first animation"),
            ("Tutorial 2", "Equations", "Adding mathematical equations"),
            ("Tutorial 3", "Shapes", "Working with shapes and transformations"),
            ("Tutorial 4", "Graphs", "Creating function graphs"),
            ("Tutorial 5", "Proofs", "Mathematical proofs and geometry"),
            ("Tutorial 6", "Advanced", "Combining multiple elements"),
        ]
        
        for num, title, desc in tutorials:
            console.print(f"  [cyan]{num}[/cyan]: [yellow]{title}[/yellow] - {desc}")
        
        console.print("\n[yellow]💡 Create all tutorials:[/yellow]")
        console.print("  manimpro wizard tutorial --create")


@wizard_group.command(
    name="achievements",
    help="View your achievements and progress",
)
@cloup.option(
    "--goals",
    is_flag=True,
    help="Show next achievement goals",
)
def achievements_command(goals: bool):
    """
    View your achievements, badges, and overall progress.
    
    Examples:
        manimpro wizard achievements
        manimpro wizard achievements --goals
    """
    try:
        if goals:
            console.print("[green]🎯 Your Next Achievement Goals[/green]")
            show_next_goals()
        else:
            console.print("[green]🏆 Your ManimPro Achievements[/green]")
            show_achievements()
    except Exception as e:
        console.print(f"[red]❌ Error showing achievements: {e}[/red]")


@wizard_group.command(
    name="inspiration",
    help="Browse inspiring animations and cool examples",
)
@cloup.option(
    "--create",
    type=str,
    help="Create a featured animation (e.g., --create golden_spiral)",
)
def inspiration_command(create: str):
    """
    Browse the inspiration gallery with amazing examples.
    
    Examples:
        manimpro wizard inspiration
        manimpro wizard inspiration --create golden_spiral
    """
    try:
        gallery = InspirationGallery()
        
        if create:
            animation = gallery.create_featured_animation(create)
            if animation:
                filename = f"{create}_inspiration.py"
                
                # Generate code for the animation
                code = f'''#!/usr/bin/env python3
"""
{animation.title} - Inspiration Animation
{animation.description}
Created with ManimPro Inspiration Gallery
"""

from manimpro.easy.inspiration import {animation.__class__.__name__}

# To render: manimpro -p -ql {filename} {animation.__class__.__name__}

if __name__ == "__main__":
    print("🎨 Inspiration animation ready!")
    print("Run: manimpro -p -ql {filename} {animation.__class__.__name__}")
'''
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    console.print(f"[green]✨ Inspiration animation created: {filename}[/green]")
                    console.print(f"[blue]🚀 To render: manimpro -p -ql {filename} {animation.__class__.__name__}[/blue]")
                except Exception as e:
                    console.print(f"[red]❌ Error creating file: {e}[/red]")
        else:
            console.print("[green]🎨 ManimPro Inspiration Gallery[/green]")
            gallery.show_gallery()
            
    except Exception as e:
        console.print(f"[red]❌ Error showing inspiration: {e}[/red]")


@wizard_group.command(
    name="challenges",
    help="View and start fun animation challenges",
)
@cloup.option(
    "--daily",
    is_flag=True,
    help="Show today's daily challenge",
)
@cloup.option(
    "--start",
    type=str,
    help="Start a specific challenge (e.g., --start color_master)",
)
@cloup.option(
    "--category",
    type=str,
    help="Filter challenges by category",
)
def challenges_command(daily: bool, start: str, category: str):
    """
    View and participate in fun animation challenges.
    
    Examples:
        manimpro wizard challenges --daily
        manimpro wizard challenges --start color_master
    """
    try:
        manager = ChallengeManager()
        
        if daily:
            console.print("[green]📅 Today's Daily Challenge[/green]")
            manager.show_daily_challenge()
        elif start:
            console.print(f"[green]🚀 Starting Challenge: {start}[/green]")
            success = manager.start_challenge(start)
            if success:
                # Record challenge attempt in progress
                tracker = get_progress_tracker()
                tracker.record_animation_created(
                    f"Challenge: {start}", 
                    "challenge", 
                    "intermediate", 
                    source="challenge"
                )
        else:
            console.print("[green]🏆 ManimPro Animation Challenges[/green]")
            manager.show_all_challenges(category)
            
    except Exception as e:
        console.print(f"[red]❌ Error with challenges: {e}[/red]")


@wizard_group.command(
    name="progress",
    help="View your learning progress and statistics",
)
@cloup.option(
    "--weekly",
    is_flag=True,
    help="Show weekly progress summary",
)
def progress_command(weekly: bool):
    """
    View your learning progress, statistics, and milestones.
    
    Examples:
        manimpro wizard progress
        manimpro wizard progress --weekly
    """
    try:
        if weekly:
            console.print("[green]📅 Weekly Progress Summary[/green]")
            show_weekly_summary()
        else:
            console.print("[green]📊 Your Progress Dashboard[/green]")
            show_progress_dashboard()
            
    except Exception as e:
        console.print(f"[red]❌ Error showing progress: {e}[/red]")


@wizard_group.command(
    name="dashboard",
    help="Show complete beginner dashboard with all features",
)
def dashboard_command():
    """
    Show the complete ManimPro beginner dashboard.
    
    Example:
        manimpro wizard dashboard
    """
    try:
        console.print("\n🎬 ManimPro Beginner Dashboard 🎬", style="bold blue")
        console.print("Your complete animation learning hub!\n")
        
        # Quick stats
        tracker = get_progress_tracker()
        achievement_tracker = get_achievement_tracker()
        
        stats = tracker._get_overview_stats()
        
        # Overview panel
        from rich.panel import Panel
        
        overview_text = f"""
🎬 Total Animations: {stats['total_animations']}
🏆 Achievements: {stats['milestones_achieved']}
🔥 Current Streak: {stats['current_streak']} days
🎨 Categories: {stats['categories_explored']}
        """
        
        overview_panel = Panel(
            overview_text.strip(),
            title="📊 Quick Stats",
            border_style="blue"
        )
        console.print(overview_panel)
        
        # Daily challenge
        console.print("\n[bold yellow]📅 Today's Challenge[/bold yellow]")
        manager = ChallengeManager()
        challenge = manager.get_daily_challenge()
        
        challenge_text = f"""
{challenge.emoji} {challenge.title}
{challenge.description}
Difficulty: {challenge.difficulty} | Time: {challenge.estimated_time}
        """
        
        challenge_panel = Panel(
            challenge_text.strip(),
            border_style="yellow"
        )
        console.print(challenge_panel)
        
        # Inspiration quote
        gallery = InspirationGallery()
        quote = gallery.get_random_inspiration()
        
        inspiration_panel = Panel(
            quote,
            title="💫 Daily Inspiration",
            border_style="magenta"
        )
        console.print(inspiration_panel)
        
        # Quick actions
        console.print("\n[bold green]🚀 Quick Actions[/bold green]")
        console.print("• [cyan]manimpro wizard[/cyan] - Create new animation")
        console.print("• [cyan]manimpro wizard challenges --daily[/cyan] - Start today's challenge")
        console.print("• [cyan]manimpro wizard examples[/cyan] - Browse examples")
        console.print("• [cyan]manimpro wizard inspiration[/cyan] - Get inspired")
        console.print("• [cyan]manimpro preview[/cyan] - View your animations")
        
    except Exception as e:
        console.print(f"[red]❌ Error showing dashboard: {e}[/red]")
