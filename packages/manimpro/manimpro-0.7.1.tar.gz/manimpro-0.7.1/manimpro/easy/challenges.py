#!/usr/bin/env python3
"""
ManimPro Animation Challenges - Fun Challenges to Keep Beginners Engaged
========================================================================

This module provides fun, bite-sized animation challenges that keep beginners
engaged and motivated while learning new skills progressively.

Features:
- Daily challenges
- Skill-building challenges
- Creative prompts
- Timed challenges
- Community challenges

Usage:
    from manimpro.easy.challenges import ChallengeManager
    
    manager = ChallengeManager()
    manager.show_daily_challenge()
    manager.start_challenge("color_master")
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .templates import EasyAnimation

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm
    import time
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


@dataclass
class Challenge:
    """Represents a single animation challenge."""
    id: str
    title: str
    description: str
    difficulty: str
    estimated_time: str
    skills_practiced: List[str]
    prompt: str
    success_criteria: List[str]
    bonus_points: int
    category: str
    emoji: str


class ChallengeManager:
    """Manages animation challenges for beginners."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        
        # Define all available challenges
        self.challenges = {
            # Beginner Challenges
            "first_steps": Challenge(
                id="first_steps",
                title="First Steps",
                description="Create your very first animation using the wizard",
                difficulty="Beginner",
                estimated_time="5 minutes",
                skills_practiced=["Basic animation", "Wizard usage"],
                prompt="Use the ManimPro wizard to create an animation with your name and a fun message!",
                success_criteria=["Animation contains text", "Animation renders successfully"],
                bonus_points=10,
                category="Getting Started",
                emoji="👶"
            ),
            
            "color_master": Challenge(
                id="color_master",
                title="Color Master",
                description="Create an animation using at least 5 different colors",
                difficulty="Beginner",
                estimated_time="10 minutes",
                skills_practiced=["Color usage", "Visual design"],
                prompt="Create a rainbow-themed animation! Use at least 5 different colors in shapes, text, or backgrounds.",
                success_criteria=["Uses 5+ different colors", "Visually appealing", "Colors are well-coordinated"],
                bonus_points=15,
                category="Design",
                emoji="🌈"
            ),
            
            "shape_shifter": Challenge(
                id="shape_shifter",
                title="Shape Shifter",
                description="Create 3 different shape transformations in one animation",
                difficulty="Beginner",
                estimated_time="15 minutes",
                skills_practiced=["Shape transformations", "Animation timing"],
                prompt="Show the magic of transformation! Create an animation where shapes morph into other shapes at least 3 times.",
                success_criteria=["3+ shape transformations", "Smooth transitions", "Creative shape choices"],
                bonus_points=20,
                category="Transformations",
                emoji="🔄"
            ),
            
            # Intermediate Challenges
            "equation_artist": Challenge(
                id="equation_artist",
                title="Equation Artist",
                description="Create a beautiful equation reveal with explanation",
                difficulty="Intermediate",
                estimated_time="20 minutes",
                skills_practiced=["LaTeX equations", "Mathematical presentation"],
                prompt="Pick your favorite mathematical equation and create a stunning reveal animation with explanation!",
                success_criteria=["Beautiful equation display", "Clear explanation", "Engaging presentation"],
                bonus_points=25,
                category="Mathematics",
                emoji="🧮"
            ),
            
            "story_teller": Challenge(
                id="story_teller",
                title="Story Teller",
                description="Create an animation that tells a mathematical story",
                difficulty="Intermediate",
                estimated_time="25 minutes",
                skills_practiced=["Narrative structure", "Sequential animation"],
                prompt="Tell a story with math! Create an animation that explains a mathematical concept through a narrative.",
                success_criteria=["Clear story structure", "Educational content", "Engaging narrative"],
                bonus_points=30,
                category="Education",
                emoji="📚"
            ),
            
            "graph_wizard": Challenge(
                id="graph_wizard",
                title="Graph Wizard",
                description="Create an animation showing how changing parameters affects a function",
                difficulty="Intermediate",
                estimated_time="30 minutes",
                skills_practiced=["Function graphing", "Parameter visualization"],
                prompt="Show the magic of mathematics! Create an animation that demonstrates how changing parameters affects a function's graph.",
                success_criteria=["Multiple function variations", "Clear parameter changes", "Educational value"],
                bonus_points=35,
                category="Functions",
                emoji="📊"
            ),
            
            # Advanced Challenges
            "3d_explorer": Challenge(
                id="3d_explorer",
                title="3D Explorer",
                description="Create your first 3D animation",
                difficulty="Advanced",
                estimated_time="45 minutes",
                skills_practiced=["3D animation", "Spatial visualization"],
                prompt="Enter the third dimension! Create a 3D animation that showcases depth and perspective.",
                success_criteria=["Uses 3D elements", "Good camera work", "Impressive visual impact"],
                bonus_points=50,
                category="3D Animation",
                emoji="🎲"
            ),
            
            "physics_simulator": Challenge(
                id="physics_simulator",
                title="Physics Simulator",
                description="Animate a physics concept with realistic motion",
                difficulty="Advanced",
                estimated_time="40 minutes",
                skills_practiced=["Physics animation", "Realistic motion"],
                prompt="Bring physics to life! Create an animation that demonstrates a physics concept with realistic motion.",
                success_criteria=["Accurate physics", "Realistic motion", "Educational clarity"],
                bonus_points=45,
                category="Physics",
                emoji="⚡"
            ),
            
            # Creative Challenges
            "minimalist_master": Challenge(
                id="minimalist_master",
                title="Minimalist Master",
                description="Create maximum impact with minimal elements",
                difficulty="Intermediate",
                estimated_time="20 minutes",
                skills_practiced=["Design principles", "Visual impact"],
                prompt="Less is more! Create a powerful animation using only 3 colors and 3 shapes maximum.",
                success_criteria=["Uses ≤3 colors", "Uses ≤3 shapes", "High visual impact", "Clean design"],
                bonus_points=30,
                category="Design",
                emoji="⚪"
            ),
            
            "speed_demon": Challenge(
                id="speed_demon",
                title="Speed Demon",
                description="Create an animation in under 5 minutes",
                difficulty="Beginner",
                estimated_time="5 minutes",
                skills_practiced=["Quick creation", "Efficiency"],
                prompt="Race against time! Create a complete animation in under 5 minutes. Quality over complexity!",
                success_criteria=["Created in <5 minutes", "Complete animation", "Good quality despite speed"],
                bonus_points=25,
                category="Speed",
                emoji="⚡"
            ),
            
            # Fun Challenges
            "emoji_animator": Challenge(
                id="emoji_animator",
                title="Emoji Animator",
                description="Create an animation inspired by your favorite emoji",
                difficulty="Beginner",
                estimated_time="15 minutes",
                skills_practiced=["Creative interpretation", "Visual storytelling"],
                prompt="Pick your favorite emoji and create an animation inspired by it! Be creative and have fun!",
                success_criteria=["Clear emoji inspiration", "Creative interpretation", "Fun and engaging"],
                bonus_points=20,
                category="Fun",
                emoji="😄"
            ),
            
            "music_visualizer": Challenge(
                id="music_visualizer",
                title="Music Visualizer",
                description="Create an animation that feels like it's dancing to music",
                difficulty="Intermediate",
                estimated_time="25 minutes",
                skills_practiced=["Rhythm visualization", "Dynamic animation"],
                prompt="Make math dance! Create an animation with rhythmic, musical movement even without sound.",
                success_criteria=["Rhythmic movement", "Musical feeling", "Dynamic visuals"],
                bonus_points=35,
                category="Creative",
                emoji="🎵"
            )
        }
        
        # Challenge categories for organization
        self.categories = {
            "Getting Started": "👶",
            "Design": "🎨", 
            "Mathematics": "🧮",
            "Transformations": "🔄",
            "Education": "📚",
            "Functions": "📊",
            "3D Animation": "🎲",
            "Physics": "⚡",
            "Speed": "⚡",
            "Fun": "😄",
            "Creative": "🎵"
        }
        
    def get_daily_challenge(self) -> Challenge:
        """Get today's daily challenge based on the date."""
        # Use date as seed for consistent daily challenge
        today = datetime.now().date()
        random.seed(today.toordinal())
        
        # Select challenge based on day of week for variety
        day_of_week = today.weekday()
        
        if day_of_week == 0:  # Monday - Start week with beginner
            candidates = [c for c in self.challenges.values() if c.difficulty == "Beginner"]
        elif day_of_week == 2:  # Wednesday - Intermediate
            candidates = [c for c in self.challenges.values() if c.difficulty == "Intermediate"]
        elif day_of_week == 4:  # Friday - Advanced or fun
            candidates = [c for c in self.challenges.values() 
                         if c.difficulty == "Advanced" or c.category == "Fun"]
        else:  # Other days - any challenge
            candidates = list(self.challenges.values())
            
        return random.choice(candidates)
        
    def show_daily_challenge(self):
        """Display today's daily challenge."""
        challenge = self.get_daily_challenge()
        
        if self.console:
            # Rich display
            content = f"""
🎯 Today's Challenge: {challenge.title}

{challenge.description}

📊 Difficulty: {challenge.difficulty}
⏱️ Estimated Time: {challenge.estimated_time}
🏆 Bonus Points: {challenge.bonus_points}

🎨 Challenge Prompt:
{challenge.prompt}

✅ Success Criteria:
{chr(10).join(f"• {criteria}" for criteria in challenge.success_criteria)}

💪 Skills You'll Practice:
{chr(10).join(f"• {skill}" for skill in challenge.skills_practiced)}

Ready to start? Use: manimpro wizard challenge --start {challenge.id}
            """
            
            panel = Panel(
                content.strip(),
                title=f"{challenge.emoji} Daily Challenge - {datetime.now().strftime('%B %d, %Y')}",
                border_style="cyan",
                padding=(1, 2)
            )
            
            self.console.print(panel)
            
        else:
            # Simple text display
            print(f"\n{challenge.emoji} Daily Challenge - {datetime.now().strftime('%B %d, %Y')}")
            print(f"🎯 {challenge.title}")
            print(f"\n{challenge.description}")
            print(f"\nDifficulty: {challenge.difficulty}")
            print(f"Time: {challenge.estimated_time}")
            print(f"Points: {challenge.bonus_points}")
            print(f"\nChallenge:")
            print(f"{challenge.prompt}")
            print(f"\nSuccess Criteria:")
            for criteria in challenge.success_criteria:
                print(f"• {criteria}")
            print()
            
    def show_all_challenges(self, category: Optional[str] = None):
        """Show all available challenges, optionally filtered by category."""
        challenges_to_show = self.challenges.values()
        
        if category:
            challenges_to_show = [c for c in challenges_to_show if c.category == category]
            
        if self.console:
            self.console.print(f"\n🏆 ManimPro Challenges", style="bold blue")
            
            if category:
                self.console.print(f"Category: {self.categories.get(category, '')} {category}", style="cyan")
                
            # Group by difficulty
            by_difficulty = {}
            for challenge in challenges_to_show:
                if challenge.difficulty not in by_difficulty:
                    by_difficulty[challenge.difficulty] = []
                by_difficulty[challenge.difficulty].append(challenge)
                
            for difficulty in ["Beginner", "Intermediate", "Advanced"]:
                if difficulty in by_difficulty:
                    self.console.print(f"\n📈 {difficulty} Challenges", style="bold yellow")
                    
                    for challenge in by_difficulty[difficulty]:
                        content = f"""
{challenge.emoji} {challenge.title}
{challenge.description}
Time: {challenge.estimated_time} | Points: {challenge.bonus_points}
                        """
                        
                        panel = Panel(
                            content.strip(),
                            border_style="yellow",
                            padding=(0, 1)
                        )
                        self.console.print(panel)
                        
        else:
            print(f"\n🏆 ManimPro Challenges")
            if category:
                print(f"Category: {category}")
                
            for challenge in challenges_to_show:
                print(f"\n{challenge.emoji} {challenge.title}")
                print(f"   {challenge.description}")
                print(f"   {challenge.difficulty} | {challenge.estimated_time} | {challenge.bonus_points} points")
                
    def start_challenge(self, challenge_id: str) -> bool:
        """Start a specific challenge with timer and guidance."""
        if challenge_id not in self.challenges:
            if self.console:
                self.console.print(f"[red]Challenge '{challenge_id}' not found![/red]")
            else:
                print(f"Challenge '{challenge_id}' not found!")
            return False
            
        challenge = self.challenges[challenge_id]
        
        if self.console:
            # Rich challenge start
            self.console.print(f"\n🚀 Starting Challenge: {challenge.emoji} {challenge.title}", style="bold green")
            
            # Show challenge details
            details = f"""
📝 Challenge: {challenge.prompt}

⏱️ Estimated Time: {challenge.estimated_time}
🎯 Difficulty: {challenge.difficulty}

✅ Success Criteria:
{chr(10).join(f"• {criteria}" for criteria in challenge.success_criteria)}
            """
            
            panel = Panel(details.strip(), title="Challenge Details", border_style="green")
            self.console.print(panel)
            
            # Ask if ready to start
            if RICH_AVAILABLE:
                from rich.prompt import Confirm
                ready = Confirm.ask("Are you ready to start this challenge?")
            else:
                ready = input("Are you ready to start this challenge? (y/n): ").lower().startswith('y')
                
            if ready:
                self.console.print("\n🎬 Challenge started! Good luck!", style="bold blue")
                self.console.print("💡 Tip: Focus on meeting the success criteria first, then add your creative touches!")
                
                # Start timer display (visual motivation)
                start_time = time.time()
                self.console.print(f"\n⏰ Timer started at {datetime.now().strftime('%H:%M:%S')}")
                
                return True
            else:
                self.console.print("Challenge cancelled. Come back when you're ready! 💪", style="yellow")
                return False
                
        else:
            # Simple text version
            print(f"\n🚀 Starting Challenge: {challenge.emoji} {challenge.title}")
            print(f"\nChallenge: {challenge.prompt}")
            print(f"Time: {challenge.estimated_time}")
            print(f"Difficulty: {challenge.difficulty}")
            print("\nSuccess Criteria:")
            for criteria in challenge.success_criteria:
                print(f"• {criteria}")
                
            ready = input("\nAre you ready to start? (y/n): ").lower().startswith('y')
            if ready:
                print("\n🎬 Challenge started! Good luck!")
                print("💡 Tip: Focus on meeting the success criteria first!")
                return True
            else:
                print("Challenge cancelled. Come back when you're ready! 💪")
                return False
                
    def get_challenge_by_skill(self, skill_level: str) -> List[Challenge]:
        """Get challenges appropriate for a skill level."""
        if skill_level.lower() == "beginner":
            return [c for c in self.challenges.values() if c.difficulty == "Beginner"]
        elif skill_level.lower() == "intermediate":
            return [c for c in self.challenges.values() if c.difficulty == "Intermediate"]
        elif skill_level.lower() == "advanced":
            return [c for c in self.challenges.values() if c.difficulty == "Advanced"]
        else:
            return list(self.challenges.values())
            
    def suggest_next_challenge(self, completed_challenges: List[str] = None) -> Challenge:
        """Suggest the next appropriate challenge."""
        if completed_challenges is None:
            completed_challenges = []
            
        # Filter out completed challenges
        available = [c for c in self.challenges.values() if c.id not in completed_challenges]
        
        if not available:
            # All challenges completed!
            return random.choice(list(self.challenges.values()))
            
        # Suggest based on progression
        beginner_count = len([c for c in completed_challenges 
                             if self.challenges.get(c, {}).get('difficulty') == 'Beginner'])
        
        if beginner_count < 3:
            # Focus on beginner challenges first
            beginners = [c for c in available if c.difficulty == "Beginner"]
            if beginners:
                return random.choice(beginners)
                
        # Mix of intermediate and advanced
        return random.choice(available)


# Convenience functions
def show_daily_challenge():
    """Show today's daily challenge."""
    manager = ChallengeManager()
    manager.show_daily_challenge()


def show_all_challenges():
    """Show all available challenges."""
    manager = ChallengeManager()
    manager.show_all_challenges()


def start_challenge(challenge_id: str):
    """Start a specific challenge."""
    manager = ChallengeManager()
    return manager.start_challenge(challenge_id)


if __name__ == "__main__":
    # Demo the challenge system
    manager = ChallengeManager()
    
    print("🏆 ManimPro Challenge System Demo")
    print("=" * 40)
    
    # Show daily challenge
    manager.show_daily_challenge()
    
    # Show some challenges
    print("\n" + "=" * 40)
    manager.show_all_challenges()
