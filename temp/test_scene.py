from manim import *

class TestScene(Scene):
    def construct(self):
        text = Text("Hello Animation!")
        self.play(Write(text))
        self.wait(1)
