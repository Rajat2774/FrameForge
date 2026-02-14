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
from config import get_settings

# Initialize settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FrameForge - Manim Animation Generator",
    description="Generate Manim animations from text prompts",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
generator = ManimCodeGenerator(model=settings.groq_model)
code_writer = ManimCodeWriter(base_dir=settings.temp_dir)
renderer = ManimRenderer(
    output_dir=settings.output_dir,
    quality=settings.manim_quality,
    format=settings.manim_format
)
validator = ManimCodeValidator(strict_mode=settings.strict_validation)


# Request/Response Models
class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500, description="Animation description")
    quality: Optional[str] = Field(default=None, description="Quality override (l/m/h/k)")


class AnimationResponse(BaseModel):
    message: str
    scene_name: str
    video_url: str
    code: Optional[str] = None
    warnings: Optional[list] = None


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "FrameForge Manim Animation Generator",
        "version": "2.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "settings": {
            "model": settings.groq_model,
            "quality": settings.manim_quality,
            "output_dir": settings.output_dir
        }
    }


@app.post("/generate-animation", response_model=AnimationResponse)
async def generate_animation(
    request: PromptRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a Manim animation from a text prompt.
    
    Args:
        request: PromptRequest with animation description
        background_tasks: FastAPI background tasks
        
    Returns:
        AnimationResponse with video URL and details
    """
    logger.info(f"Received request: '{request.prompt}'")
    
    try:
        # Step 1: Generate code
        logger.info("Step 1: Generating Manim code...")
        code = generator.generate(
            request.prompt,
            temperature=settings.llm_temperature
        )
        logger.info(f"Generated {len(code)} characters of code")
        
        # Step 2: Validate code
        logger.info("Step 2: Validating code...")
        validation_result = validator.validate(code)
        
        if not validation_result.is_valid:
            logger.error(f"Validation failed: {validation_result.errors}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Generated code failed validation",
                    "validation_errors": validation_result.errors
                }
            )
        
        logger.info(f"Validation passed. Scene: {validation_result.scene_name}")
        if validation_result.warnings:
            logger.warning(f"Validation warnings: {validation_result.warnings}")
        
        # Step 3: Save code to file
        logger.info("Step 3: Saving code to file...")
        file_path = code_writer.save_code(code, use_uuid=True)
        logger.info(f"Saved to: {file_path}")
        
        # Step 4: Render animation
        logger.info("Step 4: Rendering animation...")
        quality = request.quality or settings.manim_quality
        custom_renderer = ManimRenderer(
            output_dir=settings.output_dir,
            quality=quality,
            format=settings.manim_format,
            preview=False  # Don't open video automatically
        )
        
        render_result = custom_renderer.render(
            file_path,
            validation_result.scene_name,
            timeout=settings.render_timeout
        )
        
        video_path = render_result["video_path"]
        logger.info(f"Rendered successfully: {video_path}")
        
        # Create video URL
        video_filename = Path(video_path).name
        video_url = f"/video/{video_filename}"
        
        # Schedule cleanup in background
        if settings.cleanup_enabled:
            background_tasks.add_task(
                code_writer.cleanup_old_files,
                max_age_hours=settings.cleanup_max_age_hours
            )
        
        return AnimationResponse(
            message="Animation generated successfully",
            scene_name=validation_result.scene_name,
            video_url=video_url,
            code=code if settings.debug else None,
            warnings=validation_result.warnings if validation_result.warnings else None
        )
        
    except ManimCodeGeneratorError as e:
        logger.error(f"Code generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to generate code", "details": str(e)}
        )
    
    except CodeWriterError as e:
        logger.error(f"Code writing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to save code", "details": str(e)}
        )
    
    except RenderError as e:
        logger.error(f"Rendering error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to render animation", "details": str(e)}
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)}
        )


@app.get("/video/{filename}")
async def get_video(filename: str):
    """
    Serve rendered video file.
    
    Args:
        filename: Name of video file
        
    Returns:
        Video file response
    """
    # Security: Prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Find video file in output directory
    output_path = Path(settings.output_dir)
    
    # Search for the file
    video_files = list(output_path.glob(f"**/{filename}"))
    
    if not video_files:
        logger.warning(f"Video file not found: {filename}")
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_path = video_files[0]
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    logger.info(f"Serving video: {video_path}")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=filename
    )


@app.get("/qualities")
async def get_qualities():
    """Get available rendering quality options."""
    return renderer.get_available_qualities()


@app.post("/validate-code")
async def validate_code_endpoint(code: str):
    """
    Validate Manim code without rendering.
    
    Args:
        code: Python code to validate
        
    Returns:
        Validation result
    """
    result = validator.validate(code)
    return {
        "is_valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "scene_name": result.scene_name
    }


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 60)
    logger.info("FrameForge Manim Animation Generator Starting")
    logger.info("=" * 60)
    logger.info(f"Model: {settings.groq_model}")
    logger.info(f"Output directory: {settings.output_dir}")
    logger.info(f"Quality: {settings.manim_quality}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    
    # Create necessary directories
    Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("Directories initialized")
    logger.info("Ready to accept requests!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down FrameForge...")
    
    # Optional: Clean up old files on shutdown
    if settings.cleanup_enabled:
        logger.info("Running cleanup...")
        code_writer.cleanup_old_files(
            max_age_hours=settings.cleanup_max_age_hours
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:main",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )