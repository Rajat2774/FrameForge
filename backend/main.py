from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import logging
from pathlib import Path
from typing import Optional
import os

from generator import ManimCodeGenerator, ManimCodeGeneratorError
from code_writer import ManimCodeWriter, CodeWriterError
from renderer import ManimRenderer, RenderError
from validator import ManimCodeValidator
from code_fixer import ManimCodeFixer, LATEX_AVAILABLE
from templates.template_manager import TemplateManager
from storage.supabase_client import upload_video, SupabaseStorageError
from storage.posts_client import create_post, list_posts, PostsClientError
from config import (
    get_settings,
    SUPPORTED_CAPABILITIES,
    UNSUPPORTED_FEATURES,
    FALLBACK_SUGGESTIONS,
)

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        *(
            [logging.FileHandler(settings.log_file)]
            if settings.log_file
            else [logging.NullHandler()]
        ),
    ],
)
logger = logging.getLogger(__name__)

# ── Component initialization ──────────────────────────────────────────────────

template_manager = TemplateManager()
generator = ManimCodeGenerator(
    model=settings.groq_model,
    allow_latex=settings.allow_latex,
)
code_writer = ManimCodeWriter(base_dir=settings.temp_dir)

# FIX: Single shared renderer instance — previously two instances were created
# (one at module level, one inside generate_animation) which could cause
# format/settings mismatches where the video was rendered in one format
# but the wrong instance searched for it.
renderer = ManimRenderer(
    output_dir=settings.output_dir,
    quality=settings.manim_quality,
    video_format=settings.manim_format,  # FIX: Use correct param name from renderer.py fix
    preview=False,                        # FIX: Explicit False for server environments
)

validator = ManimCodeValidator(strict_mode=settings.strict_validation)
code_fixer = ManimCodeFixer(auto_fix=True, disable_latex=not settings.allow_latex)


# ── Lifespan (replaces deprecated @app.on_event) ─────────────────────────────

# FIX: Use lifespan context manager instead of deprecated @app.on_event("startup/shutdown")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 60)
    logger.info("FrameForge Manim Animation Generator Starting")
    logger.info("=" * 60)
    logger.info(f"Model: {settings.groq_model}")
    logger.info(f"LaTeX available: {LATEX_AVAILABLE}")
    logger.info(f"Templates loaded: {len(template_manager.list_templates())}")
    logger.info(f"Output directory: {settings.output_dir}")
    logger.info(f"Quality: {settings.manim_quality}")
    logger.info(f"Format: {settings.manim_format}")
    logger.info(f"CORS origins: {settings.cors_origins}")

    Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    logger.info("Directories initialized. Ready to accept requests!")

    yield

    # Shutdown
    logger.info("Shutting down FrameForge...")
    if settings.cleanup_enabled:
        logger.info("Running final cleanup...")
        code_writer.cleanup_old_files(max_age_hours=settings.cleanup_max_age_hours)


app = FastAPI(
    title="FrameForge - Manim Animation Generator",
    description="Generate Manim animations from text prompts",
    version="2.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500, description="Animation description")
    quality: Optional[str] = Field(default=None, description="Quality override (l/m/h/k)")


class AnimationResponse(BaseModel):
    status: str = "success"
    message: str
    scene_name: str
    video_url: str
    code: Optional[str] = None
    warnings: Optional[list] = None
    template_used: Optional[str] = None


# FIX: Proper request body model for validate endpoint
class ValidateCodeRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Manim Python code to validate")


# ── Community Posts Models ────────────────────────────────────────────────────

class PostCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Poster's display name")
    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    rating: int = Field(..., ge=1, le=5, description="Star rating 1-5")
    video_url: str = Field(..., description="Supabase public URL of the animation")


# ── Helper ────────────────────────────────────────────────────────────────────

def _error_json(
    status_code: int,
    stage: str,
    message: str,
    suggestion: Optional[str] = None,
    details: Optional[str] = None,
) -> JSONResponse:
    body = {
        "status": "error",
        "stage": stage,
        "message": message,
        "suggestion": suggestion or "Try a simpler animation prompt.",
        "suggestions": FALLBACK_SUGGESTIONS,
    }
    if details:
        body["details"] = details
    logger.error(f"[PIPELINE] Error response | stage={stage} | message={message} | details={details}")
    return JSONResponse(status_code=status_code, content=body)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "FrameForge Manim Animation Generator",
        "version": "2.2.0",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "latex_available": LATEX_AVAILABLE,
        "templates_loaded": len(template_manager.list_templates()),
        "settings": {
            "model": settings.groq_model,
            "quality": settings.manim_quality,
            "output_dir": settings.output_dir,
        },
    }


