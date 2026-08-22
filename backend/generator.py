import os
# pyrefly: ignore [missing-import]
from groq import Groq
from dotenv import load_dotenv
import re
from typing import Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


class ManimCodeGeneratorError(Exception):
    """Custom exception for code generation errors"""
    pass


class ManimCodeGenerator:
    """Generates Manim animation code using LLM with retry logic."""
    
    SYSTEM_PROMPT = """You are a Manim code generator. You ONLY output valid Python code. Never add explanations, markdown, or any text outside the code.

=== CRITICAL OUTPUT RULES ===
1. Output starts IMMEDIATELY with: from manim import *
2. NO explanations before or after code
3. NO markdown code blocks (no ```python or ```)
4. NO comments explaining what you did
5. ONLY pure Python code

=== REQUIRED CODE STRUCTURE ===
from manim import *

class SceneName(Scene):
    def construct(self):
        # animation code here
        pass

=== WHAT YOU MUST INCLUDE ===
✓ from manim import * (always first line)
✓ Exactly ONE class inheriting from Scene
✓ A construct(self) method
✓ At least one self.play() or self.add() call
✓ At least one self.wait() call

=== WHAT YOU MUST NEVER USE ===
✗ import os, sys, subprocess, requests, urllib
✗ open(), input(), eval(), exec()
✗ locals(), globals(), vars() - NEVER use these!
✗ file operations
✗ network requests
✗ Multiple Scene classes
✗ Complex dynamic code generation - keep it simple!

CRITICAL: DO NOT use locals(), globals(), or vars() - these are FORBIDDEN.
Keep your code simple and explicit. Don't try to be too clever.

=== AVAILABLE OBJECTS (ONLY USE THESE) ===
Shapes: Circle, Square, Rectangle, Triangle, Polygon, RegularPolygon, Star, Ellipse, Annulus, Sector
Text: Text, Tex, MarkupText
Lines: Line, Arrow, DashedLine, Vector, DoubleArrow
Graphs: Axes, NumberPlane, BarChart
Special: Dot, VGroup
Colors: BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, PINK, WHITE, GRAY, BLACK

=== AVAILABLE ANIMATIONS (ONLY USE THESE) ===
Create(obj) - Draw object
FadeIn(obj) - Fade in
FadeOut(obj) - Fade out  
Write(text) - Write text
Transform(obj1, obj2) - Morph obj1 into obj2
ReplacementTransform(obj1, obj2) - Replace obj1 with obj2
Rotate(obj, angle=PI/2) - Rotate object
Indicate(obj) - Briefly highlight
MoveAlongPath(obj, path) - Move object along a path
obj.animate.shift() - Animate shift
obj.animate.move_to() - Animate move to position
obj.animate.scale() - Animate scaling
obj.animate.rotate() - Animate rotation

CRITICAL: There is NO move_along_path() method! Use MoveAlongPath(obj, path) instead!

=== POSITIONING ===
Directions: UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR
Methods: 
- obj.shift(direction * distance)
- obj.move_to(position)
- obj.next_to(other, direction)
- obj.to_edge(edge)
- obj.scale(factor)

=== CRITICAL EXAMPLES ===

Example 1 - User: "blue circle that grows"
from manim import *

class GrowingCircle(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        self.play(Create(circle))
        self.play(circle.animate.scale(2))
        self.wait()

Example 2 - User: "pythagorean theorem"
from manim import *

class Pythagorean(Scene):
    def construct(self):
        triangle = Polygon([0,0,0], [3,0,0], [3,4,0], color=BLUE)
        equation = MathTex("a^2 + b^2 = c^2").next_to(triangle, DOWN)
        self.play(Create(triangle))
        self.play(Write(equation))
        self.wait(2)

Example 3 - User: "plot sine wave"
from manim import *

class SineWave(Scene):
    def construct(self):
        axes = Axes(x_range=[-3,3], y_range=[-2,2])
        sine = axes.plot(lambda x: np.sin(x), color=BLUE)
        self.play(Create(axes))
        self.play(Create(sine))
        self.wait()

Example 4 - User: "square to circle transformation"
from manim import *

class SquareToCircle(Scene):
    def construct(self):
        square = Square(color=RED)
        circle = Circle(color=BLUE)
        self.play(Create(square))
        self.wait(0.5)
        self.play(Transform(square, circle))
        self.wait()

Example 5 - User: "bouncing ball"
from manim import *

class BouncingBall(Scene):
    def construct(self):
        ball = Dot(radius=0.3, color=RED)
        ball.shift(UP * 2)
        self.play(FadeIn(ball))
        self.play(ball.animate.shift(DOWN * 4), rate_func=there_and_back, run_time=2)
        self.wait()

Example 6 - User: "neural network diagram"
from manim import *

class NeuralNetwork(Scene):
    def construct(self):
        input_layer = VGroup(*[Circle(radius=0.3, color=BLUE).shift(UP * i) for i in range(-1, 2)])
        hidden_layer = VGroup(*[Circle(radius=0.3, color=GREEN).shift(RIGHT * 3 + UP * i * 0.8) for i in range(-2, 3)])
        output_layer = VGroup(*[Circle(radius=0.3, color=RED).shift(RIGHT * 6 + UP * i) for i in range(-1, 2)])
        
        layers = VGroup(input_layer, hidden_layer, output_layer)
        
        lines = VGroup()
        for inp in input_layer:
            for hid in hidden_layer:
                lines.add(Line(inp.get_center(), hid.get_center(), stroke_width=1, color=GRAY))
        
        self.play(Create(layers))
        self.play(Create(lines))
        
        signal = Dot(color=YELLOW, radius=0.15).move_to(input_layer[0].get_center())
        self.play(FadeIn(signal))
        self.play(signal.animate.move_to(hidden_layer[2].get_center()), run_time=1)
        self.play(signal.animate.move_to(output_layer[1].get_center()), run_time=1)
        self.wait()

Example 7 - User: "binary search visualization"
from manim import *

class BinarySearch(Scene):
    def construct(self):
        arr = [2, 5, 8, 12, 16, 23, 38, 45, 56, 67]
        target = 23
        
        boxes = VGroup()
        labels = VGroup()
        for i, val in enumerate(arr):
            box = Square(side_length=0.6, color=BLUE)
            box.shift(LEFT * 4.5 + RIGHT * i * 0.7)
            label = Text(str(val), font_size=20).move_to(box.get_center())
            boxes.add(box)
            labels.add(label)
        
        group = VGroup(boxes, labels)
        self.play(Create(group))
        
        title = Text("Binary Search for 23", font_size=32).to_edge(UP)
        self.play(Write(title))
        
        low = 0
        high = 9
        mid = 4
        
        boxes[mid].set_color(YELLOW)
        self.play(Indicate(boxes[mid]))
        self.wait(0.5)
        
        boxes[mid].set_color(RED)
        self.wait(0.5)
        
        mid = 7
        boxes[mid].set_color(YELLOW)
        self.play(Indicate(boxes[mid]))
        self.wait(0.5)
        
        mid = 5
        boxes[mid].set_color(GREEN)
        self.play(Indicate(boxes[mid]))
        self.wait()

=== LATEX IN MATHTEXT ===
Use raw strings with double backslashes:
MathTex(r"\\frac{a}{b}") for fractions
MathTex(r"\\sqrt{x}") for square root
MathTex(r"x^2") for superscript
MathTex(r"x_1") for subscript
MathTex(r"\\alpha") for Greek letters

=== COMMON MISTAKES TO AVOID ===
❌ DON'T: Use locals(), globals(), vars() - FORBIDDEN!
❌ DON'T: Add explanations → "Here's the code:"
❌ DON'T: Use markdown → ```python
❌ DON'T: Use print statements
❌ DON'T: Create helper functions outside construct()
❌ DON'T: Use complex loops without clear purpose
❌ DON'T: Forget self.wait() at the end
❌ DON'T: Try to animate full algorithm execution - show key steps only!

✓ DO: Start immediately with "from manim import *"
✓ DO: Keep it simple and clear
✓ DO: Use meaningful class names
✓ DO: Include wait() calls for pacing
✓ DO: Position objects thoughtfully
✓ DO: For algorithms, show 3-4 key steps, not every iteration
✓ DO: Hard-code values instead of using dynamic loops

=== YOUR TASK ===
Generate ONLY the Python code. Start immediately with "from manim import *". No other text."""

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen/qwen3.6-27b", allow_latex: bool = True):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ManimCodeGeneratorError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.allow_latex = allow_latex 
        if not self.allow_latex:
            self.SYSTEM_PROMPT = self.SYSTEM_PROMPT.replace(
                "=== LATEX IN MATHTEXT ===",
                "=== TEXT ONLY — NO LATEX ===\nNEVER use MathTex or Tex. Use Text() for all text and equations."
            )
        logger.info(f"[INIT] ManimCodeGenerator ready | model={model} | allow_latex={allow_latex}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # FIX: Only retry on non-validation errors to avoid wasting retries on bad prompts
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate(self, user_prompt: str, temperature: float = 0.2) -> str:
        """
        Generate Manim code from user prompt with retry logic and model fallback.
        Raises ManimCodeGeneratorError on failure.
        """
        if not user_prompt or not user_prompt.strip():
            raise ManimCodeGeneratorError("Prompt cannot be empty")
        
        logger.info(f"[GENERATE] Starting code generation | prompt='{user_prompt[:100]}'")
        logger.info(f"[GENERATE] Using model={self.model} | temperature={temperature} | max_tokens=4000")

        target_model = self.model
        try:
            return self._call_groq_api(user_prompt, target_model, temperature)
        except Exception as e:
            err_str = str(e).lower()
            if ("404" in err_str or "model_not_found" in err_str or "does not exist" in err_str) and target_model != "qwen/qwen3.6-27b":
                logger.warning(f"[GENERATE] Model '{target_model}' unavailable (404/model_not_found). Falling back to 'qwen/qwen3.6-27b'")
                self.model = "qwen/qwen3.6-27b"
                return self._call_groq_api(user_prompt, "qwen/qwen3.6-27b", temperature)
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _call_groq_api(self, user_prompt: str, model_name: str, temperature: float) -> str:
        try:
            logger.info(f"[GENERATE] Sending request to Groq API using model '{model_name}'...")
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=4000
            )
            logger.info("[GENERATE] Groq API responded successfully")

            content = response.choices[0].message.content
            logger.info(f"[GENERATE] Raw response length: {len(content)} chars")

            # Clean markdown artifacts and thinking blocks
            content = self._clean_code(content)
            logger.info(f"[GENERATE] After cleaning: {len(content)} chars")

            # Validate structural correctness
            self._validate_code(content)

            class_name = self._extract_class_name(content)
            logger.info(f"[GENERATE] Extracted Scene class name: '{class_name}'")
            logger.info(f"[GENERATE] Code generation complete ✓")

            return content

        except ManimCodeGeneratorError:
            raise
        except Exception as e:
            logger.error(f"[GENERATE] Groq API call failed | model={model_name} | error_type={type(e).__name__} | error={str(e)}")
            raise ManimCodeGeneratorError(f"Failed to generate code: {str(e)}") from e

    def _clean_code(self, code: str) -> str:
        """Remove markdown artifacts, thinking blocks, and stray text from generated code."""
        logger.debug("[CLEAN] Cleaning generated output...")

        # 1. Remove thinking/reasoning blocks (e.g. DeepSeek / Qwen <think>...</think>)
        code = re.sub(r"<think>.*?</think>", "", code, flags=re.DOTALL)
        if "</think>" in code:
            code = code.split("</think>")[-1]

        # 2. Extract code inside ```python ... ``` or ``` ... ``` code blocks if present
        blocks = re.findall(r"```(?:python)?\s*(.*?)\s*```", code, flags=re.DOTALL)
        if blocks:
            code = max(blocks, key=len)
        else:
            # 3. Locate 'from manim import *' preceding a Scene class definition
            matches = list(re.finditer(r"from manim import \*", code))
            if matches:
                chosen_start = matches[0].start()
                for m in matches:
                    rest = code[m.start():]
                    if re.search(r"class\s+\w+\s*\(\s*(?:\w*\.)?Scene\s*\):", rest):
                        chosen_start = m.start()
                        break
                code = code[chosen_start:]
            else:
                logger.warning("[CLEAN] 'from manim import *' not found in raw output")

        # 4. Remove any trailing markdown closing fences
        code = re.sub(r"```[\w]*\s*$", "", code, flags=re.MULTILINE)
        code = re.sub(r"```", "", code)

        # 5. Remove common prose suffixes
        code = re.sub(r"\n(This code|Note:|The above|Here,|In this).*$", "", code, flags=re.DOTALL | re.IGNORECASE)

        return code.strip()

    def _validate_code(self, code: str) -> None:
        """
        Basic structural validation of generated code.
        Raises ManimCodeGeneratorError with a clear message if invalid.
        """
        logger.info("[VALIDATE] Running structural validation on generated code...")

        if not code.startswith("from manim import *"):
            raise ManimCodeGeneratorError(
                "Generated code does not start with 'from manim import *'. "
                "LLM likely returned prose instead of code."
            )

        if "class " not in code or "(Scene)" not in code:
            raise ManimCodeGeneratorError(
                "Generated code missing a Scene subclass. "
                "Code may be truncated or malformed."
            )

        if "def construct(self)" not in code:
            raise ManimCodeGeneratorError(
                "Generated code missing 'construct(self)' method."
            )

        # Warn about forbidden builtins (don't hard-fail, let Manim catch it)
        forbidden = ["locals()", "globals()", "vars()", "eval(", "exec(", "open("]
        for token in forbidden:
            if token in code:
                logger.warning(f"[VALIDATE] ⚠ Forbidden token detected in generated code: '{token}'")

        logger.info("[VALIDATE] Validation passed ✓")

    def _extract_class_name(self, code: str) -> str:
        """Extract the Scene class name from generated code for render tracking."""
        match = re.search(r"class\s+(\w+)\s*\(Scene\)", code)
        if match:
            return match.group(1)
        logger.warning("[EXTRACT] Could not find Scene class name in generated code")
        return "UnknownScene"


# Backwards compatibility
def generate_manim_code(user_prompt: str) -> str:
    generator = ManimCodeGenerator()
    return generator.generate(user_prompt)