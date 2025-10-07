"""
ManimPro CLI Preview Commands
============================

Command-line interface for the ManimPro web viewer functionality.
Provides the 'manimpro preview' command to launch the web-based animation viewer.
"""

from __future__ import annotations

import click
import cloup

from ...web_viewer import preview_web
from ... import console


@cloup.command(
    name="preview",
    help="Launch web viewer to preview rendered animations in browser",
)
@cloup.option(
    "--port",
    "-p",
    type=int,
    default=8000,
    help="Port to run the web server on (default: 8000)",
    show_default=True,
)
@cloup.option(
    "--host",
    "-h",
    type=str,
    default="127.0.0.1",
    help="Host to bind the server to (default: 127.0.0.1)",
    show_default=True,
)
@cloup.option(
    "--no-browser",
    is_flag=True,
    help="Don't automatically open browser",
)
def preview_command(
    port: int,
    host: str,
    no_browser: bool,
) -> None:
    """
    Launch the ManimPro web viewer to preview rendered animations.
    
    This command starts a local web server that automatically discovers
    and displays all rendered .mp4 files from your media/videos/ directory
    in a clean, responsive web interface.
    
    Features:
    - Automatic video discovery and listing
    - In-browser video playback
    - File information (size, date, quality)
    - Real-time refresh functionality
    - Mobile-responsive design
    
    Examples:
    ---------
    Launch on default port (8000):
        manimpro preview
    
    Launch on custom port:
        manimpro preview --port 3000
    
    Launch without opening browser:
        manimpro preview --no-browser
    
    Launch on all interfaces:
        manimpro preview --host 0.0.0.0
    """
    try:
        console.print("[green]🎬 ManimPro Web Viewer[/green]")
        console.print("Starting web-based animation preview...")
        
        preview_web(
            port=port,
            host=host,
            open_browser=not no_browser
        )
        
    except ImportError:
        console.print("[red]❌ Missing dependencies![/red]")
        console.print("The web viewer requires FastAPI and uvicorn.")
        console.print("Install with: [yellow]pip install fastapi uvicorn[/yellow]")
    except OSError as e:
        if "Address already in use" in str(e):
            console.print(f"[red]❌ Port {port} is already in use![/red]")
            console.print(f"Try a different port: [yellow]manimpro preview --port {port + 1}[/yellow]")
        else:
            console.print(f"[red]❌ Network error: {e}[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Web viewer stopped.[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        console.print("Please check your installation and try again.")
