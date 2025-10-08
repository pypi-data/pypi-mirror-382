from manim import Text, VGroup
from .fonts import get_persian_font
from .translit import translit_to_fa
from .layout import arrange_rtl

def create_fa_text(
    content,
    font=None,
    font_size=48,
    color="WHITE",
    weight=None,
    slant=None,
    translit=False,
    rtl=True,
    **kwargs
):
    if translit:
        content = translit_to_fa(content)

    font = get_persian_font(font)
    text = Text(content, font=font, font_size=font_size, color=color, **kwargs)

    if weight:
        text.set_weight(weight)
    if slant:
        text.set_slant(slant)

    if rtl:
        text.submobjects.reverse()

    return text