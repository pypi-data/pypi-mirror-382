#!/usr/bin/env python3
"""
ManimPro Progress Tracking & Celebration System
===============================================

This module tracks beginner progress and celebrates milestones to keep
users motivated and engaged in their animation learning journey.

Features:
- Animation creation tracking
- Skill progression monitoring
- Milestone celebrations
- Learning streaks
- Personal statistics

Usage:
    from manimpro.easy.progress import ProgressTracker
    
    tracker = ProgressTracker()
    tracker.record_animation_created("hello_world", "beginner")
    tracker.show_progress_dashboard()
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
    from rich.columns import Columns
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


@dataclass
class AnimationRecord:
    """Record of a created animation."""
    name: str
    category: str
    difficulty: str
    created_date: str
    time_spent: Optional[int] = None  # in minutes
    source: str = "unknown"  # wizard, example, preset, manual


@dataclass
class LearningStreak:
    """Tracks learning streaks."""
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[str] = None


class ProgressTracker:
    """Tracks user progress and celebrates achievements."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.progress_file = Path.home() / ".manimpro" / "progress.json"
        self.progress_file.parent.mkdir(exist_ok=True)
        
        # Initialize progress data
        self.data = {
            "animations": [],
            "skills": {
                "basic_animation": 0,
                "equations": 0,
                "shapes": 0,
                "graphs": 0,
                "3d_animation": 0,
                "transformations": 0,
                "proofs": 0
            },
            "streaks": {
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None
            },
            "milestones": {
                "first_animation": False,
                "first_week": False,
                "10_animations": False,
                "all_categories": False,
                "speed_creator": False,
                "consistent_learner": False
            },
            "stats": {
                "total_animations": 0,
                "total_time_spent": 0,
                "favorite_category": None,
                "most_productive_day": None,
                "creation_dates": []
            },
            "last_updated": None
        }
        
        # Load existing progress
        self.load_progress()
        
    def load_progress(self):
        """Load progress from file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    saved_data = json.load(f)
                    # Merge with default structure
                    self._merge_data(saved_data)
            except (json.JSONDecodeError, KeyError):
                # If file is corrupted, start fresh
                pass
                
    def _merge_data(self, saved_data: Dict[str, Any]):
        """Merge saved data with default structure."""
        for key, value in saved_data.items():
            if key in self.data:
                if isinstance(self.data[key], dict) and isinstance(value, dict):
                    self.data[key].update(value)
                else:
                    self.data[key] = value
                    
    def save_progress(self):
        """Save progress to file."""
        self.data["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            # Fail silently if we can't save
            pass
            
    def record_animation_created(self, name: str, category: str, difficulty: str = "beginner", 
                               time_spent: Optional[int] = None, source: str = "unknown"):
        """Record that an animation was created."""
        # Create animation record
        record = AnimationRecord(
            name=name,
            category=category.lower(),
            difficulty=difficulty.lower(),
            created_date=datetime.now().isoformat(),
            time_spent=time_spent,
            source=source
        )
        
        # Add to animations list
        self.data["animations"].append(asdict(record))
        
        # Update skills
        if category.lower() in self.data["skills"]:
            self.data["skills"][category.lower()] += 1
        else:
            self.data["skills"]["basic_animation"] += 1
            
        # Update stats
        self.data["stats"]["total_animations"] += 1
        if time_spent:
            self.data["stats"]["total_time_spent"] += time_spent
            
        today = datetime.now().date().isoformat()
        self.data["stats"]["creation_dates"].append(today)
        
        # Update streaks
        self._update_streaks()
        
        # Check milestones
        self._check_milestones()
        
        # Save progress
        self.save_progress()
        
        # Celebrate if appropriate
        self._celebrate_progress(record)
        
    def _update_streaks(self):
        """Update learning streaks."""
        today = datetime.now().date()
        last_date_str = self.data["streaks"]["last_activity_date"]
        
        if last_date_str:
            last_date = datetime.fromisoformat(last_date_str).date()
            days_diff = (today - last_date).days
            
            if days_diff == 1:
                # Consecutive day
                self.data["streaks"]["current_streak"] += 1
            elif days_diff > 1:
                # Streak broken
                self.data["streaks"]["current_streak"] = 1
            # Same day doesn't change streak
        else:
            # First activity
            self.data["streaks"]["current_streak"] = 1
            
        # Update longest streak
        if self.data["streaks"]["current_streak"] > self.data["streaks"]["longest_streak"]:
            self.data["streaks"]["longest_streak"] = self.data["streaks"]["current_streak"]
            
        self.data["streaks"]["last_activity_date"] = today.isoformat()
        
    def _check_milestones(self):
        """Check and unlock milestones."""
        total = self.data["stats"]["total_animations"]
        
        # First animation
        if total >= 1 and not self.data["milestones"]["first_animation"]:
            self.data["milestones"]["first_animation"] = True
            self._celebrate_milestone("first_animation", "🎬 First Animation Created!")
            
        # 10 animations
        if total >= 10 and not self.data["milestones"]["10_animations"]:
            self.data["milestones"]["10_animations"] = True
            self._celebrate_milestone("10_animations", "🏆 10 Animations Milestone!")
            
        # All categories
        categories_used = set(anim["category"] for anim in self.data["animations"])
        if len(categories_used) >= 5 and not self.data["milestones"]["all_categories"]:
            self.data["milestones"]["all_categories"] = True
            self._celebrate_milestone("all_categories", "🌟 Category Explorer!")
            
        # Consistent learner (7 day streak)
        if self.data["streaks"]["current_streak"] >= 7 and not self.data["milestones"]["consistent_learner"]:
            self.data["milestones"]["consistent_learner"] = True
            self._celebrate_milestone("consistent_learner", "🔥 7-Day Streak Master!")
            
    def _celebrate_milestone(self, milestone_id: str, message: str):
        """Celebrate a milestone achievement."""
        if self.console:
            celebration = f"""
