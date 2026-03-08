def test_shopping_index(client):
    resp = client.get('/courses')
    assert resp.status_code == 200
    assert 'Courses' in resp.data.decode()


def test_add_item(client):
    resp = client.post('/courses/ajouter', data={
        'name': 'Tomates',
        'quantity': '500',
        'unit': 'g',
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_toggle_item(client):
    client.post('/courses/ajouter', data={'name': 'Lait'})
    resp = client.patch('/courses/item/1/toggle')
    assert resp.status_code in (200, 204)


def test_clear_all(client):
    client.post('/courses/ajouter', data={'name': 'Pain'})
    resp = client.post('/courses/vider', follow_redirects=True)
    assert resp.status_code == 200


def test_add_recipe_to_list(client):
    # Create a recipe first
    client.post('/recettes/nouvelle', data={
        'title': 'Pates carbo',
        'portions': '4',
        'ing_name': ['pates', 'lardons'],
        'ing_qty': ['500', '200'],
        'ing_unit': ['g', 'g'],
        'step': ['Cuire'],
    })
    # Add recipe items
    resp = client.post('/courses/ajouter-recette', data={
        'recipe_id': '1',
        'portions': '4',
    }, follow_redirects=True)
    assert resp.status_code == 200
