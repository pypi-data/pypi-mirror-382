#!/usr/bin/env python3
"""
ManimPro Scene & Animation Helper Functions
===========================================

This module provides utilities that improve scene reliability, reduce boilerplate,
and make common animation patterns easier to implement.

Features:
- Scene preview and rendering utilities
- Following and tracking animations
- Bulk fade operations
- Animation looping and repetition
- Quick scene setup helpers

Usage:
    from manimpro.utils.scene_helpers import always_follow, fade_in_objects
    
    # Make one object follow another
    always_follow(dot, moving_circle, offset=(0, 1))
    
    # Fade multiple objects at once
    fade_in_objects([dot1, dot2, dot3], run_time=2)
"""

from __future__ import annotations

import subprocess
import sys
from typing import Union, Sequence, TYPE_CHECKING, Optional, Tuple, Any
import numpy as np

if TYPE_CHECKING:
    from ..mobject.mobject import Mobject
    from ..scene.scene import Scene
    from ..animation.animation import Animation

# Type hints
NumberType = Union[int, float]
Point3D = Union[Sequence[float], np.ndarray]


def preview_scene(scene_class: type, *args, **kwargs) -> None:
    """
    Automatically render a scene in preview mode without extra commands.
    
    This function renders a scene with optimal preview settings and opens
    the result automatically.
    
    Args:
        scene_class: The Scene class to render
        *args: Arguments to pass to the scene constructor
        **kwargs: Keyword arguments for rendering options
        
    Examples:
        class MyScene(Scene):
            def construct(self):
                circle = Circle()
                self.play(Create(circle))
        
        # Preview the scene
        preview_scene(MyScene)
        
        # With custom options
        preview_scene(MyScene, quality='medium', preview=True)
    """
    try:
        # Get the scene file name
        import inspect
        frame = inspect.currentframe().f_back
        filename = frame.f_globals.get('__file__', 'scene.py')
        
        # Default preview options
        default_options = {
            'quality': 'low',
            'preview': True,
            'format': 'mp4'
        }
        default_options.update(kwargs)
        
        # Build command
        cmd = ['manimpro']
        
        if default_options.get('preview', True):
            cmd.append('-p')
        
        quality = default_options.get('quality', 'low')
        if quality == 'low':
            cmd.append('-ql')
        elif quality == 'medium':
            cmd.append('-qm')
        elif quality == 'high':
            cmd.append('-qh')
        
        cmd.extend([filename, scene_class.__name__])
        
        # Run the command
        subprocess.run(cmd, check=True)
        
    except Exception as e:
        print(f"Error previewing scene: {e}")
        print("Make sure you're running this from a file with the scene class defined.")


def render_to_mp4(scene_class: type, filename: str = None, 
                 quality: str = 'high', **kwargs) -> str:
    """
    Simplify rendering to MP4 with quality presets.
    
    Args:
        scene_class: The Scene class to render
        filename: Output filename (auto-generated if None)
        quality: Quality preset ('low', 'medium', 'high', 'ultra')
        **kwargs: Additional rendering options
        
    Returns:
        Path to the rendered video file
        
    Examples:
        # Render with high quality
        video_path = render_to_mp4(MyScene, quality='high')
        
        # Custom filename
        render_to_mp4(MyScene, filename='my_animation.mp4', quality='medium')
    """
    try:
        import inspect
        frame = inspect.currentframe().f_back
        source_file = frame.f_globals.get('__file__', 'scene.py')
        
        # Quality presets
        quality_flags = {
            'low': '-ql',
            'medium': '-qm', 
            'high': '-qh',
            'ultra': '-qk'  # 4K quality
        }
        
        cmd = ['manimpro', quality_flags.get(quality, '-qh')]
        
        if filename:
            cmd.extend(['-o', filename])
        
        cmd.extend([source_file, scene_class.__name__])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Extract output path from result (this is a simplified approach)
        output_path = filename or f"{scene_class.__name__}.mp4"
        return output_path
        
    except Exception as e:
        print(f"Error rendering scene: {e}")
        return ""


def always_follow(follower: "Mobject", target: "Mobject", 
                 offset: Point3D = (0, 0, 0), **kwargs) -> "Mobject":
    """
    Make one object always follow another with an optional offset.
    
    This creates an updater that continuously positions the follower
    relative to the target object.
    
    Args:
        follower: The Mobject that will follow
        target: The Mobject to follow
        offset: Offset vector from target position
        **kwargs: Additional options for positioning
        
    Returns:
        The follower Mobject with updater attached
        
    Examples:
        circle = Circle()
        dot = Dot()
        
        # Dot follows circle
        always_follow(dot, circle)
        
        # With offset (dot stays above circle)
        always_follow(dot, circle, offset=(0, 1, 0))
        
        # Now when circle moves, dot follows automatically
        self.play(circle.animate.shift(RIGHT * 2))
    """
    from ..utils.positioning import set_position, get_position
    
    offset = np.array(offset)
    
    def update_follower_position(mob):
        target_pos = get_position(target)
        new_pos = target_pos + offset
        set_position(mob, new_pos)
    
    follower.add_updater(update_follower_position)
    
    # Store references for easy removal
    follower._follow_target = target
    follower._follow_offset = offset
    
    return follower


