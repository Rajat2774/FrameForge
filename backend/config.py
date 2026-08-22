import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
import logging

logger = logging.getLogger(__name__)

# ── Supported animation capabilities ──────────────────────────────────────────
SUPPORTED_CAPABILITIES = {
    "equations": {
        "label": "Equations & Formulas",
        "description": "Render mathematical equations using MathTex",
        "examples": ["animate the quadratic formula", "show Euler's identity"],
    },
    "geometry": {
        "label": "2D Geometry",
        "description": "Circles, squares, triangles, polygons and transformations",
        "examples": ["blue circle that grows", "square morphs into circle"],
    },
    "2d_graphs": {
        "label": "2D Graphs & Plots",
        "description": "Plot functions on 2D axes",
        "examples": ["plot sin(x)", "graph y = x^2"],
    },
    "transformations": {
        "label": "Transformations",
        "description": "Morph, rotate, scale, shift animations",
        "examples": ["show a square transforming into a circle"],
    },
    "text_animations": {
        "label": "Text Animations",
        "description": "Animate text, titles, and labels",
        "examples": ["animate the word hello", "typing effect for a sentence"],
    },
}

# ── Features that are NOT supported and should be blocked ─────────────────────
UNSUPPORTED_FEATURES = {
    "ThreeDScene": {
        "pattern": "ThreeDScene",
        "message": "3D scenes (ThreeDScene) are not supported.",
        "suggestion": "Try a 2D animation instead — e.g. 'plot sin(x)' or 'show a rotating square'.",
    },
    "Surface": {
        "pattern": "Surface(",
        "message": "3D Surface objects are not supported.",
        "suggestion": "Try plotting a 2D function — e.g. 'graph y = x^2'.",
    },
    "ParametricSurface": {
        "pattern": "ParametricSurface",
        "message": "ParametricSurface (3D) is not supported.",
        "suggestion": "Use a 2D parametric curve or simple plot instead.",
    },
    "Arrow3D": {
        "pattern": "Arrow3D",
        "message": "3D arrows (Arrow3D) are not supported.",
        "suggestion": "Use a regular 2D Arrow instead.",
    },
    "OpenGLRenderer": {
        "pattern": "opengl",
        "message": "OpenGL renderer is not supported.",
        "suggestion": "Use the default Cairo renderer (no changes needed for 2D scenes).",
    },
    "ThreeDAxes": {
        "pattern": "ThreeDAxes",
        "message": "3D axes are not supported.",
        "suggestion": "Use 2D Axes instead — e.g. 'plot a function on a 2D graph'.",
    },
    "Sphere": {
        "pattern": "Sphere(",
        "message": "3D Sphere objects are not supported.",
        "suggestion": "Use a Circle for 2D animations instead.",
    },
    "Cube": {
        "pattern": "Cube(",
        "message": "3D Cube objects are not supported.",
        "suggestion": "Use a Square for 2D animations instead.",
    },
}

# ── Prompt suggestions to show on failures ────────────────────────────────────
FALLBACK_SUGGESTIONS = [
    "animate the quadratic formula",
    "plot sin(x)",
    "show a square transforming into a circle",
    "create a bouncing ball animation",
    "draw a colorful neural network diagram",
    "visualize binary search step by step",
]

# ── Resolve .env path relative to this file, not the working directory ────────
# FIX: Using __file__ makes the path stable regardless of where the app is launched from
_THIS_DIR = Path(__file__).parent.resolve()
_ENV_PATHS = [
    str(_THIS_DIR / ".env"),
    str(_THIS_DIR.parent / ".env"),
]