@app.get("/capabilities")
async def get_capabilities():
    return {
        "supported": SUPPORTED_CAPABILITIES,
        "unsupported_features": list(UNSUPPORTED_FEATURES.keys()),
        "suggestions": FALLBACK_SUGGESTIONS,
        "templates": template_manager.list_templates(),
        "latex_available": LATEX_AVAILABLE,
    }


@app.post("/generate-animation")
async def generate_animation(
    request: PromptRequest,
    background_tasks: BackgroundTasks,
):
    """
    Generate a Manim animation from a text prompt.

    Pipeline:
      prompt → TemplateManager → (template or LLM) → fixer → validator → writer → renderer → Supabase
    """
    logger.info(f"[PIPELINE] ── New request ──────────────────────────────")
    logger.info(f"[PIPELINE] Prompt: '{request.prompt}'")
    logger.info(f"[PIPELINE] Quality override: {request.quality or 'none (using default)'}")

    template_key = None
    file_path = None        # Track for cleanup
    used_local_fallback = False  # FIX: Track whether we're serving locally

    try:
        # ── Step 0: Check templates ────────────────────────────────────────
        logger.info("[PIPELINE] Step 0: Checking template cache...")
        match = await template_manager.match(request.prompt, groq_client=generator.client)

        if match:
            template_key, code, scene_name, template_desc = match
            logger.info(f"[PIPELINE] Step 0: Template matched → '{template_key}': {template_desc}")
        else:
            logger.info("[PIPELINE] Step 0: No template match — proceeding to LLM")

            # ── Step 1: LLM code generation ────────────────────────────────
            logger.info("[PIPELINE] Step 1: Generating code via LLM...")
            code = generator.generate(
                request.prompt,
                temperature=settings.llm_temperature,
            )
            logger.info(f"[PIPELINE] Step 1: Generated {len(code)} chars of code")

        # ── Step 1.5: Auto-fix ─────────────────────────────────────────────
        logger.info("[PIPELINE] Step 1.5: Running auto-fixer...")
        fixed_code, fixes_applied = code_fixer.fix_code(code)
        if fixes_applied:
            logger.info(f"[PIPELINE] Step 1.5: Applied fixes: {fixes_applied}")
            code = fixed_code
        else:
            logger.info("[PIPELINE] Step 1.5: No fixes needed")

        # ── Step 2: Validate ───────────────────────────────────────────────
        logger.info("[PIPELINE] Step 2: Validating code...")
        validation_result = validator.validate(code)

        if not validation_result.is_valid:
            logger.error(f"[PIPELINE] Step 2: Validation FAILED → {validation_result.errors}")
            return _error_json(
                status_code=400,
                stage="validation",
                message=validation_result.errors[0] if validation_result.errors else "Validation failed.",
                suggestion=validation_result.suggestion,
            )

        # ── Step 2.5: Complexity / unsupported check ───────────────────────
        logger.info("[PIPELINE] Step 2.5: Checking complexity...")
        complexity_issue = validator.check_complexity(code, request.prompt)
        if complexity_issue:
            logger.warning(f"[PIPELINE] Step 2.5: Complexity issue → {complexity_issue}")
            return _error_json(
                status_code=400,
                stage="validation",
                message=complexity_issue,
                suggestion="Try a simpler 2D animation instead.",
            )

        logger.info(f"[PIPELINE] Step 2: Validation PASSED | scene='{validation_result.scene_name}'")
        if validation_result.warnings:
            logger.warning(f"[PIPELINE] Step 2: Warnings → {validation_result.warnings}")

        # ── Step 3: Save code to file ──────────────────────────────────────
        logger.info("[PIPELINE] Step 3: Writing code to temp file...")
        file_path = code_writer.save_code(code, use_uuid=True)
        logger.info(f"[PIPELINE] Step 3: Code saved to → {file_path}")

        # ── Step 4: Render ─────────────────────────────────────────────────
        logger.info("[PIPELINE] Step 4: Rendering animation...")

        # FIX: Reuse the shared renderer but allow per-request quality override
        # instead of creating a new ManimRenderer instance each request
        if request.quality and request.quality != settings.manim_quality:
            logger.info(f"[PIPELINE] Step 4: Quality override requested: {request.quality}")
            active_renderer = ManimRenderer(
                output_dir=settings.output_dir,
                quality=request.quality,
                video_format=settings.manim_format,
                preview=False,
            )
        else:
            active_renderer = renderer  # Use shared instance

        render_result = active_renderer.render(
            file_path,
            validation_result.scene_name,
            timeout=settings.render_timeout,
        )

        video_path = render_result["video_path"]
        logger.info(f"[PIPELINE] Step 4: Render complete → {video_path}")

        # ── Step 5: Upload to Supabase ─────────────────────────────────────
        logger.info("[PIPELINE] Step 5: Uploading to Supabase Storage...")
        video_url = None

        try:
            video_url = upload_video(video_path)

            # FIX: Log the exact URL being returned to the frontend
            # This is critical for debugging "video not visible" issues
            logger.info(f"[PIPELINE] Step 5: Supabase upload complete")
            logger.info(f"[PIPELINE] Step 5: Video URL returned to frontend → {video_url}")

            # FIX: Validate URL before deleting local file
            if not video_url or not video_url.startswith("http"):
                raise SupabaseStorageError(
                    f"Supabase returned invalid URL: '{video_url}'"
                )

            # Only delete local files after confirmed valid URL
            logger.info("[PIPELINE] Step 5: URL validated — cleaning up local files")
            try:
                Path(video_path).unlink()
                logger.info(f"[PIPELINE] Step 5: Deleted local video → {video_path}")
            except OSError as e:
                logger.warning(f"[PIPELINE] Step 5: Could not delete local video: {e}")

            try:
                if file_path and os.path.exists(file_path):
                    Path(file_path).unlink()
                    logger.info(f"[PIPELINE] Step 5: Deleted local code file → {file_path}")
                    file_path = None  # Mark as cleaned up
            except OSError as e:
                logger.warning(f"[PIPELINE] Step 5: Could not delete local code file: {e}")

        except SupabaseStorageError as e:
            # FIX: Fall back to local serving — but do NOT delete the local file
            logger.error(f"[PIPELINE] Step 5: Supabase upload FAILED → {e} — falling back to local serving")
            video_filename = Path(video_path).name
            video_url = f"/video/{video_filename}"
            used_local_fallback = True
            logger.info(f"[PIPELINE] Step 5: Local fallback URL → {video_url}")

        # FIX: Only schedule cleanup if we are NOT serving the file locally
        # Previously cleanup would delete the fallback file, causing immediate 404s
        if settings.cleanup_enabled and not used_local_fallback:
            logger.info("[PIPELINE] Scheduling background cleanup task")
            background_tasks.add_task(
                code_writer.cleanup_old_files,
                max_age_hours=settings.cleanup_max_age_hours,
            )

        logger.info(f"[PIPELINE] ── Request complete ✓ ──────────────────────")
        logger.info(f"[PIPELINE] scene='{validation_result.scene_name}' | url='{video_url}'")

        return AnimationResponse(
            status="success",
            message="Animation generated successfully",
            scene_name=validation_result.scene_name,
            video_url=video_url,
            code=code,
            warnings=validation_result.warnings if validation_result.warnings else None,
            template_used=template_key,
        )

    except ManimCodeGeneratorError as e:
        logger.error(f"[PIPELINE] Code generation error: {str(e)}")
        return _error_json(
            status_code=500,
            stage="generation",
            message="Failed to generate animation code.",
            suggestion="The AI model could not produce valid code. Try rephrasing your prompt.",
            details=str(e),
        )

    except CodeWriterError as e:
        logger.error(f"[PIPELINE] Code writing error: {str(e)}")
        return _error_json(
            status_code=500,
            stage="file_write",
            message="Failed to save generated code.",
            details=str(e),
        )

    except RenderError as e:
        logger.error(f"[PIPELINE] Rendering error: {str(e)}")
        error_info = e.to_dict()
        return _error_json(
            status_code=500,
            stage=error_info.get("stage", "rendering"),
            message=error_info.get("message", "Rendering failed."),
            suggestion=error_info.get("suggestion"),
            details=error_info.get("reason"),
        )

    except Exception as e:
        logger.exception(f"[PIPELINE] Unexpected error: {str(e)}")
        return _error_json(
            status_code=500,
            stage="unknown",
            message="An unexpected error occurred.",
            details=str(e),
        )


