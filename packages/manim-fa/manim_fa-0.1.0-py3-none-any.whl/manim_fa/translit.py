LATIN_TO_PERSIAN = {
    "kh": "خ", "gh": "غ", "ch": "چ", "sh": "ش", "th": "ث",
    "a": "ا", "b": "ب", "c": "ک", "d": "د", "e": "ِ", "f": "ف", "g": "گ",
    "h": "ه", "i": "ی", "j": "ج", "k": "ک", "l": "ل", "m": "م", "n": "ن",
    "o": "و", "p": "پ", "q": "ق", "r": "ر", "s": "س", "t": "ت", "u": "و",
    "v": "و", "w": "و", "x": "کس", "y": "ی", "z": "ز",
}

def translit_to_fa(text: str) -> str:
    result = text.lower()
    for latin, persian in sorted(LATIN_TO_PERSIAN.items(), key=lambda x: -len(x[0])):
        result = result.replace(latin, persian)
    return result