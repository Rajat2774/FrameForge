"""
TemplateManager — routes prompts to deterministic templates when possible.

Pipeline:
  prompt → TemplateManager.match(prompt)
  ├─ template found? → return (key, code, scene_name, description)
  └─ no match        → return None (fall back to LLM generator)

Matching strategy:
  - Uses WORD-BOUNDARY matching via regex, not plain substring `in`
  - Specific templates are checked before broad categories
  - Each rule requires at least one strong keyword match
  - First match wins
"""

import re
import logging
from typing import Optional, Tuple, List

from . import pythagorean, graph, equation, geometry

logger = logging.getLogger(__name__)


def _has_word(prompt: str, keyword: str) -> bool:
    """Check if keyword appears as whole word(s) in prompt, not as substring."""
    return bool(re.search(r'\b' + re.escape(keyword) + r'\b', prompt))


def _has_any_word(prompt: str, keywords: List[str]) -> bool:
    """Return True if ANY keyword appears as whole word(s) in the prompt."""
    return any(_has_word(prompt, kw) for kw in keywords)


def _extract_scene_name(code: str) -> Optional[str]:
    """
    Extract the Scene class name from template code.
    Used so the TemplateManager knows the class name without relying
    solely on downstream AST parsing.
    """
    match = re.search(r"class\s+(\w+)\s*\(Scene\)", code)
    if match:
        return match.group(1)
    return None


# ── Detection rules ──────────────────────────────────────────────────────────

def _build_rules():
    """
    Build ordered list of (match_fn, key, code, scene_name, description) tuples.
    IMPORTANT: Rules are evaluated top → bottom, first match wins.
    Place SPECIFIC templates before BROAD ones.
    """
    rules = []

    # ── Pythagorean theorem (specific) ───────────────────────────────────
    def _is_pythagorean(p: str) -> bool:
        return _has_any_word(p, [
            "pythagorean", "pythagoras",
            "a² + b²", "a^2 + b^2",
            "right triangle theorem",
        ])

    rules.append((
        _is_pythagorean,
        "pythagorean",
        pythagorean.TEMPLATE_CODE,
        _extract_scene_name(pythagorean.TEMPLATE_CODE),
        "Pythagorean theorem visualization",
    ))

    # ── Quadratic formula (specific) ─────────────────────────────────────
    def _is_quadratic(p: str) -> bool:
        return _has_any_word(p, [
            "quadratic formula", "quadratic equation",
            "ax^2 + bx", "ax² + bx",
        ])

    rules.append((
        _is_quadratic,
        "quadratic_formula",
        equation.QUADRATIC_FORMULA_TEMPLATE,
        _extract_scene_name(equation.QUADRATIC_FORMULA_TEMPLATE),
        "Quadratic formula step-by-step",
    ))

    # ── Euler's identity (specific) ──────────────────────────────────────
    def _is_euler(p: str) -> bool:
        # FIX: Use _has_any_word for all keyword checks for consistency.
        # Old code mixed _has_any_word with bare `in` substring checks —
        # e.g. "e^(i" could match inside unrelated strings.
        return _has_any_word(p, [
            "euler's identity", "eulers identity", "euler identity",
            "e^(ipi)", "e^ipi", "e^(iπ)",
        ])

    rules.append((
        _is_euler,
        "euler_identity",
        equation.EULER_TEMPLATE,
        _extract_scene_name(equation.EULER_TEMPLATE),
        "Euler's identity visualization",
    ))

    # ── Sin(x) plot (specific) ───────────────────────────────────────────
    def _is_sin(p: str) -> bool:
        # FIX: Reject if prompt describes a complex concept that merely contains
        # "sin" as a component — e.g. "Taylor series of sin(x)", "Fourier transform
        # of sine", "derive sin(x)". These go to the LLM, not the static template.
        COMPLEX_DISQUALIFIERS = [
            "taylor", "fourier", "maclaurin", "series", "approximat",
            "deriv", "integrat", "proof", "converg", "limit", "expand",
            "transform", "compar",
        ]
        if any(kw in p for kw in COMPLEX_DISQUALIFIERS):
            return False

        return _has_any_word(p, [
            "sine wave", "sine curve", "sin curve",
            "sin(x)", "sinx", "plot sin", "graph sin", "y = sin",
            "y=sin",
        ])

    rules.append((
        _is_sin,
        "sin_plot",
        graph.SIN_TEMPLATE,
        _extract_scene_name(graph.SIN_TEMPLATE),
        "Sine function plot",
    ))

    # ── x² / parabola (specific) ────────────────────────────────────────
    def _is_parabola(p: str) -> bool:
        return _has_any_word(p, [
            "parabola", "x squared",
            "x^2", "x²", "y = x^2", "y = x²", "plot x*x",
        ])

    rules.append((
        _is_parabola,
        "parabola_plot",
        graph.QUADRATIC_TEMPLATE,
        _extract_scene_name(graph.QUADRATIC_TEMPLATE),
        "Parabola (y=x²) plot",
    ))

    # ── Growing circle (specific) ────────────────────────────────────────
    def _is_circle(p: str) -> bool:
        return _has_any_word(p, [
            "growing circle", "expanding circle",
            "circle that grows", "circle grow",
            "circle animation",
        ])

    rules.append((
        _is_circle,
        "circle",
        geometry.CIRCLE_TEMPLATE,
        _extract_scene_name(geometry.CIRCLE_TEMPLATE),
        "Growing circle animation",
    ))

    # ── Shape transformation (specific) ─────────────────────────────────
    def _is_transform(p: str) -> bool:
        return _has_any_word(p, [
            "square to circle", "square into circle",
            "circle to square", "shape transformation",
            "square transforming into",
        ]) or (
            _has_word(p, "transform") and _has_any_word(p, [
                "square", "circle", "triangle", "shape",
            ])
        ) or (
            _has_word(p, "morph") and _has_any_word(p, [
                "square", "circle", "triangle", "shape",
            ])
        )

    rules.append((
        _is_transform,
        "transform",
        geometry.TRANSFORM_TEMPLATE,
        _extract_scene_name(geometry.TRANSFORM_TEMPLATE),
        "Shape transformation chain",
    ))

    # ── Generic graph / plot ─────────────────────────────────────────────
    def _is_graph(p: str) -> bool:
        has_plot_word = _has_any_word(p, ["plot", "graph"])
        has_math_context = _has_any_word(p, [
            "function", "cos", "tan", "log", "exp",
            "axes", "curve", "cos(x)", "tan(x)", "f(x)",
        ])

        if not has_plot_word:
            return False

        # FIX: Removed the `word_count <= 5` shortcut that caused prompts like
        # "plot a DNA helix" (5 words, has "plot") to match this template
        # and return a sine+cosine graph instead of going to the LLM.
        # Now requires explicit math context alongside the plot keyword.
        return has_math_context

    rules.append((
        _is_graph,
        "graph",
        graph.TEMPLATE_CODE,
        _extract_scene_name(graph.TEMPLATE_CODE),
        "General function plot (sin + cos)",
    ))

    # ── Equation / formula ───────────────────────────────────────────────
    def _is_equation(p: str) -> bool:
        has_eq_word = _has_any_word(p, ["equation", "formula"])
        has_math_context = _has_any_word(p, [
            "math", "famous", "quadratic", "physics",
            "newton", "einstein", "euler", "energy",
            "e = mc", "e=mc", "f = ma", "f=ma",
        ])
        if has_eq_word and has_math_context:
            return True
        return _has_any_word(p, [
            "famous equations", "math equations",
            "show equations", "mathematical equations",
        ])

    rules.append((
        _is_equation,
        "equation",
        equation.TEMPLATE_CODE,
        _extract_scene_name(equation.TEMPLATE_CODE),
        "Famous equations showcase",
    ))

    # ── Generic geometry ─────────────────────────────────────────────────
    def _is_geometry(p: str) -> bool:
        return _has_any_word(p, [
            "2d geometry", "geometric shapes",
            "triangle and square", "basic shapes",
            "geometry shapes",
        ])

    rules.append((
        _is_geometry,
        "geometry",
        geometry.TEMPLATE_CODE,
        _extract_scene_name(geometry.TEMPLATE_CODE),
        "2D geometry showcase",
    ))

    # Validate all scene names were extracted successfully at build time
    for fn, key, code, scene_name, desc in rules:
        if scene_name is None:
            logger.error(
                f"[TEMPLATE_MANAGER] Could not extract scene name from template '{key}' — "
                f"this will cause render failures if template is matched"
            )
        else:
            logger.debug(f"[TEMPLATE_MANAGER] Template '{key}' → scene class '{scene_name}'")

    return rules

