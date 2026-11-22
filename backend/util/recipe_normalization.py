"""Provider-independent text, ingredient identity and measurement rules."""
import re
from fractions import Fraction
from html.parser import HTMLParser

from util.ingredient_names_v1 import ingredient_key, ingredient_aliases


class RecipeText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden = True
        elif tag in ("br", "li", "p", "div", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = False
        elif tag in ("li", "p", "div", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def plain_text(value):
    parser = RecipeText()
    parser.feed(value or "")
    parser.close()
    lines = (" ".join(line.split()) for line in "".join(parser.parts).splitlines())
    return "\n".join(filter(None, lines))


def instruction_sections(value):
    if isinstance(value, list):
        sections = []
        for section in value:
            steps = [plain_text(step["step"]) for step in section.get("steps", [])]
            if any(steps):
                sections.append({"name": plain_text(section.get("name")), "steps": list(filter(None, steps))})
        return sections
    result = []
    heading = ""
    for index, part in enumerate(re.split(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", value or "", flags=re.I | re.S)):
        if index % 2:
            heading = plain_text(part)
        else:
            steps = list(filter(None, re.split(r"(?:^|\s+)\d+\.\s+|\n+", plain_text(part))))
            if steps:
                result.append({"name": heading, "steps": steps})
    return result


# Each factor converts to grams or millilitres. Unqualified cups and spoons vary by region.
FACTORS = {}
for names, base, factor in [
    ("g gram grams", "g", "1"), ("kg kilogram kilograms", "g", "1000"),
    ("mg milligram milligrams", "g", ".001"), ("oz ounce ounces", "g", "28.349523125"),
    ("lb lbs pound pounds", "g", "453.59237"), ("ml milliliter milliliters millilitre millilitres", "mL", "1"),
    ("l liter liters litre litres", "mL", "1000"),
]:
    for name in names.split():
        FACTORS[name] = (base, Fraction(factor))


def measurement(quantity, unit):
    if quantity is None or not str(quantity).strip():
        return None
    parts = re.split(r"\s*(?:\u2013|-|\bto\b)\s*", str(quantity))
    if len(parts) > 2 or any(not part.strip() for part in parts):
        return None
    try:
        numbers = [sum(Fraction(piece) for piece in part.split()) for part in parts]
    except (ValueError, ZeroDivisionError):
        return None
    base, factor = FACTORS.get((unit or "").lower(), (unit or "", 1))
    return [number * factor for number in numbers], base


def format_measure(numbers, unit):
    if unit in ("g", "mL") and min(numbers) >= 1000:
        numbers = [number / 1000 for number in numbers]
        unit = "kg" if unit == "g" else "L"
    def readable(number):
        if unit not in ("kg", "g", "L", "mL") and number.denominator != 1:
            return str(number)
        return format(float(number), ".4g") if number else "0"
    return " ".join(filter(None, ["–".join(map(readable, numbers)), unit]))


def display_amount(quantity, unit):
    parsed = measurement(quantity, unit)
    return format_measure(*parsed) if parsed else " ".join(filter(None, [quantity, unit]))
