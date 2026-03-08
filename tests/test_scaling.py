from app.services.scaling import parse_quantity, format_quantity, scale_ingredients


def test_parse_integer():
    assert parse_quantity('3') == 3.0


def test_parse_decimal():
    assert parse_quantity('1.5') == 1.5


def test_parse_french_decimal():
    assert parse_quantity('1,5') == 1.5


def test_parse_fraction():
    assert parse_quantity('1/2') == 0.5


def test_parse_mixed_number():
    assert parse_quantity('1 1/2') == 1.5


def test_parse_empty():
    assert parse_quantity('') is None
    assert parse_quantity(None) is None


def test_format_integer():
    assert format_quantity(4.0) == '4'


def test_format_fraction():
    assert format_quantity(0.5) == '1/2'
    assert format_quantity(0.25) == '1/4'


def test_format_mixed():
    result = format_quantity(1.5)
    assert result == '1 1/2'


def test_scale_ingredients():
    ingredients = [
        {'name': 'farine', 'quantity': '200', 'unit': 'g'},
        {'name': 'sucre', 'quantity': '100', 'unit': 'g'},
        {'name': 'sel', 'quantity': '', 'unit': ''},
    ]
    scaled = scale_ingredients(ingredients, 4, 8)
    assert scaled[0]['quantity'] == '400'
    assert scaled[1]['quantity'] == '200'
    assert scaled[2]['quantity'] == ''


def test_scale_no_change():
    ingredients = [{'name': 'test', 'quantity': '100', 'unit': 'g'}]
    scaled = scale_ingredients(ingredients, 4, 4)
    assert scaled[0]['quantity'] == '100'
