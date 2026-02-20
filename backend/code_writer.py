import os
import time
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
            base_dir: Base directory for temporary code files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[CODE_WRITER] Initialized | base_dir={self.base_dir.absolute()}")

    def save_code(
        self,
        code: str,
        filename: Optional[str] = None,
        use_uuid: bool = True,
    ) -> str:
        """
        Save Manim code to a file.

        Args:
            code:      Python code to save
            filename:  Optional custom filename (without path)
            use_uuid:  If True, append UUID to filename for uniqueness

        Returns:
            Absolute path to saved file

        Raises:
            CodeWriterError: If file writing fails
        """
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            if filename is None:
                # FIX: Use full uuid4 hex (32 chars) instead of [:8] to eliminate
                # collision risk under concurrent load
                unique_id = uuid.uuid4().hex
                filename = f"scene_{unique_id}.py" if use_uuid else "generated_scene.py"
            else:
                if not filename.endswith(".py"):
                    filename += ".py"
                if use_uuid:
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{uuid.uuid4().hex}{ext}"

            file_path = self.base_dir / filename
            logger.info(f"[CODE_WRITER] Writing code | path={file_path} | size={len(code)} chars")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            # FIX: Check actual file size instead of just existence.
            # file_path.exists() after a successful open() is always True and
            # gives false confidence. Size > 0 catches empty-write edge cases.
            written_size = file_path.stat().st_size
            if written_size == 0:
                raise CodeWriterError(f"File was written but is empty: {file_path}")

            logger.info(f"[CODE_WRITER] Write complete ✓ | path={file_path.absolute()} | bytes={written_size}")
            return str(file_path.absolute())

        except CodeWriterError:
            raise
        except IOError as e:
            logger.error(f"[CODE_WRITER] IOError writing file: {e}")
            raise CodeWriterError(f"Failed to write code file: {str(e)}")
        except Exception as e:
            logger.error(f"[CODE_WRITER] Unexpected error: {type(e).__name__}: {e}")
            raise CodeWriterError(f"Unexpected error: {str(e)}")

    def cleanup_old_files(
        self,
        max_age_hours: int = 24,
        dry_run: bool = False,
        also_clean_dir: Optional[str] = None,
        extensions: tuple = (".py",),
    ):
        """
        Remove old generated files from base_dir (and optionally another directory).

        Args:
            max_age_hours:  Remove files older than this many hours
            dry_run:        If True, only log what would be deleted
            also_clean_dir: FIX: Optional second directory to clean (e.g. output_dir
                            for .mp4 files that accumulate when Supabase upload fails)
            extensions:     File extensions to clean up (default: .py only)
        """
        dirs_to_clean = [self.base_dir]

        # FIX: Support cleaning output directory for orphaned video files
        if also_clean_dir:
            dirs_to_clean.append(Path(also_clean_dir))

        total_deleted = 0

        for target_dir in dirs_to_clean:
            if not target_dir.exists():
                logger.info(f"[CODE_WRITER] Cleanup: directory doesn't exist, skipping: {target_dir}")
                continue

            logger.info(f"[CODE_WRITER] Cleanup: scanning {target_dir} | "
                        f"max_age={max_age_hours}h | extensions={extensions} | dry_run={dry_run}")

            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0

            for ext in extensions:
                for file_path in target_dir.rglob(f"*{ext}"):
                    try:
                        file_age_seconds = current_time - file_path.stat().st_mtime
                        file_age_hours = file_age_seconds / 3600

                        if file_age_seconds > max_age_seconds:
                            if dry_run:
                                logger.info(f"[CODE_WRITER] Cleanup [DRY RUN] would delete: "
                                            f"{file_path} (age: {file_age_hours:.1f}h)")
                            else:
                                file_path.unlink()
                                logger.info(f"[CODE_WRITER] Cleanup: deleted {file_path} "
                                            f"(age: {file_age_hours:.1f}h)")
                            deleted_count += 1
                    except Exception as e:
                        logger.warning(f"[CODE_WRITER] Cleanup: failed to process {file_path}: {e}")

            action = "Would delete" if dry_run else "Deleted"
            logger.info(f"[CODE_WRITER] Cleanup: {action} {deleted_count} file(s) from {target_dir}")
            total_deleted += deleted_count

        logger.info(f"[CODE_WRITER] Cleanup complete | total={'would delete' if dry_run else 'deleted'} "
                    f"{total_deleted} file(s)")


# Backwards compatibility
def save_code(code: str, filename: str = "../runtime/temp/generated_scene.py") -> str:
    """
    Legacy function for backwards compatibility.

    Args:
        code:     Python code to save
        filename: Path to save file

    Returns:
        Path to saved file
    """
    path = Path(filename)
    # FIX: Pass base_dir to __init__ so mkdir runs correctly before any write attempt.
    # Old version mutated base_dir after construction, bypassing directory creation.
    writer = ManimCodeWriter(base_dir=str(path.parent))
    return writer.save_code(code, filename=path.name, use_uuid=False)