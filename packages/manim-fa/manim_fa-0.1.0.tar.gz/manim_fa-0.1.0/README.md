# manim-fa

Plugin Manim pour le texte persan (RTL) avec translittération automatique.

## Installation

```bash
pip install manim-fa
```

## Utilisation

```python
from manim import *
from manim_fa import create_fa_text

class Demo(Scene):
    def construct(self):
        # Texte persan direct
        t1 = create_fa_text("سلام دنیا!", color="BLUE", font_size=70)
        
        # Texte translittéré
        t2 = create_fa_text("salam manim fa", translit=True, color="GREEN", font_size=70)
        
        self.play(Write(t1))
        self.play(Transform(t1, t2))
        self.wait(2)
```

## Alignement RTL
Pour gérer plusieurs lignes :

```python
from manim_fa.layout import arrange_rtl
text_group = VGroup(line1, line2, line3)
arrange_rtl(text_group)
```