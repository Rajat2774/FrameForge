"""
Equation — deterministic Manim template for mathematical equations.
Shows famous equations using Text (LaTeX-free) with step-by-step reveal.
"""

TEMPLATE_CODE = r'''from manim import *

class FamousEquationsScene(Scene):
    def construct(self):
        title = Text("Famous Equations", font_size=38, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        equations = [
            ("Einstein's Mass-Energy", "E = mc²", BLUE),
            ("Pythagorean Theorem", "a² + b² = c²", GREEN),
            ("Euler's Identity", "e^(iπ) + 1 = 0", YELLOW),
            ("Newton's Second Law", "F = ma", RED),
        ]

        prev_group = None

        for i, (name, eq_text, color) in enumerate(equations):
            label = Text(name, font_size=22, color=GREY_B)
            eq = Text(eq_text, font_size=44, color=color)
            group = VGroup(label, eq).arrange(DOWN, buff=0.3)
            group.move_to(ORIGIN)

            if prev_group:
                self.play(FadeOut(prev_group, shift=UP * 0.5), run_time=0.5)

            self.play(FadeIn(group, shift=UP * 0.3), run_time=0.8)
            self.wait(1.5)

            prev_group = group

        # Final flourish — box the last equation
        box = SurroundingRectangle(prev_group, color=YELLOW, buff=0.2)
        self.play(Create(box), run_time=0.6)
        self.wait(1.5)
'''


QUADRATIC_FORMULA_TEMPLATE = r'''from manim import *

class QuadraticFormulaScene(Scene):
    def construct(self):
        title = Text("The Quadratic Formula", font_size=38, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # Step 1: General form
        step1_label = Text("General form:", font_size=22, color=GREY_B)
        step1 = Text("ax² + bx + c = 0", font_size=36, color=BLUE)
        g1 = VGroup(step1_label, step1).arrange(DOWN, buff=0.2)
        g1.move_to(ORIGIN + UP * 0.5)

        self.play(FadeIn(g1, shift=UP * 0.3), run_time=0.8)
        self.wait(1)

        # Step 2: Solution
        step2_label = Text("Solution:", font_size=22, color=GREY_B)
        step2 = Text("x = (-b ± √(b²-4ac)) / 2a", font_size=32, color=YELLOW)
        g2 = VGroup(step2_label, step2).arrange(DOWN, buff=0.2)
        g2.move_to(ORIGIN + DOWN * 0.5)

        self.play(FadeIn(g2, shift=UP * 0.3), run_time=1)
        self.wait(0.5)

        # Animate shrink old, grow new
        self.play(
            g1.animate.scale(0.7).shift(UP * 1),
            g2.animate.scale(1.2).move_to(ORIGIN),
            run_time=1,
        )

        box = SurroundingRectangle(g2, color=YELLOW, buff=0.15)
        self.play(Create(box), run_time=0.5)

        self.wait(2)
'''


EULER_TEMPLATE = r'''from manim import *

class EulerIdentityScene(Scene):
    def construct(self):
        title = Text("Euler's Identity", font_size=38, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        subtitle = Text('"The most beautiful equation in mathematics"',
                        font_size=18, color=GREY_B, slant=ITALIC)
        subtitle.next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(subtitle), run_time=0.5)

        eq = Text("e^(iπ) + 1 = 0", font_size=56, color=WHITE)
        eq.move_to(ORIGIN)
        self.play(Write(eq), run_time=2)
        self.wait(0.5)

        # Highlight each component
        parts = [
            ("e — Euler's number (2.718...)", BLUE, 0),
            ("i — Imaginary unit (√-1)", GREEN, 1),
            ("π — Pi (3.14159...)", YELLOW, 2),
            ("1 — Unity", RED, 3),
            ("0 — Nothingness", PURPLE, 4),
        ]

        annotations = VGroup()
        for text, color, idx in parts:
            note = Text(text, font_size=18, color=color)
            annotations.add(note)

        annotations.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        annotations.next_to(eq, DOWN, buff=0.8)

        for note in annotations:
            self.play(FadeIn(note, shift=LEFT * 0.3), run_time=0.5)

        self.wait(0.5)

        box = SurroundingRectangle(eq, color=GOLD, buff=0.15, corner_radius=0.1)
        self.play(Create(box), run_time=0.6)

        self.wait(2)
'''