async def _llm_confirms_template(prompt: str, template_desc: str, groq_client) -> bool:
    """Ask the LLM if the prompt genuinely matches the template intent."""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": (
                    f'Does this user request match this template?\n'
                    f'User request: "{prompt}"\n'
                    f'Template: "{template_desc}"\n'
                    f'Reply with only YES or NO.'
                )
            }],
            temperature=0,
            max_tokens=5,
        )
        answer = response.choices[0].message.content.strip().upper()
        logger.info(f"[TEMPLATE_MANAGER] LLM confirmation for '{template_desc}': {answer}")
        return answer == "YES"
    except Exception as e:
        logger.warning(f"[TEMPLATE_MANAGER] LLM confirmation failed: {e} — defaulting to template")
        return True


class TemplateManager:
    """
    Detects whether a prompt matches a known animation template.

    Usage:
        tm = TemplateManager()
        result = tm.match("show the pythagorean theorem")
        if result:
            key, code, scene_name, desc = result
    """

    def __init__(self):
        self._rules = _build_rules()
        logger.info(
            f"[TEMPLATE_MANAGER] Initialized with {len(self._rules)} templates: "
            f"{[r[1] for r in self._rules]}"
        )

    async def match(self, prompt: str, groq_client=None) -> Optional[Tuple[str, str, str, str]]:
        """
        Try to match a prompt to a known template.

        Args:
            prompt: The user's animation description

        Returns:
            Tuple (template_key, code, scene_name, description) if matched, else None

        NOTE: Return signature changed from (key, code, desc) to
        (key, code, scene_name, desc) — update callers in main.py accordingly.
        """
        p = prompt.lower().strip()

        # FIX: Log the normalized prompt so incorrect matches are traceable
        logger.info(f"[TEMPLATE_MANAGER] Matching prompt: '{p}'")

        for check_fn, key, code, scene_name, desc in self._rules:
            if check_fn(p):
                if groq_client:
                    confirmed = await _llm_confirms_template(p, desc, groq_client)
                    if not confirmed:
                        logger.info(
                            f"[TEMPLATE_MANAGER] Keyword matched '{key}' but "
                            f"LLM rejected — falling through to LLM generation"
                        )
                        continue
                logger.info(f"[TEMPLATE_MANAGER] ✓ Matched '{key}' | scene='{scene_name}'")
                return (key, code, scene_name, desc)

        logger.info("[TEMPLATE_MANAGER] No template matched — falling back to LLM")
        return None

    def list_templates(self) -> list:
        """Return list of available template keys and descriptions."""
        return [
            {"key": r[1], "description": r[4], "scene_name": r[3]}
            for r in self._rules
        ]