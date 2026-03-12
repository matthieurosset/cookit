import json


def test_index_page(client):
    resp = client.get('/recettes')
    assert resp.status_code == 200
    assert b'Mes recettes' in resp.data


def test_create_recipe(client):
    resp = client.post('/recettes/nouvelle', data={
        'title': 'Tarte aux pommes',
        'portions': '6',
        'prep_time': '20',
        'cook_time': '40',
        'ing_name': ['pommes', 'sucre', 'pate feuilletee'],
        'ing_qty': ['4', '100', '1'],
        'ing_unit': ['', 'g', ''],
        'step': ['Éplucher les pommes', 'Étaler la pâte', 'Enfourner 40 min'],
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Tarte aux pommes' in resp.data


def test_create_and_view_recipe(client):
    client.post('/recettes/nouvelle', data={
        'title': 'Quiche lorraine',
        'portions': '4',
        'ing_name': ['lardons', 'oeufs'],
        'ing_qty': ['200', '3'],
        'ing_unit': ['g', ''],
        'step': ['Mélanger', 'Cuire'],
    })
    resp = client.get('/recettes/1')
    assert resp.status_code == 200
    assert b'Quiche lorraine' in resp.data



def test_delete_recipe(client):
    client.post('/recettes/nouvelle', data={
        'title': 'A supprimer',
        'portions': '4',
        'ing_name': ['test'],
        'ing_qty': ['1'],
        'ing_unit': [''],
        'step': ['Test'],
    })
    resp = client.post('/recettes/1/supprimer', follow_redirects=True)
    assert resp.status_code == 200


def test_search_htmx(client):
    client.post('/recettes/nouvelle', data={
        'title': 'Ratatouille',
        'portions': '4',
        'ing_name': ['aubergine'],
        'ing_qty': ['2'],
        'ing_unit': [''],
        'step': ['Cuire'],
    })
    resp = client.get('/recettes?q=rata', headers={'HX-Request': 'true'})
    assert resp.status_code == 200
    assert b'Ratatouille' in resp.data


def test_random_no_recipes(client):
    resp = client.get('/recettes/hasard', follow_redirects=True)
    assert resp.status_code == 200


def test_scaled_ingredients(client):
    client.post('/recettes/nouvelle', data={
        'title': 'Test scaling',
        'portions': '4',
        'ing_name': ['farine'],
        'ing_qty': ['200'],
        'ing_unit': ['g'],
        'step': ['Mélanger'],
    })
    resp = client.get('/recettes/1/ingredients?portions=8')
    assert resp.status_code == 200
    assert b'400' in resp.data
