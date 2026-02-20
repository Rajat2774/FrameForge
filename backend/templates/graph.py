"""
Graph templates — deterministic Manim code for function plots.
Includes sine curve, parabola, and a generic plot demonstration.

FIX: Removed `"include_numbers": True` from all axis_config dicts.
Manim renders axis tick number labels via DecimalNumber → MathTex → pdflatex.
If LaTeX is not installed (common on Windows dev machines), this crashes with:
  FileNotFoundError: [WinError 2] The system cannot find the file specified
The fix uses `x_axis_config`/`y_axis_config` with `include_numbers: False`
and adds manual plain-Text labels instead, which require no LaTeX at all.
"""

SIN_TEMPLATE = r'''from manim import *

class SinPlotScene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-1.5, 1.5, 1],
            x_length=8,
            y_length=4,
            axis_config={"include_numbers": False, "include_tip": True},
        )
        labels = axes.get_axis_labels(
            x_label=Text("x", font_size=24),
            y_label=Text("sin(x)", font_size=24),
        )
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        self.play(Create(axes), Write(labels))
        self.play(Create(sin_graph))
        self.wait(1)
'''


QUADRATIC_TEMPLATE = r'''from manim import *

class ParabolaScene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 9, 1],
            x_length=7,
            y_length=5,
            axis_config={"include_numbers": False, "include_tip": True},
        )
        labels = axes.get_axis_labels(
            x_label=Text("x", font_size=24),
            y_label=Text("x²", font_size=24),
        )
        quad = axes.plot(lambda x: x**2, color=GREEN)
        self.play(Create(axes), Write(labels))
        self.play(Create(quad))
        self.wait(1)
'''


TEMPLATE_CODE = r'''from manim import *

class GeneralPlotScene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-1.5, 1.5, 1],
            x_length=8,
            y_length=4,
            axis_config={"include_numbers": False, "include_tip": True},
        )
        labels = axes.get_axis_labels(
            x_label=Text("x", font_size=24),
            y_label=Text("y", font_size=24),
        )
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        cos_graph = axes.plot(lambda x: np.cos(x), color=YELLOW)

        sin_label = Text("sin(x)", font_size=20, color=BLUE).to_corner(UL).shift(DOWN * 0.5)
        cos_label = Text("cos(x)", font_size=20, color=YELLOW).next_to(sin_label, DOWN, buff=0.2)

        self.play(Create(axes), Write(labels))
        self.play(Create(sin_graph), Create(cos_graph))
        self.play(FadeIn(sin_label), FadeIn(cos_label))
        self.wait(1)
'''