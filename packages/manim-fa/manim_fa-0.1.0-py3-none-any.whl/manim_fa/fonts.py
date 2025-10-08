import os
import platform
from pathlib import Path

_DEFAULT_FONTS = ["IRLotus", "XB Niloofar", "Vazir", "Tahoma"]

def _font_installed(font_name: str) -> bool:
    system = platform.system()
    if system == "Windows":
        font_dir = Path("C:/Windows/Fonts")
    elif system == "Darwin":
        font_dir = Path("/Library/Fonts")
    else:
        font_dir = Path("/usr/share/fonts")

    return any(font_name.lower() in f.name.lower() for f in font_dir.glob("**/*"))

def get_persian_font(preferred: str | None = None) -> str:
    candidates = [preferred] + _DEFAULT_FONTS if preferred else _DEFAULT_FONTS
    for font in candidates:
        if font and _font_installed(font):
            return font
    print("[manim-fa] ⚠️ Aucune police persane trouvée, utilisation de 'Arial'.")
    return "Arial"