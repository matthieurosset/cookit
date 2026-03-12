import html
import json
import re
import unicodedata

import requests
from bs4 import BeautifulSoup


def fetch_recipe(url):
    """Fetch and parse a recipe from a URL using Schema.org/JSON-LD."""
    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; Cookit/1.0)',
            'Accept-Charset': 'utf-8',
        })
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or 'utf-8'
    except requests.RequestException:
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    recipe_data = _extract_jsonld(soup)

    if not recipe_data:
        return None

    return {
        'title': _clean_text(recipe_data.get('name', '')),
        'ingredients': _parse_ingredients(recipe_data.get('recipeIngredient', [])),
        'steps': _parse_steps(recipe_data.get('recipeInstructions', [])),
        'portions': _parse_yield(recipe_data.get('recipeYield')),
        'prep_time': _parse_duration(recipe_data.get('prepTime')),
        'cook_time': _parse_duration(recipe_data.get('cookTime')),
        'image_url': _parse_image(recipe_data.get('image')),
        'source_url': url,
    }


def _clean_text(text):
    """Clean text: decode HTML entities, normalize unicode, strip whitespace."""
    if not text:
        return ''
    text = str(text)
    text = html.unescape(text)
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _extract_jsonld(soup):
    """Find Recipe in JSON-LD scripts."""
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue

        recipe = _find_recipe(data)
        if recipe:
            return recipe
    return None


def _find_recipe(data):
    """Recursively find a Recipe object in JSON-LD data."""
    if isinstance(data, dict):
        if data.get('@type') == 'Recipe' or (
            isinstance(data.get('@type'), list) and 'Recipe' in data['@type']
        ):
            return data
        if '@graph' in data:
            return _find_recipe(data['@graph'])
    elif isinstance(data, list):
        for item in data:
            result = _find_recipe(item)
            if result:
                return result
    return None


def _parse_ingredients(ingredients):
    """Parse ingredient strings into structured data."""
    parsed = []
    for text in ingredients:
        text = _clean_text(text)
        if not text:
            continue

        # Try to parse "quantity unit name" pattern
        match = re.match(
            r'^([\d.,/\s]+)\s*'  # quantity
            r'(g|kg|ml|cl|l|cs|cc|c\.\s*à\s*s\.?|c\.\s*à\s*c\.?|cuillères?\s*à\s*soupe|cuillères?\s*à\s*café|pincées?|sachets?|tranches?|gousses?|verres?|tasses?|pièces?|bouquets?|brins?|feuilles?|bottes?|poignées?|tablespoons?|teaspoons?|cups?|oz|lb|pieces?)?\s*'  # unit (optional)
            r'(?:de\s+|d\')?'  # French "de/d'" connector
            r'(.+)',  # name
            text, re.IGNORECASE
        )

        if match:
            qty = match.group(1).strip()
            unit = (match.group(2) or '').strip()
            name = match.group(3).strip()
            parsed.append({'name': name, 'quantity': qty, 'unit': unit})
        else:
            parsed.append({'name': text, 'quantity': '', 'unit': ''})

    return parsed


def _parse_steps(instructions):
    """Parse recipeInstructions (can be strings or HowToStep objects)."""
    steps = []
    if isinstance(instructions, str):
        for line in instructions.split('\n'):
            cleaned = _clean_text(line)
            if cleaned:
                steps.append(cleaned)
        return steps

    for item in instructions:
        if isinstance(item, str):
            cleaned = _clean_text(item)
            if cleaned:
                steps.append(cleaned)
        elif isinstance(item, dict):
            text = item.get('text', '')
            cleaned = _clean_text(text)
            if cleaned:
                steps.append(cleaned)
            elif 'itemListElement' in item:
                for sub in item['itemListElement']:
                    if isinstance(sub, dict) and sub.get('text'):
                        cleaned = _clean_text(sub['text'])
                        if cleaned:
                            steps.append(cleaned)
                    elif isinstance(sub, str):
                        cleaned = _clean_text(sub)
                        if cleaned:
                            steps.append(cleaned)
    return steps


def _parse_duration(duration):
    """Parse ISO 8601 duration to minutes."""
    if not duration:
        return None
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', str(duration))
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return hours * 60 + minutes
    return None


def _parse_yield(recipe_yield):
    """Parse recipeYield to integer portions."""
    if not recipe_yield:
        return 4
    if isinstance(recipe_yield, list):
        recipe_yield = recipe_yield[0] if recipe_yield else '4'
    text = str(recipe_yield)
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 4


def _parse_image(image):
    """Extract image URL from various formats."""
    if not image:
        return None
    if isinstance(image, str):
        return image
    if isinstance(image, list):
        return image[0] if image else None
    if isinstance(image, dict):
        return image.get('url')
    return None
