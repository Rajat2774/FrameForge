"""
Supabase PostgREST client for community posts.

Uses Supabase's auto-generated REST API (PostgREST) to read/write
the `posts` table without needing the supabase-py SDK.

Table schema (create this in your Supabase SQL editor):
  CREATE TABLE posts (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name       TEXT NOT NULL,
    title      TEXT NOT NULL,
    rating     INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    video_url  TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
  );
"""

import logging
from typing import Optional

import httpx

from config import get_settings

logger = logging.getLogger(__name__)


class PostsClientError(Exception):
    """Raised when a posts DB operation fails."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _posts_url(supabase_url: str) -> str:
    return f"{supabase_url}/rest/v1/posts"


def _auth_headers(supabase_key: str) -> dict:
    return {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def create_post(
    name: str,
    title: str,
    rating: int,
    video_url: str,
) -> dict:
    """
    Insert a new community post into the `posts` table.

    Returns:
        The created post record as a dict.

    Raises:
        PostsClientError: on missing credentials or HTTP failure.
    """
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_key:
        raise PostsClientError("Supabase credentials not configured (SUPABASE_URL / SUPABASE_KEY)")

    url = _posts_url(settings.supabase_url)
    headers = _auth_headers(settings.supabase_key)
    payload = {
        "name": name,
        "title": title,
        "rating": rating,
        "video_url": video_url,
    }

    logger.info(f"[POSTS] Creating post | title='{title}' | rating={rating}")

    try:
        with httpx.Client(timeout=15) as client:
            response = client.post(url, headers=headers, json=payload)

        logger.info(f"[POSTS] Create response: {response.status_code} | {response.text[:300]}")

        if response.status_code not in (200, 201):
            raise PostsClientError(
                f"Failed to create post (HTTP {response.status_code}): {response.text[:300]}"
            )

        data = response.json()
        # PostgREST returns a list with Prefer: return=representation
        if isinstance(data, list) and data:
            return data[0]
        elif isinstance(data, dict):
            return data
        else:
            raise PostsClientError("Unexpected response format from Supabase")

    except httpx.RequestError as e:
        raise PostsClientError(f"Network error creating post: {e}") from e


def list_posts(limit: int = 50, order: str = "created_at.desc") -> list:
    """
    Fetch community posts from the `posts` table.

    Args:
        limit: Maximum number of posts to return.
        order: PostgREST order string (e.g. 'created_at.desc').

    Returns:
        List of post dicts.

    Raises:
        PostsClientError: on missing credentials or HTTP failure.
    """
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_key:
        raise PostsClientError("Supabase credentials not configured")

    url = _posts_url(settings.supabase_url)
    headers = {
        "apikey": settings.supabase_key,
        "Authorization": f"Bearer {settings.supabase_key}",
    }
    params = {
        "order": order,
        "limit": limit,
        "select": "id,name,title,rating,video_url,created_at",
    }

    logger.info(f"[POSTS] Fetching posts | limit={limit}")

    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(url, headers=headers, params=params)

        logger.info(f"[POSTS] List response: {response.status_code}")

        if response.status_code != 200:
            raise PostsClientError(
                f"Failed to fetch posts (HTTP {response.status_code}): {response.text[:300]}"
            )

        return response.json()

    except httpx.RequestError as e:
        raise PostsClientError(f"Network error fetching posts: {e}") from e
