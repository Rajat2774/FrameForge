from manim import *

class PythagoreanTheorem(Scene):
    def construct(self):
        triangle = Polygon([0,0,0], [3,0,0], [3,4,0], color=BLUE)
        a = Line([0,0,0], [3,0,0], color=RED)
        b = Line([3,0,0], [3,4,0], color=GREEN)
        c = Line([0,0,0], [3,4,0], color=YELLOW)
        equation = MathTex("a^2 + b^2 = c^2").next_to(triangle, DOWN)
        a_label = MathTex("a").next_to(a, DOWN)
        b_label = MathTex("b").next_to(b, RIGHT)
        c_label = MathTex("c").next_to(c, UR)
        self.play(Create(triangle))
        self.play(Create(a), Create(b), Create(c))
        self.play(Write(equation))
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(2)