#!/usr/bin/env python3
"""
ManimPro Web Viewer - Browser-based Animation Preview
====================================================

This module provides a lightweight web interface for previewing rendered ManimPro animations
directly in your browser. It automatically discovers and displays all .mp4 files from your
media/videos/ directory with a clean, responsive interface.

Usage:
------
From command line:
    manimpro preview

From Python:
    from manimpro.web_viewer import preview_web
    preview_web()

Features:
---------
- Automatic discovery of rendered animations
- Clean, responsive web interface with TailwindCSS
- Real-time refresh without server restart
- Cross-platform compatibility (Windows, macOS, Linux)
- Lightweight FastAPI backend
- No external dependencies beyond FastAPI

The web server runs on http://localhost:8000 by default and provides:
- Video gallery with thumbnails
- Direct video playback in browser
- File information (size, date, resolution)
- Refresh functionality for new renders
- Mobile-responsive design

Author: ManimPro Team
License: MIT
"""

from __future__ import annotations

import os
import sys
import webbrowser
import subprocess
import base64
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:
    uvicorn = None
    FastAPI = None
    print("FastAPI not installed. Install with: pip install fastapi uvicorn")

from . import config, console


class ManimProWebViewer:
    """Web viewer for ManimPro rendered animations."""
    
    def __init__(self, port: int = 8000, host: str = "127.0.0.1"):
        self.port = port
        self.host = host
        self.app = None
        self.media_dir = Path(config["media_dir"] if "media_dir" in config else "media")
        self.videos_dir = self.media_dir / "videos"
        self.thumbnails_dir = self.media_dir / "thumbnails"
        self.thumbnails_dir.mkdir(exist_ok=True)
        
    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        app = FastAPI(
            title="ManimPro Web Viewer",
            description="Preview your rendered ManimPro animations in the browser",
            version="1.0.0"
        )
        
        # Serve static video files
        if self.videos_dir.exists():
            app.mount("/videos", StaticFiles(directory=str(self.videos_dir)), name="videos")
        
        # Serve thumbnail files
        if self.thumbnails_dir.exists():
            app.mount("/thumbnails", StaticFiles(directory=str(self.thumbnails_dir)), name="thumbnails")
        
        @app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """Main page with video gallery."""
            return self.generate_html()
        
        @app.get("/api/videos")
        async def get_videos():
            """API endpoint to get list of videos."""
            return self.get_video_list()
        
        @app.get("/api/refresh")
        async def refresh_videos():
            """API endpoint to refresh video list."""
            return {"status": "success", "videos": self.get_video_list()}
        
        @app.get("/api/generate-thumbnails")
        async def generate_all_thumbnails():
            """API endpoint to generate thumbnails for all videos."""
            videos = self.get_video_list()
            generated = 0
            for video in videos:
                if not video['thumbnail']:
                    video_path = self.videos_dir / video['path']
                    if self.generate_thumbnail(video_path):
                        generated += 1
            return {"status": "success", "generated": generated, "total": len(videos)}
        
        @app.get("/video/{file_path:path}")
        async def serve_video(file_path: str):
            """Serve video files directly."""
            video_path = self.videos_dir / file_path
            if video_path.exists() and video_path.suffix.lower() == '.mp4':
                return FileResponse(video_path)
            return {"error": "Video not found"}
        
        return app
    
    def get_video_list(self) -> list[dict[str, Any]]:
        """Get list of all rendered video files with metadata."""
        videos = []
        
        if not self.videos_dir.exists():
            return videos
        
        # Find all .mp4 files recursively
        for video_file in self.videos_dir.rglob("*.mp4"):
            try:
                stat = video_file.stat()
                relative_path = video_file.relative_to(self.videos_dir)
                
                # Extract scene and quality info from path
                path_parts = relative_path.parts
                scene_name = path_parts[0] if path_parts else "Unknown"
                quality = path_parts[1] if len(path_parts) > 1 else "Unknown"
                
                # Generate thumbnail
                thumbnail_url = self.generate_thumbnail(video_file)
                
                videos.append({
                    "name": video_file.stem,
                    "path": str(relative_path).replace("\\", "/"),
                    "full_path": str(video_file),
                    "scene": scene_name,
                    "quality": quality,
                    "size": self.format_file_size(stat.st_size),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "modified_timestamp": stat.st_mtime,
                    "thumbnail": thumbnail_url
                })
            except (OSError, ValueError):
                continue
        
        # Sort by modification time (newest first)
        videos.sort(key=lambda x: x["modified_timestamp"], reverse=True)
        return videos
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def generate_thumbnail(self, video_path: Path) -> str | None:
        """Generate thumbnail for video using ffmpeg."""
        try:
            # Create thumbnail filename
            relative_path = video_path.relative_to(self.videos_dir)
            thumbnail_name = str(relative_path).replace("\\", "_").replace("/", "_").replace(".mp4", ".jpg")
            thumbnail_path = self.thumbnails_dir / thumbnail_name
            
            # Check if thumbnail already exists and is newer than video
            if thumbnail_path.exists():
                video_mtime = video_path.stat().st_mtime
                thumb_mtime = thumbnail_path.stat().st_mtime
                if thumb_mtime > video_mtime:
                    return f"/thumbnails/{thumbnail_name}"
            
            # Generate thumbnail using ffmpeg
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-ss", "00:00:01",  # Take frame at 1 second
                "-vframes", "1",
                "-vf", "scale=320:180",  # 16:9 aspect ratio thumbnail
                "-y",  # Overwrite existing
                str(thumbnail_path)
            ]
            
            # Run ffmpeg quietly
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and thumbnail_path.exists():
                return f"/thumbnails/{thumbnail_name}"
            else:
                console.print(f"[yellow]Warning: Could not generate thumbnail for {video_path.name}[/yellow]")
                return None
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # ffmpeg not available or failed
            return None
        except Exception as e:
            console.print(f"[yellow]Warning: Thumbnail generation failed for {video_path.name}: {e}[/yellow]")
            return None
    
    def generate_html(self) -> str:
        """Generate the main HTML page."""
        videos = self.get_video_list()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ManimPro Web Viewer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'manim-blue': '#3B82F6',
                        'manim-purple': '#8B5CF6',
                    }}
                }}
            }}
        }}
    </script>
    <style>
        .gradient-bg {{
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        }}
        .video-card {{
            transition: all 0.3s ease;
        }}
        .video-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold">ManimPro Web Viewer</h1>
                    <p class="text-blue-100 mt-1">Preview your rendered animations</p>
                </div>
                <div class="flex items-center space-x-4">
                    <button onclick="generateThumbnails()" 
                            class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-all duration-200 flex items-center space-x-2 mr-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <span>Generate Thumbnails</span>
                    </button>
                    <button onclick="refreshVideos()" 
                            class="bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-all duration-200 flex items-center space-x-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        <span>Refresh</span>
                    </button>
                    <div class="text-sm bg-white bg-opacity-20 px-3 py-2 rounded-lg">
                        {len(videos)} videos found
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <div id="loading" class="hidden text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-manim-blue"></div>
            <p class="mt-2 text-gray-600">Refreshing videos...</p>
        </div>
        
        <div id="video-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {self.generate_video_cards(videos)}
        </div>
        
        {self.generate_empty_state() if not videos else ""}
    </main>

    <!-- Video Modal -->
    <div id="videoModal" class="fixed inset-0 bg-black bg-opacity-75 hidden z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-lg max-w-4xl w-full max-h-full overflow-hidden">
            <div class="flex justify-between items-center p-4 border-b">
                <h3 id="modalTitle" class="text-lg font-semibold"></h3>
                <button onclick="closeModal()" class="text-gray-500 hover:text-gray-700">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div class="p-4">
                <video id="modalVideo" controls class="w-full h-auto max-h-96">
                    <source src="" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <div id="modalInfo" class="mt-4 text-sm text-gray-600"></div>
            </div>
        </div>
    </div>

    <script>
        function refreshVideos() {{
            const loading = document.getElementById('loading');
            const grid = document.getElementById('video-grid');
            
            loading.classList.remove('hidden');
            grid.style.opacity = '0.5';
            
            fetch('/api/refresh')
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        location.reload(); // Simple reload for now
                    }}
                }})
                .catch(error => {{
                    console.error('Error refreshing videos:', error);
                    loading.classList.add('hidden');
                    grid.style.opacity = '1';
                }});
        }}
        
        function generateThumbnails() {{
            const loading = document.getElementById('loading');
            const grid = document.getElementById('video-grid');
            
            loading.classList.remove('hidden');
            grid.style.opacity = '0.5';
            
            // Update loading text
            const loadingText = loading.querySelector('p');
            loadingText.textContent = 'Generating thumbnails...';
            
            fetch('/api/generate-thumbnails')
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        console.log(`Generated ${{data.generated}} thumbnails out of ${{data.total}} videos`);
                        location.reload(); // Reload to show new thumbnails
                    }}
                }})
                .catch(error => {{
                    console.error('Error generating thumbnails:', error);
                    loading.classList.add('hidden');
                    grid.style.opacity = '1';
                    loadingText.textContent = 'Refreshing videos...';
                }});
        }}
        
        function playVideo(path, name, info) {{
            const modal = document.getElementById('videoModal');
            const video = document.getElementById('modalVideo');
            const title = document.getElementById('modalTitle');
            const infoDiv = document.getElementById('modalInfo');
            
            video.src = '/video/' + path;
            title.textContent = name;
            infoDiv.innerHTML = info;
            modal.classList.remove('hidden');
        }}
        
        function closeModal() {{
            const modal = document.getElementById('videoModal');
            const video = document.getElementById('modalVideo');
            
            video.pause();
            video.src = '';
            modal.classList.add('hidden');
        }}
        
        // Close modal on escape key
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeModal();
            }}
        }});
        
        // Close modal on background click
        document.getElementById('videoModal').addEventListener('click', function(event) {{
            if (event.target === this) {{
                closeModal();
            }}
        }});
    </script>
