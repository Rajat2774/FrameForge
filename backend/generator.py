import os
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
✗ file operations
✗ network requests
✗ Multiple Scene classes

=== AVAILABLE OBJECTS (ONLY USE THESE) ===
Shapes: Circle, Square, Rectangle, Triangle, Polygon, RegularPolygon, Star, Ellipse, Annulus, Sector
Text: Text,MarkupText
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

All coordinates must be 3D: (x, y, 0)
Never use (x, y)

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

=== LATEX IN MATHTEXT ===
Use raw strings with double backslashes:
MathTex(r"\\frac{a}{b}") for fractions
MathTex(r"\\sqrt{x}") for square root
MathTex(r"x^2") for superscript
MathTex(r"x_1") for subscript
MathTex(r"\\alpha") for Greek letters

NEVER USE:
MathTex
Tex
LaTeX
always_redraw
updaters
ValueTracker
lambda animations
np.sin
np.cos
import numpy


=== COMMON MISTAKES TO AVOID ===
❌ DON'T: Add explanations → "Here's the code:"
❌ DON'T: Use markdown → ```python
❌ DON'T: Use print statements
❌ DON'T: Create helper functions outside construct()
❌ DON'T: Use complex loops without clear purpose
❌ DON'T: Forget self.wait() at the end

✓ DO: Start immediately with "from manim import *"
✓ DO: Keep it simple and clear
✓ DO: Use meaningful class names
✓ DO: Include wait() calls for pacing
✓ DO: Position objects thoughtfully

=== YOUR TASK ===
Generate ONLY the Python code. Start immediately with "from manim import *". No other text."""

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the Manim code generator.
        
        Args:
            api_key: Groq API key (if None, reads from environment)
            model: LLM model to use
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ManimCodeGeneratorError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        logger.info(f"Initialized ManimCodeGenerator with model: {model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate(self, user_prompt: str, temperature: float = 0.2) -> str:
        """
        Generate Manim code from user prompt with retry logic.
        
        Args:
            user_prompt: User's description of desired animation
            temperature: LLM temperature (0.0-1.0)
            
        Returns:
            Generated Python code as string
            
        Raises:
            ManimCodeGeneratorError: If generation fails after retries
        """
        if not user_prompt or not user_prompt.strip():
            raise ManimCodeGeneratorError("Prompt cannot be empty")
        
        logger.info(f"Generating code for prompt: '{user_prompt[:100]}...'")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Clean up markdown artifacts
            content = self._clean_code(content)
            
            logger.info(f"Successfully generated code ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise ManimCodeGeneratorError(f"Failed to generate code: {str(e)}")

    def _clean_code(self, code: str) -> str:
        """Remove markdown artifacts from generated code."""
        # Remove markdown code blocks
        code = re.sub(r"```python\s*", "", code)
        code = re.sub(r"```\s*", "", code)
        
        # Remove common prefixes
        code = re.sub(r"^Here'?s? the code:?\s*\n", "", code, flags=re.IGNORECASE)
        code = re.sub(r"^Here you go:?\s*\n", "", code, flags=re.IGNORECASE)
        
        return code.strip()


# Backwards compatibility function
def generate_manim_code(user_prompt: str) -> str:
    """
    Legacy function for backwards compatibility.
    
    Args:
        user_prompt: User's description of desired animation
        
    Returns:
        Generated Python code as string
    """
    generator = ManimCodeGenerator()
    return generator.generate(user_prompt)