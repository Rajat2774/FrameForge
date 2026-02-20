"""
ManimRenderer — handles rendering Manim animations with structured error handling.
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class RenderError(Exception):
    """Custom exception for rendering errors with structured info."""

    def __init__(self, message: str, reason: Optional[str] = None):
        self.message = message
        self.reason = reason
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "status": "error",
            "stage": "rendering",
            "message": self.message,
            "reason": self.reason,
            "suggestion": self._suggest(),
        }

    def _suggest(self) -> str:
        msg = (self.message + " " + (self.reason or "")).lower()
        if "latex" in msg or "tex" in msg:
            return (
                "LaTeX rendering failed. Try a prompt that doesn't require "
                "mathematical typesetting, or check your LaTeX installation."
            )
        if "timeout" in msg:
            return (
                "The animation took too long to render. "
                "Try a simpler prompt with fewer elements."
            )
        if "opengl" in msg:
            return "OpenGL is not available. Try a 2D animation instead."
        if "memory" in msg or "killed" in msg:
            return "The renderer ran out of memory. Try a simpler animation."
        return "Try a simpler animation prompt."


class ManimRenderer:
    """Handles rendering Manim animations."""

    def __init__(
        self,
        output_dir: str = "../runtime/outputs",
        quality: str = "l",
        # FIX: Default preview=False — in a server environment, preview=True
        # tries to open a media player which hangs or crashes the subprocess
        preview: bool = False,
        video_format: str = "mp4",  # FIX: Renamed from 'format' to avoid shadowing built-in
    ):
        """
        Initialize Manim renderer.

        Args:
            output_dir:    Directory for output videos
            quality:       Quality flag (l=480p / m=720p / h=1080p / k=4K)
            preview:       Whether to open video in media player after render.
                           MUST be False in server/headless environments.
            video_format:  Output format (mp4, mov, gif)
        """
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.preview = preview
        self.video_format = video_format

        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"[RENDERER] Initialized | output_dir={self.output_dir} | "
            f"quality={quality} | format={video_format} | preview={preview}"
        )

        if preview:
            logger.warning(
                "[RENDERER] preview=True is set — this will attempt to open a media player. "
                "Set preview=False in server/headless environments."
            )

    def render(
        self,
        file_path: str,
        scene_name: str,
        timeout: int = 120,
    ) -> Dict[str, str]:
        """
        Render a Manim scene.

        Args:
            file_path:  Path to Python file containing scene
            scene_name: Name of Scene class to render
            timeout:    Maximum seconds to wait for render (default 120s)

        Returns:
            Dictionary with 'video_path', 'output_dir', 'scene_name'

        Raises:
            RenderError: If rendering fails (with structured reason)
        """
        logger.info(f"[RENDER] Starting render | scene='{scene_name}' | file='{file_path}'")
        logger.info(f"[RENDER] Settings: quality={self.quality} | format={self.video_format} | timeout={timeout}s")

        # Validate inputs
        if not os.path.exists(file_path):
            raise RenderError(
                f"File not found: {file_path}",
                reason="The generated code file could not be located.",
            )
        logger.info(f"[RENDER] Input file exists ✓")

        # Build manim command
        # FIX: Only add -p flag when preview is explicitly requested
        command = [
            sys.executable,
            "-m", "manim",
            f"-q{self.quality}",
            file_path,
            scene_name,
            "--media_dir", str(self.output_dir),
            "--format", self.video_format,
        ]

        if self.preview:
            command.append("-p")

        logger.info(f"[RENDER] Command: {' '.join(command)}")

        process = None
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.info(f"[RENDER] Subprocess started | PID={process.pid}")

            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # FIX: Kill the process on timeout so it doesn't linger as a zombie
                logger.error(f"[RENDER] Timeout after {timeout}s — killing PID {process.pid}")
                process.kill()
                process.communicate()  # Drain pipes after kill
                raise RenderError(
                    message=f"Rendering timed out after {timeout} seconds.",
                    reason="The animation was too complex to render in time.",
                )

            # FIX: Log stdout/stderr at INFO on failure, DEBUG on success
            # so errors are visible without needing DEBUG-level logging
            if process.returncode != 0:
                logger.error(f"[RENDER] Manim process exited with code {process.returncode}")
                if stdout:
                    logger.error(f"[RENDER] STDOUT:\n{stdout}")
                if stderr:
                    logger.error(f"[RENDER] STDERR:\n{stderr}")

                error_output = stderr or stdout or "Unknown error"
                reason = self._classify_error(error_output)
                raise RenderError(
                    message="Manim rendering failed.",
                    reason=reason,
                )
            else:
                logger.info(f"[RENDER] Manim process completed successfully (exit 0)")
                if stdout:
                    logger.debug(f"[RENDER] STDOUT:\n{stdout}")
                if stderr:
                    # Manim often writes progress to stderr even on success
                    logger.debug(f"[RENDER] STDERR:\n{stderr}")

            # Find the generated video file
            logger.info(f"[RENDER] Searching for output video file...")
            video_path = self._find_video_file(scene_name)

            if not video_path:
                logger.error(
                    f"[RENDER] Video file not found after render completed. "
                    f"Searched in: {self.output_dir} | scene_name='{scene_name}' | format={self.video_format}"
                )
                # Log the directory tree to aid debugging
                self._log_output_dir_tree()
                raise RenderError(
                    message="Video file not found after rendering.",
                    reason=f"Searched for '{scene_name}.{self.video_format}' in {self.output_dir}",
                )

            # FIX: Log the full resolved path so frontend path mismatches are traceable
            logger.info(f"[RENDER] Video found at: {video_path} ✓")
            logger.info(f"[RENDER] File size: {video_path.stat().st_size} bytes")

            return {
                "video_path": str(video_path),
                "output_dir": str(self.output_dir),
                "scene_name": scene_name,
            }

        except RenderError:
            raise
        except Exception as e:
            logger.error(f"[RENDER] Unexpected error | type={type(e).__name__} | error={str(e)}")
            raise RenderError(
                message="An unexpected error occurred during rendering.",
                reason=str(e),
            ) from e

    # ── private helpers ───────────────────────────────────────────────────────

    def _classify_error(self, error_output: str) -> str:
        """Classify a rendering error into a human-friendly reason."""
        lower = error_output.lower()
        if "latex" in lower or "xelatex" in lower or "pdflatex" in lower:
            return (
                "LaTeX compilation failed. The generated code contains "
                "mathematical expressions that could not be rendered."
            )
        if "opengl" in lower:
            return "OpenGL is required but not available in this environment."
        if "no scene" in lower or "not found" in lower:
            return "The scene class could not be found in the generated code."
        if "import" in lower and "error" in lower:
            return "A required Python module could not be imported."
        if "memory" in lower or "killed" in lower:
            return "The renderer ran out of memory."
        return error_output[:300]

    def _find_video_file(self, scene_name: str) -> Optional[Path]:
        """
        Find the rendered video file by scene name.

        Manim output path: output_dir/videos/<script_stem>/<quality_dir>/<SceneName>.mp4

        FIX: Prefer exact filename match before falling back to glob wildcard,
        to avoid returning a wrong file when scene names share substrings
        (e.g. 'Wave' matching 'SineWave').
        """
        # Pass 1: Exact filename match
        exact_pattern = f"**/{scene_name}.{self.video_format}"
        exact_matches = list(self.output_dir.glob(exact_pattern))
        if exact_matches:
            # If multiple (e.g. from prior runs), take the newest
            result = max(exact_matches, key=lambda p: p.stat().st_mtime)
            logger.info(f"[RENDER] Exact match found: {result}")
            return result

        # Pass 2: Fuzzy match — only if exact fails
        # FIX: Use word-boundary-like check: scene_name must appear as a full
        # path component, not just a substring
        fuzzy_pattern = f"**/*{scene_name}*.{self.video_format}"
        fuzzy_matches = [
            p for p in self.output_dir.glob(fuzzy_pattern)
            # Ensure the stem is exactly scene_name, not a superstring
            if p.stem == scene_name or p.stem.endswith(f"_{scene_name}") or p.stem.startswith(f"{scene_name}_")
        ]
        if fuzzy_matches:
            result = max(fuzzy_matches, key=lambda p: p.stat().st_mtime)
            logger.info(f"[RENDER] Fuzzy match found: {result}")
            return result

        logger.warning(f"[RENDER] No video file found for scene='{scene_name}' format='{self.video_format}'")
        return None

    def _log_output_dir_tree(self):
        """Log the contents of the output directory to aid debugging video-not-found issues."""
        try:
            all_files = list(self.output_dir.rglob("*"))
            if not all_files:
                logger.warning(f"[RENDER] Output directory is empty: {self.output_dir}")
            else:
                logger.info(f"[RENDER] Output directory contents ({len(all_files)} files):")
                for f in sorted(all_files)[:30]:  # Cap at 30 to avoid log spam
                    logger.info(f"[RENDER]   {f}")
        except Exception as e:
            logger.warning(f"[RENDER] Could not list output directory: {e}")

    def get_available_qualities(self) -> list:
        """Return list of available quality settings."""
        return [
            {"flag": "l", "name": "Low (480p)", "resolution": "854x480"},
            {"flag": "m", "name": "Medium (720p)", "resolution": "1280x720"},
            {"flag": "h", "name": "High (1080p)", "resolution": "1920x1080"},
            {"flag": "k", "name": "4K (2160p)", "resolution": "3840x2160"},
        ]


# Backwards compatibility
def render_scene(file_path: str, scene_name: str) -> str:
    """Legacy wrapper. Returns output directory path."""
    renderer = ManimRenderer()
    result = renderer.render(file_path, scene_name)
    return result["output_dir"]