🎉 MILESTONE ACHIEVED! 🎉

{message}

You're making incredible progress!
Keep up the amazing work!
            """
            
            panel = Panel(
                celebration.strip(),
                title="🏆 NEW MILESTONE 🏆",
                border_style="gold",
                padding=(1, 2)
            )
            
            self.console.print()
            self.console.print(panel)
            self.console.print()
        else:
            print(f"\n🎉 MILESTONE ACHIEVED! 🎉")
            print(f"{message}")
            print("You're making incredible progress!")
            print()
            
    def _celebrate_progress(self, record: AnimationRecord):
        """Celebrate progress after creating an animation."""
        total = self.data["stats"]["total_animations"]
        
        # Celebration messages based on progress
        celebrations = []
        
        if total == 1:
            celebrations.append("🎊 Congratulations on your first animation!")
        elif total == 5:
            celebrations.append("🌟 5 animations created! You're on fire!")
        elif total == 10:
            celebrations.append("🏆 Double digits! 10 animations completed!")
        elif total % 10 == 0:
            celebrations.append(f"🎯 Amazing! {total} animations created!")
            
        # Streak celebrations
        streak = self.data["streaks"]["current_streak"]
        if streak == 3:
            celebrations.append("🔥 3-day streak! You're building momentum!")
        elif streak == 7:
            celebrations.append("⚡ 1 week streak! Incredible consistency!")
        elif streak == 30:
            celebrations.append("🏅 30-day streak! You're a ManimPro champion!")
            
        # Show celebrations
        for celebration in celebrations:
            if self.console:
                self.console.print(f"[green]{celebration}[/green]")
            else:
                print(celebration)
                
    def show_progress_dashboard(self):
        """Display comprehensive progress dashboard."""
        if self.console:
            self.console.print("\n📊 Your ManimPro Progress Dashboard 📊", style="bold blue")
            
            # Overview stats
            overview = self._get_overview_stats()
            overview_panel = Panel(
                self._format_overview(overview),
                title="📈 Overview",
                border_style="blue"
            )
            
            # Skills breakdown
            skills_table = self._create_skills_table()
            
            # Recent activity
            recent_panel = Panel(
                self._format_recent_activity(),
                title="🕒 Recent Activity",
                border_style="green"
            )
            
            # Display in columns
            self.console.print(overview_panel)
            self.console.print(skills_table)
            self.console.print(recent_panel)
            
            # Motivational message
            self._show_motivational_dashboard_message()
            
        else:
            # Simple text dashboard
            print("\n📊 Your ManimPro Progress Dashboard 📊")
            
            overview = self._get_overview_stats()
            print(f"\n📈 Overview:")
            print(f"  Total Animations: {overview['total_animations']}")
            print(f"  Current Streak: {overview['current_streak']} days")
            print(f"  Longest Streak: {overview['longest_streak']} days")
            print(f"  Time Spent: {overview['total_time']} minutes")
            
            print(f"\n🎯 Skills:")
            for skill, count in self.data["skills"].items():
                if count > 0:
                    print(f"  {skill.replace('_', ' ').title()}: {count}")
                    
    def _get_overview_stats(self) -> Dict[str, Any]:
        """Get overview statistics."""
        return {
            "total_animations": self.data["stats"]["total_animations"],
            "current_streak": self.data["streaks"]["current_streak"],
            "longest_streak": self.data["streaks"]["longest_streak"],
            "total_time": self.data["stats"]["total_time_spent"],
            "categories_explored": len(set(anim["category"] for anim in self.data["animations"])),
            "milestones_achieved": sum(1 for achieved in self.data["milestones"].values() if achieved)
        }
        
    def _format_overview(self, stats: Dict[str, Any]) -> str:
        """Format overview statistics."""
        return f"""
