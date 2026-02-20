"""
ManimCodeValidator — validates LLM-generated Manim code before execution.
Uses AST parsing for safety checks and detects unsupported animation types.
"""

import ast
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import logging

from config import UNSUPPORTED_FEATURES, SUPPORTED_CAPABILITIES

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of code validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    scene_name: Optional[str] = None
    stage: str = "validation"
    suggestion: Optional[str] = None
    unsupported_feature: Optional[str] = None

    def __str__(self) -> str:
        status = "✓ VALID" if self.is_valid else "✗ INVALID"
        msg = f"{status}"
        if self.scene_name:
            msg += f" - Scene: {self.scene_name}"
        if self.errors:
            msg += f"\nErrors: {', '.join(self.errors)}"
        if self.warnings:
            msg += f"\nWarnings: {', '.join(self.warnings)}"
        return msg


class ManimCodeValidator:
    """
    Validates LLM-generated Manim code before execution.
    Uses AST parsing to ensure safety and correct structure.
    """

    DANGEROUS_IMPORTS = {
        "os", "sys", "subprocess", "shutil", "pathlib",
        "socket", "requests", "urllib", "urllib3", "http",
        "ftplib", "smtplib", "pickle", "shelve",
        "importlib", "builtins", "__builtin__",
    }

    # Hard errors — these are genuinely unsafe
    DANGEROUS_FUNCTIONS_HARD = {
        "eval", "exec", "__import__", "compile",
        "open", "input", "raw_input",
        "globals", "locals", "vars",
    }

    # FIX: Demoted to warnings — getattr/setattr/delattr are used legitimately
    # in Manim internals and user code; hard-failing on them causes false positives
    DANGEROUS_FUNCTIONS_WARN = {
        "getattr", "setattr", "delattr",
    }

    DANGEROUS_ATTRIBUTES = {
        "__dict__", "__class__", "__bases__", "__subclasses__",
        "__globals__", "__code__", "__builtins__",
    }

    NONEXISTENT_METHODS = {
        "move_along_path",
        "animate_along_path",
        "follow_path",
        "trace_path",
    }

    # FIX: Added MovingCameraScene note — it's allowed but worth a warning
    VALID_SCENE_BASES = {"Scene", "MovingCameraScene"}

    REQUIRED_IMPORT = "from manim import *"
    MAX_CODE_LENGTH = 10000
    # FIX: Renamed to reflect what it actually measures after the loop depth fix
    MAX_LOOP_NESTING = 3

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        logger.info(f"[VALIDATOR] Initialized | strict_mode={strict_mode}")

    # ── public API ────────────────────────────────────────────────────────────

    def validate(self, code: str) -> ValidationResult:
        """
        Validate generated Manim code.
        Runs ALL checks (security + structure) regardless of unsupported features.
        """
        errors: List[str] = []
        warnings: List[str] = []

        logger.info(f"[VALIDATE] Starting validation | code_length={len(code) if code else 0}")

        # ── Basic pre-checks ─────────────────────────────────────────────────
        if not code or not code.strip():
            logger.error("[VALIDATE] Code is empty")
            return ValidationResult(False, ["Code is empty"], [], stage="validation")

        if len(code) > self.MAX_CODE_LENGTH:
            err = f"Code too long ({len(code)} > {self.MAX_CODE_LENGTH} chars)"
            logger.error(f"[VALIDATE] {err}")
            errors.append(err)

        if self.REQUIRED_IMPORT not in code:
            err = "Missing 'from manim import *' import"
            logger.error(f"[VALIDATE] {err}")
            errors.append(err)

        # ── Unsupported feature detection ─────────────────────────────────────
        # FIX: Run this as a warning/metadata step but DO NOT return early —
        # security checks must always complete
        unsupported_feature = None
        unsupported_info = None
        unsupported = self._detect_unsupported_features(code)
        if unsupported:
            unsupported_feature, unsupported_info = unsupported
            err = unsupported_info["message"]
            logger.warning(f"[VALIDATE] Unsupported feature detected: '{unsupported_feature}' — {err}")
            errors.append(err)

        # ── AST Parsing ───────────────────────────────────────────────────────
        logger.info("[VALIDATE] Parsing AST...")
        try:
            tree = ast.parse(code)
            logger.info("[VALIDATE] AST parsed successfully")
        except SyntaxError as e:
            err = f"Syntax error at line {e.lineno}: {e.msg}"
            logger.error(f"[VALIDATE] {err}")
            return ValidationResult(False, errors + [err], warnings, stage="validation")
        except Exception as e:
            err = f"Failed to parse code: {str(e)}"
            logger.error(f"[VALIDATE] {err}")
            return ValidationResult(False, errors + [err], warnings, stage="validation")

        # ── AST Walk Checks ───────────────────────────────────────────────────
        scene_name = None
        scene_count = 0

        for node in ast.walk(tree):

            # Dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.DANGEROUS_IMPORTS:
                        err = f"Forbidden import: {alias.name}"
                        logger.error(f"[VALIDATE] Security: {err}")
                        errors.append(err)
                    elif alias.name not in {"manim", "numpy", "math"}:
                        w = f"Unexpected import: {alias.name}"
                        logger.warning(f"[VALIDATE] {w}")
                        warnings.append(w)

            if isinstance(node, ast.ImportFrom):
                if node.module in self.DANGEROUS_IMPORTS:
                    err = f"Forbidden import: {node.module}"
                    logger.error(f"[VALIDATE] Security: {err}")
                    errors.append(err)
                elif node.module and node.module not in {"manim"}:
                    w = f"Unexpected import from: {node.module}"
                    logger.warning(f"[VALIDATE] {w}")
                    warnings.append(w)

            # Dangerous function calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                fn = node.func.id
                if fn in self.DANGEROUS_FUNCTIONS_HARD:
                    err = f"Forbidden function: {fn}()"
                    logger.error(f"[VALIDATE] Security: {err}")
                    errors.append(err)
                elif fn in self.DANGEROUS_FUNCTIONS_WARN:
                    # FIX: Warn instead of error for getattr/setattr/delattr
                    w = f"Potentially unsafe function: {fn}() — verify usage"
                    logger.warning(f"[VALIDATE] {w}")
                    warnings.append(w)

            # Dangerous attribute access
            if isinstance(node, ast.Attribute):
                if node.attr in self.DANGEROUS_ATTRIBUTES:
                    err = f"Forbidden attribute access: {node.attr}"
                    logger.error(f"[VALIDATE] Security: {err}")
                    errors.append(err)

                # LLM hallucinated method names
                if node.attr in self.NONEXISTENT_METHODS:
                    err = (
                        f"Method '{node.attr}()' does not exist in Manim. "
                        f"Use MoveAlongPath(obj, path) instead."
                    )
                    logger.error(f"[VALIDATE] Hallucinated method: {err}")
                    errors.append(err)

            # Scene class detection
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in self.VALID_SCENE_BASES:
                        scene_count += 1
                        scene_name = node.name
                        logger.info(f"[VALIDATE] Found Scene class: '{scene_name}' (base: {base.id})")

                        if base.id == "MovingCameraScene":
                            w = "MovingCameraScene used — ensure your render environment supports it"
                            logger.warning(f"[VALIDATE] {w}")
                            warnings.append(w)

                        if scene_count > 1:
                            err = "Multiple Scene classes found (only one allowed)"
                            logger.error(f"[VALIDATE] {err}")
                            errors.append(err)

                        has_construct = False
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name == "construct":
                                has_construct = True
                                if not item.args.args or item.args.args[0].arg != "self":
                                    err = "construct() must have 'self' as first parameter"
                                    logger.error(f"[VALIDATE] {err}")
                                    errors.append(err)

                        if not has_construct:
                            err = f"Scene '{scene_name}' missing construct() method"
                            logger.error(f"[VALIDATE] {err}")
                            errors.append(err)

        if not scene_name:
            err = "No Scene class found"
            logger.error(f"[VALIDATE] {err}")
            errors.append(err)

        # ── Loop nesting depth check (FIXED) ──────────────────────────────────
        # FIX: ast.walk() is flat — it doesn't track nesting.
        # We use a recursive visitor to correctly measure actual nesting depth.
        max_nesting = self._get_max_loop_nesting(tree)
        logger.info(f"[VALIDATE] Max loop nesting depth: {max_nesting}")
        if max_nesting > self.MAX_LOOP_NESTING:
            w = (
                f"Deep loop nesting detected (depth {max_nesting} > {self.MAX_LOOP_NESTING}), "
                "may cause long render times"
            )
            logger.warning(f"[VALIDATE] {w}")
            warnings.append(w)

        # ── Strict mode extra checks ──────────────────────────────────────────
        if self.strict_mode:
            logger.info("[VALIDATE] Running strict mode checks...")
            self._strict_validation(code, tree, warnings)

        is_valid = len(errors) == 0
        result = ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            scene_name=scene_name,
            stage="validation",
            suggestion=unsupported_info.get("suggestion") if unsupported_info else None,
            unsupported_feature=unsupported_feature,
        )

        logger.info(f"[VALIDATE] Result: {'✓ VALID' if is_valid else '✗ INVALID'} | "
                    f"errors={len(errors)} | warnings={len(warnings)} | scene='{scene_name}'")
        if errors:
            logger.error(f"[VALIDATE] Errors: {errors}")
        if warnings:
            logger.warning(f"[VALIDATE] Warnings: {warnings}")

        return result

    def check_complexity(self, code: str, prompt: str) -> Optional[str]:
        """
        Check for unsupported features in code or prompt keywords.
        NOTE: Does not re-run full validation — call validate() for that.
        """
        logger.info(f"[COMPLEXITY] Checking prompt: '{prompt[:80]}'")

        # Code-level unsupported features
        unsupported = self._detect_unsupported_features(code)
        if unsupported:
            _, info = unsupported
            logger.warning(f"[COMPLEXITY] Unsupported feature in code: {info['message']}")
            return info["message"]

        # Prompt-level 3D keyword detection
        prompt_lower = prompt.lower()
        three_d_keywords = [
            "3d", "three dimension", "surface plot", "3-d",
            "torus", "opengl", "three_d",
        ]
        # FIX: Removed 'sphere', 'cube', 'cylinder' — these are valid 2D representations
        # (e.g. drawing a circle labeled "sphere" or a square labeled "cube") and were
        # causing false positives on legitimate simple prompts
        for kw in three_d_keywords:
            if kw in prompt_lower:
                msg = (
                    f"3D animations (keyword: '{kw}') are not yet supported. "
                    "Try a 2D animation instead."
                )
                logger.warning(f"[COMPLEXITY] 3D keyword detected: '{kw}'")
                return msg

        logger.info("[COMPLEXITY] No unsupported features detected ✓")
        return None

    # ── private helpers ───────────────────────────────────────────────────────

    def _detect_unsupported_features(self, code: str):
        """
        Scan code for unsupported Manim features defined in config.
        Returns (feature_name, info_dict) if found, else None.
        """
        code_lower = code.lower()
        for feature_name, info in UNSUPPORTED_FEATURES.items():
            pattern = info["pattern"]
            if pattern.lower() == "opengl":
                if pattern.lower() in code_lower:
                    return (feature_name, info)
            else:
                if pattern in code:
                    return (feature_name, info)
        return None

    def _get_max_loop_nesting(self, tree: ast.AST) -> int:
        """
        FIX: Correctly compute max loop nesting depth using recursive traversal.
        The old approach used ast.walk() which is flat and only counted total loops,
        not actual nesting depth. This visitor tracks real depth.
        """
        def _visit(node: ast.AST, depth: int) -> int:
            max_depth = depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.For, ast.While)):
                    max_depth = max(max_depth, _visit(child, depth + 1))
                else:
                    max_depth = max(max_depth, _visit(child, depth))
            return max_depth

        return _visit(tree, 0)

    def _strict_validation(self, code: str, tree: ast.AST, warnings: List[str]):
        """Apply additional strict validation rules."""

        if "while True" in code:
            w = "Infinite loop detected (while True)"
            logger.warning(f"[VALIDATE][STRICT] {w}")
            warnings.append(w)

        # Recursion detection
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            if child.func.id == node.name:
                                w = f"Recursive function detected: {node.name}()"
                                logger.warning(f"[VALIDATE][STRICT] {w}")
                                warnings.append(w)

        # Long animation detection
        wait_count = code.count("self.wait(")
        if wait_count > 20:
            w = f"Many wait() calls ({wait_count}), animation may be very long"
            logger.warning(f"[VALIDATE][STRICT] {w}")
            warnings.append(w)


def validate_manim_code(code: str) -> ValidationResult:
    """Convenience wrapper for validating Manim code."""
    validator = ManimCodeValidator()
    return validator.validate(code)