</body>
</html>
        """
        return html
    
    def generate_video_cards(self, videos: list[dict[str, Any]]) -> str:
        """Generate HTML for video cards."""
        if not videos:
            return ""
        
        cards_html = ""
        for video in videos:
            info_html = f"""
                <strong>Scene:</strong> {video['scene']}<br>
                <strong>Quality:</strong> {video['quality']}<br>
                <strong>Size:</strong> {video['size']}<br>
                <strong>Modified:</strong> {video['modified']}
            """
            
            # Create thumbnail section
            if video['thumbnail']:
                thumbnail_section = f"""
                <div class="aspect-video bg-gray-200 relative overflow-hidden">
                    <img src="{video['thumbnail']}" alt="{video['name']} thumbnail" 
                         class="w-full h-full object-cover">
                    <div class="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                        <svg class="w-12 h-12 text-white opacity-0 hover:opacity-100 transition-opacity duration-200" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z"/>
                        </svg>
                    </div>
                </div>"""
            else:
                thumbnail_section = f"""
                <div class="aspect-video bg-gradient-to-br from-manim-blue to-manim-purple flex items-center justify-center">
                    <svg class="w-16 h-16 text-white opacity-80" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                </div>"""
            
            cards_html += f"""
            <div class="video-card bg-white rounded-lg shadow-md overflow-hidden cursor-pointer"
                 onclick="playVideo('{video['path']}', '{video['name']}', '{info_html}')">
                {thumbnail_section}
                <div class="p-4">
                    <h3 class="font-semibold text-gray-800 truncate" title="{video['name']}">{video['name']}</h3>
                    <div class="mt-2 space-y-1">
                        <p class="text-sm text-gray-600">
                            <span class="font-medium">Scene:</span> {video['scene']}
                        </p>
                        <p class="text-sm text-gray-600">
                            <span class="font-medium">Quality:</span> {video['quality']}
                        </p>
                        <div class="flex justify-between items-center mt-3">
                            <span class="text-xs text-gray-500">{video['size']}</span>
                            <span class="text-xs text-gray-500">{video['modified'].split()[0]}</span>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        return cards_html
    
    def generate_empty_state(self) -> str:
        """Generate HTML for empty state when no videos are found."""
        return """
        <div class="col-span-full text-center py-16">
            <svg class="mx-auto h-24 w-24 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">No videos found</h3>
            <p class="mt-2 text-gray-500 max-w-md mx-auto">
                Render some animations with ManimPro first, then refresh this page to see them here.
            </p>
            <div class="mt-6">
                <button onclick="refreshVideos()" 
                        class="bg-manim-blue hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors duration-200">
                    Refresh Videos
                </button>
            </div>
        </div>
        """
    
    def start_server(self, open_browser: bool = True) -> None:
        """Start the web server."""
        if not uvicorn or not FastAPI:
            console.print("[red]Error: FastAPI and uvicorn are required for web preview.[/red]")
            console.print("Install with: [yellow]pip install fastapi uvicorn[/yellow]")
            return
        
        self.app = self.create_app()
        
        console.print(f"[green]Starting ManimPro Web Viewer...[/green]")
        console.print(f"[blue]Server running at: http://{self.host}:{self.port}[/blue]")
        console.print(f"[gray]Media directory: {self.videos_dir}[/gray]")
        
        if open_browser:
            webbrowser.open(f"http://{self.host}:{self.port}")
        
        try:
            uvicorn.run(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=False
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped by user.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error starting server: {e}[/red]")


def preview_web(port: int = 8000, host: str = "127.0.0.1", open_browser: bool = True) -> None:
    """
    Launch the ManimPro web viewer.
    
    Args:
        port: Port to run the server on (default: 8000)
        host: Host to bind to (default: 127.0.0.1)
        open_browser: Whether to automatically open browser (default: True)
    
    Example:
        >>> from manimpro.web_viewer import preview_web
        >>> preview_web()  # Starts server on http://localhost:8000
    """
    viewer = ManimProWebViewer(port=port, host=host)
    viewer.start_server(open_browser=open_browser)


if __name__ == "__main__":
    # Allow running directly: python -m manimpro.web_viewer
    preview_web()