@app.get("/video/{filename}")
async def get_video(filename: str):
    """Serve rendered video file (local fallback when Supabase is unavailable)."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    output_path = Path(settings.output_dir)
    video_files = list(output_path.glob(f"**/{filename}"))

    if not video_files:
        logger.warning(f"[VIDEO] File not found: {filename}")
        raise HTTPException(status_code=404, detail="Video not found")

    video_path = video_files[0]
    logger.info(f"[VIDEO] Serving local file: {video_path}")
    return FileResponse(video_path, media_type="video/mp4", filename=filename)


@app.get("/qualities")
async def get_qualities():
    return renderer.get_available_qualities()


@app.get("/templates")
async def get_templates():
    templates = template_manager.list_templates()
    return {"templates": templates, "count": len(templates)}


@app.post("/validate-code")
async def validate_code_endpoint(request: ValidateCodeRequest):
    """
    Validate Manim code without rendering.
    FIX: Accepts JSON body instead of query parameter —
    query params are URL-length-limited and break on special characters.
    """
    logger.info(f"[VALIDATE_ENDPOINT] Validating submitted code ({len(request.code)} chars)")
    result = validator.validate(request.code)
    logger.info(f"[VALIDATE_ENDPOINT] Result: valid={result.is_valid} | errors={result.errors}")
    return {
        "is_valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "scene_name": result.scene_name,
        "suggestion": result.suggestion,
    }



# ── Community Posts Endpoints ─────────────────────────────────────────────────

@app.post("/posts", status_code=201)
async def create_community_post(post: PostCreate):
    """
    Save a community animation post to Supabase Postgres.
    The video must already be uploaded to Supabase Storage.
    """
    logger.info(f"[POSTS] New post from '{post.name}' | title='{post.title}' | rating={post.rating}")
    try:
        record = create_post(
            name=post.name,
            title=post.title,
            rating=post.rating,
            video_url=post.video_url,
        )
        logger.info(f"[POSTS] Post created: {record.get('id')}")
        return {"status": "success", "post": record}
    except PostsClientError as e:
        logger.error(f"[POSTS] Failed to create post: {e.message}")
        raise HTTPException(status_code=502, detail=e.message)


@app.get("/posts")
async def get_community_posts(limit: int = 50):
    """
    Fetch the latest community animation posts.
    """
    logger.info(f"[POSTS] Fetching posts (limit={limit})")
    try:
        posts = list_posts(limit=limit)
        logger.info(f"[POSTS] Returning {len(posts)} posts")
        return {"status": "success", "posts": posts, "count": len(posts)}
    except PostsClientError as e:
        logger.error(f"[POSTS] Failed to fetch posts: {e.message}")
        raise HTTPException(status_code=502, detail=e.message)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )