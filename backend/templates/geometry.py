"""
Geometry — deterministic Manim template for 2D geometry animations.
Circle, square, triangle, polygon, and shape transformation demos.
"""

TEMPLATE_CODE = r'''from manim import *

class GeometryShowcaseScene(Scene):
    def construct(self):
        title = Text("2D Geometry", font_size=38, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # Create shapes
        circle = Circle(radius=1.0, color=BLUE, stroke_width=3)
        square = Square(side_length=1.8, color=GREEN, stroke_width=3)
        triangle = Triangle(color=RED, stroke_width=3).scale(1.2)

        shapes = VGroup(circle, square, triangle)
        shapes.arrange(RIGHT, buff=1.2)
        shapes.move_to(ORIGIN)

        # Animate creation one by one
        for shape in shapes:
            self.play(Create(shape), run_time=0.8)

        self.wait(0.5)

        # Labels
        c_label = Text("Circle", font_size=18, color=BLUE).next_to(circle, DOWN, buff=0.3)
        s_label = Text("Square", font_size=18, color=GREEN).next_to(square, DOWN, buff=0.3)
        t_label = Text("Triangle", font_size=18, color=RED).next_to(triangle, DOWN, buff=0.3)
        self.play(FadeIn(c_label), FadeIn(s_label), FadeIn(t_label), run_time=0.6)

        self.wait(0.8)

        # Fill them in
        self.play(
            circle.animate.set_fill(BLUE, opacity=0.3),
            square.animate.set_fill(GREEN, opacity=0.3),
            triangle.animate.set_fill(RED, opacity=0.3),
            run_time=1,
        )

        self.wait(0.5)

        # Rotate all together
        all_shapes = VGroup(circle, square, triangle, c_label, s_label, t_label)
        self.play(Rotate(all_shapes, angle=PI / 4), run_time=1.5)
        self.play(Rotate(all_shapes, angle=-PI / 4), run_time=1.5)

        self.wait(1)
'''


CIRCLE_TEMPLATE = r'''from manim import *

class GrowingCircleScene(Scene):
    def construct(self):
        title = Text("Circle Animation", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # Small circle that grows
        circle = Circle(radius=0.1, color=BLUE, stroke_width=3, fill_opacity=0.2)
        circle.move_to(ORIGIN)
        self.play(Create(circle), run_time=0.5)

        # Grow it
        self.play(circle.animate.scale(15), run_time=2)
        self.wait(0.5)

        # Shrink and change color
        self.play(
            circle.animate.scale(0.3).set_color(GREEN).set_fill(GREEN, opacity=0.3),
            run_time=1.5,
        )
        self.wait(0.3)

        # Add radius line and label
        center = circle.get_center()
        edge = circle.point_at_angle(0)
        radius_line = Line(center, edge, color=YELLOW, stroke_width=2)
        r_label = Text("r", font_size=22, color=YELLOW).next_to(radius_line, DOWN, buff=0.1)

        self.play(Create(radius_line), FadeIn(r_label), run_time=0.8)
        self.wait(1)

        # Show area formula
        formula = Text("A = πr²", font_size=32, color=YELLOW)
        formula.to_edge(DOWN, buff=0.8)
        self.play(Write(formula), run_time=1)

        self.wait(2)
'''


TRANSFORM_TEMPLATE = r'''from manim import *

class ShapeTransformScene(Scene):
    def construct(self):
        title = Text("Shape Transformation", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # Square
        square = Square(side_length=2.0, color=BLUE, fill_opacity=0.3, stroke_width=3)
        square.move_to(ORIGIN)
        sq_text = Text("Square", font_size=20, color=BLUE)
        sq_text.next_to(square, DOWN, buff=0.3)
        self.play(Create(square), FadeIn(sq_text), run_time=1)
        self.wait(0.5)

        # Transform to circle
        circle = Circle(radius=1.2, color=GREEN, fill_opacity=0.3, stroke_width=3)
        circle.move_to(ORIGIN)
        ci_text = Text("Circle", font_size=20, color=GREEN)
        ci_text.next_to(circle, DOWN, buff=0.3)
        self.play(
            Transform(square, circle),
            Transform(sq_text, ci_text),
            run_time=2,
        )
        self.wait(0.5)

        # Transform to triangle
        triangle = Triangle(color=RED, fill_opacity=0.3, stroke_width=3).scale(1.5)
        triangle.move_to(ORIGIN)
        tr_text = Text("Triangle", font_size=20, color=RED)
        tr_text.next_to(triangle, DOWN, buff=0.3)
        self.play(
            Transform(square, triangle),
            Transform(sq_text, tr_text),
            run_time=2,
        )
        self.wait(0.5)

        # Transform to star (RegularPolygon with 5 points)
        star = Star(n=5, outer_radius=1.5, inner_radius=0.7, color=YELLOW,
                    fill_opacity=0.3, stroke_width=3)
        star.move_to(ORIGIN)
        st_text = Text("Star", font_size=20, color=YELLOW)
        st_text.next_to(star, DOWN, buff=0.3)
        self.play(
            Transform(square, star),
            Transform(sq_text, st_text),
            run_time=2,
        )

        self.wait(2)
'''
