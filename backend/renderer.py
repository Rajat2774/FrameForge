import subprocess
import os
import sys
from pathlib import Path
from typing import Optional, Dict
import logging
import glob

logger = logging.getLogger(__name__)


class RenderError(Exception):
    """Custom exception for rendering errors."""
    pass


class ManimRenderer:
    """Handles rendering Manim animations."""
    
    def __init__(
        self,
        output_dir: str = "../runtime/outputs",
        quality: str = "l",  # l=low, m=medium, h=high, k=4k
        preview: bool = True,
        format: str = "mp4"
    ):
        """
        Initialize Manim renderer.
        
        Args:
            output_dir: Directory for output videos
            quality: Quality flag (l/m/h/k)
            preview: Whether to preview video after rendering
            format: Output format (mp4, mov, gif)
        """
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.preview = preview
        self.format = format
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"Initialized ManimRenderer: "
            f"output_dir={self.output_dir}, quality={quality}, format={format}"
        )
    
    def render(
        self,
        file_path: str,
        scene_name: str,
        timeout: int = 300
    ) -> Dict[str, str]:
        """
        Render a Manim scene.
        
        Args:
            file_path: Path to Python file containing scene
            scene_name: Name of Scene class to render
            timeout: Maximum seconds to wait for render (default 5 minutes)
            
        Returns:
            Dictionary with 'video_path' and 'output_dir'
            
        Raises:
            RenderError: If rendering fails
        """
        logger.info(f"Rendering scene '{scene_name}' from {file_path}")
        
        # Validate inputs
        if not os.path.exists(file_path):
            raise RenderError(f"File not found: {file_path}")
        
        # Build manim command
        quality_flag = f"-q{self.quality}"
        preview_flag = "-p" if self.preview else ""
        
        command = [
            sys.executable,
            "-m",
            "manim",
            quality_flag,
            preview_flag,
            file_path,
            scene_name,
            "--media_dir",
            str(self.output_dir),
            "--format",
            self.format
        ]
        
        # Remove empty strings from command
        command = [c for c in command if c]
        
        logger.info(f"Executing: {' '.join(command)}")
        
        try:
            # Run manim with timeout
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # Don't raise on non-zero exit
            )
            
            # Log output
            if result.stdout:
                logger.debug(f"STDOUT: {result.stdout}")
            if result.stderr:
                logger.debug(f"STDERR: {result.stderr}")
            
            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                logger.error(f"Rendering failed with code {result.returncode}: {error_msg}")
                raise RenderError(f"Manim rendering failed: {error_msg}")
            
            # Find the generated video file
            video_path = self._find_video_file(scene_name)
            
            if not video_path:
                raise RenderError(
                    f"Video file not found after rendering. "
                    f"Looked in: {self.output_dir}"
                )
            
            logger.info(f"Successfully rendered: {video_path}")
            
            return {
                "video_path": str(video_path),
                "output_dir": str(self.output_dir),
                "scene_name": scene_name
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Rendering timed out after {timeout} seconds")
            raise RenderError(f"Rendering timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Rendering failed: {str(e)}")
            raise RenderError(f"Rendering failed: {str(e)}")
    
    def _find_video_file(self, scene_name: str) -> Optional[Path]:
        """
        Find the rendered video file.
        
        Manim creates videos in: output_dir/videos/[scene_file]/[quality]/[scene_name].mp4
        
        Args:
            scene_name: Name of the scene
            
        Returns:
            Path to video file if found, None otherwise
        """
        # Search for video files with scene name
        patterns = [
            f"**/{scene_name}.{self.format}",
            f"**/*{scene_name}*.{self.format}",
        ]
        
        for pattern in patterns:
            matches = list(self.output_dir.glob(pattern))
            if matches:
                # Return the most recently created file
                return max(matches, key=lambda p: p.stat().st_mtime)
        
        return None
    
    def get_available_qualities(self) -> list:
        """Return list of available quality settings."""
        return [
            {"flag": "l", "name": "Low (480p)", "resolution": "854x480"},
            {"flag": "m", "name": "Medium (720p)", "resolution": "1280x720"},
            {"flag": "h", "name": "High (1080p)", "resolution": "1920x1080"},
            {"flag": "k", "name": "4K (2160p)", "resolution": "3840x2160"}
        ]


# Backwards compatibility function
def render_scene(file_path: str, scene_name: str) -> str:
    """
    Legacy function for backwards compatibility.
    
    Args:
        file_path: Path to Python file
        scene_name: Name of scene to render
        
    Returns:
        Output directory path
    """
    renderer = ManimRenderer()
    result = renderer.render(file_path, scene_name)
    return result["output_dir"]