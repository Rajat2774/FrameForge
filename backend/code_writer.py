import os
import uuid
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CodeWriterError(Exception):
    """Custom exception for code writing errors."""
    pass


class ManimCodeWriter:
    """Handles writing generated Manim code to files."""
    
    def __init__(self, base_dir: str = "../runtime/temp"):
        """
        Initialize code writer.
        
        Args:
            base_dir: Base directory for temporary files
        """
        self.base_dir = Path(base_dir)
        logger.info(f"Initialized ManimCodeWriter with base_dir: {self.base_dir}")
    
    def save_code(
        self,
        code: str,
        filename: Optional[str] = None,
        use_uuid: bool = True
    ) -> str:
        """
        Save Manim code to a file.
        
        Args:
            code: Python code to save
            filename: Optional custom filename (without path)
            use_uuid: If True, append UUID to filename for uniqueness
            
        Returns:
            Absolute path to saved file
            
        Raises:
            CodeWriterError: If file writing fails
        """
        try:
            # Create directory if it doesn't exist
            self.base_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            if filename is None:
                if use_uuid:
                    unique_id = uuid.uuid4().hex[:8]
                    filename = f"scene_{unique_id}.py"
                else:
                    filename = "generated_scene.py"
            else:
                # Ensure .py extension
                if not filename.endswith('.py'):
                    filename += '.py'
                
                # Add UUID if requested
                if use_uuid:
                    name, ext = os.path.splitext(filename)
                    unique_id = uuid.uuid4().hex[:8]
                    filename = f"{name}_{unique_id}{ext}"
            
            # Full path
            file_path = self.base_dir / filename
            
            # Write code to file
            logger.info(f"Writing code to: {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Verify file was written
            if not file_path.exists():
                raise CodeWriterError(f"File was not created: {file_path}")
            
            logger.info(f"Successfully wrote {len(code)} bytes to {file_path}")
            return str(file_path.absolute())
            
        except IOError as e:
            logger.error(f"Failed to write code: {str(e)}")
            raise CodeWriterError(f"Failed to write code file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error writing code: {str(e)}")
            raise CodeWriterError(f"Unexpected error: {str(e)}")
    
    def cleanup_old_files(self, max_age_hours: int = 24, dry_run: bool = False):
        """
        Remove old generated files.
        
        Args:
            max_age_hours: Remove files older than this many hours
            dry_run: If True, only log what would be deleted
        """
        import time
        
        if not self.base_dir.exists():
            logger.info("Temp directory doesn't exist, nothing to clean")
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for file_path in self.base_dir.glob("*.py"):
            try:
                file_age = current_time - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    if dry_run:
                        logger.info(f"Would delete: {file_path} (age: {file_age/3600:.1f}h)")
                    else:
                        file_path.unlink()
                        logger.info(f"Deleted: {file_path}")
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {str(e)}")
        
        action = "Would delete" if dry_run else "Deleted"
        logger.info(f"{action} {deleted_count} old file(s)")


# Backwards compatibility function
def save_code(code: str, filename: str = "../runtime/temp/generated_scene.py") -> str:
    """
    Legacy function for backwards compatibility.
    
    Args:
        code: Python code to save
        filename: Path to save file (default keeps old behavior)
        
    Returns:
        Path to saved file
    """
    writer = ManimCodeWriter()
    # Extract directory and filename
    path = Path(filename)
    writer.base_dir = path.parent
    return writer.save_code(code, filename=path.name, use_uuid=False)