def stop_following(follower: "Mobject") -> "Mobject":
    """
    Stop a Mobject from following its target.
    
    Args:
        follower: The Mobject to stop following
        
    Returns:
        The follower Mobject with updater removed
        
    Examples:
        always_follow(dot, circle)
        # ... later ...
        stop_following(dot)  # Dot stops following circle
    """
    follower.clear_updaters()
    
    # Clean up references
    if hasattr(follower, '_follow_target'):
        delattr(follower, '_follow_target')
    if hasattr(follower, '_follow_offset'):
        delattr(follower, '_follow_offset')
    
    return follower


def fade_in_objects(objects: Sequence["Mobject"], run_time: NumberType = 1,
                   lag_ratio: NumberType = 0.1, **kwargs) -> "Animation":
    """
    Fade in multiple objects with optional lag between them.
    
    Args:
        objects: Sequence of Mobjects to fade in
        run_time: Total duration of the fade-in animation
        lag_ratio: Delay between each object's fade (0 = simultaneous, 1 = sequential)
        **kwargs: Additional animation arguments
        
    Returns:
        Animation group that fades in all objects
        
    Examples:
        dots = [Dot() for _ in range(5)]
        
        # Fade all at once
        self.play(fade_in_objects(dots))
        
        # Fade with stagger effect
        self.play(fade_in_objects(dots, lag_ratio=0.2, run_time=3))
    """
    from ..animation.fading import FadeIn
    from ..animation.composition import AnimationGroup
    
    animations = [FadeIn(obj, **kwargs) for obj in objects]
    
    return AnimationGroup(*animations, run_time=run_time, lag_ratio=lag_ratio)


def fade_out_objects(objects: Sequence["Mobject"], run_time: NumberType = 1,
                    lag_ratio: NumberType = 0.1, **kwargs) -> "Animation":
    """
    Fade out multiple objects with optional lag between them.
    
    Args:
        objects: Sequence of Mobjects to fade out
        run_time: Total duration of the fade-out animation
        lag_ratio: Delay between each object's fade
        **kwargs: Additional animation arguments
        
    Returns:
        Animation group that fades out all objects
        
    Examples:
        # Fade out all objects
        self.play(fade_out_objects([dot1, dot2, circle, text]))
        
        # Sequential fade out
        self.play(fade_out_objects(all_objects, lag_ratio=0.3))
    """
    from ..animation.fading import FadeOut
    from ..animation.composition import AnimationGroup
    
    animations = [FadeOut(obj, **kwargs) for obj in objects]
    
    return AnimationGroup(*animations, run_time=run_time, lag_ratio=lag_ratio)


def loop_animation(animation: "Animation", times: int = 2, 
                  pause_between: NumberType = 0) -> "Animation":
    """
    Automatically loop any animation a specified number of times.
    
    Args:
        animation: The animation to loop
        times: Number of times to repeat the animation
        pause_between: Pause duration between loops
        
    Returns:
        Animation sequence that loops the original animation
        
    Examples:
        circle = Circle()
        rotate_anim = Rotate(circle, TAU)
        
        # Loop rotation 3 times
        looped = loop_animation(rotate_anim, times=3)
        self.play(looped)
        
        # With pause between loops
        looped = loop_animation(rotate_anim, times=5, pause_between=0.5)
    """
    from ..animation.composition import Succession
    from ..animation.transform import Wait
    
    animations = []
    
    for i in range(times):
        # Add the animation
        animations.append(animation.copy() if hasattr(animation, 'copy') else animation)
        
        # Add pause if not the last iteration
        if i < times - 1 and pause_between > 0:
            animations.append(Wait(pause_between))
    
    return Succession(*animations)


def create_animation_sequence(*animations: "Animation", 
                            run_time: NumberType = None) -> "Animation":
    """
    Create a sequence of animations that play one after another.
    
    Args:
        *animations: Variable number of animations to sequence
        run_time: Total run time for the sequence (distributes evenly if provided)
        
    Returns:
        Animation sequence
        
    Examples:
        circle = Circle()
        
        # Create sequence
        seq = create_animation_sequence(
            Create(circle),
            circle.animate.shift(UP),
            circle.animate.set_color(RED),
            FadeOut(circle)
        )
        self.play(seq)
    """
    from ..animation.composition import Succession
    
    if run_time is not None:
        # Distribute run time evenly among animations
        individual_time = run_time / len(animations)
        animations = [anim.set_run_time(individual_time) for anim in animations]
    
    return Succession(*animations)


def create_animation_group(*animations: "Animation", 
                          lag_ratio: NumberType = 0) -> "Animation":
    """
    Create a group of animations that play simultaneously with optional lag.
    
    Args:
        *animations: Variable number of animations to group
        lag_ratio: Delay between animation starts (0 = simultaneous)
        
    Returns:
        Animation group
        
    Examples:
        dots = [Dot() for _ in range(3)]
        
        # Simultaneous creation
        group = create_animation_group(*[Create(dot) for dot in dots])
        
        # Staggered creation
        group = create_animation_group(
            *[Create(dot) for dot in dots], 
            lag_ratio=0.2
        )
    """
    from ..animation.composition import AnimationGroup
    
    return AnimationGroup(*animations, lag_ratio=lag_ratio)


def quick_scene_setup(background_color: str = None, camera_config: dict = None) -> dict:
    """
    Quickly set up common scene configurations.
    
    Args:
        background_color: Background color for the scene
        camera_config: Camera configuration dictionary
        
    Returns:
        Configuration dictionary for scene setup
        
    Examples:
        class MyScene(Scene):
            def __init__(self, **kwargs):
                config = quick_scene_setup(background_color="BLACK")
                super().__init__(**config, **kwargs)
    """
    config = {}
    
    if background_color:
        config['background_color'] = background_color
    
    if camera_config:
        config['camera_config'] = camera_config
    
    return config


def batch_transform(source_objects: Sequence["Mobject"], 
                   target_objects: Sequence["Mobject"],
                   run_time: NumberType = 1, **kwargs) -> "Animation":
    """
    Transform multiple objects to multiple targets simultaneously.
    
    Args:
        source_objects: Objects to transform from
        target_objects: Objects to transform to
        run_time: Duration of transformations
        **kwargs: Additional animation arguments
        
    Returns:
        Animation group of all transformations
        
    Examples:
        circles = [Circle() for _ in range(3)]
        squares = [Square() for _ in range(3)]
        
        # Transform all circles to squares
        self.play(batch_transform(circles, squares, run_time=2))
    """
    from ..animation.transform import Transform
    from ..animation.composition import AnimationGroup
    
    if len(source_objects) != len(target_objects):
        raise ValueError("Source and target object lists must have the same length")
    
    transforms = [
        Transform(source, target, **kwargs) 
        for source, target in zip(source_objects, target_objects)
    ]
    
    return AnimationGroup(*transforms, run_time=run_time)


def auto_arrange_objects(objects: Sequence["Mobject"], 
                        arrangement: str = "row", spacing: NumberType = 1.0,
                        center: Point3D = None) -> None:
    """
    Automatically arrange multiple objects in common patterns.
    
    Args:
        objects: Objects to arrange
        arrangement: Arrangement type ('row', 'column', 'circle', 'grid')
        spacing: Spacing between objects
        center: Center point for arrangement
        
    Examples:
        dots = [Dot() for _ in range(6)]
        
        # Arrange in a row
        auto_arrange_objects(dots, arrangement="row", spacing=1.5)
        
        # Arrange in a circle
        auto_arrange_objects(dots, arrangement="circle", spacing=2.0)
        
        # Grid arrangement
        auto_arrange_objects(dots, arrangement="grid", spacing=1.0)
    """
    from ..utils.positioning import set_position, position_on_circle, position_in_grid
    
    if center is None:
        center = np.array([0, 0, 0])
    else:
        center = np.array(center)
    
    n = len(objects)
    
    if arrangement == "row":
        # Arrange horizontally
        start_x = center[0] - (n - 1) * spacing / 2
        for i, obj in enumerate(objects):
            x = start_x + i * spacing
            set_position(obj, [x, center[1], center[2]])
            
    elif arrangement == "column":
        # Arrange vertically
        start_y = center[1] + (n - 1) * spacing / 2
        for i, obj in enumerate(objects):
            y = start_y - i * spacing
            set_position(obj, [center[0], y, center[2]])
            
    elif arrangement == "circle":
        # Arrange in a circle
        radius = spacing
        for i, obj in enumerate(objects):
            angle = i * 2 * np.pi / n
            position_on_circle(obj, center, radius, angle)
            
    elif arrangement == "grid":
        # Arrange in a grid (square-ish)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        position_in_grid(objects, rows, cols, spacing, center)
    
    else:
        raise ValueError(f"Unknown arrangement type: {arrangement}")


# Export all scene helper functions
__all__ = [
    "preview_scene",
    "render_to_mp4",
    "always_follow",
    "stop_following", 
    "fade_in_objects",
    "fade_out_objects",
    "loop_animation",
    "create_animation_sequence",
    "create_animation_group",
    "quick_scene_setup",
    "batch_transform",
    "auto_arrange_objects",
]
