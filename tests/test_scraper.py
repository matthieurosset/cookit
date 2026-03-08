import json

from app.services.scraper import (
    _parse_ingredients, _parse_steps, _parse_duration,
    _parse_yield, _parse_image, _find_recipe
)


def test_parse_duration_minutes():
    assert _parse_duration('PT30M') == 30


def test_parse_duration_hours_minutes():
    assert _parse_duration('PT1H30M') == 90


def test_parse_duration_hours_only():
    assert _parse_duration('PT2H') == 120


def test_parse_duration_none():
    assert _parse_duration(None) is None


def test_parse_yield_string():
    assert _parse_yield('4 personnes') == 4


def test_parse_yield_list():
    assert _parse_yield(['6']) == 6


def test_parse_yield_none():
    assert _parse_yield(None) == 4


def test_parse_image_string():
    assert _parse_image('https://example.com/img.jpg') == 'https://example.com/img.jpg'


def test_parse_image_list():
    assert _parse_image(['https://example.com/img.jpg']) == 'https://example.com/img.jpg'


def test_parse_image_dict():
    assert _parse_image({'url': 'https://example.com/img.jpg'}) == 'https://example.com/img.jpg'


def test_parse_steps_strings():
    steps = _parse_steps(['Step 1', 'Step 2'])
    assert steps == ['Step 1', 'Step 2']


def test_parse_steps_howto():
    steps = _parse_steps([
        {'@type': 'HowToStep', 'text': 'Do this'},
        {'@type': 'HowToStep', 'text': 'Then that'},
    ])
    assert steps == ['Do this', 'Then that']


def test_parse_ingredients_simple():
    result = _parse_ingredients(['200 g de farine', '3 oeufs'])
    assert len(result) == 2
    assert result[0]['name'] == 'farine'
    assert result[0]['quantity'] == '200'


def test_find_recipe_in_graph():
    data = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'WebPage'},
            {'@type': 'Recipe', 'name': 'Test'},
        ]
    }
    result = _find_recipe(data)
    assert result['name'] == 'Test'


def test_find_recipe_direct():
    data = {'@type': 'Recipe', 'name': 'Direct'}
    result = _find_recipe(data)
    assert result['name'] == 'Direct'


def test_find_recipe_list_type():
    data = {'@type': ['Recipe', 'CreativeWork'], 'name': 'Multi'}
    result = _find_recipe(data)
    assert result['name'] == 'Multi'
