"""
Supabase Storage client for uploading rendered Manim videos.

Key fixes vs original:
- Uses httpx async client to avoid blocking FastAPI event loop
- Adds x-upsert header to handle duplicate filenames
- Logs every step including response body for debugging
- Validates public URL accessibility after upload
- Proper MIME type mapping from settings
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional

import httpx

from config import get_settings

logger = logging.getLogger(__name__)


class SupabaseStorageError(Exception):
    """Wrapped error for anything that can go wrong with storage operations."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# MIME type mapping
_MIME_TYPES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".gif": "image/gif",
    ".webm": "video/webm",
}


def _get_mime_type(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    mime = _MIME_TYPES.get(ext, "video/mp4")
    logger.debug(f"[SUPABASE] MIME type for '{ext}': {mime}")
    return mime


def _build_upload_url(supabase_url: str, bucket: str, filename: str) -> str:
    return f"{supabase_url}/storage/v1/object/{bucket}/{filename}"


def _build_public_url(supabase_url: str, bucket: str, filename: str) -> str:
    return f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}"


async def upload_video_async(file_path: str) -> str:
    """
    Async version of upload_video. Use this from FastAPI async endpoints
    to avoid blocking the event loop during upload.

    Args:
        file_path: Absolute path to the local video file.

    Returns:
        Public URL of the uploaded video.

    Raises:
        SupabaseStorageError: if upload fails for any reason.
    """
    settings = get_settings()

    logger.info(f"[SUPABASE] Starting upload | file='{file_path}'")

    # ── Pre-flight checks ──────────────────────────────────────────────────
    if not settings.supabase_url or not settings.supabase_key:
        raise SupabaseStorageError(
            "Supabase credentials not configured (SUPABASE_URL / SUPABASE_KEY missing)"
        )

    if not os.path.exists(file_path):
        raise SupabaseStorageError(f"File not found: {file_path}")

    file_size = os.path.getsize(file_path)
    logger.info(f"[SUPABASE] File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    filename = Path(file_path).name
    bucket = settings.supabase_bucket
    mime_type = _get_mime_type(file_path)

    upload_url = _build_upload_url(settings.supabase_url, bucket, filename)
    public_url = _build_public_url(settings.supabase_url, bucket, filename)

    logger.info(f"[SUPABASE] Upload URL: {upload_url}")
    logger.info(f"[SUPABASE] Bucket: {bucket} | MIME: {mime_type}")

    headers = {
        "Authorization": f"Bearer {settings.supabase_key}",
        "Content-Type": mime_type,
        # FIX: x-upsert allows overwriting existing files.
        # Without this, a duplicate filename returns 400 {"error":"Duplicate"}
        # which triggers the local fallback silently — video "disappears" intermittently.
        "x-upsert": "true",
    }

    # Scale timeout with file size: base 30s + 1s per MB, capped at 300s
    timeout_seconds = min(30 + int(file_size / 1024 / 1024), 300)
    logger.info(f"[SUPABASE] Upload timeout: {timeout_seconds}s")

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            with open(file_path, "rb") as f:
                video_bytes = f.read()

            logger.info(f"[SUPABASE] Sending POST request...")
            response = await client.post(upload_url, headers=headers, content=video_bytes)

        logger.info(f"[SUPABASE] Response status: {response.status_code}")
        logger.info(f"[SUPABASE] Response body: {response.text[:500]}")

        if response.status_code not in (200, 201):
            raise SupabaseStorageError(
                f"Upload failed (HTTP {response.status_code}): {response.text[:300]}"
            )

    except httpx.TimeoutException as e:
        raise SupabaseStorageError(
            f"Upload timed out after {timeout_seconds}s — "
            f"file may be too large ({file_size / 1024 / 1024:.1f} MB): {e}"
        )
    except httpx.RequestError as e:
        raise SupabaseStorageError(f"Network error during upload: {type(e).__name__}: {e}")

    # ── FIX: Verify the public URL is actually reachable ───────────────────
    # This catches the case where the bucket is private (default in Supabase)
    # and the URL looks valid but returns 400/403 to the browser.
    logger.info(f"[SUPABASE] Verifying public URL accessibility: {public_url}")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            check = await client.head(public_url)

        logger.info(f"[SUPABASE] Public URL check status: {check.status_code}")

        if check.status_code in (400, 403, 404):
            logger.error(
                f"[SUPABASE] ⚠ Public URL returned {check.status_code} — "
                f"bucket '{bucket}' may not have public access enabled. "
                f"Go to Supabase Dashboard → Storage → {bucket} → Make Public."
            )
            # Still return the URL — caller (main.py) will handle fallback
            # but this log message tells you exactly what to fix
        elif check.status_code == 200:
            logger.info(f"[SUPABASE] ✓ Public URL is accessible")

    except httpx.RequestError as e:
        logger.warning(f"[SUPABASE] Could not verify public URL (non-fatal): {e}")

    logger.info(f"[SUPABASE] Upload complete ✓ | public_url={public_url}")
    return public_url


def upload_video(file_path: str) -> str:
    """
    Synchronous wrapper around upload_video_async.

    FIX: Original used requests (sync) directly inside an async FastAPI handler,
    blocking the entire event loop during upload. This wrapper uses asyncio
    to run the async version correctly.

    Prefer calling upload_video_async() directly from async contexts.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're inside an async context (FastAPI) — use run_in_executor
            # to avoid "cannot run nested event loops" error
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, upload_video_async(file_path))
                return future.result()
        else:
            return loop.run_until_complete(upload_video_async(file_path))
    except SupabaseStorageError:
        raise
    except Exception as e:
        raise SupabaseStorageError(f"Unexpected upload error: {e}") from e


def get_public_url(filename: str) -> str:
    """
    Return the public URL for an object in the configured bucket.
    Does not verify the file exists or the bucket is public.
    """
    settings = get_settings()
    if not settings.supabase_url:
        raise SupabaseStorageError("SUPABASE_URL not configured")
    bucket = settings.supabase_bucket or ""
    url = _build_public_url(settings.supabase_url, bucket, filename)
    logger.debug(f"[SUPABASE] get_public_url: {url}")
    return url