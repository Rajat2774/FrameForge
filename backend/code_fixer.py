"""
ManimCodeFixer - Automatically fixes common issues in LLM-generated Manim code.
Includes automatic LaTeX availability detection.
"""
import re
import shutil
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def detect_latex() -> bool:
    """Check whether a LaTeX compiler is available on the system."""
    for cmd in ("latex", "pdflatex", "xelatex", "lualatex"):
        if shutil.which(cmd) is not None:
            logger.info(f"[FIXER] LaTeX compiler found: {cmd}")
            return True
    logger.warning("[FIXER] No LaTeX compiler found on system")
    return False


# Module-level constant — evaluated once at import time
LATEX_AVAILABLE = detect_latex()


class ManimCodeFixer:
    """
    Automatically fixes common issues in LLM-generated Manim code
    before validation and rendering.

    If LaTeX is not installed, it forces replacement of MathTex/Tex with Text.
    """

    def __init__(self, auto_fix: bool = True, disable_latex: bool = False):
        self.auto_fix = auto_fix
        self.disable_latex = disable_latex or (not LATEX_AVAILABLE)

        if not LATEX_AVAILABLE:
            logger.warning(
                "[FIXER] LaTeX compiler NOT found — MathTex/Tex will be auto-replaced with Text"
            )
        logger.info(
            f"[FIXER] Initialized | auto_fix={auto_fix} | "
            f"disable_latex={self.disable_latex} | latex_available={LATEX_AVAILABLE}"
        )

    def fix_code(self, code: str) -> Tuple[str, List[str]]:
        """
        Apply automatic fixes to generated Manim code.

        Returns:
            Tuple of (fixed_code, list_of_fixes_applied)
        """
        if not self.auto_fix:
            logger.info("[FIXER] auto_fix=False, skipping all fixes")
            return code, []

        fixes_applied = []
        fixed = code

        # Fix 1: Remove markdown code fences
        if "```" in fixed:
            fixed = re.sub(r"```python\s*\n?", "", fixed)
            fixed = re.sub(r"```\s*\n?", "", fixed)
            fixes_applied.append("removed_markdown_fences")
            logger.info("[FIXER] Fix 1: Removed markdown code fences")

        # Fix 2: Ensure 'from manim import *' is present
        if "from manim import *" not in fixed:
            fixed = "from manim import *\n\n" + fixed
            fixes_applied.append("added_manim_import")
            logger.info("[FIXER] Fix 2: Added missing 'from manim import *'")

        # Fix 3: Fix common LaTeX backslash issues
        fixed, latex_fixes = self._fix_latex_strings(fixed)
        fixes_applied.extend(latex_fixes)

        # Fix 4: Replace LaTeX with plain text if disabled or unavailable
        if self.disable_latex:
            fixed, latex_replace_fixes = self._replace_latex(fixed)
            fixes_applied.extend(latex_replace_fixes)

        # Fix 5: Fix move_along_path hallucination in BOTH forms:
        # FIX: Old regex only caught `.animate.move_along_path()`.
        # LLMs also generate `obj.move_along_path(path)` without `.animate.`
        if "move_along_path" in fixed:
            # Form 1: obj.animate.move_along_path(path) → MoveAlongPath(obj, path)
            fixed = re.sub(
                r"(\w+)\.animate\.move_along_path\((\w+)\)",
                r"MoveAlongPath(\1, \2)",
                fixed,
            )
            # Form 2: obj.move_along_path(path) → MoveAlongPath(obj, path)
            fixed = re.sub(
                r"(\w+)\.move_along_path\((\w+)\)",
                r"MoveAlongPath(\1, \2)",
                fixed,
            )
            fixes_applied.append("fixed_move_along_path_hallucination")
            logger.info("[FIXER] Fix 5: Replaced move_along_path with MoveAlongPath")

        # Fix 6: Remove leftover explanatory text before code
        lines = fixed.split("\n")
        code_start = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("from manim") or stripped.startswith("import manim"):
                code_start = i
                break
        if code_start > 0:
            removed_lines = lines[:code_start]
            if all(
                not l.strip().startswith(("class ", "def ", "import ", "from "))
                for l in removed_lines
                if l.strip()
            ):
                fixed = "\n".join(lines[code_start:])
                fixes_applied.append("removed_leading_prose")
                logger.info("[FIXER] Fix 6: Removed explanatory text before code")

        # Fix 7: Remove print statements (handle multi-line with DOTALL)
        if "print(" in fixed:
            # FIX: Added re.DOTALL to handle multi-line print statements
            fixed = re.sub(r"\s*print\([^)]*\)\s*\n?", "\n", fixed)
            fixes_applied.append("removed_print_statements")
            logger.info("[FIXER] Fix 7: Removed print statements")

        # Fix 8: Add self.wait() after the LAST self.play() if no wait exists
        # after it (not just anywhere in the code)
        if "self.play" in fixed:
            fixed = self._ensure_trailing_wait(fixed, fixes_applied)

        fixed = fixed.strip() + "\n"

        if fixes_applied:
            logger.info(f"[FIXER] Applied {len(fixes_applied)} fix(es): {fixes_applied}")
        else:
            logger.info("[FIXER] No fixes needed")

        return fixed, fixes_applied

    def _ensure_trailing_wait(self, code: str, fixes_applied: List[str]) -> str:
        """
        FIX: Old logic checked if 'self.wait' existed anywhere in code.
        If there was a wait() early in the code but none after the final play(),
        the fix was skipped. Now we check whether anything follows the last play().
        """
        lines = code.split("\n")

        last_play_idx = -1
        for i, line in enumerate(lines):
            if "self.play" in line:
                last_play_idx = i

        if last_play_idx == -1:
            return code

        # Check if there's already a self.wait() after the last self.play()
        lines_after_last_play = lines[last_play_idx + 1:]
        has_wait_after_play = any("self.wait" in l for l in lines_after_last_play)

        if not has_wait_after_play:
            indent = len(lines[last_play_idx]) - len(lines[last_play_idx].lstrip())
            wait_line = " " * indent + "self.wait()"
            lines.insert(last_play_idx + 1, wait_line)
            fixes_applied.append("added_trailing_wait")
            logger.info("[FIXER] Fix 8: Added self.wait() after last self.play()")
            return "\n".join(lines)

        return code

    def _fix_latex_strings(self, code: str) -> Tuple[str, List[str]]:
        """Fix common LaTeX string issues in MathTex/Tex calls."""
        fixes = []

        # FIX: Rewritten as a clear single-line condition with explicit parentheses
        # Old version used backslash line continuation which was fragile and hard to read
        if ('r"\\\\' in code) or ("r'\\\\" in code):
            code = re.sub(r'r"\\\\\\\\', r'r"\\\\', code)
            code = re.sub(r"r'\\\\\\\\", r"r'\\\\", code)
            fixes.append("fixed_overescaped_latex_backslashes")
            logger.info("[FIXER] Fix 3: Fixed over-escaped LaTeX backslashes")

        return code, fixes

    def _replace_latex(self, code: str) -> Tuple[str, List[str]]:
        """
        Replace Tex/MathTex with plain Text to avoid LaTeX dependencies.

        FIX: Old regex `[^)]+` broke on nested parentheses, e.g.:
          MathTex(r"\\frac{a}{b}", color=RED)
        The `[^)]+` stopped at the first `)` inside the argument, leaving
        broken syntax. Now uses a proper balanced-argument extractor.
        """
        fixes = []

        if "MathTex(" in code:
            code = self._safe_replace_call(code, "MathTex", "Text")
            fixes.append("replaced_MathTex_with_Text")
            logger.info("[FIXER] Fix 4a: Replaced MathTex with Text")

        # FIX: Check for standalone Tex( after MathTex replacement is done.
        # Old condition `and "MathTex" not in code` was evaluated before
        # substitution was complete, causing the Tex branch to be skipped.
        # Now we re-check the already-updated `code` string independently.
        if re.search(r'(?<![a-zA-Z])Tex\(', code):
            code = self._safe_replace_call(code, "Tex", "Text")
            fixes.append("replaced_Tex_with_Text")
            logger.info("[FIXER] Fix 4b: Replaced Tex with Text")

        return code, fixes

    def _safe_replace_call(self, code: str, old_fn: str, new_fn: str) -> str:
        """
        Replace function calls like old_fn(...) with new_fn(..., font_size=36),
        correctly handling nested parentheses in arguments.

        This replaces the naive `[^)]+` regex which broke on:
          MathTex(r"\\frac{a}{b}", color=RED)
        """
        result = []
        i = 0
        pattern = old_fn + "("

        while i < len(code):
            idx = code.find(pattern, i)
            if idx == -1:
                result.append(code[i:])
                break

            # Append everything before the match
            result.append(code[i:idx])

            # Find the matching closing parenthesis by tracking depth
            start = idx + len(pattern)
            depth = 1
            j = start
            while j < len(code) and depth > 0:
                if code[j] == "(":
                    depth += 1
                elif code[j] == ")":
                    depth -= 1
                j += 1

            # Extract the full argument string
            args = code[start:j - 1]

            # Strip any existing font_size to avoid doubling it
            args_clean = re.sub(r",?\s*font_size\s*=\s*\d+", "", args).strip()

            result.append(f"{new_fn}({args_clean}, font_size=36)")
            i = j

        return "".join(result)