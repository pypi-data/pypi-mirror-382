from manim import Scene, VGroup, DOWN, UP, FadeIn, Write, ScaleInPlace, PI
from .text import create_fa_text

class FaTextScene(Scene):
    def construct(self):
        line1 = create_fa_text("اولین انیمیشن فارسی", color="BLUE", font_size=70)
        line2 = create_fa_text("در حال ایجاد افزونه", translit=True, color="GREEN", font_size=70)
        line3 = create_fa_text("این خط ایتالیک است", color="RED", font_size=70, slant="ITALIC")

        text_group = VGroup(line1, line2, line3).arrange(DOWN).shift(UP)
        self.play(FadeIn(text_group))
        self.wait(2)