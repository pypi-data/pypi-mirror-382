#!/usr/bin/env python3
"""
ManimPro Achievement System - Encouraging Beginners with Badges & Progress
=========================================================================

This module provides an achievement and badge system that encourages beginners
by celebrating their progress and milestones in learning animation creation.

Features:
- Achievement tracking
- Badge collection system
- Progress celebration
- Motivational messages
- Milestone rewards

Usage:
    from manimpro.easy.achievements import AchievementTracker
    
    tracker = AchievementTracker()
    tracker.unlock_achievement("first_animation")
    tracker.show_progress()
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.progress import Progress, BarColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


@dataclass
class Achievement:
    """Represents a single achievement."""
    id: str
    name: str
    description: str
    emoji: str
    category: str
    points: int
    unlocked: bool = False
    unlock_date: Optional[str] = None
    
    def unlock(self):
        """Unlock this achievement."""
        self.unlocked = True
        self.unlock_date = datetime.now().isoformat()


class AchievementTracker:
    """Tracks user achievements and progress."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.achievements_file = Path.home() / ".manimpro" / "achievements.json"
        self.achievements_file.parent.mkdir(exist_ok=True)
        
        # Define all available achievements
        self.all_achievements = {
            # First Steps
            "first_animation": Achievement(
                "first_animation", "First Animation", 
                "Created your very first animation!", "🎬", "First Steps", 10
            ),
            "first_wizard": Achievement(
                "first_wizard", "Wizard Master", 
                "Used the animation wizard for the first time!", "🧙‍♂️", "First Steps", 10
            ),
            "first_example": Achievement(
                "first_example", "Example Explorer", 
                "Copied and ran your first example!", "📚", "First Steps", 10
            ),
            "first_preset": Achievement(
                "first_preset", "Preset Pro", 
                "Created animation using a preset!", "⚡", "First Steps", 10
            ),
            
            # Learning Milestones
            "equation_master": Achievement(
                "equation_master", "Equation Master", 
                "Created 5 animations with mathematical equations!", "🧮", "Learning", 25
            ),
            "shape_shifter": Achievement(
                "shape_shifter", "Shape Shifter", 
                "Created 3 shape transformation animations!", "🔄", "Learning", 20
            ),
            "graph_guru": Achievement(
                "graph_guru", "Graph Guru", 
                "Created 3 function graph animations!", "📊", "Learning", 20
            ),
            "proof_pioneer": Achievement(
                "proof_pioneer", "Proof Pioneer", 
                "Created your first mathematical proof animation!", "🔺", "Learning", 30
            ),
            
            # Creativity & Exploration
            "creative_genius": Achievement(
                "creative_genius", "Creative Genius", 
                "Created 10 different animations!", "🎨", "Creativity", 50
            ),
            "tutorial_graduate": Achievement(
                "tutorial_graduate", "Tutorial Graduate", 
                "Completed all 6 tutorial lessons!", "🎓", "Learning", 40
            ),
            "preview_master": Achievement(
                "preview_master", "Preview Master", 
                "Used the web preview 5 times!", "🌐", "Tools", 15
            ),
            
            # Advanced Achievements
            "animation_architect": Achievement(
                "animation_architect", "Animation Architect", 
                "Created 25 animations - you're becoming an expert!", "🏗️", "Mastery", 100
            ),
            "math_visualizer": Achievement(
                "math_visualizer", "Math Visualizer", 
                "Created animations in all categories!", "🌟", "Mastery", 75
            ),
            "community_contributor": Achievement(
                "community_contributor", "Community Contributor", 
                "Shared your first animation!", "🤝", "Community", 30
            ),
            
            # Special Achievements
            "speed_demon": Achievement(
                "speed_demon", "Speed Demon", 
                "Created an animation in under 1 minute!", "⚡", "Special", 20
            ),
            "night_owl": Achievement(
                "night_owl", "Night Owl", 
                "Created an animation after midnight!", "🦉", "Special", 15
            ),
            "early_bird": Achievement(
                "early_bird", "Early Bird", 
                "Created an animation before 6 AM!", "🐦", "Special", 15
            ),
            "weekend_warrior": Achievement(
                "weekend_warrior", "Weekend Warrior", 
                "Created animations on both Saturday and Sunday!", "⚔️", "Special", 25
            )
        }
        
        # Load existing progress
        self.load_progress()
        
    def load_progress(self):
        """Load achievement progress from file."""
        if self.achievements_file.exists():
            try:
                with open(self.achievements_file, 'r') as f:
                    data = json.load(f)
                    
                # Update achievements with saved progress
                for achievement_id, achievement_data in data.get('achievements', {}).items():
                    if achievement_id in self.all_achievements:
                        achievement = self.all_achievements[achievement_id]
                        achievement.unlocked = achievement_data.get('unlocked', False)
                        achievement.unlock_date = achievement_data.get('unlock_date')
                        
            except (json.JSONDecodeError, KeyError):
                # If file is corrupted, start fresh
                pass
                
    def save_progress(self):
        """Save achievement progress to file."""
        data = {
            'achievements': {
                aid: asdict(achievement) for aid, achievement in self.all_achievements.items()
            },
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.achievements_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Fail silently if we can't save
            pass
            
    def unlock_achievement(self, achievement_id: str, show_celebration: bool = True) -> bool:
        """
        Unlock an achievement and show celebration.
        
        Args:
            achievement_id: ID of achievement to unlock
            show_celebration: Whether to show celebration message
            
        Returns:
            True if achievement was newly unlocked, False if already unlocked
        """
        if achievement_id not in self.all_achievements:
            return False
            
        achievement = self.all_achievements[achievement_id]
        
        if achievement.unlocked:
            return False  # Already unlocked
            
        # Unlock the achievement
        achievement.unlock()
        self.save_progress()
        
        if show_celebration:
            self.celebrate_achievement(achievement)
            
        return True
        
    def celebrate_achievement(self, achievement: Achievement):
        """Show celebration for unlocked achievement."""
        if self.console:
            # Rich celebration
            celebration_text = f"""
🎉 ACHIEVEMENT UNLOCKED! 🎉

{achievement.emoji} {achievement.name}

{achievement.description}

Category: {achievement.category}
Points: +{achievement.points}

Keep up the amazing work!
            """
            
            panel = Panel(
                celebration_text,
                title="🏆 NEW ACHIEVEMENT 🏆",
                border_style="gold",
                padding=(1, 2)
            )
            
            self.console.print()
            self.console.print(panel)
            self.console.print()
        else:
            # Simple text celebration
            print(f"\n🎉 ACHIEVEMENT UNLOCKED! 🎉")
            print(f"{achievement.emoji} {achievement.name}")
            print(f"{achievement.description}")
            print(f"Points: +{achievement.points}")
            print()
            
    def get_progress_stats(self) -> Dict[str, Any]:
        """Get overall progress statistics."""
        unlocked = [a for a in self.all_achievements.values() if a.unlocked]
        total = len(self.all_achievements)
        
        total_points = sum(a.points for a in unlocked)
        max_points = sum(a.points for a in self.all_achievements.values())
        
        categories = {}
        for achievement in self.all_achievements.values():
            if achievement.category not in categories:
                categories[achievement.category] = {'total': 0, 'unlocked': 0}
            categories[achievement.category]['total'] += 1
            if achievement.unlocked:
                categories[achievement.category]['unlocked'] += 1
                
        return {
            'unlocked_count': len(unlocked),
            'total_count': total,
            'completion_percentage': (len(unlocked) / total) * 100,
            'total_points': total_points,
            'max_points': max_points,
            'categories': categories,
            'recent_achievements': sorted(unlocked, key=lambda a: a.unlock_date or '', reverse=True)[:3]
        }
        
    def show_progress(self):
        """Display current progress and achievements."""
        stats = self.get_progress_stats()
        
        if self.console:
            # Rich progress display
            self.console.print("\n🏆 Your ManimPro Journey 🏆", style="bold blue")
            
            # Overall progress
            progress_text = f"""
📊 Overall Progress: {stats['unlocked_count']}/{stats['total_count']} ({stats['completion_percentage']:.1f}%)
🎯 Points Earned: {stats['total_points']}/{stats['max_points']}
            """
            
            panel = Panel(progress_text, title="Progress Summary", border_style="blue")
            self.console.print(panel)
            
            # Category breakdown
            table = Table(title="Progress by Category")
            table.add_column("Category", style="cyan")
            table.add_column("Progress", style="yellow")
            table.add_column("Completion", style="green")
            
            for category, data in stats['categories'].items():
                progress = f"{data['unlocked']}/{data['total']}"
                percentage = f"{(data['unlocked']/data['total'])*100:.0f}%"
                table.add_row(category, progress, percentage)
                
            self.console.print(table)
            
            # Recent achievements
            if stats['recent_achievements']:
                self.console.print("\n🌟 Recent Achievements:", style="bold green")
                for achievement in stats['recent_achievements']:
                    self.console.print(f"  {achievement.emoji} {achievement.name}")
                    
            # Motivational message
            self.show_motivational_message(stats)
            
        else:
            # Simple text display
            print(f"\n🏆 Your ManimPro Journey 🏆")
            print(f"Progress: {stats['unlocked_count']}/{stats['total_count']} ({stats['completion_percentage']:.1f}%)")
            print(f"Points: {stats['total_points']}/{stats['max_points']}")
            
            print(f"\nProgress by Category:")
            for category, data in stats['categories'].items():
                print(f"  {category}: {data['unlocked']}/{data['total']}")
                
    def show_motivational_message(self, stats: Dict[str, Any]):
        """Show personalized motivational message."""
        completion = stats['completion_percentage']
        
        if completion == 0:
            message = "🌟 Welcome to ManimPro! Your animation journey starts here. Try creating your first animation!"
        elif completion < 25:
            message = "🚀 Great start! You're building momentum. Keep exploring and creating!"
        elif completion < 50:
            message = "🎯 You're making excellent progress! You're becoming a real animation creator!"
        elif completion < 75:
            message = "🔥 Wow! You're really getting the hang of this. Your skills are impressive!"
        elif completion < 100:
            message = "⭐ Amazing work! You're almost a ManimPro master. Just a few more achievements to go!"
        else:
            message = "🏆 CONGRATULATIONS! You've mastered ManimPro! You're now an animation expert!"
            
        if self.console:
            motivational_panel = Panel(
                message,
                title="💪 Keep Going!",
                border_style="green",
                padding=(1, 2)
            )
            self.console.print(motivational_panel)
        else:
            print(f"\n💪 {message}")
            
    def get_next_achievements(self, limit: int = 3) -> List[Achievement]:
        """Get suggested next achievements to work towards."""
        unlocked = [a for a in self.all_achievements.values() if not a.unlocked]
        
        # Sort by points (easier achievements first)
        unlocked.sort(key=lambda a: a.points)
        
        return unlocked[:limit]
        
    def show_next_goals(self):
        """Show suggested next achievements."""
        next_achievements = self.get_next_achievements()
        
        if not next_achievements:
            if self.console:
                self.console.print("🎉 You've unlocked all achievements! You're a ManimPro master!", style="bold gold")
            else:
                print("🎉 You've unlocked all achievements! You're a ManimPro master!")
            return
            
        if self.console:
            self.console.print("\n🎯 Next Goals:", style="bold yellow")
            
            for achievement in next_achievements:
                goal_text = f"{achievement.emoji} {achievement.name}\n{achievement.description}\nReward: {achievement.points} points"
                panel = Panel(goal_text, border_style="yellow", padding=(0, 1))
                self.console.print(panel)
        else:
            print("\n🎯 Next Goals:")
            for achievement in next_achievements:
                print(f"  {achievement.emoji} {achievement.name}")
                print(f"    {achievement.description}")
                print(f"    Reward: {achievement.points} points")
                print()


# Global achievement tracker instance
_achievement_tracker = None

def get_achievement_tracker() -> AchievementTracker:
    """Get the global achievement tracker instance."""
    global _achievement_tracker
    if _achievement_tracker is None:
        _achievement_tracker = AchievementTracker()
    return _achievement_tracker


def unlock_achievement(achievement_id: str, show_celebration: bool = True) -> bool:
    """Convenience function to unlock an achievement."""
    return get_achievement_tracker().unlock_achievement(achievement_id, show_celebration)


def show_progress():
    """Convenience function to show progress."""
    get_achievement_tracker().show_progress()


def show_next_goals():
    """Convenience function to show next goals."""
    get_achievement_tracker().show_next_goals()


if __name__ == "__main__":
    # Demo the achievement system
    tracker = AchievementTracker()
    
    print("🏆 ManimPro Achievement System Demo")
    print("=" * 40)
    
    # Unlock some achievements for demo
    tracker.unlock_achievement("first_animation")
    tracker.unlock_achievement("first_wizard")
    tracker.unlock_achievement("equation_master")
    
    # Show progress
    tracker.show_progress()
    tracker.show_next_goals()
