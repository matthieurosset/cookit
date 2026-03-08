import re
from fractions import Fraction


def parse_quantity(text):
    """Parse a quantity string to a float. Handles integers, decimals (. or ,), fractions, mixed numbers."""
    if not text:
        return None

    text = str(text).strip()
    if not text:
        return None

    # Replace French comma decimal
    text = text.replace(',', '.')

    # Mixed number: "1 1/2"
    match = re.match(r'^(\d+)\s+(\d+)/(\d+)$', text)
    if match:
        whole, num, den = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return whole + num / den if den != 0 else float(whole)

    # Fraction: "1/2"
    match = re.match(r'^(\d+)/(\d+)$', text)
    if match:
        num, den = int(match.group(1)), int(match.group(2))
        return num / den if den != 0 else 0.0

    # Number
    try:
        return float(text)
    except ValueError:
        return None


def format_quantity(value):
    """Format a float back to a readable quantity string."""
    if value is None:
        return ''

    # Check for common fractions
    frac = Fraction(value).limit_denominator(8)
    if frac.denominator in (2, 3, 4, 8) and frac.numerator != 0:
        whole = frac.numerator // frac.denominator
        remainder = Fraction(frac.numerator % frac.denominator, frac.denominator)
        if whole > 0 and remainder:
            return f'{whole} {remainder}'
        elif remainder:
            return str(remainder)
        else:
            return str(whole)

    # Clean integer display
    if value == int(value):
        return str(int(value))

    # Round to 2 decimals
    return str(round(value, 2)).replace('.', ',')


def scale_ingredients(ingredients, original_portions, new_portions):
    """Scale ingredient quantities from original to new portions."""
    if original_portions == new_portions or original_portions == 0:
        return ingredients

    ratio = new_portions / original_portions
    scaled = []

    for ing in ingredients:
        new_ing = dict(ing)
        qty = parse_quantity(ing.get('quantity', ''))
        if qty is not None:
            new_ing['quantity'] = format_quantity(qty * ratio)
        scaled.append(new_ing)

    return scaled