🎬 Total Animations: {stats['total_animations']}
🔥 Current Streak: {stats['current_streak']} days
🏆 Longest Streak: {stats['longest_streak']} days
⏱️ Time Spent: {stats['total_time']} minutes
🎨 Categories Explored: {stats['categories_explored']}
🏅 Milestones Achieved: {stats['milestones_achieved']}
        """.strip()
        
    def _create_skills_table(self) -> Table:
        """Create skills progress table."""
        table = Table(title="🎯 Skills Progress")
        table.add_column("Skill", style="cyan")
        table.add_column("Count", style="yellow")
        table.add_column("Level", style="green")
        
        for skill, count in self.data["skills"].items():
            if count > 0:
                level = self._get_skill_level(count)
                skill_name = skill.replace('_', ' ').title()
                table.add_row(skill_name, str(count), level)
                
        return table
        
    def _get_skill_level(self, count: int) -> str:
        """Get skill level based on count."""
        if count >= 20:
            return "🏆 Master"
        elif count >= 10:
            return "⭐ Expert"
        elif count >= 5:
            return "🎯 Advanced"
        elif count >= 2:
            return "📈 Intermediate"
        else:
            return "🌱 Beginner"
            
    def _format_recent_activity(self) -> str:
        """Format recent activity."""
        recent_animations = self.data["animations"][-5:]  # Last 5
        
        if not recent_animations:
            return "No animations created yet. Start your journey today!"
            
        activity_lines = []
        for anim in reversed(recent_animations):  # Most recent first
            date = datetime.fromisoformat(anim["created_date"]).strftime("%m/%d")
            activity_lines.append(f"• {date}: {anim['name']} ({anim['category']})")
            
        return "\n".join(activity_lines)
        
    def _show_motivational_dashboard_message(self):
        """Show motivational message on dashboard."""
        total = self.data["stats"]["total_animations"]
        streak = self.data["streaks"]["current_streak"]
        
        if total == 0:
            message = "🌟 Ready to start your animation journey? Create your first animation today!"
        elif total < 5:
            message = f"🚀 Great start with {total} animations! Keep the momentum going!"
        elif streak >= 7:
            message = f"🔥 Amazing {streak}-day streak! You're building incredible habits!"
        elif total >= 20:
            message = f"🏆 Wow! {total} animations! You're becoming a true ManimPro master!"
        else:
            message = f"💪 {total} animations created! You're making excellent progress!"
            
        if self.console:
            motivational_panel = Panel(
                message,
                title="💫 Keep Going!",
                border_style="magenta",
                padding=(1, 2)
            )
            self.console.print(motivational_panel)
        else:
            print(f"\n💫 {message}")
            
    def get_weekly_summary(self) -> Dict[str, Any]:
        """Get summary of this week's progress."""
        week_ago = datetime.now() - timedelta(days=7)
        
        week_animations = [
            anim for anim in self.data["animations"]
            if datetime.fromisoformat(anim["created_date"]) >= week_ago
        ]
        
        return {
            "animations_this_week": len(week_animations),
            "categories_this_week": len(set(anim["category"] for anim in week_animations)),
            "time_this_week": sum(anim.get("time_spent", 0) for anim in week_animations),
            "streak_maintained": self.data["streaks"]["current_streak"] >= 7,
            "most_active_day": self._get_most_active_day(week_animations)
        }
        
    def _get_most_active_day(self, animations: List[Dict]) -> Optional[str]:
        """Get the most active day from a list of animations."""
        if not animations:
            return None
            
        day_counts = defaultdict(int)
        for anim in animations:
            day = datetime.fromisoformat(anim["created_date"]).strftime("%A")
            day_counts[day] += 1
            
        return max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else None
        
    def show_weekly_summary(self):
        """Show weekly progress summary."""
        summary = self.get_weekly_summary()
        
        if self.console:
            content = f"""
📅 This Week's Progress

🎬 Animations Created: {summary['animations_this_week']}
🎨 Categories Explored: {summary['categories_this_week']}
⏱️ Time Spent: {summary['time_this_week']} minutes
🔥 Streak Status: {'✅ Active' if summary['streak_maintained'] else '⏰ Keep going!'}
📈 Most Active Day: {summary['most_active_day'] or 'None yet'}
            """
            
            panel = Panel(
                content.strip(),
                title="📊 Weekly Summary",
                border_style="cyan"
            )
            
            self.console.print(panel)
        else:
            print("\n📅 This Week's Progress")
            print(f"Animations: {summary['animations_this_week']}")
            print(f"Categories: {summary['categories_this_week']}")
            print(f"Time: {summary['time_this_week']} minutes")
            print(f"Most Active: {summary['most_active_day'] or 'None yet'}")


# Global progress tracker instance
_progress_tracker = None

def get_progress_tracker() -> ProgressTracker:
    """Get the global progress tracker instance."""
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker()
    return _progress_tracker


def record_animation(name: str, category: str, difficulty: str = "beginner", 
                    time_spent: Optional[int] = None, source: str = "unknown"):
    """Convenience function to record an animation."""
    get_progress_tracker().record_animation_created(name, category, difficulty, time_spent, source)


def show_progress():
    """Convenience function to show progress dashboard."""
    get_progress_tracker().show_progress_dashboard()


def show_weekly_summary():
    """Convenience function to show weekly summary."""
    get_progress_tracker().show_weekly_summary()


if __name__ == "__main__":
    # Demo the progress tracking system
    tracker = ProgressTracker()
    
    print("📊 ManimPro Progress Tracking Demo")
    print("=" * 40)
    
    # Simulate some progress
    tracker.record_animation_created("Hello World", "basic", "beginner", 5, "wizard")
    tracker.record_animation_created("Equation Demo", "equations", "beginner", 8, "example")
    tracker.record_animation_created("Shape Morph", "shapes", "intermediate", 12, "preset")
    
    # Show dashboard
    tracker.show_progress_dashboard()
    tracker.show_weekly_summary()
