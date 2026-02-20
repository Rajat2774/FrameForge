"""
FrameForge Templates — deterministic animation templates for common prompts.

This package exposes individual template modules; clients should import
what they need explicitly. Importing :class:`TemplateManager` from here
used to cause a circular import because the manager itself imports from
this package.  By keeping ``__init__`` minimal we avoid that problem.
"""

# no top‑level imports to avoid circular references

__all__ = []

