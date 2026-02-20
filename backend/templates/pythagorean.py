"""
Pythagorean Theorem — deterministic Manim template.
Shows a right triangle with squares on each side and the a² + b² = c² equation.
"""

TEMPLATE_CODE = r'''from manim import *

class PythagoreanScene(Scene):
    def construct(self):
        # Title
        title = Text("Pythagorean Theorem", font_size=40, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=1)

        # Right triangle
        a_len = 2.0
        b_len = 1.5
        A = ORIGIN
        B = RIGHT * a_len
        C = RIGHT * a_len + UP * b_len

        triangle = Polygon(A, B, C, color=WHITE, stroke_width=3)
        triangle.move_to(ORIGIN)

        # Shift triangle to center-left so squares fit
        triangle.shift(LEFT * 0.5 + DOWN * 0.5)
        A, B, C = triangle.get_vertices()

        self.play(Create(triangle), run_time=1)

        # Side labels
        label_a = Text("a", font_size=28, color=BLUE).next_to(
            Line(A, B), DOWN, buff=0.2
        )
        label_b = Text("b", font_size=28, color=GREEN).next_to(
            Line(B, C), RIGHT, buff=0.2
        )
        label_c = Text("c", font_size=28, color=RED).next_to(
            Line(A, C), LEFT, buff=0.2
        )
        self.play(
            FadeIn(label_a), FadeIn(label_b), FadeIn(label_c), run_time=0.8
        )

        # Squares on each side
        sq_a = Square(side_length=a_len, color=BLUE, fill_opacity=0.15, stroke_width=2)
        sq_a.next_to(Line(A, B), DOWN, buff=0)
        sq_a.align_to(A, LEFT)

        sq_b = Square(side_length=b_len, color=GREEN, fill_opacity=0.15, stroke_width=2)
        sq_b.next_to(Line(B, C), RIGHT, buff=0)
        sq_b.align_to(B, DOWN)

        self.play(Create(sq_a), Create(sq_b), run_time=1)

        # Right angle indicator
        right_angle = RightAngle(
            Line(A, B), Line(B, C), length=0.25, color=YELLOW
        )
        self.play(Create(right_angle), run_time=0.5)

        self.wait(0.5)

        # Equation
        equation = Text("a² + b² = c²", font_size=36, color=YELLOW)
        equation.to_edge(DOWN, buff=0.8)
        self.play(Write(equation), run_time=1)

        self.wait(1)

        # Highlight
        box = SurroundingRectangle(equation, color=YELLOW, buff=0.15)
        self.play(Create(box), run_time=0.6)

        self.wait(2)
'''