class Settings(BaseSettings):
    """Application configuration settings."""

    # API Configuration
    groq_api_key: str = Field(..., validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="qwen/qwen3.6-27b", validation_alias="GROQ_MODEL")

    # Server Configuration
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")
    debug: bool = Field(default=False, validation_alias="DEBUG")

    # FIX: Use List[str] and handle comma-separated env var values.
    # If CORS_ORIGINS is set as a JSON array string e.g. '["http://..."]' it parses correctly.
    # If set as comma-separated "http://a,http://b" the validator below splits it.
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        validation_alias="CORS_ORIGINS",
    )

    # File Paths
    temp_dir: str = Field(default="../runtime/temp", validation_alias="TEMP_DIR")
    output_dir: str = Field(default="../runtime/outputs", validation_alias="OUTPUT_DIR")

    # Rendering Configuration
    manim_quality: str = Field(default="l", validation_alias="MANIM_QUALITY")
    manim_format: str = Field(default="mp4", validation_alias="MANIM_FORMAT")
    # FIX: Matched to renderer.py default (was 300 here, 120 in renderer — now both 120,
    # and renderer.render() always receives this value from main.py anyway)
    render_timeout: int = Field(default=120, validation_alias="RENDER_TIMEOUT")

    # Code Generation
    llm_temperature: float = Field(default=0.2, validation_alias="LLM_TEMPERATURE")
    # FIX: Updated to 4000 to match the fix in generator.py (was 2000, caused truncation)
    llm_max_tokens: int = Field(default=4000, validation_alias="LLM_MAX_TOKENS")
    llm_retry_attempts: int = Field(default=3, validation_alias="LLM_RETRY_ATTEMPTS")
    allow_latex: bool = Field(default=False, validation_alias="ALLOW_LATEX")

    # Validation
    strict_validation: bool = Field(default=True, validation_alias="STRICT_VALIDATION")
    max_code_length: int = Field(default=10000, validation_alias="MAX_CODE_LENGTH")

    # Cleanup
    cleanup_enabled: bool = Field(default=True, validation_alias="CLEANUP_ENABLED")
    cleanup_max_age_hours: int = Field(default=24, validation_alias="CLEANUP_MAX_AGE_HOURS")

    # Supabase Storage
    supabase_url: Optional[str] = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, validation_alias="SUPABASE_KEY")
    supabase_bucket: str = Field(default="animations", validation_alias="SUPABASE_BUCKET")

    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, validation_alias="LOG_FILE")

    # FIX: Pydantic v2 style config replaces deprecated inner `class Config`
    model_config = SettingsConfigDict(
        env_file=_ENV_PATHS,
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Allow population by field name as well as alias
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def _validate_and_warn(self) -> "Settings":
        """
        Post-init validation: warn about missing optional-but-critical settings,
        and normalize cors_origins if provided as a comma-separated string.
        """
        # FIX: Warn at startup if Supabase credentials are missing.
        # Without this, the app runs the full pipeline and only fails at Step 5.
        if not self.supabase_url:
            logger.warning(
                "[CONFIG] SUPABASE_URL is not set — Supabase uploads will fail. "
                "Videos will be served locally as fallback."
            )
        if not self.supabase_key:
            logger.warning(
                "[CONFIG] SUPABASE_KEY is not set — Supabase uploads will fail. "
                "Videos will be served locally as fallback."
            )

        # FIX: Handle comma-separated CORS_ORIGINS env var.
        # e.g. CORS_ORIGINS="http://localhost:3000,https://myapp.com"
        # Pydantic won't auto-split this — we do it here.
        if isinstance(self.cors_origins, list) and len(self.cors_origins) == 1:
            single = self.cors_origins[0]
            if "," in single:
                self.cors_origins = [o.strip() for o in single.split(",") if o.strip()]
                logger.info(f"[CONFIG] Parsed comma-separated CORS_ORIGINS: {self.cors_origins}")

        # Warn if render_timeout seems very low
        if self.render_timeout < 60:
            logger.warning(
                f"[CONFIG] render_timeout={self.render_timeout}s is very low — "
                "complex animations may time out. Consider setting RENDER_TIMEOUT=120 or higher."
            )

        logger.info(f"[CONFIG] Settings loaded ✓")
        logger.info(f"[CONFIG] model={self.groq_model} | quality={self.manim_quality} | "
                    f"format={self.manim_format} | timeout={self.render_timeout}s | "
                    f"max_tokens={self.llm_max_tokens}")
        logger.info(f"[CONFIG] Supabase configured: {bool(self.supabase_url and self.supabase_key)}")
        logger.info(f"[CONFIG] CORS origins: {self.cors_origins}")

        return self


# ── Singleton ─────────────────────────────────────────────────────────────────

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment (useful for testing)."""
    global _settings
    _settings = None
    return get_settings()